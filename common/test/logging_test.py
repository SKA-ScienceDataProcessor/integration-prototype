import unittest
import os

os.environ['SIP_HOSTNAME'] = os.uname()[1]

from sip_common import logger

class LoggerTest(unittest.TestCase):
    def testError(self):
        logger.info('An error message')

    def testInfo(self):
        logger.info('An info message')

    def testTrace(self):
        logger.info('A trace message')

    def testWarn(self):
        logger.info('A warn message')

if __name__ == "__main__":
    unittest.main()
