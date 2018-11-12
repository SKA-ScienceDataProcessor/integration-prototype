# coding: utf-8
"""Unit tests of the SIP logging utility module."""
import logging

from ..sip_logging import init_logger


def test_logging(capsys):
    """Test generating some log messages."""
    print('')
    init_logger()
    log = logging.getLogger('sip.test')

    log.info('hello')
    captured = capsys.readouterr()
    assert 'sip.test' in captured.out
    assert 'INFO' in captured.out
    assert 'hello' in captured.out

    log.debug('hello again')
    captured = capsys.readouterr()
    assert 'sip.test' in captured.out
    assert 'DEBUG' in captured.out
    assert 'hello again' in captured.out
