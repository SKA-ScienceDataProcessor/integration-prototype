# -*- coding: utf-8 -*-
"""Dask workflow for generating model data for the SIP example ICAL workflow.

This is code based on the test ICAL pipeline notebook from ARL.
"""
import logging
import pickle
import os
import sys
import json

import numpy

from astropy import units as u
from astropy.coordinates import SkyCoord

from data_models.data_model_helpers import export_blockvisibility_to_hdf5
from data_models.polarisation import PolarisationFrame

from workflows.arlexecute.execution_support.arlexecute import arlexecute
from workflows.arlexecute.execution_support.dask_init import get_dask_Client
from processing_components.imaging.base import advise_wide_field
from workflows.arlexecute.imaging.imaging_arlexecute import predict_arlexecute
from workflows.arlexecute.simulation.simulation_arlexecute import simulate_arlexecute, \
    corrupt_arlexecute

from processing_components.simulation.testing_support import \
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

    # Read parameters
    PARFILE = 'parameters.json'
    if len(sys.argv) > 1:
       PARFILE = sys.argv[1]
    LOG.info("JSON parameter file = %s", PARFILE)

    try: 	
       with open(PARFILE, "r") as par_file:
             jspar = json.load(par_file)       
    except AssertionError as error:
       LOG.critical('ERROR %s', error)
       return

    # Model parameters
    configuration= jspar["modeling"]["configuration"]["name"]
    num_freq_win = jspar["modeling"]["configuration"]["num_freq_win"] # 7
    num_times    = jspar["modeling"]["configuration"]["num_times"] # 11
    r_max        = jspar["modeling"]["configuration"]["r_max"] # 300.0
    fstart	 = jspar["modeling"]["configuration"]["fstart"]
    fend	 = jspar["modeling"]["configuration"]["fend"]
    timestart_pi = jspar["modeling"]["configuration"]["timestart_pi"] # -1/3
    timeend_pi   = jspar["modeling"]["configuration"]["timeend_pi"] # 1/3
    polframe     = jspar["modeling"]["configuration"]["PolarisationFrame"] # StokesI

    frequency = numpy.linspace(fstart, fend, num_freq_win)
    channel_bw = numpy.array(num_freq_win * [frequency[1] - frequency[0]]) # 0.9e8 ... 1.1e8
    times = numpy.linspace(numpy.pi * timestart_pi, numpy.pi * timeend_pi, num_times)

    phase_centre = SkyCoord(	ra     =jspar["modeling"]["phasecentre"]["RA"] * u.deg, 
				dec    =jspar["modeling"]["phasecentre"]["Dec"] * u.deg,
                            	frame  =jspar["modeling"]["phasecentre"]["frame"], 
				equinox=jspar["modeling"]["phasecentre"]["equinox"])

    # Simulate visibilities
    vis_list = simulate_arlexecute(configuration,
                                  frequency=frequency,
                                  channel_bandwidth=channel_bw,
                                  times=times,
                                  phasecentre=phase_centre,
                                  order=jspar["modeling"]["simulate"]["order"],
                                  rmax=r_max)

    LOG.info('%d elements in vis_list', len(vis_list))
    LOG.info('About to make visibility')
    vis_list = arlexecute.compute(vis_list, sync=True)
    LOG.debug('vis_list type: %s', type(vis_list))
    LOG.debug('vis_list element type: %s', type(vis_list[0]))
    try:
        export_blockvisibility_to_hdf5(vis_list,
                                       '%s/%s' % (RESULTS_DIR, jspar["files"]["vis_list"]))
    except AssertionError as error:
        LOG.critical('ERROR %s', error)
        return

    wprojection_planes = jspar["advice"]["wprojection_planes"]
    guard_band_image   = jspar["advice"]["guard_band_image"]
    delA               = jspar["advice"]["delA"]
    advice_low = advise_wide_field(vis_list[0], guard_band_image=guard_band_image,
                                   delA=delA,
                                   wprojection_planes=wprojection_planes)
    advice_high = advise_wide_field(vis_list[-1], guard_band_image=guard_band_image,
                                    delA=delA,
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
            polarisation_frame=PolarisationFrame(polframe),
            flux_limit=jspar["modeling"]["gleam_model"]["flux_limit"], # 1.0,
            applybeam =jspar["modeling"]["gleam_model"]["applybeam"])  # True
        for f, freq in enumerate(frequency)
    ]


    LOG.info('About to make GLEAM model')
    gleam_model = arlexecute.compute(gleam_model, sync=True)
    # future_gleam_model = arlexecute.scatter(gleam_model)

    # Get predicted visibilities for GLEAM model
    LOG.info('About to run predict to get predicted visibility')
    future_vis_graph = arlexecute.scatter(vis_list)
    predicted_vis_list = predict_arlexecute(future_vis_graph, gleam_model,
                                           context=jspar["modeling"]["predict"]["context"],  #'wstack'
                                           vis_slices=vis_slices)
    predicted_vis_list = arlexecute.compute(predicted_vis_list, sync=True)
    corrupted_vis_list = corrupt_arlexecute(predicted_vis_list, phase_error=jspar["modeling"]["corrupt"]["phase_error"]) #1.0

    LOG.info('About to run corrupt to get corrupted visibility')
    corrupted_vis_list = arlexecute.compute(corrupted_vis_list, sync=True)

    LOG.info('About to output predicted_vislist.hdf')
    export_blockvisibility_to_hdf5(predicted_vis_list,
                                   '%s/%s' % (RESULTS_DIR,jspar["files"]["predicted_vis_list"]))

    LOG.info('About to output corrupted_vislist.hdf')

    export_blockvisibility_to_hdf5(corrupted_vis_list,
                                   '%s/%s' % (RESULTS_DIR, jspar["files"]["corrupted_vis_list"]))
    # Close Dask client
    arlexecute.close()


if __name__ == '__main__':
    main()
