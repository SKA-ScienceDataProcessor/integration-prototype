# coding=utf-8
"""High-level interface for subarray objects."""
import ast
import inspect
import logging
import os
from typing import List, Union

from . import events
from .config_db_redis import ConfigDb
from .sbi import SchedulingBlockInstance

DB = ConfigDb()
LOG = logging.getLogger('SIP.EC.CDB')

AGGREGATE_TYPE = 'subarray'


class Subarray:
    """Subarray API."""

    def __init__(self, subarray_id: Union[int, str]):
        """Initialise the subarray object."""
        if isinstance(subarray_id, int):
            self._id = self.get_id(subarray_id)
        else:
            self._id = subarray_id
        LOG.debug("Initialising subarray %s.", self._id)
        subarray_config = dict(id=self._id, active=False, parameters={},
                               sbi_ids=[], state='UNKNOWN')
        self.key = '{}:{}'.format(AGGREGATE_TYPE, self._id)
        if not DB.key_exists(self.key):
            DB.set_hash_values(self.key, subarray_config)

    # -------------------------------------------------------------------------
    # Properties / attributes
    # -------------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Return the subarrary Id."""
        return self._id

    @property
    def active(self) -> bool:
        """Return True if the subarray is active, otherwise False.

        Returns:
            bool, True if the subarray is active, otherwise False

        """
        value = DB.get_hash_value(self.key, 'active')
        return True if value == 'True' else False

    @property
    def config(self) -> dict:
        """Return the subarray configuration.

        Returns:
            dict, the subarray configuration

        """
        return DB.get_hash_dict(self.key)

    @property
    def parameters(self) -> dict:
        """Get the subarray parameters dictionary.

        Returns:
            dict, dictionary of subarray parameters.

        """
        return ast.literal_eval(DB.get_hash_value(self.key, 'parameters'))

    @property
    def get_state(self) -> str:
        """Get the state of the subarray."""
        return DB.get_hash_value(self.key, 'state')

    def set_parameters(self, parameters_dict):
        """Set the subarray parameters.

        Args:
            parameters_dict (dict): Dictionary of Subarray parameters
        """
        DB.set_hash_value(self.key, 'parameters', parameters_dict)
        self.publish("parameters_updated")

    @property
    def sbi_ids(self) -> List[str]:
        """Get the list of SBI Ids.

        Returns:
            list, list of SBI ids associated with this subarray.

        """
        return ast.literal_eval(DB.get_hash_value(self.key, 'sbi_ids'))

    # -------------------------------------------------------------------------
    # Methods / commands
    # -------------------------------------------------------------------------

    def configure_sbi(self, sbi_config: dict, schema_path: str = None):
        """Add a new SBI to the database associated with this subarray.

        Args:
            sbi_config (dict): SBI configuration.
            schema_path (str, optional): Path to the SBI config schema.

        """
        if not self.active:
            raise RuntimeError("Unable to add SBIs to inactive subarray!")
        sbi_config['subarray_id'] = self._id
        sbi = SchedulingBlockInstance.from_config(sbi_config, schema_path)
        self._add_sbi_id(sbi_config['id'])
        return sbi

    def abort(self):
        """Abort all SBIs associated with the subarray."""
        for sbi_id in self.sbi_ids:
            sbi = SchedulingBlockInstance(sbi_id)
            sbi.abort()
        self.set_state('ABORTED')

    def set_state(self, value):
        """Set the state of the subarray."""
        DB.set_hash_value(self.key, 'state', value)

    def activate(self):
        """Activate the subarray."""
        DB.set_hash_value(self.key, 'active', 'True')
        self.publish('subarray_activated')

    def deactivate(self):
        """Deactivate the subarray."""
        DB.set_hash_value(self.key, 'active', 'False')
        # Remove the subarray from each of the SBIs
        for sbi_id in self.sbi_ids:
            SchedulingBlockInstance(sbi_id).clear_subarray()
        DB.set_hash_value(self.key, 'sbi_ids', [])
        self.publish('subarray_deactivated')

    def remove_sbi_id(self, sbi_id):
        """Remove an SBI Identifier."""
        sbi_ids = self.sbi_ids
        sbi_ids.remove(sbi_id)
        DB.set_hash_value(self.key, 'sbi_ids', sbi_ids)

    @staticmethod
    def get_id(index: int):
        """Convert a subarray index into a subarray id.

        Returns:
            str, the subarray id for the specified index

        """
        return 'subarray_{:02d}'.format(index)

    @staticmethod
    def get_key(index: int):
        """Get the subarray key for a given index.

        Returns:
            str, the subarray key

        """
        return '{}:{}'.format(AGGREGATE_TYPE, Subarray.get_id(index))

    def _add_sbi_id(self, sbi_id):
        """Add a SBI Identifier."""
        sbi_ids = self.sbi_ids
        sbi_ids.append(sbi_id)
        DB.set_hash_value(self.key, 'sbi_ids', sbi_ids)

    # -------------------------------------------------------------------------
    # Event queue methods
    # -------------------------------------------------------------------------

    @staticmethod
    def subscribe(subscriber: str) -> events.EventQueue:
        """Subscribe to subarray events.

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying events.

        """
        return events.subscribe(AGGREGATE_TYPE, subscriber)

    @staticmethod
    def get_subscribers():
        """Get the list of subscribers to subarray events.

        Returns:
            List[str], list of subscriber names.

        """
        return events.get_subscribers(AGGREGATE_TYPE)

    def publish(self, event_type: str, event_data: dict = None):
        """Publish a subarray event.

        Args:
            event_type (str): Type of event.
            event_data (dict, optional): Event data.

        """
        _stack = inspect.stack()
        _origin = (os.path.basename(_stack[2][1]) + '::' +
                   _stack[2][3]+'::L{}'.format(_stack[2][2]))
        events.publish(AGGREGATE_TYPE, self._id, event_type, event_data,
                       origin=_origin)
