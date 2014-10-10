import numbers
from PIL import Image
import cProfile

def mandlebrot(c, max_iter):
	if  isinstance(c, numbers.Number) \
	and isinstance(max_iter, numbers.Number):
		return __mandlebrot_internal(c, max_iter)
	else:
		return None

def __mandlebrot_internal(c, max_iter):
	z = c
	z_old = 0
	for i in xrange(max_iter):
		z = z*z + c
		if (z.real >= 2.0 or z.imag >= 2.0):
			return 1.0 - float(i)/max_iter
		if (z == z_old):
			break
		z_old = z

	return 0.0

temp = 512
image_width  = temp
image_height = temp

view = { "x":0.0, "y":0.5, "width":2.0, "height":2.0, "zoom":4.0 }

def view_coordinates( view, p ):
	width  = view["width"]  / view["zoom"]
	height = view["height"] / view["zoom"]
	sw = 1.0/width
	sh = 1.0/height
	sx = width/2  - view["x"]
	sy = height/2 - view["y"]

	vx = p[0]/(image_width  * sw) - sx
	vy = p[1]/(image_height * sh) - sy
	return (vx, vy)

def get_mandlebrot_img():
	c = -1
	max_iter = 1000
	data = [None]*image_width*image_height
	for y in xrange(image_height):
		print "Row " + str(y) + " of " + str(image_height)
		for x in xrange(image_width):
			vp = view_coordinates(view, (x,y))
			c = complex( vp[0], vp[1] )
			data[x + y*image_width] = int(mandlebrot(c, max_iter)*255)

	im = Image.new("RGB", (image_width, image_height), "white")
	im.putdata(data)
	im.save("test.png")

cProfile.run("get_mandlebrot_img()")