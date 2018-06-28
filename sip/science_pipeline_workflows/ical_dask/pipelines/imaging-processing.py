#!/usr/bin/python3 -u
# coding: utf-8

# # Pipeline processing using Dask (processing stage only)
# 
# This script demonstrates the continuum imaging and ICAL pipelines.

import os
import sys

sys.path.append(os.path.join('..', '..'))

from data_models.parameters import arl_path

results_dir = arl_path('test_results')

import numpy

from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.wcs.utils import pixel_to_skycoord

from data_models.polarisation import PolarisationFrame
from data_models.data_model_helpers import export_blockvisibility_to_hdf5, import_blockvisibility_from_hdf5

from processing_components.calibration.calibration import solve_gaintable
from processing_components.calibration.operations import apply_gaintable
from processing_components.calibration.calibration_control import create_calibration_controls
from processing_components.visibility.base import create_blockvisibility
from processing_components.skycomponent.operations import create_skycomponent
from processing_components.image.deconvolution import deconvolve_cube
from processing_components.image.operations import show_image, export_image_to_fits, qa_image
from processing_components.visibility.iterators import vis_timeslice_iter
from processing_components.util.testing_support import create_named_configuration, create_low_test_image_from_gleam
from processing_components.imaging.base import predict_2d, create_image_from_visibility, advise_wide_field

from processing_components.component_support.dask_init import get_dask_Client
from processing_components.imaging.imaging_components import invert_component, predict_component,     deconvolve_component
from processing_components.util.support_components import simulate_component,     corrupt_component
from processing_components.pipelines.pipeline_components import continuum_imaging_component,     ical_component

from processing_components.component_support.arlexecute import arlexecute

import pprint

pp = pprint.PrettyPrinter()

import logging

