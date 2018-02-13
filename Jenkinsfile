// SIP Jenkinsfile (CI/CD pipline)
//
// https://jenkins.io/doc/book/pipeline/jenkinsfile/
//
// Stages section:
// - Setup
// - Analysis
// - Build
// - Test
//
// Post section: (https://jenkins.io/doc/book/pipeline/syntax/#post)
// - success
// - unstable
// - failure
// - always

pipeline {

  agent { label 'sdp-ci-01' }

  stages {

    stage('Setup') {
      steps {
        // Create a fresh Virtual environment
        sh '''
        virtualenv -p `which python3` venv
        '''

        // Install requirements
        sh '''
        source venv/bin/activate
        pip install pylint pycodestyle
        find emulators -iname "requirements.txt" | xargs -n1 pip install -r
        find sip/execution_control -iname "requirements.txt" | \
          xargs -n1 pip install -r
        '''
      }
    } // End stage('Setup')

    stage('Analysis') {
      steps {
        // Run PyLint and PyCodeStyle
        sh '''
        source venv/bin/activate
        uname -rm
        pylint --version
        pycodestyle --version
        python --version

        # find emulators -iname "*.py" | xargs pylint > pylint.log || true
        # find sip -iname "*.py" | xargs pylint >> pylint.log || true
        # find emulators -iname "*.py" | xargs pycodestyle > style.log || true
        # find sip -iname "*.py" | xargs pycodestyle >> style.log || true

        echo $(pwd)
        # find emulators -iname "*.py" | xargs pylint  || true
        pylint emulators/csp_vis_sender_01/app/__main__.py
        # find emulators -iname "*.py" | xargs pycodestyle || true
        '''

        // Publish warnings. Currently, this does not affect the build status.
        // Can report difference from last stable build using
        // 'useStableBuildAsReference'
        step([
          $class : 'WarningsPublisher',
          parserConfigurations : [[
            parserName: 'PyLint',
            pattern   : 'pylint.log'
          ]],
          changeBuildStatus : false,
          usePreviousBuildAsReference: true
        ])

        step([
          $class : 'WarningsPublisher',
          parserConfigurations : [[
            parserName: 'PEP8',
            pattern   : 'style.log'
          ]],
          changeBuildStatus : false,
          usePreviousBuildAsReference: true
        ])
      }
    } // End stage('Analysis')

    // stage('Build') {
    //   steps {
    //     // Build and install SIP, build containers
    //     // Tag container with branch name (JOB_BASE_NAME)
    //     // sh '''
    //     // . _build/bin/activate
    //     //
    //     // python3 ./setup.py install
    //     // docker build -t sip:${JOB_BASE_NAME} .
    //     // '''
    //   }
    // } // End stage('Build')

    // stage('Test') {
    //   steps {
    //     // // Run unit tests, then publish JUnit-style report
    //     // // use 'coverage' to generate code coverage report &&
    //     // // publish results through Cobertura plugin
    //     // sh '''
    //     // . _build/bin/activate
    //     //
    //     // coverage run \
    //     // --omit=*/tests/*,*/_*.py,*/__init__.py,sip/ext/* \
    //     // --source=sip ./setup.py test -r xmlrunner
    //     // # coverage run -a --source=sip sip/tests/test_execution.py || true
    //     // coverage xml
    //     // '''
    //     //
    //     // junit 'test_reports.xml'
    //     //
    //     // // Coverage report.
    //     // // 'onlyStable = false' to enable report publication even when build
    //     // // status is not 'SUCCESS'
    //     // step ([$class: 'CoberturaPublisher',
    //     // coberturaReportFile: 'coverage.xml',
    //     // onlyStable: false,
    //     // sourceEncoding: 'ASCII'])
    //   }
    // } // end stage('Test')
  } // end stages



  post {

    success {
      echo 'Build stable. Pushing image as -latest and -stable.'
      // // Push -stable
      // sh '''
      // /usr/local/bin/delete_from_reg.sh localhost:5000 sip `cat dockerimage-stable.digest`
      // docker tag sip:${JOB_BASE_NAME} localhost:5000/sip:${JOB_BASE_NAME}-stable
      // docker push localhost:5000/sip:${JOB_BASE_NAME}-stable
      // '''
      //
      // // Push -latest
      // sh '''
      // /usr/local/bin/delete_from_reg.sh localhost:5000 sip `cat dockerimage.digest`
      // docker tag sip:${JOB_BASE_NAME} localhost:5000/sip:${JOB_BASE_NAME}-latest
      // docker push localhost:5000/sip:${JOB_BASE_NAME}-latest
      // '''
    }

    unstable {
      echo 'Build unstable. Pushing image as -latest only.'

      // // Push -latest
      // sh '''
      // /usr/local/bin/delete_from_reg.sh localhost:5000 sip `cat dockerimage.digest`
      // docker tag sip:${JOB_BASE_NAME} localhost:5000/sip:${JOB_BASE_NAME}-latest
      // docker push localhost:5000/sip:${JOB_BASE_NAME}-latest
      // '''
    }

    failure {
      echo 'Build failure. No images pushed to registry.'
    }

    always {
      // Inspect current Docker Setup
      sh '''
      docker image ls || true
      docker volume ls || true
      docker network ls || true
      docker system df || true
      '''

      // Try to clean Docker up a bit
      sh '''
      docker image prune -f
      docker volume prune -f
      docker network prune -f
      docker system prune -f
      docker system df
      '''
    }

  } // end post
}
