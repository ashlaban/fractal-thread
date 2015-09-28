#include <stdio.h>

#include "f3c-c.h"

#include <time.h>

#define WITH_SSE 1
#define WITH_AVX 1

/*
	Points are the Valleys of Seahorse, Elephant, Triple-Spiral and Quad-Spiral.
 */
double c_re[4] = {-0.75, 0.275, -0.088, 0.274};
double c_im[4] = { 0.10, 0.   ,  0.654, 0.482};

int main(int argc, char const *argv[])
{
	int max_iter = 1000; // TODO: Take from command line.
	int test_max_iter = 1000000;
	int count;
	int i, j;

	double msec;
	clock_t start, diff;

	// Single
	start = clock();
	for (j = 0; j < test_max_iter; ++j)
	{
		count = 0;
		for (i=0; i<4; i+=1) {
			count += _mandelbrot_1(c_re+i, c_im+i, max_iter);
		}
	}
	diff = clock() - start;
	msec = diff * 1000 / CLOCKS_PER_SEC;
	printf("_mandelbrot_1 :: %i\n", count);
	printf("msecs         :: %f\n", msec);

	// SSE
	#if WITH_SSE
	start = clock();
	for (j = 0; j < test_max_iter; ++j)
	{
		count = 0;
		for (i=0; i<4; i+=2) {
			count += _mandelbrot_2(c_re+i, c_im+i, max_iter);
		}
	}
	diff = clock() - start;
	msec = diff * 1000 / CLOCKS_PER_SEC;
	printf("_mandelbrot_2 :: %i\n", count);
	printf("msecs         :: %f\n", msec);
	#endif
	
	// AVX
	#if WITH_AVX
	start = clock();
	for (j = 0; j < test_max_iter; ++j)
	{
		count = 0;
		for (i=0; i<4; i+=4) {
			count += _mandelbrot_4(c_re+i, c_im+i, max_iter);
		}
	}
	diff = clock() - start;
	msec = diff * 1000 / CLOCKS_PER_SEC;
	printf("_mandelbrot_4 :: %i\n", count);
	printf("msecs         :: %f\n", msec);
	#endif


	return 0;
}