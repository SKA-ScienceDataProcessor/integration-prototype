pipeline {
	agent any

	stages {
		stage('Build') {
			steps {
				echo 'Build stage initiating'
				sh 'echo $WORKSPACE'

				sh '''
					# Set up fresh Python virtual environment
					virtualenv -p `which python3` --no-site-packages _build
				'''

				sh '''
					# Install requirements
					. _build/bin/activate
					pip install -U pip setuptools
					pip install -r requirements.txt
				'''

				sh '''
					# Make documentation
					cd sdoc
					make html
				'''

				sh '''
					# Make Docker containers
					#docker swarm init
					#docker network create --driver overlay sip
					docker build -t sip .
				'''

			}
		}
		stage('Test') {
			steps {
				echo 'Test stage initiating'

				sh '''
					# Run unit tests
					. _build/bin/activate
					python3 ./setup.py test -r xmlrunner
				'''
				junit 'test_reports.xml'
			}
		}
	}
}
