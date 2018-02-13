# TODO

- General
    - [x] Add Jenkinsfile
    - [ ] Update Jenkinsfile code.
- Deployment 
    - [ ] Add deployment script (using images from dockerhub?)
    - [ ] Review Ansible scripts in deploy
- Documentation
    - [x] Master Controller
    - [x] Processing Controller Interface
    - [ ] Processing Controller Scheduler
    - [x] Processing Block Controller
    - [ ] Configuration DB
- REST Services
    - [x] Split out different resources in the Processing Controller into 
          separate files
    - [ ] Create Processing block scheduler with watcher on the scheduling 
          block list
    - [ ] Create Processing block Controller Celery worker
    - [ ] Trigger Processing block controller from processing controller 
          scheduler
    - [ ] Add Dockerfiles + Docker compose files
    - [ ] Add unit tests
- Tango Services
    - [ ] Add templates for Tango services
    - [ ] Add Dockerfiles + Docker compose files
- Pipelines
   -  [x] receive_visibilities
   -  [ ] Sort out `science_pipeline_workflows/receive_visibilties` folder
   -  [ ] Fred's imaging pipelines
   -  [ ] Vlad's pipelines (ICAL etc) 
- Emulators
    - [x] Update emulator from Nijin's branch (vis_ingest_multi)
    - [ ] Check with Nijin about CSP PSS emulator
    - [ ] Check with Nijin about visibility emulator and receiver / ingest 

