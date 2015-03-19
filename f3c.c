#include <Python/Python.h> // Mac specific use <Python.h> in linux

#include <emmintrin.h>

#include <stdio.h>

// Compile gcc -O3 -msse2 -mavx -shared -lpython -o f3cmodule.so f3c.c

static PyObject * f3c_mandelbrot ( PyObject *self, PyObject *args );
static int        _mandelbrot_sse( double const * const c_re, double const * const c_im, int max_iter );
static int        _mandelbrot    ( double const * const c_re, double const * const c_im, int max_iter );

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
}

// Python functions

static PyObject *
f3c_mandelbrot(PyObject *self, PyObject *args)
{
	PyObject * pyList;
	Py_complex pc;
	double c_re[2];
	double c_im[2];
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
	
	double val = 0.0;
	for (int i = pyList_length; i > 1; i-=2)
	{
		PyObject * z0 = PyList_GetItem(pyList, 0);
		PyObject * z1 = PyList_GetItem(pyList, 1);

		if (!PyComplex_Check(z0)) {printf("Error verifying format of complex number in args -- z0");}
		if (!PyComplex_Check(z1)) {printf("Error verifying format of complex number in args -- z1");}

		c_re[0] = PyComplex_RealAsDouble(z0);
		c_re[1] = PyComplex_RealAsDouble(z1);

		c_im[0] = PyComplex_ImagAsDouble(z0);
		c_im[1] = PyComplex_ImagAsDouble(z1);

		double incr = _mandelbrot_sse(&c_re[0], &c_im[0], max_iter);
		val += incr;
		// val += _mandelbrot(&c_re[0], &c_im[0], max_iter);
	}

	// val = 1.0 - (val / (double) pyList_length / (double) max_iter);
	val = (double) max_iter - val / (double) pyList_length;
	PyObject *  ret_val = Py_BuildValue("d", val);
	// double val = _mandelbrot(c_re, c_im, max_iter);
	// PyObject *  ret_val = Py_BuildValue("d", val);
	Py_INCREF(ret_val);
	return ret_val;
}

// C functions

// typedef double v2d __attribute__ ((vector_size (16)));

#define PRINT_M128I(x, y) printf("%s : %x\n", y, _mm_cvtsi128_si32(x))
#define PRINT_M128D(z_re, z_im) printf("(%5.2f+%5.2fi)\t(%5.2f+%5.2fi)\n", z_re[0], z_im[0], z_re[1], z_im[1]);

/**
 * Processes two doubles at a time
 */
static int
_mandelbrot_sse( double const * const c_re_arg, 
	             double const * const c_im_arg, 
	             int                  max_iter 
	           )
{
	__m128d z_re = _mm_load_pd(c_re_arg);
	__m128d z_im = _mm_load_pd(c_im_arg);
	__m128d y_re;
	__m128d y_im;
	__m128d c_re = z_re;
	__m128d c_im = z_im;

	__m128i count = _mm_set1_epi64x(0);

	__m128d md;
	__m128d mt;
	__m128i mi;

	__m128d two = _mm_set1_pd(2.0);
	__m128i one  = _mm_set1_epi32(1);

	for (int i = 0; i<max_iter; i+=1)
	{
		// y = z .* z;
		y_re = _mm_mul_pd(z_re, z_re);
		y_im = _mm_mul_pd(z_im, z_im);

		// y = z * z;
		y_re = _mm_sub_pd(y_re, y_im);
		y_im = _mm_mul_pd(z_re, z_im);
		y_im = _mm_add_pd(y_im, y_im);

		// z = z * z + c
		z_re = _mm_add_pd(y_re, c_re);
		z_im = _mm_add_pd(y_im, c_im);

		// if condition
		// md = _mm_add_pd(z_re, z_im);
		// md = _mm_cmplt_pd(md, four);
		md = _mm_cmplt_pd(z_re, two);
		mt = _mm_cmplt_pd(z_im, two);
		md = _mm_and_pd(md, mt);
		mi = (__m128i) md;
		if ( !_mm_movemask_pd(md) ) { break; }

		// count iterations
		count = _mm_add_epi64( count, _mm_and_si128( mi, one) );
	}

	int val;
	count = _mm_add_epi64( _mm_srli_si128(count, 8), count );
	val   = _mm_cvtsi128_si64( count );

	// printf("val %i\n", val);

	return val;
}

/**
 * Processes two doubles at a time
 */
static int
_mandelbrot( double const * const c_re_arg, 
	         double const * const c_im_arg, 
	         int                  max_iter 
	       )
{
	double z_re;
	double z_im;
	double c_re;
	double c_im;
	double temp;
	int count = 0;
	int i;

	z_re = *c_re_arg;
	z_im = *c_im_arg;
	c_re = *c_re_arg;
	c_im = *c_im_arg;
	temp = 0;
	for (i = 0; i<max_iter; ++i)
	{
		// z = z^2 + c
		temp = z_re;
		z_re = (z_re * z_re - z_im * z_im) + c_re;
		z_im = (2 * temp * z_im          ) + c_im;

		if (z_re + z_im >= 4.0) { break; }
	}
	count += i;

	z_re = *(c_re_arg+1);
	z_im = *(c_im_arg+1);
	c_re = *(c_re_arg+1);
	c_im = *(c_im_arg+1);
	temp = 0;
	for (i = 0; i<max_iter; ++i)
	{
		// z = z^2 + c
		temp = z_re;
		z_re = (z_re * z_re - z_im * z_im) + c_re;
		z_im = (2 * temp * z_im          ) + c_im;

		if (z_re + z_im >= 4.0) { break; }
	}
	count += i;

	return count;
}
