import unittest
import os

os.environ['SIP_HOSTNAME'] = os.uname()[1]

from sip_common import logger

class LoggerTest(unittest.TestCase):
    def testError(self):
        logger.info('An error message')

    def testInfo(self):
        logger.info('An info message')

    def testDebug(self):
        logger.info('A debug message')

    def testWarn(self):
        logger.info('A warn message')

    def testFatal(self):
        logger.info('A fatal message')

if __name__ == "__main__":
    unittest.main()
