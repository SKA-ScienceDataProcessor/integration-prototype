""" This is a trival test task 

It sleeps for a time specified by the first command line argument (seconds)
and then exits with a status specified by the second.
"""
import sys
import time

time.sleep(float(sys.argv[1]))

sys.exit(int(sys.argv[2]))
