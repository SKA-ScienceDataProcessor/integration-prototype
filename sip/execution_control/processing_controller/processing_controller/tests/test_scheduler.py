# coding=utf-8
"""."""

from ..scheduler.db.generate import generate_sbi_config
from ..scheduler.db.sbi import add_sbi
from ..scheduler.scheduler import ProcessingBlockScheduler


def test_late_initialisation():
    """Test creating the Scheduler after SBI data is already in the db."""
    # Add a number of SBIs to the database.
    for _ in range(2):
        add_sbi(generate_sbi_config())

    scheduler = ProcessingBlockScheduler()

    print(scheduler.queue())
