#!/usr/bin/python3 -u
# coding: utf-8

"""Pipeline processing using Dask (processing stage only).

This script demonstrates the continuum imaging and ICAL pipelines.
"""
import logging
import pprint
import pickle

import numpy
import sys
import json

from data_models.polarisation import PolarisationFrame
from data_models.data_model_helpers import import_blockvisibility_from_hdf5

from processing_components.calibration.calibration_control import \
    create_calibration_controls
from processing_components.image.operations import export_image_to_fits, \
    qa_image
from processing_components.imaging.base import create_image_from_visibility
from workflows.arlexecute.pipelines.pipeline_arlexecute import continuum_imaging_arlexecute, \
    ical_arlexecute

from processing_components.imaging.base import advise_wide_field

from workflows.arlexecute.execution_support.arlexecute import arlexecute
from workflows.arlexecute.execution_support.dask_init import get_dask_Client


PP = pprint.PrettyPrinter()
RESULTS_DIR = 'results'
LOG = logging.getLogger('sip.ical.generate_data')


def init_logging():
    """Initialise Python logging."""
    fmt = '%(asctime)s.%(msecs)03d | %(name)-60s | %(levelname)-7s ' \
          '| %(message)s'
    logging.basicConfig(format=fmt, datefmt='%H:%M:%S', level=logging.DEBUG)


def main():
    """Run the workflow."""
    init_logging()

    LOG.info("Starting imaging-pipeline")

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

    # We will use dask
    arlexecute.set_client(get_dask_Client())
    arlexecute.run(init_logging)

    # Import visibility list from HDF5 file
    vis_list = import_blockvisibility_from_hdf5(
        '%s/%s' % (RESULTS_DIR, jspar["files"]["vis_list"]))

    # Now read the BlockVisibilities constructed using a model drawn from GLEAM
    predicted_vislist = import_blockvisibility_from_hdf5(
        '%s/%s' % (RESULTS_DIR, jspar["files"]["predicted_vis_list"]))
    corrupted_vislist = import_blockvisibility_from_hdf5(
        '%s/%s' % (RESULTS_DIR, jspar["files"]["corrupted_vis_list"]))

# Reproduce parameters from the visibility data
    ntimes = vis_list[0].nvis

    phasecentre = vis_list[0].phasecentre
    print(phasecentre)
    polframe = vis_list[0].polarisation_frame.type
    LOG.info("Polarisation Frame of vis_list: %s", polframe)

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
    npixel = advice_high['npixels2']
    cellsize = min(advice_low['cellsize'], advice_high['cellsize'])
    
# Recovering frequencies
    fstart = vis_list[0].frequency
    fend = vis_list[-1].frequency
    num_freq_win = len(vis_list)
    frequency = numpy.linspace(fstart, fend, num_freq_win)

