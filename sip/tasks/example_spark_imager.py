# -*- coding: utf-8 -*-
"""Implements a simple test imaging pipeline using Spark and the OSKAR imager.

This pipeline makes dirty images from all Measurement Sets in a specified
directory, the name of which is given on the command line.

Usage: spark-submit spark_imager_test.py <settings_file> <dir> [partitions]

Each Measurement Set is processed on a different Spark cluster node, so there
should be enough input Measurement Sets to parallelize the work effectively.
(For example, each Measurement Set could contain data for a different
frequency channel.)

Input visibility datasets are not placed in RDDs here. Instead, the initial
RDD contains only the names of the input data files. Gridded visibilities
(or weights) are then reduced using a new RDD. If uniform weighting
is selected, the reduced weights grid is sent to cluster nodes using a
Spark Broadcast variable, before using it to make a second pass of the
data for the actual gridding.

The pipeline can be configured to make a separate dirty image from each
Measurement Set, or to combine the visibility data from all of them into
one dirty image. In the latter case, the visibility grids from each node are
combined into a single grid, and the image is then finalised by
the driver program.
"""

from __future__ import print_function, division

from functools import partial
from glob import glob
from os.path import join, splitext
import logging
import sys

from astropy.io import fits
import numpy
import oskar
import pyspark
import simplejson as json


def node_run(input_file, coords_only, bc_settings, bc_grid_weights):
    """Main function to process visibility data on Spark cluster nodes.

    Args:
        input_file (str):
            RDD element containing filename to process.
        coords_only (boolean):
            If true, read only baseline coordinates to define the weights grid.
        bc_settings (pyspark.broadcast.Broadcast):
            Spark broadcast variable containing pipeline settings dictionary.
        bc_grid_weights (pyspark.broadcast.Broadcast):
            Spark broadcast variable containing weights grid. May be None.

    Returns:
        tuple: Output RDD element.
    """
    # Create a logger.
    log = logging.getLogger('pyspark')
    log.setLevel(logging.INFO)
    if len(log.handlers) == 0:
        log.addHandler(logging.StreamHandler(sys.stdout))

    # Create an imager and configure it.
    precision = bc_settings.value['precision']
    imager = oskar.Imager(precision)
    for key, value in bc_settings.value['imager'].items():
        setattr(imager, key, value)
    grid_size = imager.plane_size
    grid_weights = None

    # Get a handle to the input Measurement Set.
    ms_han = oskar.MeasurementSet.open(input_file)

    # Check if doing a first pass.
    if coords_only:
        # If necessary, generate a local weights grid.
        if imager.weighting == 'Uniform':
            grid_weights = numpy.zeros([grid_size, grid_size], dtype=precision)

        # Do a first pass for uniform weighting or W-projection.
        log.info('Reading coordinates from %s', input_file)
        imager.coords_only = True
        process_input_data(ms_han, imager, None, grid_weights)
        imager.coords_only = False

        # Return weights grid and required number of W-planes as RDD element.
        return grid_weights, imager.num_w_planes

    # Allocate a local visibility grid on the node.
    grid_data = numpy.zeros([grid_size, grid_size],
                            dtype='c8' if precision == 'single' else 'c16')

    # Process data according to mode.
    log.info('Reading visibilities from %s', input_file)
    if bc_settings.value['combine']:
        # Get weights grid from Spark Broadcast variable.
        if imager.weighting == 'Uniform':
            grid_weights = bc_grid_weights.value

        # Populate the local visibility grid.
        grid_norm = process_input_data(ms_han, imager, grid_data, grid_weights)

        # Return grid as RDD element.
        log.info('Returning gridded visibilities to RDD')
        return grid_data, grid_norm
    else:
        # If necessary, generate a local weights grid.
        if imager.weighting == 'Uniform':
            grid_weights = numpy.zeros([grid_size, grid_size], dtype=precision)

        # If necessary, do a first pass for uniform weighting or W-projection.
        if imager.weighting == 'Uniform' or imager.algorithm == 'W-projection':
            imager.coords_only = True
            process_input_data(ms_han, imager, None, grid_weights)
            imager.coords_only = False

        # Populate the local visibility grid.
        grid_norm = process_input_data(ms_han, imager, grid_data, grid_weights)

        # Save image by finalising grid.
        output_file = splitext(input_file)[0] + '.fits'
        save_image(imager, grid_data, grid_norm, output_file)
        log.info('Finished. Output file is %s', output_file)
        return 0


