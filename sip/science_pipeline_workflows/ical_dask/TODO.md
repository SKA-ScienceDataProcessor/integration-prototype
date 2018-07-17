# Suggestions / todo list / questions to resolve for Dask ICAL pipeline

- [ ] Move ARL into the image but first stripping out all of the non-essential
      parts (use a multi-stage build for this? 
      see: <https://docs.docker.com/develop/develop-images/multistage-build/>)
      
- [x] Move the pipeline scripts into the pipeline container

- [x] Sort out where the data & outputs are written - at the moment they 
      are written into the ARL `test_results` folder.

- [ ] Review exactly what steps are done in the data generation. Some steps
      might be better moved to processing as they are not generating raw 
      (ingested) data.
      
- [ ] Review exactly what steps are done in the processing script.
      Initial inspection appears to indicate that `psf_list`, `dirty_list`,
      and `deconvolved_list` don't data objects are not used.
      
- [x] Remove `DaskSwarmICALstart` script which is a combined data generation
      and processing script.

- [ ] Review and update data placement model for deploying with multiple 
      workers if needed. If running with multiple workers the current script 
      complains not scattering the BlockVisibility object ahead of time.

- [ ] Pass workflow script parameters through the command line argument as a 
      JSON dictionary.

- [ ] Profile and record performance of the pipeline. CPU, memory, network etc.
      This can be done with the Scheduler web UI, `docker stats`, and 
      the monitoring interface on P3.
      
- [ ] Work out how to install ARL without needing the `sys.path.append`.
      (Liaise with Tim about this.)
      
- [ ] Identify use of QA functions and work out how to connect them to a 
      queue service (if applicable).

