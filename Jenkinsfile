pipeline {
	agent { label 'sdp-ci-01' }

	stages {
		stage('Setup') {
			steps {
				sh '''
				  # Need to rm old virtualenv dir or else PIP will try to
					# to install a hybrid old/new version. I don't get it
					# either. NEEDS FIX.
					rm -r _build || true
					# Set up fresh Python virtual environment
					virtualenv -p `which python3` --no-site-packages _build
				'''

				sh '''
					# Install requirements
					. _build/bin/activate
					pip install -U pip setuptools
					pip install -U pyflakes
					pip install -r requirements.txt
				'''

			}
		}
		stage('Build SIP') {
			steps {
				sh '''
					. _build/bin/activate

				  # build sip
					python3 ./setup.py build
					python3 ./setup.py install
				'''

				sh '''
					# Make Docker containers
					#docker swarm init
					#docker network create --driver overlay sip
					docker build -t sip .
				'''
			}
		}
		stage('Build docs') {
			steps {
				sh '''
					. _build/bin/activate
					# Make documentation
					cd sdoc
					make html
				'''
			}
		}
		stage('Test') {
			steps {

				sh '''
					# Run unit tests
					. _build/bin/activate
					python3 ./setup.py test -r xmlrunner
					# Kill stray processes (NEEDS TO BE FIXED)
					pkill python3 || true
				'''
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