def process_input_data(ms, imager, grid_data, grid_weights):
    """Reads visibility data from a Measurement Set.

    The visibility grid or weights grid is updated accordingly.

    Visibility data are read from disk in blocks of size num_baselines.

    Args:
        ms (oskar.MeasurementSet):         Handle to opened Measurement Set.
        imager (oskar.Imager):             Handle to configured imager.
        grid_data (numpy.ndarray or None): Visibility grid to populate.
        grid_weights (numpy.ndarray):      Weights grid to populate or read.

    Returns:
        grid_norm (float):                 Grid normalisation.
    """
    # Get data from the input Measurement Set.
    grid_norm = 0.
    block_start = 0
    num_rows = ms.num_rows
    num_baselines = ms.num_stations * (ms.num_stations - 1) // 2

    # Loop over data blocks of size num_baselines.
    while block_start < num_rows:
        block_size = num_rows - block_start
        if block_size > num_baselines:
            block_size = num_baselines

        # Get the baseline coordinates. (Replace this with a query to LTS.)
        uvw = ms.read_column('UVW', block_start, block_size)

        # Read the Stokes-I visibility weights.
        vis_weights = ms.read_column('WEIGHT', block_start, block_size)
        if ms.num_pols == 4:
            vis_weights = 0.5 * (vis_weights[:, 0] + vis_weights[:, 3])

        # Loop over frequency channels.
        # (We expect there to be only one channel here, but loop just in case.)
        for j in range(ms.num_channels):
            # Get coordinates in wavelengths.
            coords = uvw * (ms.freq_start_hz + j * ms.freq_inc_hz) / 299792458.

            # Get the Stokes-I visibilities for this channel.
            vis_data = None
            if not imager.coords_only:
                vis_data = ms.read_vis(block_start, j, 1, block_size)
                if ms.num_pols == 4:
                    vis_data = 0.5 * (vis_data[0, :, 0] + vis_data[0, :, 3])

            # Update the grid plane with this visibility block.
            grid_norm = imager.update_plane(
                coords[:, 0], coords[:, 1], coords[:, 2], vis_data,
                vis_weights, grid_data, grid_norm, grid_weights)

        # Increment start row by block size.
        block_start += block_size

    # Return grid normalisation.
    return grid_norm


def save_image(imager, grid_data, grid_norm, output_file):
    """Makes an image from gridded visibilities and saves it to a FITS file.

    Args:
        imager (oskar.Imager):          Handle to configured imager.
        grid_data (numpy.ndarray):      Final visibility grid.
        grid_norm (float):              Grid normalisation to apply.
        output_file (str):              Name of output FITS file to write.
    """
    # Make the image (take the FFT, normalise, and apply grid correction).
    imager.finalise_plane(grid_data, grid_norm)
    grid_data = numpy.real(grid_data)

    # Trim the image if required.
    border = (imager.plane_size - imager.image_size) // 2
    if border > 0:
        end = border + imager.image_size
        grid_data = grid_data[border:end, border:end]

    # Write the FITS file.
    hdr = fits.header.Header()
    fits.writeto(output_file, grid_data, hdr, clobber=True)


def reduce_sequences(object_a, object_b):
    """Performs an element-wise addition of sequences into a new list.

    Both sequences must have the same length, and the addition operator must be
    defined for each element of the sequence.
    """
    def is_seq(obj):
        """Returns true if the object passed is a sequence."""
        return hasattr(obj, "__getitem__") or hasattr(obj, "__iter__")
    if object_a is None or object_b is None:
        return None
    elif is_seq(object_a) and is_seq(object_b):
        reduced = []
        for element_a, element_b in zip(object_a, object_b):
            if element_a is not None and element_b is not None:
                reduced.append(element_a + element_b)
            else:
                reduced.append(None)
        return reduced
    else:
        return object_a + object_b


def main():
    """Runs test imaging pipeline using Spark."""
    # Check command line arguments.
    if len(sys.argv) < 3:
        raise RuntimeError(
            'Usage: spark-submit spark_imager_test.py <settings_file> <dir> '
            '[partitions]')

    # Create log object.
    log = logging.getLogger('pyspark')
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler(sys.stdout))

    # Load pipeline settings.
    with open(sys.argv[1]) as f:
        settings = json.load(f)

    # Get a list of input Measurement Sets to process.
    data_dir = str(sys.argv[2])
    inputs = glob(join(data_dir, '*.ms')) + glob(join(data_dir, '*.MS'))
    inputs = filter(None, inputs)
    log.info('Found input Measurement Sets: %s', ', '.join(inputs))

    # Get a Spark context.
    context = pyspark.SparkContext(appName="spark_imager_test")

    # Create the Spark RDD containing the input filenames,
    # suitably parallelized.
    partitions = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    rdd = context.parallelize(inputs, partitions)

    # Define Spark broadcast variables.
    bc_settings = context.broadcast(settings)
    bc_grid_weights = None

    # Process coordinates first if required.
    if (settings['combine'] and (
            settings['imager']['weighting'] == 'Uniform' or
            settings['imager']['algorithm'] == 'W-projection')):
        # Create RDD to generate weights grids.
        rdd_coords = rdd.map(
            partial(node_run, coords_only=True, bc_settings=bc_settings,
                    bc_grid_weights=None))

        # Mark this RDD as persistent so it isn't computed more than once.
        rdd_coords.persist()

        # Get the maximum number of W-planes required, and update settings.
        num_w_planes = rdd_coords.map(lambda x: x[1]).max()
        settings['imager']['num_w_planes'] = num_w_planes

        # Get the combined grid of weights and broadcast it to nodes.
        output = rdd_coords.reduce(reduce_sequences)
        bc_grid_weights = context.broadcast(output[0])

        # Delete this RDD.
        rdd_coords.unpersist()

    # Re-broadcast updated settings.
    bc_settings = context.broadcast(settings)

    # Run parallel pipeline on worker nodes and combine visibility grids.
    output = rdd.map(
        partial(node_run, coords_only=False, bc_settings=bc_settings,
                bc_grid_weights=bc_grid_weights)).reduce(reduce_sequences)

    # Finalise combined visibility grids if required.
    if settings['combine']:
        # Create an imager to finalise (FFT) the gridded data.
        imager = oskar.Imager(settings['precision'])
        for key, value in settings['imager'].items():
            setattr(imager, key, value)

        # Finalise grid and save image.
        save_image(imager, output[0], output[1], settings['output_file'])
        log.info('Finished. Output file is %s', settings['output_file'])

    context.stop()


if __name__ == "__main__":
    main()
