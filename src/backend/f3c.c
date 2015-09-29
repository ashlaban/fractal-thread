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
f3c_mandelbrot_random_sample(PyObject *self, PyObject *args)
{
	int    num_sample_points;
	double center_x;
	double center_y;
	double per_pixel_width;
	double per_pixel_height;
	int    max_iter;

	if (!PyArg_ParseTuple(
		args, 
		"iddddi:mandelbrot_random_sample;",
		&num_sample_points,
		&center_x,
		&center_y,
		&per_pixel_width,
		&per_pixel_height,
		&max_iter)
	) {
		return NULL;
	}
	
	int count;
	double val;

	count = _mandelbrot_sample_pixel( num_sample_points, center_x, center_y, per_pixel_width, per_pixel_height, max_iter );
	val   = (double)max_iter - (double)count / (double)num_sample_points;
	
	PyObject *  ret_val = Py_BuildValue("d", val);
	Py_INCREF(ret_val);

	return ret_val;

}

static PyObject *
f3c_mandelbrot(PyObject *self, PyObject *args)
{
	PyObject * pyList;
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
	
	double c_re[pyList_length];
	double c_im[pyList_length];

	int i;
	for (i=0; i<pyList_length; ++i) {
		PyObject * z0 = PyList_GetItem(pyList, i);
		if (!PyComplex_Check(z0)) {printf("Error verifying format of complex number in args -- z0");}
		c_re[i] = PyComplex_RealAsDouble(z0);
		c_im[i] = PyComplex_ImagAsDouble(z0);
	}

	int count = _mandelbrot_4_2_1(&c_re[0], &c_im[0], max_iter, pyList_length);

	// val = 1.0 - (val / (double) pyList_length / (double) max_iter);
	double val;
	val = (double)max_iter - (double)count / (double)pyList_length;
	PyObject *  ret_val = Py_BuildValue("d", val);
	// double val = _mandelbrot(c_re, c_im, max_iter);
	// PyObject *  ret_val = Py_BuildValue("d", val);
	Py_INCREF(ret_val);
	return ret_val;
}
