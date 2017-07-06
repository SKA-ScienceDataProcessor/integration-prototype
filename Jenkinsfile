pipeline {
	agent { label 'sdp-ci-01' }

	stages {
		stage('Setup') {
			steps {
				// Set up fresh Python virtual environment
				sh '''
					# Need to rm old virtualenv dir or else PIP will try to
					# to install a hybrid old/new version. I don't get it
					# either. NEEDS FIX.
					rm -r _build || true # Jenkins bails on non-zero exit code o.O
					virtualenv -p `which python3` --no-site-packages _build
				'''

				// Install requirements
				sh '''
					. _build/bin/activate
					pip install -U pip setuptools
					pip install pylint flake8
					pip install -r requirements.txt
				'''

			}
		}
		stage('Analysis') {
			steps {
				// TODO: we need to decide to go with PyLint, Flake8, both or other
				sh '''
					. _build/bin/activate
					#Run PyLint
					pylint --output-format=parseable sip *.py > pylint.log || true
					flake8 sip *.py > flake8.log || true
				'''

				// Temporary try/catch -- for Jenkins without Warnings Plugin installed
				script {
					try {
				// Submit result. TODO: determine when to declare healthy/unstable/fail
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
						pattern   : 'flake8.log'
						]],
						unstableTotalAll           : '0',
						usePreviousBuildAsReference: true
				])
					}
					finally {
						echo "Warnings plugin not supported on this Jenkins install"
					}
				}
			}
		}
		stage('Build SIP') {
			steps {
				// Build and install sip
				// Also build docker container
				sh '''
					. _build/bin/activate

					python3 ./setup.py install

					docker build -t sip .
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
				// Run unittests and generate XML report (JUnit compatible)
				sh '''
					. _build/bin/activate

					python3 ./setup.py test -r xmlrunner
					# Kill stray processes (NEEDS TO BE FIXED)
					pkill python3 || true
				'''

				// Publish JUnit report
				junit 'test_reports.xml'
			}
		}
		stage('Deploy') {
			steps {
				echo 'To be implemented'
			}
		}
	}
}
