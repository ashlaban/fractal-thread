#include "f3c-c.h"

#include <stdlib.h> // Used for random, TODO: Replace with dedicated random function.

#define RANDOM_DOUBLE() ((double)rand()/RAND_MAX)

int 
_mandelbrot_sample_pixel (
	int num_sample_points,
	double center_x,
	double center_y,
	double per_pixel_width,
	double per_pixel_height,
	int max_iter
) {
	double sample_point_x[num_sample_points];
	double sample_point_y[num_sample_points];
	double val;
	int i;

	// Fill sample points array
	for (i=0; i<num_sample_points; ++i) {
		sample_point_x[i] = center_x + per_pixel_width*(RANDOM_DOUBLE()-0.5);
		sample_point_y[i] = center_y + per_pixel_height*(RANDOM_DOUBLE()-0.5);
	}

	// Process
	val = _mandelbrot_4_2_1(&sample_point_x[0], &sample_point_y[0], max_iter, num_sample_points);
	
	return val;
}

int
_mandelbrot_4_2_1 (
	double const * const c_re,
	double const * const c_im,
	int max_iter,
	int num_sample_points
) {
	int count = 0;
	int i = num_sample_points;
	for (; i >= 4; i-=4) {
		count += _mandelbrot_4(&c_re[i-4], &c_im[i-4], max_iter);
	}
	for (; i >= 2; i-=2) {
		count += _mandelbrot_2(&c_re[i-2], &c_im[i-2], max_iter);
	}
	for (; i >= 1; i-=1) {
		count += _mandelbrot_1(&c_re[i-1], &c_im[i-1], max_iter);
	}
	return count;
}