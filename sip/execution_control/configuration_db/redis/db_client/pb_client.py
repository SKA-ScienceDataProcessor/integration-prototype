# -*- coding: utf-8 -*-
"""High Level Processing Block Instance Client API."""
import ast
from typing import List

from .config_db_redis import ConfigDb
from .processing_controller_client import ProcessingControllerDbClient

AGGREGATE_TYPE = 'pb'
SBI_AGGREGATE_TYPE = 'sbi'


###########################################################################
# Add functions
###########################################################################

class ProcessingBlockDbClient(ProcessingControllerDbClient):
    """Configuration Database client API for the Processing Block."""

    def __init__(self):
        """Initialise variables."""
        self._db = ConfigDb()
        ProcessingControllerDbClient.__init__(self, AGGREGATE_TYPE, self._db)

    ###########################################################################
    # Add functions
    ###########################################################################

    def add_pb(self, processing_block_data: dict, sbi_key: str):
        """Add processing blocks to db.

        Args:
            processing_block_data (dict): Processing block data
            sbi_key (str): Scheduling BLock Instance key

        """
        # Adding Processing block with id
        for pb_config in processing_block_data:
            pb_id = pb_config['id']
            pb_key = self.get_key(pb_id)
            pb_config['scheduling_block_id'] = sbi_key
            self._db.set_hash_values(pb_key, pb_config)
            self._db.append_to_list('{}:active'.format(AGGREGATE_TYPE), pb_id)
            self._db.append_to_list('{}:active:{}'.format(
                AGGREGATE_TYPE, pb_config['type']), pb_id)

            # Publish an event to notify subscribers of the new PB
            self.publish(pb_config["id"], 'created')

    def get_pb_ids(self, sbi_id: str) -> List[str]:
        """Return the list of PB ids associated with the SBI.

        Args:
            sbi_id (str): Scheduling block instance id

        Returns:
            list, Processing block ids

        """
        # TODO(BM) move this hardcoded key to a function?
        key = 'processing_block_ids'
        return ast.literal_eval(self._db.get_hash_value(
            self._get_sbi_key(sbi_id), key))

    def get_num_pb_ids(self):
        """Get number of processing block ids."""
        return len(self.get_active())

    # #########################################################################
    # Cancel functions
    # #########################################################################

    def cancel_processing_block(self, pb_id: str):
        """Cancel a processing_block.

        Args:
            pb_id (str): Processing block id

        """
        pb_key = self.get_key(pb_id)

        # Check that the key exists!
        if not self._db.get_keys(pb_key):
            raise KeyError('Processing Block not found: {}'
                           .format(pb_id))

        pb_type = self._db.get_hash_value(pb_key, 'type')
        self.publish(pb_id, 'cancelled')
        self._db.remove_element('{}:active'.format(AGGREGATE_TYPE), 0, pb_id)
        self._db.remove_element('{}:active:{}'.format(AGGREGATE_TYPE,
                                                      pb_type), 0, pb_id)
        self._db.append_to_list('{}:cancelled'.format(AGGREGATE_TYPE), pb_id)
        self._db.append_to_list('{}:cancelled:{}'.format(AGGREGATE_TYPE,
                                                         pb_type), pb_id)

    # #########################################################################
    # Private functions
    # #########################################################################

    @staticmethod
    def _get_sbi_key(block_id: str,) -> str:
        """Return a Scheduling Block Instance or Processing Block db key.

        Args:
            block_id (str): Scheduling block instance or Processing BLock id

        Returns:
            str, db key for the specified SBI or PB

        """
        return '{}:{}'.format(SBI_AGGREGATE_TYPE, block_id)
