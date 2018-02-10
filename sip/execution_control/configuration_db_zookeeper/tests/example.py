# -*- coding: utf-8 -*-
import logging

from kazoo.client import KazooClient

logging.basicConfig()

zk = KazooClient(hosts='127.0.0.1:2181')
zk.start()

try:
    zk.ensure_path('/scheduling_blocks')
except:
    pass
try:
    rtn = zk.create('/scheduling_blocks/sb-01', b"value")
    print(rtn)
except:
    pass

try:
    zk.create('/scheduling_blocks/sb-01/processing_blocks', b'value')
except:
    pass

try:
    zk.create('/scheduling_blocks/sb-01/status', b'value')
except:
    pass

zk.set('/scheduling_blocks/sb-01/status', b'OK')

data, stat = zk.get('/scheduling_blocks/sb-01')
print('data', data)
print('stat', stat)

children = zk.get_children('/scheduling_blocks/sb-01')
print('children', children)
print(type(children))

data, stat = zk.get('/scheduling_blocks/sb-01/status')
print('data', data)
print('stat', stat)

zk.stop()
