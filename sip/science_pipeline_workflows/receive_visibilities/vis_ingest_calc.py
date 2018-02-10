# -*- coding: utf-8 -*-
"""Module for processing visibility data received from CSP.

This module makes use of the VisINgestProcessing class to further 
process visibility data
"""

class VisIngestProcessing():
    def __init__(self, log):
        """Class to develop ingest processing components
        
        The ingest processing workflow contains more steps than just the 
        visibility receive task. 
        """
        self._log = log

    def data_weight(self):
        """Calculate the data weighs from the fraction of data 
        flagged and autocorrelation data """
        self._log.info("Calculate data weights")

    def flag_vis_data(self):
        """Flagging the visibility data for known RFI 
        and apparent bad data"""
        self._log.info("Flag visibility data")


    def demix_vis_data(self):
        """Demix to remove the effect of a small number of very
        bright source"""
        self._log.info("Demix visibility data or direct "
                       "solve and subtract")

    def avg_vis_data(self):
        """Averaging to reduce data rate while staying within the 
        smearing limits"""
        self._log.info("Averaging visibility data")
