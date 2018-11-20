# coding=utf-8
"""."""

from ..scheduler.generate_scheduling_data import generate_sbi_config
from config_db import SchedulingBlockDbClient
from ..scheduler.scheduler import ProcessingBlockScheduler


def test_late_initialisation():
    """Test creating the Scheduler after SBI data is already in the db."""
    # Add a number of SBIs to the database.
    _db = SchedulingBlockDbClient()
    for _ in range(2):
        _db.add_sbi(generate_sbi_config())
        # add(generate_sbi_config())

    scheduler = ProcessingBlockScheduler()

    # FIXME(BM) At this point the queue should not be empty!
    assert not scheduler.queue()
