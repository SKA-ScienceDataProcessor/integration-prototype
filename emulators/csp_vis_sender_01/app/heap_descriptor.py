# -*- coding: utf-8 -*-
"""Module defining the SKA SPEAD heap descriptors.

This *should* match the description in the CSP-SDP ICD.
"""


def get_heap_descriptor(frame_shape):
    """Return a SPEAD heap descriptor for a given heap frame shape"""
    return [
        # Per SPEAD heap_descriptor
        {
            "id": 0x0045,
            "name": "timestamp_utc",
            "description": "SDP_REQ_INT-45.",
            "format": [('u', 32), ('u', 32)],
            "shape": (1,)
        },
        {
            "id": 0x0046,
            "name": "channel_baseline_id",
            "description": "SDP_REQ_INT-46",
            "format": [('u', 26), ('u', 22)],
            "shape": (1,)
        },
        {
            "id": 0x0047,
            "name": "channel_baseline_count",
            "description": "SDP_REQ_INT-47",
            "format": [('u', 26), ('u', 22)],
            "shape": (1,)
        },
        {
            "id": 0x0048,
            "name": "schedule_block",
            "description": "SDP_REQ_INT-48",
            "type": "u8",
            "shape": (1,)
        },
        {
            "id": 0x0049,
            "name": "hardware_source_id",
            "description": "SDP_REQ_INT-49",
            "format": [('u', 24)],
            "shape": (1,)
        },
        # Per visibility data
        {
            "id": 0x0050,
            "name": "time_centroid_index",
            "description": "SDP_REQ_INT-50",
            "format": [('u', 8)],
            "shape": frame_shape
        },
        {
            "id": 0x0051,
            "name": "complex_visibility",
            "description": "SDP_REQ_INT-51",
            "type": 'c8',
            "shape": frame_shape
        },
        {
            "id": 0x0052,
            "name": "flagging_fraction",
            "description": "SDP_REQ_INT-52",
            "format": [('u', 8)],
            "shape": frame_shape
        }
    ]
