""" Simple Apache Spark job to support the unit test (test_paas_spark.py).

Create context, sleep & stop

.. moduleauthor:: Arjen Tamerus <at748@cam.ac.uk> 
"""
import time
from pyspark import SparkContext

sc = SparkContext()

time.sleep(3)

sc.stop()
