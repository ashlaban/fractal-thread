#include <Python/Python.h> // Mac specific use <Python.h> in linux

#include <stdio.h>

static PyObject * f3c_mandelbrot ( PyObject *self, PyObject *args );
static double     _mandelbrot    ( double c_real, double c_imag, int max_iter );

static PyMethodDef moduleMethods[] = {
    {"mandelbrot",  f3c_mandelbrot, METH_VARARGS, "Test of python c extensions."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initf3c(void)
{
    PyObject *m;

    m = Py_InitModule("f3c", moduleMethods);
    if (m == NULL)
        return;

    // SpamError = PyErr_NewException("spam.error", NULL, NULL);
    // Py_INCREF(SpamError);
    // PyModule_AddObject(m, "error", SpamError);
}

// Python functions

static PyObject *
f3c_mandelbrot(PyObject *self, PyObject *args)
{
	Py_complex pc;
	double c_real;
	double c_imag;
	int    max_iter;

	PyArg_ParseTuple(args, "Di:mandelbrot;", &pc, &max_iter);
	c_real = pc.real;
	c_imag = pc.imag;

	// printf("val : %f\n", _mandelbrot(c_real, c_imag, max_iter) );

	double val = _mandelbrot(c_real, c_imag, max_iter);
	PyObject *  ret_val = Py_BuildValue("d", val);
	Py_INCREF(ret_val);
	return ret_val;
}

// C functions

typedef double v4d __attribute__ ((vector_size (16)));

static double
_mandelbrot( double c_real, double c_imag, int max_iter )
{
	double z_real = 0;
	double z_imag = 0;
	double temp = 0;

	for (int i = 0; i<max_iter; ++i)
	{
		// z = z^2 + c
		temp = z_real;
		z_real = (z_real * z_real - z_imag * z_imag) + c_real;
		z_imag = (2 * temp * z_imag              ) + c_imag;

		if (z_real >= 2.0 || z_imag >= 2.0)
		{
			return 1.0 - ((double)i) / max_iter;
		}
	}

	return 0.0;
}