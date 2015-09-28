#include "f3c-c.h"

#include <stdio.h>

#include <emmintrin.h> // SSE2 extensions

// #define PRINT_M128I(x, y) printf("%s : %x\n", y, _mm_cvtsi128_si32(x))
#define PRINT_M128D(z_re, z_im) printf("(%5.2f+%5.2fi)\t(%5.2f+%5.2fi)\n", z_re[0], z_im[0], z_re[1], z_im[1]);
#define PRINT_M128I(x) printf("%.16llx%.16llx\n", x[1], x[0])

/**
 * Processes two doubles at a time
 */
int
_mandelbrot_2( double const * const c_re_arg, 
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
	__m128i mi = _mm_set1_epi16(0xffff);;

	__m128d two = _mm_set1_pd(2.0);
	__m128i one = _mm_set1_epi64x(1);

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
		mi = _mm_and_si128(mi, (__m128i) md);
		// PRINT_M128I(mi);
		if ( !_mm_movemask_pd(md) ) { break; }

		// count iterations
		count = _mm_add_epi64( count, _mm_and_si128( mi, one) );
	}

	int val;
	count = _mm_add_epi64( _mm_srli_si128(count, 8), count );
	val   = _mm_cvtsi128_si64( count );

	return val;
}