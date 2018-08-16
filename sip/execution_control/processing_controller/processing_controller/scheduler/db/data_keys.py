# coding=utf-8
"""Module of functions defining db keys used for aggregate data."""


def get_sbi_key(sbi_id: str) -> str:
    """Return a Scheduling Block Instance db key.

    Args:
        sbi_id (str): Scheduling block instance id

    Returns:
        str, db key for the specified SBI

    """
    return 'sbi:{}'.format(sbi_id)


def get_pb_key(pb_id: str) -> str:
    """Return a Processing Block db key.

    Args:
        pb_id (str): Processing Block instance id

    Returns:
        str, db key for the specified PB

    """
    return 'pb:{}'.format(pb_id)
