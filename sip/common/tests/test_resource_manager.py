# coding: utf-8
""" Tests of the resource manager.
"""
import unittest

from sip.common.resource_manager import ResourceManager


class ResourceManagerTest(unittest.TestCase):
    """ Tests of the ResourceManager
    """

    def setUp(self):
        """ Set up test fixture.

        Creates a ResourceManager object.
        """
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

    def test_explicit_host(self):
        """ Test explicit host
        """
        self.assertEqual(
            self.mgr.allocate_host('test1', {'host': 'localhost'}, {}),
            'localhost')
        self.assertEqual(
            self.mgr.allocate_host('test2', {'host': 'docker'}, {}),
            'docker')
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_host('test3', {'host': 'xxxxx'}, {})

    def test_exclusive1(self):
        """ Test the exclusive flag
        """
        self.mgr.allocate_host('test1',
                               {'host': 'localhost', 'exclusive': True},
                               {})
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_host('test2', {'host': 'localhost'}, {})

    def test_exclusive2(self):
        """ Test the exclusive flag
        """
        self.mgr.allocate_host('test1', {'host': 'localhost'}, {})
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_host('test2',
                                   {'host': 'localhost', 'exclusive': True},
                                   {})

    def test_select_unused(self):
        """ FIXME(BM): add description
        """
        host1 = self.mgr.allocate_host('test1', {}, {})
        host2 = self.mgr.allocate_host('test2', {}, {})
        host3 = self.mgr.allocate_host('test3', {}, {})
        self.assertNotEqual(host1, host2)
        self.assertNotEqual(host1, host3)
        self.assertNotEqual(host2, host3)
        _ = self.mgr.allocate_host('test4', {}, {})

    def test_duplicate(self):
        """ FIXME(BM): add description
        """
        self.mgr.allocate_host('test1', {'host': 'localhost'}, {})
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_host('test1', {}, {})

    def test_release(self):
        """ FIXME(BM): add description
        """
        self.mgr.allocate_host('test1', {'host': 'localhost'}, {})
        self.mgr.release_host('test1')
        self.mgr.allocate_host('test1', {'host': 'localhost'}, {})

    def test_bad_resource(self):
        """ FIXME(BM): add description
        """
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_resource('test1', 'tcp_port')
        self.mgr.allocate_host('test1', {}, {})
        with self.assertRaises(RuntimeError):
            self.mgr.allocate_resource('test1', 'xxxx')

    def test_allocate_tcp_port(self):
        """ FIXME(BM): add description
        """
        self.mgr.allocate_host('test1', {}, {})
        self.assertEqual(self.mgr.allocate_resource('test1', 'tcp_port'),
                         6000)
        self.assertEqual(self.mgr.allocate_resource('test1', 'tcp_port'),
                         6001)

    def test_deallocate_tcp_port(self):
        """ FIXME(BM): add description
        """
        self.mgr.allocate_host('test1', {'host': 'localhost'}, {})
        self.assertEqual(self.mgr.allocate_resource('test1', 'tcp_port'),
                         6000)
        self.mgr.release_host('test1')
        self.mgr.allocate_host('test2', {'host': 'localhost'}, {})
        self.assertEqual(self.mgr.allocate_resource('test2', 'tcp_port'),
                         6000)

    def test_launch_protocol(self):
        """ FIXME(BM): add description
        """
        self.mgr.allocate_host(
            'test1', {'host': 'localhost', 'exclusive': True}, {})
        self.assertEqual(self.mgr.allocate_host(
            'test2', {'launch_protocol': 'ssh'}, {}), 'ssh')
        self.assertEqual(self.mgr.allocate_host(
            'test3', {'launch_protocol': 'docker'}, {}), 'docker')

    def test_sip_root(self):
        """ FIXME(BM): add description
        """
        self.assertEqual(self.mgr.sip_root('localhost'), 'root1')
        self.assertEqual(self.mgr.sip_root('docker'), 'root2')
