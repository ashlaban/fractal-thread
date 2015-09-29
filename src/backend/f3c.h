#include <Python.h> // Mac specific use <Python.h> in linux

#include <stdio.h>

// Compile gcc -I/usr/local/Cellar/python3/3.4.2_1/Frameworks/Python.framework/Versions/3.4/Headers/ -L/usr/local/Cellar/python3/3.4.2_1/Frameworks/Python.framework/Versions/3.4/lib/ -O3 -msse2 -mavx -shared -lpython3.4 -o f3c.so f3c.c

static PyObject * f3c_mandelbrot               ( PyObject *self, PyObject *args );
static PyObject * f3c_mandelbrot_random_sample ( PyObject *self, PyObject *args );

static PyMethodDef moduleMethods[] = {
    {"mandelbrot"              ,  f3c_mandelbrot              , METH_VARARGS, "Calculates the mandelbrot for a given set of points."},
    {"mandelbrot_random_sample",  f3c_mandelbrot_random_sample, METH_VARARGS, "Samples a point using random sampling."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef f3cmodule = {
        PyModuleDef_HEAD_INIT,
        "f3c",               /* m_name */
        "Kernel for computing mandelbrot fractals.", /* m_doc */
        -1,                  /* m_size */
        moduleMethods,       /* m_methods */
        NULL,                /* m_reload */
        NULL,                /* m_traverse */
        NULL,                /* m_clear */
        NULL,                /* m_free */
};