# coding=utf-8
"""."""

import json
from os.path import dirname, join


from sip_config_db import DB
from sip_config_db.scheduling import SchedulingBlockInstance
from .test_utils import add_workflow_definitions
from ..scheduler.scheduler import ProcessingBlockScheduler
# from ..processing_block_controller.tasks import APP, execute_processing_block


def test_scheduler():
    """Test creating the Scheduler after SBI data is already in the db."""
    # Add a number of SBIs to the database.
    DB.flush_db()
    data_dir = join(dirname(__file__), 'data')
    add_workflow_definitions(join(data_dir, 'workflow_definitions'))
    with open(join(data_dir, 'sbi_config_2.json')) as _file:
        sbi_config = json.load(_file)
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.processing_block_ids
    assert len(pb_ids) == 1
    assert pb_ids[0] == 'PB-20181116-sip-001'
    assert isinstance(pb_ids[0], str)

    scheduler = ProcessingBlockScheduler()

    print("QUEUE: {}".format(scheduler.queue()))

    # FIXME(BM) At this point the queue should not be empty!
    assert not scheduler.queue()


# def test_late_initialisation():
#     """Test creating the Scheduler after SBI data is already in the db."""
#     # Add a number of SBIs to the database.
#     _db = SchedulingBlockDbClient()
#     for _ in range(2):
#         _db.add_sbi(generate_sbi_config())
#         # add(generate_sbi_config())
#
#     scheduler = ProcessingBlockScheduler()
#
#     # FIXME(BM) At this point the queue should not be empty!
#     assert not scheduler.queue()
