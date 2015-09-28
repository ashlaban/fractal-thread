#include "f3c-c.h"

/**
 * Processes one double at a time
 */
int
_mandelbrot_1( double const * const c_re_arg, 
	           double const * const c_im_arg, 
	           int                  max_iter 
	         )
{
	double z_re;
	double z_im;
	double c_re;
	double c_im;
	double temp;
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

		if (z_re >= 2.0 || z_im >= 2.0) { break; }
	}

	return i;
}