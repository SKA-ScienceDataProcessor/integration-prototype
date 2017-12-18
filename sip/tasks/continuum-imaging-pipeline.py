#!/usr/bin/python3
# coding: utf-8

# # Pipeline processing using Dask
# Requires dask/distributed and ARL installed
# This script demonstrates the continuum imaging pipeline.

import os
import sys

results_dir = './results'
os.makedirs(results_dir, exist_ok=True)

from dask import delayed
import dask
import dask.distributed

sys.path.append(os.path.join('..', '..'))

results_dir = './results'
os.makedirs(results_dir, exist_ok=True)

import numpy

from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.wcs.utils import pixel_to_skycoord

from matplotlib import pyplot as plt

from arl.calibration.solvers import solve_gaintable
from arl.calibration.operations import apply_gaintable
from arl.data.data_models import Image
from arl.data.polarisation import PolarisationFrame
from arl.data.parameters import get_parameter
from arl.visibility.base import create_blockvisibility
from arl.skycomponent.operations import create_skycomponent
from arl.image.deconvolution import deconvolve_cube
from arl.image.operations import show_image, export_image_to_fits, qa_image, copy_image, create_empty_image_like
from arl.visibility.iterators import vis_timeslice_iter
from arl.util.testing_support import create_named_configuration, create_low_test_beam
from arl.imaging import predict_2d, create_image_from_visibility, advise_wide_field

from arl.graphs.dask_init import get_dask_Client
from arl.graphs.graphs import create_invert_wstack_graph, create_predict_wstack_graph, create_deconvolve_facet_graph,     create_residual_wstack_graph, compute_list

from arl.graphs.generic_graphs import create_generic_image_graph
from arl.util.graph_support import create_simulate_vis_graph,     create_low_test_image_from_gleam, create_corrupt_vis_graph
from arl.pipelines.graphs import create_continuum_imaging_pipeline_graph,     create_ical_pipeline_graph    
from arl.graphs.vis import simple_vis

import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler(sys.stdout))

import time
start_time = time.time()


# Make a Dask client to manage the processing. Diagnostics are available at the URL given. Try the Status entry.
c=get_dask_Client()


# We create a graph to make the visibility. The parameter rmax determines the distance of the furthest antenna/stations used. All over parameters are determined from this number.
nfreqwin=7
ntimes=11
rmax=300.0
frequency=numpy.linspace(0.8e8,1.2e8,nfreqwin)
channel_bandwidth=numpy.array(nfreqwin*[frequency[1]-frequency[0]])
times = numpy.linspace(-numpy.pi/3.0, numpy.pi/3.0, ntimes)
phasecentre=SkyCoord(ra=+30.0 * u.deg, dec=-60.0 * u.deg, frame='icrs', equinox='J2000')

vis_graph_list=create_simulate_vis_graph('LOWBD2',
                                         frequency=frequency, 
                                         channel_bandwidth=channel_bandwidth,
                                         times=times,
                                         phasecentre=phasecentre,
                                         order='frequency',
                                        rmax=rmax)
print('%d elements in vis_graph_list' % len(vis_graph_list))
vis_graph_list = compute_list(c, vis_graph_list)


wprojection_planes=1
advice_low=advise_wide_field(vis_graph_list[0], guard_band_image=4.0, delA=0.02,
                             wprojection_planes=wprojection_planes)

advice_high=advise_wide_field(vis_graph_list[-1], guard_band_image=4.0, delA=0.02,
                              wprojection_planes=wprojection_planes)

vis_slices = advice_low['vis_slices']
npixel=advice_high['npixels2']
cellsize=min(advice_low['cellsize'], advice_high['cellsize'])


# Now make a graph to fill with a model drawn from GLEAM 
gleam_model = create_low_test_image_from_gleam(npixel=npixel, frequency=frequency,
                                    channel_bandwidth=channel_bandwidth,
                                             cellsize=cellsize, phasecentre=phasecentre)
beam = create_low_test_beam(gleam_model)
gleam_model.data *= beam.data


#vis_graph_list=create_simulate_vis_graph('LOWBD2',
#                                         frequency=frequency, 
#                                         channel_bandwidth=channel_bandwidth,
#                                         times=times,
#                                         phasecentre=phasecentre,
#                                         order='frequency',
#                                         rmax=rmax)
predicted_vis_graph_list = create_predict_wstack_graph(vis_graph_list, gleam_model, vis_slices=5)
predicted_vis_graph_list = compute_list(c, predicted_vis_graph_list)
corrupted_vis_graph_list = create_corrupt_vis_graph(predicted_vis_graph_list, phase_error=1.0)
corrupted_vis_graph_list = compute_list(c, corrupted_vis_graph_list)


# Get the LSM. This is currently blank.
def get_LSM(vt, npixel = 512, cellsize=0.001, reffrequency=[1e8]):
    model = create_image_from_visibility(vt, npixel=npixel, cellsize=cellsize, 
                                         npol=1, frequency=reffrequency,
                                         polarisation_frame=PolarisationFrame("stokesI"))
    return model

model_graph=delayed(get_LSM)(predicted_vis_graph_list[len(vis_graph_list)//2], cellsize=cellsize)


# Create a graph to make the dirty image 
from arl.graphs.graphs import create_invert_facet_wstack_graph
dirty_graph = create_invert_facet_wstack_graph(predicted_vis_graph_list, model_graph, 
                                         vis_slices=vis_slices, dopsf=False)


future=c.compute(dirty_graph)
dirty=future.result()[0]

continuum_imaging_graph =     create_continuum_imaging_pipeline_graph(predicted_vis_graph_list, 
                                            model_graph=model_graph, 
                                            c_deconvolve_graph=create_deconvolve_facet_graph,
                                            facets=1,
                                            c_invert_graph=create_invert_wstack_graph,
                                            c_residual_graph=create_residual_wstack_graph,
                                            vis_slices=vis_slices, 
                                            algorithm='hogbom', niter=1000, 
                                            fractional_threshold=0.1,
                                            threshold=0.1, nmajor=5, gain=0.1)
future=c.compute(continuum_imaging_graph)

deconvolved = future.result()[0]
residual = future.result()[1]
restored = future.result()[2]

print(qa_image(deconvolved, context='Clean image - no selfcal'))
export_image_to_fits(deconvolved, '%s/imaging-dask_continuum_imaging_clean.fits' 
                     %(results_dir))
print(qa_image(restored, context='Restored clean image - no selfcal'))
export_image_to_fits(restored, '%s/imaging-dask_continuum_imaging_restored.fits' 
                     %(results_dir))

print(qa_image(residual[0], context='Residual clean image - no selfcal'))
export_image_to_fits(residual[0], '%s/imaging-dask_continuum_imaging_residual.fits' 
                     %(results_dir))

c.shutdown()

print("--- %s seconds ---" % (time.time() - start_time))

