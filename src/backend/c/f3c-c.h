#ifndef F3C_C
#define F3C_C

/**
 * [_mandelbrot     description]
 * @param  c_re     [description]
 * @param  c_im     [description]
 * @param  max_iter [description]
 * @return          [description]
 */
int _mandelbrot_1 ( double const * const c_re, double const * const c_im, int max_iter );

/**
 * [_mandelbrot_2  description]
 * @param  c_re     [description]
 * @param  c_im     [description]
 * @param  max_iter [description]
 * @return          [description]
 */
int _mandelbrot_2 ( double const * const c_re, double const * const c_im, int max_iter );

/**
 * Process
 * @param  c_re     [description]
 * @param  c_im     [description]
 * @param  max_iter [description]
 * @return          [description]
 */
int _mandelbrot_4 ( double const * const c_re, double const * const c_im, int max_iter );

int _mandelbrot_4_2_1 ( double const * const c_re, double const * const c_im, int max_iter, int num_sample_points );
int _mandelbrot_2_1   ( double const * const c_re, double const * const c_im, int max_iter, int num_sample_points );

int 
_mandelbrot_sample_pixel (
	int num_sample_points,
	double center_x,
	double center_y,
	double per_pixel_width,
	double per_pixel_height,
	int max_iter
);

#endif