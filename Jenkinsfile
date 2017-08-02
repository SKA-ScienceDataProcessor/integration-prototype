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
					#rm -r _build || true
					virtualenv -p `which python3` _build
				'''

				// Install requirements
				sh '''
					. _build/bin/activate
					pip install -U pip setuptools Sphinx sphinx-rtd-theme pep8 pylint
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
				// Run unit tests, then publish JUnit-style report
				sh '''
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
