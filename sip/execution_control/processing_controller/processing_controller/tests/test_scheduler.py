# coding=utf-8
"""."""

from ..scheduler.db.generate import generate_sbi_config
from ..scheduler.db.sbi import add
from ..scheduler.scheduler import ProcessingBlockScheduler


def test_late_initialisation():
    """Test creating the Scheduler after SBI data is already in the db."""
    # Add a number of SBIs to the database.
    for _ in range(2):
        add(generate_sbi_config())

    scheduler = ProcessingBlockScheduler()

    # FIXME(BM) At this point the queue should not be empty!
    assert not scheduler.queue()
