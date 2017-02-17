#include <stdlib.h>
#include <Python.h>

/* http://docs.scipy.org/doc/numpy-dev/reference/c-api.deprecations.html */
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

static const char module_doc[] = "This is a test module.";

/* NOTE: Remember to update method table at end of file
 * when adding new methods! */

/*===========================================================================*/
/* EXAMPLE 1: Simple stateless C Python extensions. */
static PyObject* hello1(PyObject* self, PyObject* args)
{
    return Py_BuildValue("s", "hello from C");
}

static PyObject* hello2(PyObject* self, PyObject* args)
{
    return Py_BuildValue("s", "hello from C (again)");
}


/*===========================================================================*/
/* EXAMPLE 2: Expose functions that could be from an external C API. */
/* These are pure C objects and functions. */
struct TestObject
{
    double scale_a, scale_b;
};
typedef struct TestObject TestObject;

/* TestObject constructor. */
TestObject* test_object_create(double scale_a, double scale_b)
{
    TestObject* handle = (TestObject*) calloc(1, sizeof(TestObject));
    handle->scale_a = scale_a;
    handle->scale_b = scale_b;
    return handle;
}

/* TestObject destructor. */
void test_object_free(TestObject* handle)
{
    free(handle);
}

/* A function that uses TestObject: c = a * scale_a + b * scale_b */
void test_object_add_arrays(const TestObject* handle,
        int num_points, const double* a, const double* b, double* c)
{
    for (int i = 0; i < num_points; ++i)
        c[i] = a[i] * handle->scale_a + b[i] * handle->scale_b;
}

/*---------------------------------------------------------------------------*/
/* Define Python methods to interact with C object using PyCapsule. */
static const char name[] = "TestObject";


/* Helper function to return a handle to the C object inside the PyCapsule. */
static TestObject* get_handle(PyObject* capsule)
{
    TestObject* handle = 0;
    if (!PyCapsule_CheckExact(capsule))
    {
        PyErr_SetString(PyExc_RuntimeError, "Input is not a PyCapsule object!");
        return 0;
    }
    if (!(handle = (TestObject*) PyCapsule_GetPointer(capsule, name)))
    {
        PyErr_SetString(PyExc_RuntimeError, "Cannot get handle to TestObject.");
        return 0;
    }
    return handle;
}


/* Helper function to tell PyCapsule how to release the object it contains. */
static void capsule_destructor(PyObject* capsule)
{
    test_object_free(get_handle(capsule));
}


/* Exposes test_object_create(). */
static PyObject* create(PyObject* self, PyObject* args)
{
    /* Parse the Python function arguments. */
    double scale_a = 0.0, scale_b = 0.0;
    if (!PyArg_ParseTuple(args, "dd", &scale_a, &scale_b)) return 0;

    /* Use the C API to create a handle to the TestObject. */
    TestObject* handle = test_object_create(scale_a, scale_b);

    /* Store the handle to the TestObject inside a new PyCapsule,
     * and define its destructor. */
    PyObject* capsule = PyCapsule_New((void*) handle, name,
            (PyCapsule_Destructor) capsule_destructor);

    /* Return the capsule to Python, but don't increment its reference count. */
    return Py_BuildValue("N", capsule);
}


/* Exposes test_object_add_arrays(). */
static PyObject* add_arrays(PyObject* self, PyObject* args)
{
    npy_intp num_points = 0;
    TestObject* handle = 0;
    PyArrayObject *a = 0, *b = 0, *c = 0;

    /* Parse the Python function arguments. */
    PyObject *capsule = 0;
    PyObject *ob[] = {0, 0};
    if (!PyArg_ParseTuple(args, "OOO", &capsule, &ob[0], &ob[1])) return 0;

    /* Get a handle to the C object from the PyCapsule. */
    if (!(handle = get_handle(capsule))) return 0;

    /* Make sure inputs are double-precision arrays. Convert if required. */
    a = (PyArrayObject*)PyArray_FROM_OTF(ob[0], NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);
    b = (PyArrayObject*)PyArray_FROM_OTF(ob[1], NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);
    if (!a || !b) goto fail;

    /* Get input array lengths. */
    num_points = PyArray_SIZE(a);
    if (num_points != PyArray_SIZE(b))
    {
        PyErr_SetString(PyExc_RuntimeError, "Input data dimension mismatch.");
        goto fail;
    }

    /* Create an output array. */
    c = (PyArrayObject*)PyArray_SimpleNew(1, &num_points, NPY_DOUBLE);

    /* Release the Python Global Interpreter Lock,
     * as this might be an expensive external call. */
    Py_BEGIN_ALLOW_THREADS

    /* Call the function provided by our C API. */
    test_object_add_arrays(handle, (int) num_points,
            (const double*) PyArray_DATA(a), (const double*) PyArray_DATA(b),
            (double*) PyArray_DATA(c));

    /* Re-acquire the Python Global Interpreter Lock. */
    Py_END_ALLOW_THREADS

    /* In this example, we return the output array to Python. */
    Py_XDECREF(a);
    Py_XDECREF(b);
    return Py_BuildValue("N", c); /* Don't increment reference count. */

fail:
    Py_XDECREF(a);
    Py_XDECREF(b);
    Py_XDECREF(c);
    return 0;
}


/*===========================================================================*/
/* Methods provided by this extension module. */
static PyMethodDef methods[] =
{
        /* EXAMPLE 1: Simple stateless C Python extensions. */
        {"hello1", (PyCFunction)hello1, METH_VARARGS, "hello1()"},
        {"hello2", (PyCFunction)hello2, METH_VARARGS, "hello2()"},

        /* EXAMPLE 2: Expose functions that could be from an external C API. */
        {"create", (PyCFunction)create,
                METH_VARARGS, "create(scale_a, scale_b)"},
        {"add_arrays", (PyCFunction)add_arrays,
                METH_VARARGS, "add_arrays(a, b)"},

        /* Method table terminates here. */
        {NULL, NULL, 0, NULL}
};

/*===========================================================================*/
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
