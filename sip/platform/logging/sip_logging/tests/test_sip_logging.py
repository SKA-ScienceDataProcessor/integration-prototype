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

    # from ..sip_logging import disable_logger, set_log_level
    # print('')
    # print('**************')
    # log2 = logging.getLogger('foo.test')
    # init_logger(logger_name='', p3_mode=False)
    # log.info('xx 1')
    # log2.info('yy 1')
    #
    # disable_logger(logger_name='foo.test')
    #
    # init_logger(p3_mode=False, show_thread=False, show_log_origin=True)
    # set_log_level('sip', logging.CRITICAL)
    # log.info('xx 2')
    # set_log_level('', logging.DEBUG)
    # log2.info('yy 2')
    #
    # init_logger(p3_mode=False, show_thread=True)
    # log.debug('xx 3')
    #
    # init_logger(p3_mode=True, show_thread=False)
    # log.info('xx 4')
    #
    # init_logger(p3_mode=True, show_thread=True)
    # log.info('xx 5')
