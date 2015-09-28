import math
import random
import numbers
import json
import time
from PIL import Image
import cProfile

import f3c

def mandelbrot(cList, max_iter, api):
	# if  isinstance(c, numbers.Number) \
	# and isinstance(max_iter, numbers.Number):
	
	if api == "python":
		return __mandelbrot_internal(cList, max_iter)
	if api == "c":
		return f3c.mandelbrot(cList, max_iter)
	else:
		return None
		# raise Error()
	# else:
	# 	return None

# Render one pixel with subpixel resolution.
# Quality of subpixel rendering determined by the number of points in cList.
def __mandelbrot_internal(cList, max_iter):

	mandelbrot_factor = 0.10
	julia_factor   = 0.90
	julia_constant = (0.285+0.01j)

	val = 0
	for c in cList:

		# Quick cardoid check
		# p = math.sqrt( (c.real-0.25)**2 + c.imag**2 )
		# if ( c.real < (p - 2*p**2+0.25) ):
		# 	return 0.0
		# if ( ((c.real + 1)**2 + c.imag**2) < (1.0/16) ):
		# 	return 0.0

		# True calculation
		z = julia_factor*c
		for i in range(1, max_iter+1):
			z = z*z + mandelbrot_factor*c + julia_factor*julia_constant
			if (z.real >= 2.0 or z.imag >= 2.0 or i==max_iter):
				break
		val += i

	 # Return 
	# ret_val = 1.0 - float(val) / (len(cList)*max_iter)
	ret_val = max_iter - int(float(val)/len(cList))
	return ret_val

# TODO: Density of colors
class ColorPalette(object):
	def __init__(self):
		n = 2
		# self.color  = [i for i in xrange(0, 256, n)] + [255 + i*256 for i in xrange(0, 256, n)] + [255*256 + i*256*256 for i in xrange(0, 256, n)]
		self.color = [ i+j*256+k*256*256 for k in range(0, 256, n) for j in range(0, 256, n) for i in range(0, 256, n) ]
		self.length = len(self.color)

	def getColorForValue(self, val):
		# index = int(val*0.99 * self.length)
		color_density = 5.0
		index = int(val * color_density)
		return self.color[ index % self.length ]

class RenderSettings(object):
	def __init__(self, json_data = None):
		self.x      = 0.0
		self.y      = 0.0
		self.zoom   = 0.0
		self.aspect_ratio = 0.0

		self.pixel_x  = 0
		self.pixel_y  = 0
		self.pixel_width  = 0

		self.max_iter = 0
		self.c        = 0.0 # (-0.8+0.156j)

		self.num_sample_points = 1

		self.data = None

		self.api = "c"

		if (not (json_data is None)):
			for prop in json_data:
				self[prop] = json_data[prop]

	def subdivide(self, n_levels):
		if n_levels < 1:
			return self

		ret = {}
		for direction in ["NE", "NW", "SW", "SE"]:
			render_settings = RenderSettings()
			render_settings.aspect_ratio = self.aspect_ratio
			render_settings.pixel_width  = int(self.pixel_width / 2.0)
			pixel_height  = int(self.pixel_width*self.aspect_ratio / 2.0)

			render_settings.zoom       = self.zoom * 2
			render_settings.max_iter   = self.max_iter

			render_settings.c   = self.c
			render_settings.api = self.api

			if direction == "NE":
				render_settings.x = self.x + 4.0 * self.zoom
				render_settings.y = self.y - 4.0 * self.zoom * self.aspect_ratio
				render_settings.pixel_x = render_settings.pixel_width
				render_settings.pixel_y = 0.0
			if direction == "NW":
				render_settings.x = self.x - 4.0 * self.zoom
				render_settings.y = self.y - 4.0 * self.zoom  * self.aspect_ratio
				render_settings.pixel_x = 0.0
				render_settings.pixel_y = 0.0
			if direction == "SE":
				render_settings.x = self.x + 4.0 * self.zoom
				render_settings.y = self.y + 4.0 * self.zoom  * self.aspect_ratio
				render_settings.pixel_x = 0.0
				render_settings.pixel_y = pixel_height
			if direction == "SW":
				render_settings.x = self.x - 4.0 * self.zoom
				render_settings.y = self.y + 4.0 * self.zoom  * self.aspect_ratio
				render_settings.pixel_x = render_settings.pixel_width
				render_settings.pixel_y = pixel_height

			if n_levels > 1:
				ret[direction] = render_settings.subdivide(n_levels-1)
			else:
				ret[direction] = render_settings

		return ret
	def __setitem__(self, key, val):
		self.__dict__[key] = val

	def __repr__(self):
		# return "( x: %f, y: %f, w: %f, h: %f, z: %f, pw: %f, ph: %f, iter: %i, num_sample_points: %i)" % (self.x, self.y, self._width, self._height, self.zoom, self.pixel_width, self.pixel_height, self.max_iter, self.num_sample_points)
		return json.dumps(self.__dict__)

#
# Takes a pixel coordinate p = (x, y) and translates it into real coordinates in the view.
#
def coords_pixel_to_view( render_settings, p ):
	pixel_width  = render_settings.pixel_width
	pixel_height = pixel_width * render_settings.aspect_ratio
	width  = 1.0   / render_settings.zoom
	height = width * render_settings.aspect_ratio

	pixel_scale = width / float(pixel_width)
	 
	px = float(p[0])
	py = float(p[1])
	vx = (px * pixel_scale) - width  / 2 + render_settings.x
	vy = (py * pixel_scale) - height / 2 + render_settings.y

	# print (vx,vy)

	return (vx, vy)

