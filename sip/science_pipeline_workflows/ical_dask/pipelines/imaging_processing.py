#!/usr/bin/python3 -u
# coding: utf-8

"""Pipeline processing using Dask (processing stage only).

This script demonstrates the continuum imaging and ICAL pipelines.
"""
import logging
import pprint
import pickle
import sys

import numpy

sys.path.append('sdp_arl')

from data_models.polarisation import PolarisationFrame
from data_models.data_model_helpers import import_blockvisibility_from_hdf5

from processing_components.calibration.calibration_control import \
    create_calibration_controls
from processing_components.image.operations import export_image_to_fits, \
    qa_image
from processing_components.imaging.base import create_image_from_visibility
from processing_components.component_support.dask_init import get_dask_Client
# from sdp_arl.processing_components.imaging.imaging_components import \
#     invert_component, deconvolve_component
from processing_components.pipelines.pipeline_components import \
    continuum_imaging_component, ical_component
from processing_components.component_support.arlexecute import arlexecute


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

    # We will use dask
    arlexecute.set_client(get_dask_Client())
    arlexecute.run(init_logging)

    # Read the parameters (nfreqwin, ntimes, phasecentre) from pickle
    infile = open('%s/dict_parameters.pkl' % RESULTS_DIR, 'rb')
    dict_parameters = pickle.load(infile)
    infile.close()

    # Read frequency and bandwidth lists from numpy-formatted files
    frequency = numpy.fromfile('%s/frequency.np' % RESULTS_DIR)
    channel_bandwidth = numpy.fromfile('%s/channel_bandwidth.np' % RESULTS_DIR)
    # nfreqwin = dict_parameters["nfreqwin"]
    ntimes = dict_parameters["ntimes"]
    phasecentre = dict_parameters["phasecentre"]

    # Import visibility list from HDF5 file
    vis_list = import_blockvisibility_from_hdf5('%s/vis_list.hdf' % RESULTS_DIR)
    vis_slices = dict_parameters["vis_slices"]
    npixel = dict_parameters["npixel"]
    cellsize = dict_parameters["cellsize"]

    # Now read the BlockVisibilities constructed using a model drawn from GLEAM
    predicted_vislist = import_blockvisibility_from_hdf5(
        '%s/predicted_vislist.hdf' % RESULTS_DIR)
    corrupted_vislist = import_blockvisibility_from_hdf5(
        '%s/corrupted_vislist.hdf' % RESULTS_DIR)

    # Get the LSM. This is currently blank.
    model_list = [
        arlexecute.execute(create_image_from_visibility)(
            vis_list[f],
            npixel=npixel,
            frequency=[frequency[f]],
            channel_bandwidth=[channel_bandwidth[f]],
            cellsize=cellsize,
            phasecentre=phasecentre,
            polarisation_frame=PolarisationFrame("stokesI"))
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
    continuum_imaging_list = continuum_imaging_component(
        predicted_vislist,
        model_imagelist=model_list,
        context='wstack',
        vis_slices=vis_slices,
        scales=[0, 3, 10],
        algorithm='mmclean',
        nmoment=3,
        niter=1000,
        fractional_threshold=0.1,
        threshold=0.1,
        nmajor=5,
        gain=0.25,
        deconvolve_facets=8,
        deconvolve_overlap=16,
        deconvolve_taper='tukey',
        psf_support=64)
    result = arlexecute.compute(continuum_imaging_list, sync=True)
    deconvolved = result[0][0]
    residual = result[1][0]
    restored = result[2][0]

    print(qa_image(deconvolved, context='Clean image - no selfcal'))
    print(qa_image(restored, context='Restored clean image - no selfcal'))
    export_image_to_fits(restored,
                         '%s/imaging-dask_continuum_imaging_restored.fits'
                         % RESULTS_DIR)

    print(qa_image(residual[0], context='Residual clean image - no selfcal'))
    export_image_to_fits(residual[0],
                         '%s/imaging-dask_continuum_imaging_residual.fits'
                         % RESULTS_DIR)

    controls = create_calibration_controls()

    controls['T']['first_selfcal'] = 1
    controls['G']['first_selfcal'] = 3
    controls['B']['first_selfcal'] = 4

    controls['T']['timescale'] = 'auto'
    controls['G']['timescale'] = 'auto'
    controls['B']['timescale'] = 1e5

    PP.pprint(controls)

    future_corrupted_vislist = arlexecute.scatter(corrupted_vislist)
    ical_list = ical_component(future_corrupted_vislist,
                               model_imagelist=model_list,
                               context='wstack',
                               calibration_context='TG',
                               controls=controls,
                               scales=[0, 3, 10], algorithm='mmclean',
                               nmoment=3,
                               niter=1000,
                               fractional_threshold=0.1,
                               threshold=0.1,
                               nmajor=5,
                               gain=0.25,
                               deconvolve_facets=8,
                               deconvolve_overlap=16,
                               deconvolve_taper='tukey',
                               vis_slices=ntimes,
                               timeslice='auto',
                               global_solution=False,
                               psf_support=64,
                               do_selfcal=True)

    LOG.info('About to run ical')
    result = arlexecute.compute(ical_list, sync=True)
    deconvolved = result[0][0]
    residual = result[1][0]
    restored = result[2][0]

    print(qa_image(deconvolved, context='Clean image'))
    print(qa_image(restored, context='Restored clean image'))
    export_image_to_fits(restored, '%s/imaging-dask_ical_restored.fits'
                         % RESULTS_DIR)

    print(qa_image(residual[0], context='Residual clean image'))
    export_image_to_fits(residual[0], '%s/imaging-dask_ical_residual.fits'
                         % RESULTS_DIR)

    arlexecute.close()


if __name__ == '__main__':
    main()
