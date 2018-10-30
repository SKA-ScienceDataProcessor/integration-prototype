# coding=utf-8
"""High Level interface to Scheduling Block Instance (SBI) objects."""
import logging
import ast
import datetime
from random import randint

from .scheduling_data_object import SchedulingDataObject
from .pb import ProcessingBlock
from .config_db_redis import ConfigDb

DB = ConfigDb()
LOG = logging.getLogger('SIP.EC.CDB')


class SchedulingBlockInstance(SchedulingDataObject):
    """Scheduling Block Instance Configuration Database API."""

    def __init__(self, sbi_id):
        """."""
        SchedulingDataObject.__init__(self, 'sbi', DB)
        self._id = sbi_id
        self._key = self.primary_key(self._id)

    def get_config(self):
        """Return the SBI configuration."""
        return self.get_block_details(self._id)

    def abort(self):
        """Abort the Scheduling Block Instance."""
        LOG.debug('Deleting SBI %s', self._id)
        sbi_key = self.primary_key(self._id)

        # Check that the key exists!
        if not DB.get_keys(sbi_key):
            raise KeyError('Scheduling Block Instance not found: {}'
                           .format(self._id))

        # lists in one atomic transaction (using pipelines)
        self.publish(self._id, 'aborted')
        DB.remove_element('{}:active'.format(self.aggregate_type), 0, self._id)
        DB.append_to_list('{}:aborted'.format(self.aggregate_type), self._id)
        # sbi_pb_ids = get_hash_value(block_id, 'processing_block_ids')
        sbi_pb_ids = ast.literal_eval(
            DB.get_hash_value(sbi_key, 'processing_block_ids'))

        for pb_id in sbi_pb_ids:
            pb = ProcessingBlock(pb_id)
            pb.abort()

    @staticmethod
    def get_id(date=None, project: str = 'sip',
               instance_id: int = None) -> str:
        """Get a Scheduling Block Instance (SBI) ID.

        Args:
            date (str or datetime.datetime, optional): UTC date of the SBI
            project (str, optional ): Project Name
            instance_id (int, optional): SBI instance identifier

        Returns:
            str, Scheduling Block Instance (SBI) ID.

        """
        if date is None:
            date = datetime.datetime.utcnow()

        if isinstance(date, datetime.datetime):
            date = date.strftime('%Y%m%d')

        if instance_id is None:
            instance_id = randint(0, 9999)

        return 'SBI-{}-{}-{:04d}'.format(date, project, instance_id)
