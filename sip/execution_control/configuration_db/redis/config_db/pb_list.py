# -*- coding: utf-8 -*-
"""High Level interface to the List of Processing Block (PB) objects."""
import logging

from .config_db_redis import ConfigDb
from .scheduling_data_object import PB_TYPE_PREFIX, SchedulingDataObject

LOG = logging.getLogger('SIP.EC.CDB')
DB = ConfigDb()


class ProcessingBlockList(SchedulingDataObject):
    """Configuration Database Processing Block List API."""

    def __init__(self):
        """Initialise variables."""
        SchedulingDataObject.__init__(self, PB_TYPE_PREFIX, DB)

    # #########################################################################
    # Get functions
    # #########################################################################

    def get_num_pb_ids(self):
        """Get number of processing block ids."""
        return len(self.get_active())

    # #########################################################################
    # Abort functions
    # #########################################################################

    def abort(self, pb_id: str):
        """Abort a processing_block.

        Args:
            pb_id (str): Processing block id

        """
        pb_key = self.primary_key(pb_id)

        # Check that the key exists!
        if not DB.get_keys(pb_key):
            raise KeyError('Processing Block not found: {}'
                           .format(pb_id))

        pb_type = DB.get_hash_value(pb_key, 'type')
        self.publish(pb_id, 'aborted')
        DB.remove_element('{}:active'.format(self.aggregate_type), 0, pb_id)
        DB.remove_element('{}:active:{}'.format(self.aggregate_type,
                                                pb_type), 0, pb_id)
        DB.append_to_list('{}:aborted'.format(self.aggregate_type), pb_id)
        DB.append_to_list('{}:aborted:{}'.format(self.aggregate_type,
                                                 pb_type), pb_id)

    # #########################################################################
    # Private functions
    # #########################################################################
