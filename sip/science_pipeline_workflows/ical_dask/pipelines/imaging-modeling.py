#!/usr/bin/python3 -u
# coding: utf-8

import os
import sys

sys.path.append(os.path.join('..', '..'))

from data_models.parameters import arl_path

results_dir = arl_path('test_results')
print(results_dir)

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
    logging.basicConfig(filename='%s/imaging-modeling.log' % results_dir,
                        filemode='a',
                        format='%(thread)s %(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)
log = logging.getLogger()
logging.info("Starting imaging-modeling")
print("Starting imaging-modeling")

import pickle

# Get Dask client
arlexecute.set_client(get_dask_Client())
arlexecute.run(init_logging)



# Model parameters
nfreqwin=7
ntimes=11
rmax=300.0
frequency=numpy.linspace(0.9e8,1.1e8,nfreqwin)
channel_bandwidth=numpy.array(nfreqwin*[frequency[1]-frequency[0]])
times = numpy.linspace(-numpy.pi/3.0, numpy.pi/3.0, ntimes)
phasecentre=SkyCoord(ra=+30.0 * u.deg, dec=-60.0 * u.deg, frame='icrs', equinox='J2000')

# Simulate visibilities
vis_list=simulate_component('LOWBD2',
                                         frequency=frequency, 
                                         channel_bandwidth=channel_bandwidth,
                                         times=times,
                                         phasecentre=phasecentre,
                                         order='frequency',
                                        rmax=rmax)
print('%d elements in vis_list' % len(vis_list))
log.info('About to make visibility')
vis_list = arlexecute.compute(vis_list, sync=True)
export_blockvisibility_to_hdf5(vis_list, '%s/vis_list.hdf'%(results_dir))


wprojection_planes=1
advice_low=advise_wide_field(vis_list[0], guard_band_image=8.0, delA=0.02,
                             wprojection_planes=wprojection_planes)

advice_high=advise_wide_field(vis_list[-1], guard_band_image=8.0, delA=0.02,
                              wprojection_planes=wprojection_planes)

vis_slices = advice_low['vis_slices']
npixel=advice_high['npixels2']
cellsize=min(advice_low['cellsize'], advice_high['cellsize'])

# Create GLEAM model
gleam_model = [arlexecute.execute(create_low_test_image_from_gleam)(npixel=npixel,
                                                               frequency=[frequency[f]],
                                                               channel_bandwidth=[channel_bandwidth[f]],
                                                               cellsize=cellsize,
                                                               phasecentre=phasecentre,
                                                               polarisation_frame=PolarisationFrame("stokesI"),
                                                               flux_limit=1.0,
                                                               applybeam=True)
                     for f, freq in enumerate(frequency)]
log.info('About to make GLEAM model')
gleam_model = arlexecute.compute(gleam_model, sync=True)
future_gleam_model = arlexecute.scatter(gleam_model)


# Get predicted visibilities for GLEAM model
log.info('About to run predict to get predicted visibility')
future_vis_graph = arlexecute.scatter(vis_list)
predicted_vislist = predict_component(future_vis_graph, gleam_model,  
                                                context='wstack', vis_slices=vis_slices)
predicted_vislist = arlexecute.compute(predicted_vislist, sync=True)
corrupted_vislist = corrupt_component(predicted_vislist, phase_error=1.0)
log.info('About to run corrupt to get corrupted visibility')
corrupted_vislist =  arlexecute.compute(corrupted_vislist, sync=True)


log.info('About to output predicted_vislist.hdf')
export_blockvisibility_to_hdf5(predicted_vislist, '%s/predicted_vislist.hdf'%(results_dir))

log.info('About to output corrupted_vislist.hdf')
export_blockvisibility_to_hdf5(corrupted_vislist, '%s/corrupted_vislist.hdf'%(results_dir))


# Prepare a dictionaty with parameters for pickle export
dict_parameters = {"npixel":npixel,
                  "cellsize":cellsize,
                  "phasecentre":phasecentre,
                  "vis_slices":vis_slices,
                  "nfreqwin":nfreqwin,
                  "ntimes":ntimes                   
                  }


log.info('About to output dict_parameters.pkl')
outfile = open('%s/dict_parameters.pkl'%(results_dir),"wb")
pickle.dump(dict_parameters,outfile)
outfile.close()


# Save frequency and bandwidth numpy arrays into numpy-formatted objects
log.info('About to output frequency.np and channel_bandwidth.np')
frequency.tofile('%s/frequency.np'%(results_dir))
channel_bandwidth.tofile('%s/channel_bandwidth.np'%(results_dir))

# Close Dask client
arlexecute.close()

