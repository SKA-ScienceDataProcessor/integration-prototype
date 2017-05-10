# -*- coding: utf-8 -*-
"""Implements a simple test imaging pipeline using MPI and the OSKAR imager.

This pipeline makes dirty images from all Measurement Sets in a specified
directory, the name of which is given on the command line.

Usage: mpiexec -n <np> python mpi_imager_test.py <settings_file> <dir>

Measurement Sets are processed in a round-robin fashion on MPI cluster nodes,
so there should be enough Measurement Sets to parallelize the work effectively.
(For example, each Measurement Set could contain data for a different
frequency channel.)

The pipeline can be configured to make a separate dirty image from each
Measurement Set, or to combine the visibility data from all of them into
one dirty image. In the latter case, the visibility grids from each node are
combined into a single grid, and the image is then finalised by rank 0.
"""

from __future__ import print_function, division

from glob import glob
from os.path import join, splitext
import logging
import sys

from astropy.io import fits
import numpy
import oskar
from mpi4py import MPI
import simplejson as json


def process_input_data(filename, imager, grid_data, grid_norm, grid_weights):
    """Reads visibility data from a Measurement Set.

    The visibility grid or weights grid is updated accordingly.

    Visibility data are read from disk in blocks of size num_baselines.

    Args:
        filename (str):                    Name of Measurement Set to open.
        imager (oskar.Imager):             Handle to configured imager.
        grid_data (numpy.ndarray or None): Visibility grid to populate.
        grid_norm (float)                  Current grid normalisation.
        grid_weights (numpy.ndarray):      Weights grid to populate or read.

    Returns:
        grid_norm (float):                 Updated grid normalisation.
    """
    # Get data from the input Measurement Set.
    ms = oskar.MeasurementSet.open(filename)
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

    # Return updated grid normalisation.
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


def chunks(seq, n):
    """Splits a list into n approximately-equal-size chunks.

    Args:
        seq (array-like): Input list to split.
        n (int):          Number of chunks to return.
    """
    return [seq[i::n] for i in range(n)]


def main():
    """Runs test imaging pipeline using MPI."""
    # Check command line arguments.
    if len(sys.argv) < 2:
        raise RuntimeError(
            'Usage: mpiexec -n <np> '
            'python mpi_imager_test.py <settings_file> <dir>')

    # Get the MPI communicator and initialise broadcast variables.
    comm = MPI.COMM_WORLD
    settings = None
    inputs = None
    grid_weights = None

    # Create log.
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    if len(log.handlers) == 0:
        log.addHandler(logging.StreamHandler(sys.stdout))

    if comm.Get_rank() == 0:
        # Load pipeline settings.
        with open(sys.argv[1]) as f:
            settings = json.load(f)

        # Get a list of input Measurement Sets to process.
        data_dir = str(sys.argv[2])
        inputs = glob(join(data_dir, '*.ms')) + glob(join(data_dir, '*.MS'))
        inputs = filter(None, inputs)
        log.info('Found input Measurement Sets: %s', ', '.join(inputs))

        # Distribute the list of Measurement Sets among processors.
        inputs = chunks(inputs, comm.Get_size())

    # Broadcast settings and scatter list of input files.
    comm.barrier()
    settings = comm.bcast(settings)
    inputs = comm.scatter(inputs)

    # Record which file(s) this node is working on.
    log.debug('Rank %d, processing [%s]', comm.Get_rank(), ', '.join(inputs))

    # Create an imager and configure it.
    precision = settings['precision']
    imager = oskar.Imager(precision)
    for key, value in settings['imager'].items():
        setattr(imager, key, value)

    # Allocate a local visibility grid.
    grid_norm = 0.
    grid_dim = [imager.plane_size, imager.plane_size]
    grid_data = numpy.zeros(grid_dim,
                            dtype='c8' if precision == 'single' else 'c16')

    # Process data according to mode.
    if settings['combine']:
        if imager.weighting == 'Uniform' or imager.algorithm == 'W-projection':
            # If necessary, generate a local weights grid.
            local_weights = None
            if imager.weighting == 'Uniform':
                grid_weights = numpy.zeros(grid_dim, dtype=precision)
                local_weights = numpy.zeros(grid_dim, dtype=precision)

            # Do a first pass for uniform weighting or W-projection.
            imager.coords_only = True
            for f in inputs:
                log.info('Reading coordinates from %s', f)
                process_input_data(f, imager, None, 0.0, local_weights)
            imager.coords_only = False

            # Get maximum number of W-projection planes required.
            num_w_planes = imager.num_w_planes
            num_w_planes = comm.allreduce(num_w_planes, op=MPI.MAX)
            imager.num_w_planes = num_w_planes

            # Combine (reduce) weights grids, and broadcast the result.
            if local_weights is not None:
                comm.Allreduce(local_weights, grid_weights, op=MPI.SUM)

        # Populate the local visibility grid.
        for f in inputs:
            log.info('Reading visibilities from %s', f)
            grid_norm = process_input_data(f, imager, grid_data, grid_norm,
                                           grid_weights)

        # Combine (reduce) visibility grids.
        grid = numpy.zeros_like(grid_data)
        comm.Reduce(grid_data, grid, op=MPI.SUM)
        grid_norm = comm.reduce(grid_norm, op=MPI.SUM)

        # Finalise grid and save image.
        if comm.Get_rank() == 0:
            save_image(imager, grid, grid_norm, settings['output_file'])
            log.info('Finished. Output file is %s', settings['output_file'])
    else:
        for f in inputs:
            # Clear the grid.
            grid_norm = 0.
            grid_data.fill(0)
            if imager.weighting == 'Uniform':
                grid_weights = numpy.zeros(grid_dim, dtype=precision)

            # Do a first pass for uniform weighting or W-projection.
            if imager.weighting == 'Uniform' or \
                    imager.algorithm == 'W-projection':
                imager.coords_only = True
                log.info('Reading coordinates from %s', f)
                process_input_data(f, imager, None, 0.0, grid_weights)
                imager.coords_only = False

            # Populate the local visibility grid.
            log.info('Reading visibilities from %s', f)
            grid_norm = process_input_data(f, imager, grid_data, grid_norm,
                                           grid_weights)

            # Save image by finalising grid.
            output_file = splitext(f)[0] + '.fits'
            save_image(imager, grid_data, grid_norm, output_file)
            log.info('Finished. Output file is %s', output_file)


if __name__ == "__main__":
    main()
