
#include <Python.h>

/* http://docs.scipy.org/doc/numpy-dev/reference/c-api.deprecations.html */
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

static const char module_doc[] = "This is a test module.";


static PyObject* print_hello1(PyObject* self, PyObject* args)
{
    return Py_BuildValue("s", "hello from C");
}

static PyObject* print_hello2(PyObject* self, PyObject* args)
{
    return Py_BuildValue("s", "hello from C (again)");
}

/* Method table. */
static PyMethodDef methods[] =
{
        {"print_hello1", (PyCFunction)print_hello1,
                METH_VARARGS, "print_hello1()"},
        {"print_hello2", (PyCFunction)print_hello2,
                METH_VARARGS, "print_hello2()"},
        {NULL, NULL, 0, NULL}
};

/* The rest of this is standard boilerplate.
 * Just remember to update the module name. */
#if PY_MAJOR_VERSION >= 3
static PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "_test_lib",        /* m_name */
        module_doc,         /* m_doc */
        -1,                 /* m_size */
        methods             /* m_methods */
};
#endif

static PyObject* moduleinit(void)
{
    PyObject* m;
#if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&moduledef);
#else
    m = Py_InitModule3("_test_lib", methods, module_doc);
#endif
    return m;
}

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit__test_lib(void)
{
    import_array();
    return moduleinit();
}
#else
/* The init function name has to match that of the compiled module
 * with the pattern 'init<module name>'. This module is called '_test_lib' */
PyMODINIT_FUNC init_test_lib(void)
{
    import_array();
    moduleinit();
    return;
}
#endif
