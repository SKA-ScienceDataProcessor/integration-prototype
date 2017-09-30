import unittest

from sip.common.resource_manager import ResourceManager


class ResourceManagerTest(unittest.TestCase):
    def setUp(self):
        self.mgr = ResourceManager({
            'localhost': {
                 'sip_root': 'root1',
                 'launch_protocol': ['ssh', 'docker']
            },
            'docker': {
                 'sip_root': 'root2',
                 'launch_protocol': ['docker']
            },
            'ssh': {
                 'sip_root': 'root3',
                 'launch_protocol': ['ssh']
            }
        })

    def testExplicitHost(self):

        # Test explicit host
        self.assertEqual(
            self.mgr.allocate_host('test1', {'host': 'localhost'}, {}),
                'localhost')
        self.assertEqual(
            self.mgr.allocate_host('test2', {'host': 'docker'}, {}), 'docker')
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_host('test3', {'host': 'xxxxx'}, {})

    def testExclusive1(self):

        # Test the exclusive flag
        self.mgr.allocate_host('test1',
                {'host': 'localhost', 'exclusive': True}, {})
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_host('test2', {'host': 'localhost'}, {})

    def testExclusive2(self):

        # Test the exclusive flag
        self.mgr.allocate_host('test1', {'host': 'localhost'}, {})
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_host('test2',
                {'host': 'localhost', 'exclusive': True}, {})

    def testSelectUnused(self):
        t1 = self.mgr.allocate_host('test1', {}, {})
        t2 = self.mgr.allocate_host('test2', {}, {})
        t3 = self.mgr.allocate_host('test3', {}, {})
        self.assertNotEqual(t1, t2)
        self.assertNotEqual(t1, t3)
        self.assertNotEqual(t2, t3)
        t4 = self.mgr.allocate_host('test4', {}, {})

    def testDuplicate(self):
        self.mgr.allocate_host('test1', {'host': 'localhost'}, {})
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_host('test1', {}, {})

    def testRelease(self):
        self.mgr.allocate_host('test1', {'host': 'localhost'}, {})
        self.mgr.release_host('test1')
        self.mgr.allocate_host('test1', {'host': 'localhost'}, {})

    def testBadResource(self):
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_resource('test1', 'tcp_port')
        self.mgr.allocate_host('test1', {}, {})
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_resource('test1', 'xxxx')

    def testAllocateTcpPort(self):
        self.mgr.allocate_host('test1', {}, {})
        self.assertEqual(self.mgr.allocate_resource('test1', 'tcp_port'),
                6000)
        self.assertEqual(self.mgr.allocate_resource('test1', 'tcp_port'),
                6001)

    def testDeallocateTcpPort(self):
        self.mgr.allocate_host('test1', {'host': 'localhost'}, {})
        self.assertEqual(self.mgr.allocate_resource('test1', 'tcp_port'),
                6000)
        self.mgr.release_host('test1')
        self.mgr.allocate_host('test2', {'host': 'localhost'}, {})
        self.assertEqual(self.mgr.allocate_resource('test2', 'tcp_port'),
                6000)

    def testLaunchProtocol(self):
        self.mgr.allocate_host('test1',
                {'host': 'localhost', 'exclusive': True}, {})
        self.assertEqual(self.mgr.allocate_host('test2',
                {'launch_protocol': 'ssh'}, {}), 'ssh')
        self.assertEqual(self.mgr.allocate_host('test3',
                {'launch_protocol': 'docker'}, {}), 'docker')

    def testSipRoot(self):
        self.assertEqual(self.mgr.sip_root('localhost'), 'root1')
        self.assertEqual(self.mgr.sip_root('docker'), 'root2')

if __name__ == "__main__":
    unittest.main()
