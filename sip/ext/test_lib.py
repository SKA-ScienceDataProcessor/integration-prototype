# coding: utf-8
"""Example showing how to wrap a C object in a Python class.

This relies on the C extension _test_lib, which is built as part of
running setup.py.

If the extension is not found, this module will do nothing.
"""

try:
    from sip.ext import _test_lib
except ImportError:
    _test_lib = None


class TestObject:
    def __init__(self, scale_a=1.0, scale_b=1.0):
        """Creates the TestObject.

        Args:
            scale_a (float): Value by which to scale input vector a.
            scale_b (float): Value by which to scale input vector b.
        """
        self._capsule = None
        if _test_lib is None:
            print("Unable to use _test_lib. Ensure sip has been installed.")
            return

        # Store the PyCapsule, which encapsulates the TestObject created in C,
        # as a private member of this class.
        self._capsule = _test_lib.create(scale_a, scale_b)

    def add_arrays(self, a, b):
        """Exposes the C function test_object_add_arrays().

        Performs the operation c = a * scale_a + b * scale_b

        Args:
            a (float, array-like): Input vector a.
            b (float, array-like): Input vector b.

        Returns:
            c (float, numpy.array): Output vector c.
        """
        if self._capsule is None:
            return None
        return _test_lib.add_arrays(self._capsule, a, b)
