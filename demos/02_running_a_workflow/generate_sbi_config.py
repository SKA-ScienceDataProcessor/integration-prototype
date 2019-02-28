# coding: utf-8
"""Script to generate an SBI configuration for this demo."""
import datetime
import json
import sys
from random import randint


def generate_sbi(index: int = None):
    """Generate a SBI config JSON string."""
    date = datetime.datetime.utcnow().strftime('%Y%m%d')
    if index is None:
        index = randint(0, 999)
    sbi_id = 'SBI-{}-sip-demo-{:03d}'.format(date, index)
    sb_id = 'SBI-{}-sip-demo-{:03d}'.format(date, index)
    pb_id = 'PB-{}-sip-demo-{:03d}'.format(date, index)
    print('* Generating SBI: %s, PB: %s' % (sb_id, pb_id))
    sbi = dict(
        id=sbi_id,
        version='1.0.0',
        scheduling_block=dict(
            id=sb_id,
            project='sip',
            programme_block='sip_demos'
        ),
        processing_blocks=[
            dict(
                id=pb_id,
                version='1.0.0',
                type='offline',
                priority=1,
                dependencies=[],
                resources_required=[],
                workflow=dict(
                    id='mock_workflow',
                    version='1.0.0',
                    parameters=dict(
                        stage1=dict(duration=30),
                        stage2=dict(duration=30),
                        stage3=dict(duration=30)
                    )
                )
            )
        ]
    )
    return sbi


if __name__ == '__main__':
    _index = int(sys.argv[1]) if len(sys.argv) == 2 else None
    sbi_config = generate_sbi(_index)
    sbi_json = json.dumps(sbi_config)