def sample_pixel( x, y, render_settings ):
	pixel_width  = render_settings.pixel_width
	pixel_height = render_settings.pixel_height
	max_iter     = render_settings.max_iter

	ppw = 1.0 / render_settings.zoom / pixel_width  # per pixel width
	pph = 1.0 / render_settings.zoom / pixel_height # per pixel height

	if render_settings.num_sample_points == 1:
		vp = coords_pixel_to_view(render_settings, (x, y))
		z  = complex( vp[0], vp[1] )
		val  = mandelbrot(z , max_iter)

	elif render_settings.num_sample_points == 2:
		pass

	elif render_settings.num_sample_points == 3:
		# Do this
		pass

	elif render_settings.num_sample_points == 5:
		vp = coords_pixel_to_view(render_settings, (x, y))
		z  = complex( vp[0]      , vp[1] )
		z1 = complex( vp[0]+ppw/3, vp[1]+pph/3 )
		z2 = complex( vp[0]-ppw/3, vp[1]+pph/3 )
		z4 = complex( vp[0]+ppw/3, vp[1]-pph/3 )
		z5 = complex( vp[0]-ppw/3, vp[1]-pph/3 )
		val  = mandelbrot(z , max_iter)
		val += mandelbrot(z1, max_iter)
		val += mandelbrot(z2, max_iter)
		val += mandelbrot(z4, max_iter)
		val += mandelbrot(z5, max_iter)
		val /= 5

	else:
		print("Sampling scheme not implemented.")

	return val

def random_sample_pixel( x, y, render_settings ):
	pixel_width  = render_settings.pixel_width
	pixel_height = render_settings.pixel_width*render_settings.aspect_ratio
	max_iter     = render_settings.max_iter

	ppw = 1.0 / render_settings.zoom / pixel_width  # per pixel width
	# pph = 1.0 / render_settings.zoom / pixel_height # per pixel height
	pph = ppw

	vp = coords_pixel_to_view(render_settings, (x, y))
	vp = complex(vp[0], vp[1])

	val = 0.0
	zList = [None]*render_settings.num_sample_points
	for i in range(render_settings.num_sample_points):
		dx = ppw*(random.random()-0.5)
		dy = pph*(random.random()-0.5)
		zList[i] = complex( dx, dy ) + vp
		# print vp, (vp[0]+dx, vp[1]+dy)
	val = mandelbrot( zList, max_iter, render_settings.api )

	return val

def render_region( render_settings ):
	time_start = time.clock()

	pixel_width  = render_settings.pixel_width
	pixel_height = int(render_settings.pixel_width*render_settings.aspect_ratio)
	max_iter     = render_settings.max_iter

	color_palette = ColorPalette()
	data = [None]*pixel_width*pixel_height
	
	for y in range(pixel_height):
		for x in range(pixel_width):
			val = random_sample_pixel(x, y, render_settings)
			color = color_palette.getColorForValue(val)
			data[x + y*render_settings.pixel_width] = color

	render_settings.data = data

	time_end = time.clock()
	print("Rendered region in: " + str(time_end-time_start))

	return render_settings

def write_data(render_settings, name):
	pixel_height = int(render_settings.pixel_width*render_settings.aspect_ratio)
	im = Image.new("RGB", (render_settings.pixel_width, pixel_height), "white")
	im.putdata(render_settings.data)
	im.save("out/" + name + ".png")


def write_region(region_settings, direction):
	if type(region_settings) == dict:
		subregions = region_settings
		for subdirection in subregions:
			sub_region_settings = subregions[subdirection]
			if direction == "Base":
				write_region(sub_region_settings, subdirection)
			else:
				write_region(sub_region_settings, direction + "-" + subdirection)
	else:
		data = render_region( region_settings )

		im = Image.new("RGB", (region_settings.pixel_width, region_settings.pixel_height), "white")
		im.putdata(data)
		im.save("out/" + direction + ".png")
		print("Done: " + direction)


if __name__ == "__main__":
	p = 11
	render_settings = RenderSettings()
	render_settings.x            = 0
	render_settings.y            = 0
	render_settings.zoom         = 0.25
	render_settings.aspect_ratio = 1.0
	render_settings.pixel_width  = pow(2,p)
	render_settings.max_iter     = 10000
	render_settings.num_sample_points = 20

	def profile_test(api):
		render_settings.api = api
		render_region( render_settings )
		write_data(render_settings, "data")

	# def subdivision_test(api):
	# 	render_settings.api = api
	# 	regions = render_settings.subdivide(1)
	# 	for region_name in regions:
	# 		render_region( regions[region_name] )
	# 		write_data( regions[region_name], region_name )

	# cProfile.run('profile_test("python")')
	# cProfile.run('profile_test("c")')
	profile_test("c")
	# subdivision_test("c")
	
	# z0 = complex( 0.75, -0.75 );
	# z1 = complex( 0.80, -0.75 );
	# print mandelbrot( [z0, z1], 10, "python" )
	# print mandelbrot( [z0, z1], 10, "c" )