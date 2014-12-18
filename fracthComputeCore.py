import math
import random
import numbers
import json
import time
# from PIL import Image
import cProfile

import f3c

def mandelbrot(c, max_iter, api):
	if  isinstance(c, numbers.Number) \
	and isinstance(max_iter, numbers.Number):

		p = math.sqrt( (c.real-0.25)**2 + c.imag**2 )
		if ( c.real < (p - 2*p**2+0.25) ):
			return 0.0
		if ( ((c.real + 1)**2 + c.imag**2) < (1.0/16) ):
			return 0.0

		if api == "python":
			return __mandelbrot_internal(c, max_iter)
		if api == "c":
			return f3c.mandelbrot(c, max_iter)
	else:
		return None

def __mandelbrot_internal(c, max_iter):
	z = 0
	for i in xrange(max_iter):
		z = z*z + c
		if (z.real >= 2.0 or z.imag >= 2.0):
			return 1.0 - float(i)/max_iter
	return 0.0

class ColorPalette(object):
	def __init__(self):
		self.color  = [i for i in xrange(0, 256, 32)] + [255 + i*256 for i in xrange(0, 256, 32)] + [255*256 + i*256*256 for i in xrange(0, 256, 32)]
		self.length = len(self.color)
	
	def getColorForValue(self, val):
		index = int(math.sqrt(val*0.99) * self.length)
		return self.color[ index ]

class RenderSettings(object):
	def __init__(self):
		self.x      = 0
		self.y      = 0
		self.width  = 0
		self.height = 0

		self.pixel_x  = 0
		self.pixel_y  = 0
		self.pixel_width  = 0
		self.pixel_height = 0

		self.zoom     = 0
		self.max_iter = 0
		self.c        = 0 # (-0.8+0.156j)

		self.num_sample_points = 1

		self.data = None

		self.api = "c"

	def subdivide(self, n_levels):
		if n_levels < 1:
			return self

		ret = {}
		for direction in ["NE", "NW", "SW", "SE"]:
			render_settings = RenderSettings()
			render_settings.width  = self.width  / 2.0
			render_settings.height = self.height / 2.0
			render_settings.pixel_width  = int(self.pixel_width  / 2.0)
			render_settings.pixel_height = int(self.pixel_height / 2.0)

			render_settings.zoom       = self.zoom
			render_settings.max_iter   = self.max_iter

			# TODO: Subdivide pixel_x and pixel_y
			# TODO: Do we really need to subdivide anything but pixel_ vars?
			if direction == "NE":
				render_settings.x = self.x + self.width  / 4.0
				render_settings.y = self.y - self.height / 4.0
			if direction == "NW":
				render_settings.x = self.x - self.width  / 4.0
				render_settings.y = self.y - self.height / 4.0
			if direction == "SE":
				render_settings.x = self.x + self.width  / 4.0
				render_settings.y = self.y + self.height / 4.0
			if direction == "SW":
				render_settings.x = self.x - self.width  / 4.0
				render_settings.y = self.y + self.height / 4.0

			if n_levels > 1:
				ret[direction] = render_settings.subdivide(n_levels-1)
			else:
				ret[direction] = render_settings

		return ret

	def __repr__(self):
		# return "( x: %f, y: %f, w: %f, h: %f, z: %f, pw: %f, ph: %f, iter: %i, num_sample_points: %i)" % (self.x, self.y, self.width, self.height, self.zoom, self.pixel_width, self.pixel_height, self.max_iter, self.num_sample_points)
		return json.dumps(self.__dict__)

def view_coordinates( render_settings, p ):
	width  = render_settings.width  / render_settings.zoom
	height = render_settings.height / render_settings.zoom
	sw = 1.0/width
	sh = 1.0/height
	sx = width/2  - render_settings.x
	sy = height/2 - render_settings.y

	vx = p[0]/(render_settings.pixel_width  * sw) - sx
	vy = p[1]/(render_settings.pixel_height * sh) - sy

	return (vx, vy)

def sample_pixel( x, y, render_settings ):
	width  = render_settings.width
	height = render_settings.height
	pixel_width  = render_settings.pixel_width
	pixel_height = render_settings.pixel_height
	max_iter     = render_settings.max_iter

	ppw = width  / pixel_width  # per pixel width
	pph = height / pixel_height # per pixel height

	if render_settings.num_sample_points == 1:
		vp = view_coordinates(render_settings, (x, y))
		z  = complex( vp[0], vp[1] )
		val  = mandelbrot(z , max_iter)

	elif render_settings.num_sample_points == 2:
		pass

	elif render_settings.num_sample_points == 3:
		# Do this
		pass

	elif render_settings.num_sample_points == 5:
		vp = view_coordinates(render_settings, (x, y))
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
		print "Sampling scheme not implemented."

	return val

def random_sample_pixel( x, y, render_settings ):
	width  = render_settings.width
	height = render_settings.height
	pixel_width  = render_settings.pixel_width
	pixel_height = render_settings.pixel_height
	max_iter     = render_settings.max_iter

	ppw = width  / pixel_width  # per pixel width
	pph = height / pixel_height # per pixel height

	vp = view_coordinates(render_settings, (x, y))

	val = 0.0
	for i in xrange(render_settings.num_sample_points):
		dx = random.random()*ppw*1
		dy = random.random()*pph*1
		z = complex( vp[0]+dx, vp[1]+dy )
		# print vp, (vp[0]+dx, vp[1]+dy)
		val += mandelbrot( z, max_iter, render_settings.api )

	return val / render_settings.num_sample_points

def render_region( render_settings ):
	time_start = time.clock()

	width  = render_settings.width
	height = render_settings.height
	pixel_width  = render_settings.pixel_width
	pixel_height = render_settings.pixel_height
	max_iter     = render_settings.max_iter

	ppw = width  / pixel_width  # per pixel width
	pph = height / pixel_height # per pixel height

	color_palette = ColorPalette()
	data = [None]*pixel_width*pixel_height
	
	for y in xrange(pixel_height):
		for x in xrange(pixel_width):
			# TODO: Introduce sampling function.
			val = random_sample_pixel(x, y, render_settings)
			color = color_palette.getColorForValue(val)
			data[x + y*render_settings.pixel_width] = color

	render_settings.data = data

	time_end = time.clock()
	print "Rendered region in :" + str(time_end-time_start)

	return render_settings

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
		print "Done: " + direction


if __name__ == "__main__":
	p = 9
	render_settings = RenderSettings()
	render_settings.x            = -0.75
	render_settings.y            = 0.10
	render_settings.width        = 2.0
	render_settings.height       = 2.0
	render_settings.zoom         = 1.0
	render_settings.pixel_width  = pow(2,p)
	render_settings.pixel_height = pow(2,p)
	render_settings.max_iter     = 1000

	def profile_test(api):
		render_settings.api          = api
		data = render_region( render_settings )

	cProfile.run('profile_test("python")')
	cProfile.run('profile_test("c")')

# subregions = render_settings.subdivide(0)
# write_region(subregions, "Base")

# threads = []
# for direction in subregions:
# 	region_settings = subregions[direction]
	#thread = threading.Thread(target=write_region, args=(region_settings, direction))
	#threads += [thread]

# for thread in threads:
# 	thread.start()

# for thread in threads:
# 	thread.join()

#cProfile.run("get_mandlebrot_img()")