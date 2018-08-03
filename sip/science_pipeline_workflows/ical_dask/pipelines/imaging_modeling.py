# -*- coding: utf-8 -*-
"""Dask workflow for generating model data for the SIP example ICAL workflow.

This is code based on the test ICAL pipeline notebook from ARL.
"""
import logging
import pickle
import os

import numpy

from astropy import units as u
from astropy.coordinates import SkyCoord

from data_models.data_model_helpers import export_blockvisibility_to_hdf5
from data_models.polarisation import PolarisationFrame

from processing_components.component_support.arlexecute import arlexecute
from processing_components.component_support.dask_init import get_dask_Client
from processing_components.imaging.base import advise_wide_field
from processing_components.imaging.imaging_components import predict_component
from processing_components.util.support_components import corrupt_component, \
    simulate_component
from processing_components.util.testing_support import \
    create_low_test_image_from_gleam


LOG = logging.getLogger('sip.ical.generate_data')
RESULTS_DIR = 'results'
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)


def init_logging():
    """Initialise Python logging."""
    # fmt = '%(thread)s %(asctime)s,%(msecs)d %(name)s %(levelname)s ' \
    #       '%(message)s'
    # logging.basicConfig(filename='%s/imaging_modeling.log' % RESULTS_DIR,
    #                     filemode='a', format=fmt, datefmt='%H:%M:%S',
    #                     level=logging.INFO)
    fmt = '%(asctime)s.%(msecs)03d | %(name)-60s | %(levelname)-7s ' \
          '| %(message)s'
    logging.basicConfig(format=fmt, datefmt='%H:%M:%S', level=logging.DEBUG)


def main():
    """Main workflow function."""
    init_logging()

    # Get Dask client
    arlexecute.set_client(get_dask_Client())
    arlexecute.run(init_logging)

    LOG.info('Results dir = %s', RESULTS_DIR)
    LOG.info("Starting imaging-modeling")

    # Model parameters
    num_freq_win = 7
    num_times = 11
    r_max = 300.0
    frequency = numpy.linspace(0.9e8, 1.1e8, num_freq_win)
    channel_bw = numpy.array(num_freq_win * [frequency[1] - frequency[0]])
    times = numpy.linspace(-numpy.pi / 3.0, numpy.pi / 3.0, num_times)
    phase_centre = SkyCoord(ra=+30.0 * u.deg, dec=-60.0 * u.deg,
                            frame='icrs', equinox='J2000')

    # Simulate visibilities
    vis_list = simulate_component('LOWBD2',
                                  frequency=frequency,
                                  channel_bandwidth=channel_bw,
                                  times=times,
                                  phasecentre=phase_centre,
                                  order='frequency',
                                  rmax=r_max)

    LOG.info('%d elements in vis_list', len(vis_list))
    LOG.info('About to make visibility')
    vis_list = arlexecute.compute(vis_list, sync=True)
    LOG.debug('vis_list type: %s', type(vis_list))
    LOG.debug('vis_list element type: %s', type(vis_list[0]))
    try:
        export_blockvisibility_to_hdf5(vis_list,
                                       '%s/vis_list.hdf' % RESULTS_DIR)
    except AssertionError as error:
        LOG.critical('ERROR %s', error)
        return
    wprojection_planes = 1
    advice_low = advise_wide_field(vis_list[0], guard_band_image=8.0,
                                   delA=0.02,
                                   wprojection_planes=wprojection_planes)
    advice_high = advise_wide_field(vis_list[-1], guard_band_image=8.0,
                                    delA=0.02,
                                    wprojection_planes=wprojection_planes)

    vis_slices = advice_low['vis_slices']
    num_pixels = advice_high['npixels2']
    cellsize = min(advice_low['cellsize'], advice_high['cellsize'])

    # Create GLEAM model
    gleam_model = [
        arlexecute.execute(create_low_test_image_from_gleam)(
            npixel=num_pixels,
            frequency=[frequency[f]],
            channel_bandwidth=[channel_bw[f]],
            cellsize=cellsize,
            phasecentre=phase_centre,
            polarisation_frame=PolarisationFrame("stokesI"),
            flux_limit=1.0,
            applybeam=True)
        for f, freq in enumerate(frequency)
    ]
    LOG.info('About to make GLEAM model')
    gleam_model = arlexecute.compute(gleam_model, sync=True)
    # future_gleam_model = arlexecute.scatter(gleam_model)

    # Get predicted visibilities for GLEAM model
    LOG.info('About to run predict to get predicted visibility')
    future_vis_graph = arlexecute.scatter(vis_list)
    predicted_vis_list = predict_component(future_vis_graph, gleam_model,
                                           context='wstack',
                                           vis_slices=vis_slices)
    predicted_vis_list = arlexecute.compute(predicted_vis_list, sync=True)
    corrupted_vis_list = corrupt_component(predicted_vis_list, phase_error=1.0)

    LOG.info('About to run corrupt to get corrupted visibility')
    corrupted_vis_list = arlexecute.compute(corrupted_vis_list, sync=True)

    LOG.info('About to output predicted_vislist.hdf')
    export_blockvisibility_to_hdf5(predicted_vis_list,
                                   '%s/predicted_vislist.hdf' % RESULTS_DIR)

    LOG.info('About to output corrupted_vislist.hdf')
    export_blockvisibility_to_hdf5(corrupted_vis_list,
                                   '%s/corrupted_vislist.hdf' % RESULTS_DIR)

    # Prepare a dictionary with parameters for pickle export
    dict_parameters = {
        "npixel": num_pixels,
        "cellsize": cellsize,
        "phasecentre": phase_centre,
        "vis_slices": vis_slices,
        "nfreqwin": num_freq_win,
        "ntimes": num_times
    }

    LOG.info('About to output dict_parameters.pkl')
    outfile = open('%s/dict_parameters.pkl' % RESULTS_DIR, "wb")
    pickle.dump(dict_parameters, outfile)
    outfile.close()

    # Save frequency and bandwidth numpy arrays into numpy-formatted objects
    LOG.info('About to output frequency.np and channel_bandwidth.np')
    frequency.tofile('%s/frequency.np' % RESULTS_DIR)
    channel_bw.tofile('%s/channel_bandwidth.np' % RESULTS_DIR)

    # Close Dask client
    arlexecute.close()


if __name__ == '__main__':
    main()
