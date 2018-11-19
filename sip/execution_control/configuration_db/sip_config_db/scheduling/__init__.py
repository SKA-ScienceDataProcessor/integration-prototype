# coding=utf-8
"""Objects used for scheduling processing on SDP."""
from .dependency import Dependency
from .resource import Resource
from .workflow_stage import WorkflowStage
from .processing_block import ProcessingBlock
from .processing_block_list import ProcessingBlockList
from .scheduling_block_instance import SchedulingBlockInstance
from .scheduling_block_instance_list import SchedulingBlockInstanceList
from .subarray import Subarray
from .subarray_list import SubarrayList

__all__ = [
    'Dependency',
    'Resource',
    'WorkflowStage',
    'ProcessingBlock',
    'ProcessingBlockList',
    'SchedulingBlockInstance',
    'SchedulingBlockInstanceList',
    'Subarray',
    'SubarrayList'
]

SBI_VERSION = "1.0.0"
PB_VERSION = "1.0.0"
