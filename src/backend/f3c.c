#include "f3c.h"
#include "f3c-c.h"

PyMODINIT_FUNC
PyInit_f3c(void)
{
    PyObject *m;

    m = PyModule_Create(&f3cmodule);
    if (m == NULL) {
        return NULL;
    }
    return m;
}

// Python functions

static PyObject *
f3c_mandelbrot(PyObject *self, PyObject *args)
{
	PyObject * pyList;
	double c_re[4];
	double c_im[4];
	int    max_iter;

	// printf( "%s%s%d%s", __FILE__ , " : " , __LINE__ , " -- error parse args!\n");

	// Check args
	if (!PyArg_ParseTuple(args, "Oi:mandelbrot;", &pyList, &max_iter)) {
		return NULL;
	}

	if (!PyList_Check(pyList)) {
		return NULL;
	}

	int pyList_length = PyList_Size(pyList);
	// int num_batch_4 = (pyList_length) / 4;
	// int num_batch_2 = (pyList_length - num_batch_4*4) / 2;
	// int num_batch_1 = (pyList_length - num_batch_4*4 - num_batch_2*2) / 1;
	

	// TODO: Make this into a separate function.
	// TODO: Copy the random_sample into C.
	int count = 0;
	int i = pyList_length;
	for (; i >= 4; i-=4)
	{
		PyObject * z0 = PyList_GetItem(pyList, i-1);
		PyObject * z1 = PyList_GetItem(pyList, i-2);
		PyObject * z2 = PyList_GetItem(pyList, i-3);
		PyObject * z3 = PyList_GetItem(pyList, i-4);

		if (!PyComplex_Check(z0)) {printf("Error verifying format of complex number in args -- z0");}
		if (!PyComplex_Check(z1)) {printf("Error verifying format of complex number in args -- z1");}
		if (!PyComplex_Check(z2)) {printf("Error verifying format of complex number in args -- z2");}
		if (!PyComplex_Check(z3)) {printf("Error verifying format of complex number in args -- z3");}

		c_re[0] = PyComplex_RealAsDouble(z0);
		c_re[1] = PyComplex_RealAsDouble(z1);
		c_re[2] = PyComplex_RealAsDouble(z0);
		c_re[3] = PyComplex_RealAsDouble(z1);

		c_im[0] = PyComplex_ImagAsDouble(z0);
		c_im[1] = PyComplex_ImagAsDouble(z1);
		c_im[2] = PyComplex_ImagAsDouble(z0);
		c_im[3] = PyComplex_ImagAsDouble(z1);

		double incr = _mandelbrot_4(&c_re[0], &c_im[0], max_iter);
		count += incr;
	}
	for (; i >= 2; i-=2)
	{
		PyObject * z0 = PyList_GetItem(pyList, i-1);
		PyObject * z1 = PyList_GetItem(pyList, i-2);

		if (!PyComplex_Check(z0)) {printf("Error verifying format of complex number in args -- z0");}
		if (!PyComplex_Check(z1)) {printf("Error verifying format of complex number in args -- z1");}

		c_re[0] = PyComplex_RealAsDouble(z0);
		c_re[1] = PyComplex_RealAsDouble(z1);

		c_im[0] = PyComplex_ImagAsDouble(z0);
		c_im[1] = PyComplex_ImagAsDouble(z1);

		double incr = _mandelbrot_2(&c_re[0], &c_im[0], max_iter);
		count += incr;
	}
	for (; i >= 1; i-=1)
	{
		PyObject * z0 = PyList_GetItem(pyList, i-1);
		
		if (!PyComplex_Check(z0)) {printf("Error verifying format of complex number in args -- z0");}

		c_re[0] = PyComplex_RealAsDouble(z0);
		c_im[0] = PyComplex_ImagAsDouble(z0);

		double incr = _mandelbrot_1(&c_re[0], &c_im[0], max_iter);
		count += incr;
	}

	// val = 1.0 - (val / (double) pyList_length / (double) max_iter);
	double val;
	val = (double)max_iter - (double)count / (double)pyList_length;
	PyObject *  ret_val = Py_BuildValue("d", val);
	// double val = _mandelbrot(c_re, c_im, max_iter);
	// PyObject *  ret_val = Py_BuildValue("d", val);
	Py_INCREF(ret_val);
	return ret_val;
}
