# TODO

- General
    - [x] Add Jenkinsfile
    - [ ] Update / fix Jenkinsfile.
- Deployment
    - [ ] Add deployment script (using images from dockerhub?)
    - [ ] Review Ansible scripts in deploy
- Documentation
    - [x] SIP
        - [x] Core Processing
            - [x] Receive
        - [x] Execution control
            - [x] Master Controller
            - [x] Processing Controller Interface
            - [x] Processing Controller Scheduler
            - [x] Processing Block Controller
            - [x] Configuration DB
        - [x] Execution Frameworks
        - [x] Execution Framework Interface
        - [ ] Science Pipeline workflows

- REST Services
    - Bare-bones implementations:
        - [x] Master Controller
        - [ ] Processing Controller Interface
        - [ ] Processing Controller Scheduler
        - [ ] Processing Block Controller
        - [ ] Configuration database
    - [ ] Add unit tests
        - [x] Master Controller
        - [ ] Processing Controller Interface
        - [ ] Processing Controller Scheduler
        - [ ] Processing Block Controller
        - [ ] Configuration database
    
- Tango Services
    - Bare-bones implementations:
        - [ ] Master Controller device server and Master Controller device
        - [ ] Processing Controller device server, Processing Controller 
              device, and Processing block devices
    - [ ] Docker deployment scripts
        - [ ] Database
        - [ ] DataBaseds

- Pipelines
   -  [x] receive_visibilities
   -  [ ] Sort out `science_pipeline_workflows/receive_visibilties` folder
   -  [ ] Fred's imaging pipelines
   -  [ ] Vlad's pipelines (ICAL etc)

- Emulators
    - [x] Update emulator from Nijin's branch (vis_ingest_multi)
    - [ ] Check with Nijin about CSP PSS emulator
    - [ ] Check with Nijin about visibility emulator and receiver / ingest
