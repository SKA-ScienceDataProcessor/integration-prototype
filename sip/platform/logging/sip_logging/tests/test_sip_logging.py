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

    init_logger(show_thread=True)
    log.critical('hello!!')
    captured = capsys.readouterr()
    assert 'sip.test' in captured.out
    assert 'CRITICAL' in captured.out
    assert 'MainThread' in captured.out
    assert 'hello!!' in captured.out

    init_logger(show_thread=True, p3_mode=False)
    log.warning('hello there')
    captured = capsys.readouterr()
    assert 'sip.test' in captured.out
    assert 'WARNING' in captured.out
    assert 'MainThread' in captured.out
    assert 'hello there' in captured.out

    init_logger(p3_mode=False)
    log.warning('hello there again')
    captured = capsys.readouterr()
    assert 'sip.test' in captured.out
    assert 'WARNING' in captured.out
    assert 'hello there' in captured.out

    # print('')
    # init_logger(p3_mode=False, show_thread=False)
    # log.info('xx')
    #
    # print('')
    # init_logger(p3_mode=False, show_thread=True)
    # log.info('xx')
    #
    # print('')
    # init_logger(p3_mode=True, show_thread=False)
    # log.info('xx')
    #
    # print('')
    # init_logger(p3_mode=True, show_thread=True)
    # log.info('xx')
