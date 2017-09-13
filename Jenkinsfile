pipeline {
	agent { label 'sdp-ci-01' }

	stages {
		stage('Setup') {
			steps {
				// Get digests for current -latest and -stable docker images
				// and save to file. We need these so we can delete the old
				// images when pushing the new ones to the registry
				sh '''
				  /usr/local/bin/get_reg_digest.sh localhost:5000 sip ${JOB_BASE_NAME}-latest > dockerimage.digest
				  /usr/local/bin/get_reg_digest.sh localhost:5000 sip ${JOB_BASE_NAME}-stable > dockerimage-stable.digest
				'''

				// Set up fresh Python virtual environment
				sh '''
					# Need to rm old virtualenv dir or else PIP will try to
					# to install a hybrid old/new version. I don't get it
					# either. NEEDS FIX.
					#rm -r _build || true
					virtualenv -p `which python3` _build
				'''

				// Install requirements
				sh '''
					. _build/bin/activate
					pip install -U pip setuptools Sphinx sphinx-rtd-theme coverage pep8 pylint
					pip install -r requirements.txt
				'''

			}
		}
		stage('Analysis') {
			steps {
				// Run PyLint for code errors, PEP8 for style checking
				sh '''
					. _build/bin/activate
					pylint --output-format=parseable --disable=C,too-many-branches,no-self-use,consider-using-ternary,mixed-indentation,unnecessary-semicolon,no-else-return,too-few-public-methods,too-many-public-methods,too-many-return-statements,too-many-branches sip *.py > pylint.log || true

					#PEP8 - ignore E402: module level import not on top of file (due to code requirements)
					pep8 --ignore=E402 sip *.py > pep8.log || true
				'''

				// Publish warings. Right now: Unstable on any warning
				// TODO: Determine when to set build as 'Stable' or 'Failed'
				step([
					$class                     : 'WarningsPublisher',
					parserConfigurations       : [[
									      parserName: 'PyLint',
									      pattern   : 'pylint.log'
								      ]],
					unstableTotalAll           : '0',
					usePreviousBuildAsReference: true
				])
				step([
					$class                     : 'WarningsPublisher',
					parserConfigurations       : [[
									      parserName: 'PEP8',
									      pattern   : 'pep8.log'
								      ]],
					unstableTotalAll           : '0',
					usePreviousBuildAsReference: true
				])
			}
		}
		stage('Build SIP') {
			steps {
				// build and install SIP, build containers
				// Tag container with branch name (JOB_BASE_NAME)
				sh '''
					. _build/bin/activate

					python3 ./setup.py install
					docker build -t sip:${JOB_BASE_NAME} .
				'''
			}
		}
		stage('Build docs') {
			steps {
				sh '''
					. _build/bin/activate
					cd sdoc
					make html
				'''
			}
		}
		stage('Test') {
			steps {
				// Run unit tests, then publish JUnit-style report
				// use 'coverage' to generate code coverage report &&
				// publish results through Cobertura plugin
				sh '''
					. _build/bin/activate

					coverage run --source=sip ./setup.py test -r xmlrunner
					coverage run -a --source=sip sip/test/test_execution.py || true
					coverage xml
					
					# Kill stray processes (NEEDS TO BE FIXED)
					pkill python3 || true
				'''

				junit 'test_reports.xml'

				// Coverage report.
				// 'onlyStable = false' to enable report publication even when build
				// status is not 'SUCCESS'
				step ([$class: 'CoberturaPublisher',
                coberturaReportFile: 'coverage.xml',
                onlyStable: false,
                sourceEncoding: 'ASCII'])
			}
		}
	}
	post {
		success {
			echo 'Build stable. Pushing image as -latest and -stable.'

			// Push -stable
			sh '''
				/usr/local/bin/delete_from_reg.sh localhost:5000 sip `cat dockerimage-stable.digest`
				sh 'docker tag sip:${JOB_BASE_NAME} localhost:5000/sip:${JOB_BASE_NAME}-stable
				sh 'docker push localhost:5000/sip:${JOB_BASE_NAME}-stable
			'''

			// Push -latest
			sh '''
				'/usr/local/bin/delete_from_reg.sh localhost:5000 sip `cat dockerimage.digest`
				'docker tag sip:${JOB_BASE_NAME} localhost:5000/sip:${JOB_BASE_NAME}-latest
				'docker push localhost:5000/sip:${JOB_BASE_NAME}-latest
			'''
		}
		unstable {
			echo 'Build unstable. Only pushing -latest image.'

			// Push -latest
			sh '''
				/usr/local/bin/delete_from_reg.sh localhost:5000 sip `cat dockerimage.digest`
				docker tag sip:${JOB_BASE_NAME} localhost:5000/sip:${JOB_BASE_NAME}-latest
				docker push localhost:5000/sip:${JOB_BASE_NAME}-latest
			'''
		}
		failure {
			echo 'Build failure. No images pushed to registry.'
		}
		always {
			// Some of the Docker services tend to go haywire and kill Jenkins
			// They should all be removed, or at least fully stopped
			// This hackaround kills all services
			// Keep until problem is fixed (`docker service ls` should be empty)
			sh 'docker service ls'
			sh 'docker service rm `docker service ls -q`'
		}
	}
}