# Recovering bandwidths
    channel_bandwidth = numpy.array(num_freq_win * [vis_list[1].frequency - vis_list[0].frequency])
    
    # Get the LSM. This is currently blank.
    model_list = [
        arlexecute.execute(create_image_from_visibility)(
            vis_list[f],
            npixel=npixel,
            frequency=[frequency[f]],
            channel_bandwidth=[channel_bandwidth[f]],
            cellsize=cellsize,
            phasecentre=phasecentre,
            polarisation_frame=PolarisationFrame(polframe))
        for f, freq in enumerate(frequency)
    ]
    # future_predicted_vislist = arlexecute.scatter(predicted_vislist)

    # Create and execute graphs to make the dirty image and PSF
    # LOG.info('About to run invert to get dirty image')
    # dirty_list = invert_component(future_predicted_vislist, model_list,
    #                               context='wstack',
    #                               vis_slices=vis_slices, dopsf=False)
    # dirty_list = arlexecute.compute(dirty_list, sync=True)

    # LOG.info('About to run invert to get PSF')
    # psf_list = invert_component(future_predicted_vislist, model_list,
    #                             context='wstack',
    #                             vis_slices=vis_slices, dopsf=True)
    # psf_list = arlexecute.compute(psf_list, sync=True)

    # Now deconvolve using msclean
    # LOG.info('About to run deconvolve')
    # deconvolve_list, _ = deconvolve_component(
    #     dirty_list, psf_list,
    #     model_imagelist=model_list,
    #     deconvolve_facets=8,
    #     deconvolve_overlap=16,
    #     deconvolve_taper='tukey',
    #     scales=[0, 3, 10],
    #     algorithm='msclean',
    #     niter=1000,
    #     fractional_threshold=0.1,
    #     threshold=0.1,
    #     gain=0.1,
    #     psf_support=64)
    # deconvolved = arlexecute.compute(deconvolve_list, sync=True)

    LOG.info('About to run continuum imaging')
    continuum_imaging_list = continuum_imaging_arlexecute(
        predicted_vislist,
        model_imagelist		= model_list,
        context			= jspar["processing"]["continuum_imaging"]["context"] , #'wstack',
        vis_slices		= vis_slices,
        scales			= jspar["processing"]["continuum_imaging"]["scales"],             #[0, 3, 10],
        algorithm		= jspar["processing"]["continuum_imaging"]["algorithm"],          #'mmclean',
        nmoment			= jspar["processing"]["continuum_imaging"]["nmoment"],            #3,
        niter			= jspar["processing"]["continuum_imaging"]["niter"],		  #1000,
        fractional_threshold	= jspar["processing"]["continuum_imaging"]["fractional_threshold"], #0.1,
        threshold		= jspar["processing"]["continuum_imaging"]["threshold"], 	  #0.1,
        nmajor			= jspar["processing"]["continuum_imaging"]["nmajor"], 		  #5,
        gain			= jspar["processing"]["continuum_imaging"]["gain"],               #0.25,
        deconvolve_facets	= jspar["processing"]["continuum_imaging"]["deconvolve_facets"],  #8,
        deconvolve_overlap	= jspar["processing"]["continuum_imaging"]["deconvolve_overlap"], #16,
        deconvolve_taper	= jspar["processing"]["continuum_imaging"]["deconvolve_taper"],   #'tukey',
        psf_support		= jspar["processing"]["continuum_imaging"]["psf_support"] )        #64)
    result = arlexecute.compute(continuum_imaging_list, sync=True)
    deconvolved = result[0][0]
    residual = result[1][0]
    restored = result[2][0]

    print(qa_image(deconvolved, context='Clean image - no selfcal'))
    print(qa_image(restored, context='Restored clean image - no selfcal'))
    export_image_to_fits(restored,
                         '%s/%s' % (RESULTS_DIR, jspar["files"]["continuum_imaging_restored"]))

    print(qa_image(residual[0], context='Residual clean image - no selfcal'))
    export_image_to_fits(residual[0],
                         '%s/%s' % (RESULTS_DIR, jspar["files"]["continuum_imaging_residual"]))

    controls = create_calibration_controls()

    controls['T']['first_selfcal'] = jspar["processing"]["controls"]["T"]["first_selfcal"]
    controls['G']['first_selfcal'] = jspar["processing"]["controls"]["G"]["first_selfcal"]
    controls['B']['first_selfcal'] = jspar["processing"]["controls"]["B"]["first_selfcal"]

    controls['T']['timescale'] = jspar["processing"]["controls"]["T"]["timescale"]
    controls['G']['timescale'] = jspar["processing"]["controls"]["G"]["timescale"]
    controls['B']['timescale'] = jspar["processing"]["controls"]["B"]["timescale"]

    PP.pprint(controls)

    future_corrupted_vislist = arlexecute.scatter(corrupted_vislist)
    ical_list = ical_arlexecute(future_corrupted_vislist,
        model_imagelist		= model_list,
        context			= jspar["processing"]["ical"]["context"] , 		#'wstack',
        calibration_context	= jspar["processing"]["ical"]["calibration_context"] , 	#'TG',
        controls		= controls,
        vis_slices		= ntimes,
        scales			= jspar["processing"]["ical"]["scales"],             	#[0, 3, 10],
        timeslice		= jspar["processing"]["ical"]["timeslice"],          	#'auto',
        algorithm		= jspar["processing"]["ical"]["algorithm"],          	#'mmclean',
        nmoment			= jspar["processing"]["ical"]["nmoment"],            	#3,
        niter			= jspar["processing"]["ical"]["niter"],		  	#1000,
        fractional_threshold	= jspar["processing"]["ical"]["fractional_threshold"], 	#0.1,
        threshold		= jspar["processing"]["ical"]["threshold"], 	  	#0.1,
        nmajor			= jspar["processing"]["ical"]["nmajor"], 		#5,
        gain			= jspar["processing"]["ical"]["gain"],               	#0.25,
        deconvolve_facets	= jspar["processing"]["ical"]["deconvolve_facets"],  	#8,
        deconvolve_overlap	= jspar["processing"]["ical"]["deconvolve_overlap"], 	#16,
        deconvolve_taper	= jspar["processing"]["ical"]["deconvolve_taper"],   	#'tukey',
        global_solution		= jspar["processing"]["ical"]["global_solution"],    	#False,
        do_selfcal		= jspar["processing"]["ical"]["do_selfcal"],         	#True,
        psf_support		= jspar["processing"]["ical"]["psf_support"])         	#64


    LOG.info('About to run ical')
    result = arlexecute.compute(ical_list, sync=True)
    deconvolved = result[0][0]
    residual = result[1][0]
    restored = result[2][0]

    print(qa_image(deconvolved, context='Clean image'))
    print(qa_image(restored, context='Restored clean image'))
    export_image_to_fits(restored, '%s/%s' % (RESULTS_DIR, jspar["files"]["ical_restored"]))

    print(qa_image(residual[0], context='Residual clean image'))
    export_image_to_fits(residual[0], '%s/%s' % (RESULTS_DIR, jspar["files"]["ical_residual"]))

    arlexecute.close()


if __name__ == '__main__':
    main()
