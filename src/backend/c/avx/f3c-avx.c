#include "f3c-c.h"

#include <stdio.h>

#include <immintrin.h> // AVX  extensions

#define PRINT_M256I(x) printf("|%.16llx|%.16llx|%.16llx|%.16llx|\n", x[3], x[2], x[1], x[0])

static __m256i _mm256_hadd_epi64(__m256i a) {
	__m256i temp1, temp2, temp3, temp4, temp5;
	temp1 = _mm256_srli_si256( a, 8 );
	temp2 = _mm256_add_epi64(a, temp1);
	temp3 = _mm256_permute4x64_epi64( temp2, (char) 0x28 );
	temp4 = _mm256_srli_si256( temp3, 8 );
	temp5 = _mm256_add_epi64(temp4, temp3);

	// printf("-================-================-================-================-\n");
	// PRINT_M256I(a);
	// PRINT_M256I(temp1);
	// PRINT_M256I(temp2);
	// PRINT_M256I(temp3);
	// PRINT_M256I(temp4);
	// PRINT_M256I(temp5);
	// printf("-================-================-================-================-\n");

	return temp5;
}

/**
 * Processes four doubles at a time
 */
int
_mandelbrot_4( double const * const c_re_arg, 
	           double const * const c_im_arg, 
	           int                  max_iter 
	         )
{
	__m256d z_re = _mm256_load_pd(c_re_arg);
	__m256d z_im = _mm256_load_pd(c_im_arg);
	__m256d y_re;
	__m256d y_im;
	__m256d c_re = z_re;
	__m256d c_im = z_im;

	__m256i count = _mm256_set1_epi64x(0);

	__m256d md;
	__m256d mt;
	__m256i mi = _mm256_set1_epi16(0xffff);;

	__m256d two = _mm256_set1_pd(2.0);
	__m256i one = _mm256_set1_epi64x(1);

	for (int i = 0; i<max_iter; i+=1)
	{
		// y = z .* z;
		y_re = _mm256_mul_pd(z_re, z_re);
		y_im = _mm256_mul_pd(z_im, z_im);

		// y = z * z;
		y_re = _mm256_sub_pd(y_re, y_im);
		y_im = _mm256_mul_pd(z_re, z_im);
		y_im = _mm256_add_pd(y_im, y_im);

		// z = z * z + c
		z_re = _mm256_add_pd(y_re, c_re);
		z_im = _mm256_add_pd(y_im, c_im);

		// if condition
		// md = _mm_add_pd(z_re, z_im);
		// md = _mm_cmplt_pd(md, four);
		md = _mm256_cmp_pd(z_re, two, _CMP_LT_OQ);
		mt = _mm256_cmp_pd(z_im, two, _CMP_LT_OQ);
		md = _mm256_and_pd(md, mt);
		mi = _mm256_and_pd(mi, (__m256i) md);
		// PRINT_M256I(mi);
		if ( !_mm256_movemask_pd(md) ) { break; }

		// count iterations
		count = _mm256_add_epi64( count, _mm256_and_si256( mi, one) );
	}

	int val;
	val = _mm256_hadd_epi64(count)[0];

	return val;
}