def init_logging():
    log = logging.getLogger()
    logging.basicConfig(filename='%s/imaging-pipeline.log' % results_dir,
                        filemode='a',
                        format='%(thread)s %(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)
log = logging.getLogger()
logging.info("Starting imaging-pipeline")

import pickle


# We will use dask
arlexecute.set_client(get_dask_Client())
arlexecute.run(init_logging)



# Read the parameters (nfreqwin, ntimes, phasecentre) from pickle
infile = open('%s/dict_parameters.pkl'%(results_dir),'rb')
dict_parameters = pickle.load(infile)
infile.close()

# Read frequency and bandwidth lists from numpy-formatted files
frequency=numpy.fromfile('%s/frequency.np'%(results_dir))
channel_bandwidth=numpy.fromfile('%s/channel_bandwidth.np'%(results_dir))
nfreqwin = dict_parameters["nfreqwin"]
ntimes = dict_parameters["ntimes"]
phasecentre=dict_parameters["phasecentre"]

# Import visibility list from HDF5 file
vis_list = import_blockvisibility_from_hdf5('%s/vis_list.hdf'%(results_dir))
vis_slices = dict_parameters["vis_slices"]
npixel     = dict_parameters["npixel"]
cellsize   = dict_parameters["cellsize"]


# Now read the blockvisibilities constructed using a model drawn from GLEAM 
predicted_vislist = import_blockvisibility_from_hdf5('%s/predicted_vislist.hdf'%(results_dir))
corrupted_vislist = import_blockvisibility_from_hdf5('%s/corrupted_vislist.hdf'%(results_dir))


# Get the LSM. This is currently blank.
model_list = [arlexecute.execute(create_image_from_visibility)(vis_list[f],
                                                     npixel=npixel,
                                                     frequency=[frequency[f]],
                                                     channel_bandwidth=[channel_bandwidth[f]],
                                                     cellsize=cellsize,
                                                     phasecentre=phasecentre,
                                                     polarisation_frame=PolarisationFrame("stokesI"))
               for f, freq in enumerate(frequency)]

future_predicted_vislist=arlexecute.scatter(predicted_vislist)
dirty_list = invert_component(future_predicted_vislist, model_list, 
                                  context='wstack',
                                  vis_slices=vis_slices, dopsf=False)
psf_list = invert_component(future_predicted_vislist, model_list, 
                                context='wstack',
                                vis_slices=vis_slices, dopsf=True)


# Create and execute graphs to make the dirty image and PSF
log.info('About to run invert to get dirty image')

dirty_list =  arlexecute.compute(dirty_list, sync=True)
dirty = dirty_list[0][0]

log.info('About to run invert to get PSF')
psf_list =  arlexecute.compute(psf_list, sync=True)
psf = psf_list[0][0]

type(dirty_list[0][0])


# Now deconvolve using msclean
log.info('About to run deconvolve')

deconvolve_list, _ =     deconvolve_component(dirty_list, psf_list, model_imagelist=model_list, 
                            deconvolve_facets=8, deconvolve_overlap=16, deconvolve_taper='tukey',
                            scales=[0, 3, 10],
                            algorithm='msclean', niter=1000, 
                            fractional_threshold=0.1,
                            threshold=0.1, gain=0.1, psf_support=64)
    
deconvolved = arlexecute.compute(deconvolve_list, sync=True)


continuum_imaging_list =     continuum_imaging_component(predicted_vislist, 
                                            model_imagelist=model_list, 
                                            context='wstack', vis_slices=vis_slices, 
                                            scales=[0, 3, 10], algorithm='mmclean', 
                                            nmoment=3, niter=1000, 
                                            fractional_threshold=0.1,
                                            threshold=0.1, nmajor=5, gain=0.25,
                                            deconvolve_facets = 8, deconvolve_overlap=16, 
                                            deconvolve_taper='tukey', psf_support=64)


log.info('About to run continuum imaging')

result=arlexecute.compute(continuum_imaging_list, sync=True)
deconvolved = result[0][0]
residual = result[1][0]
restored = result[2][0]

print(qa_image(deconvolved, context='Clean image - no selfcal'))
print(qa_image(restored, context='Restored clean image - no selfcal'))

export_image_to_fits(restored, '%s/imaging-dask_continuum_imaging_restored.fits' 
                     %(results_dir))

print(qa_image(residual[0], context='Residual clean image - no selfcal'))
export_image_to_fits(residual[0], '%s/imaging-dask_continuum_imaging_residual.fits' 
                     %(results_dir))


for chan in range(nfreqwin):
    residual = result[1][chan]

controls = create_calibration_controls()
        
controls['T']['first_selfcal'] = 1
controls['G']['first_selfcal'] = 3
controls['B']['first_selfcal'] = 4

controls['T']['timescale'] = 'auto'
controls['G']['timescale'] = 'auto'
controls['B']['timescale'] = 1e5

pp.pprint(controls)


future_corrupted_vislist = arlexecute.scatter(corrupted_vislist)
ical_list = ical_component(future_corrupted_vislist, 
                                        model_imagelist=model_list,  
                                        context='wstack', 
                                        calibration_context = 'TG', 
                                        controls=controls,
                                        scales=[0, 3, 10], algorithm='mmclean', 
                                        nmoment=3, niter=1000, 
                                        fractional_threshold=0.1,
                                        threshold=0.1, nmajor=5, gain=0.25,
                                        deconvolve_facets = 8, 
                                        deconvolve_overlap=16,
                                        deconvolve_taper='tukey',
                                        vis_slices=ntimes,
                                        timeslice='auto',
                                        global_solution=False, 
                                        psf_support=64,
                                        do_selfcal=True)


log.info('About to run ical')
result=arlexecute.compute(ical_list, sync=True)
deconvolved = result[0][0]
residual = result[1][0]
restored = result[2][0]

print(qa_image(deconvolved, context='Clean image'))
print(qa_image(restored, context='Restored clean image'))
export_image_to_fits(restored, '%s/imaging-dask_ical_restored.fits' 
                     %(results_dir))

print(qa_image(residual[0], context='Residual clean image'))
export_image_to_fits(residual[0], '%s/imaging-dask_ical_residual.fits' 
                     %(results_dir))


arlexecute.close()

