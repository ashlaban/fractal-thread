CanvasRenderer = function()
{
	this.commitRenderSettings = function()
	{
		var w = parseInt(document.getElementById('pixel_width').value);
		var h = parseInt(document.getElementById('pixel_height').value)
		var aspect_ratio = h/w;

		this.render_settings.x = parseFloat(document.getElementById('x').value);
		this.render_settings.y = parseFloat(document.getElementById('y').value);
		this.render_settings.aspect_ratio = aspect_ratio;
		this.render_settings.pixel_width  = parseInt(document.getElementById('pixel_width').value);
		this.render_settings.zoom     = parseFloat(document.getElementById('zoom').value);
		this.render_settings.max_iter = parseFloat(document.getElementById('max-iter').value);
		this.render_settings.num_sample_points = parseInt(document.getElementById('num-sample-points').value);
		this.render_settings.api = document.getElementById('api').value;

		this.render_settings.sub_regions = []
	}

	this.getImage = function()
	{
		this.commitRenderSettings();

		var c = $('#fracth-canvas')[0];
		w = this.render_settings.pixel_width;
		h = this.render_settings.pixel_width * this.render_settings.aspect_ratio;
		if (c.width != w || c.height != h)
		{
			c.width = 1; // FIX ME: This is currently required to update the size of the canvas if only height changes.
			c.width  = w;
			c.height = h;
			c.style.width  = w;
			c.style.height = h;
		}

		// TODO: Specify square width
		var n = Math.log2(this.render_settings.pixel_width) - 8;
		this.render_settings.subdivide(n);
		this.render_settings.render();
	}

	this.putFractalPiece = function ( data )
	{
		console.log('Fractal received.');
		console.log(data)

		var c = document.getElementById("fracth-canvas");
		var ctx = c.getContext("2d");

		var x, y;

		x = data.pixel_x;
		y = data.pixel_y;
		var width  = data.pixel_width;
		var height = data.pixel_width*data.aspect_ratio;
		imageData = ctx.getImageData(x, y, width, height);

		for ( var i = 0; i < width*height; i++ )
		{
			imageData.data[i*4+0] = (data.data[i] >>  0) & 0xff; // red   channel
			imageData.data[i*4+1] = (data.data[i] >>  8) & 0xff; // green channel
			imageData.data[i*4+2] = (data.data[i] >> 16) & 0xff; // blue  channel
			imageData.data[i*4+3] = 0xff;//(data.data[i] >> 24) & 0xff; // alpha channel
		}

		ctx.putImageData(imageData, x, y);
	}

	this.render = $.debounce(function( old_zoom )
	{
		this.x = parseFloat(document.getElementById('x').value);
		this.y = parseFloat(document.getElementById('y').value);
		this.zoom = parseFloat(document.getElementById('zoom').value);

		var canvas  = $('#fracth-canvas')[0];
		var context = canvas.getContext('2d');
		context.setTransform( zoom, 1, 0, 1, zoom, 0 );

		this.getImage();
	}, 250);

	// ========================================================================
	
	this.x    = 0.0;
	this.y    = 0.0;
	this.zoom = 1.0;

	this.render_settings = new RenderSettings();
	this.render_settings.default();
	this.render_settings.callback = this.putFractalPiece;
}

var canvasRender = new CanvasRenderer();

$(window).bind('mousemove', function(event)
{
	// TODO: Implement mouse move similar to control panel as well?

	var canvas = $('#fracth-canvas');
	var ex = event.pageX;
	var ey = event.pageY;
	var cx = canvas.offset().left;
	var cy = canvas.offset().top;

	// var insideCanvas =  ex > cx
	//                  && ey > cy
	//                  && ex < cx+canvas.width()
	//                  && ey < cy+canvas.height();

	if ( $(event.target).is(canvas) )
	{
		var zoom = parseFloat(document.getElementById('zoom').value);

		var dx = (event.pageX - $('#fracth-canvas').offset().left);
		var dy = (event.pageY - $('#fracth-canvas').offset().top );
		var fx = (dx / canvas.width()  - 0.5) / zoom;
		var fy = (dy / canvas.height() - 0.5) / zoom;

		document.getElementById('x').value = canvasRender.x + fx;
		document.getElementById('y').value = canvasRender.y + fy;
	}
});

$(window).bind('mousewheel', function(event)
{
	var canvas = $('#fracth-canvas');
	var ex = event.pageX;
	var ey = event.pageY;
	var cx = canvas.offset().left;
	var cy = canvas.offset().top;

	// var insideCanvas =  ex > cx
	//                  && ey > cy
	//                  && ex < cx+canvas.width()
	//                  && ey < cy+canvas.height();

	if ( $(event.target).is(canvas) )
	{
		event.preventDefault();
		var zoom     = parseFloat(document.getElementById('zoom').value);
		var old_zoom = zoom;

		console.log(canvasRender.zoom)
		// zoom += event.originalEvent.deltaY / 10;
		scaling_factor = 0.025;
		scaling_amount = Math.abs(event.originalEvent.deltaY);

		if (event.originalEvent.deltaY >= 0)
		{
			zoom *= 1 + scaling_factor * scaling_amount;
		}
		else if (event.originalEvent.deltaY < 0)
		{
			zoom /= 1 + scaling_factor * scaling_amount;
		}

		if (zoom < 0.1)
		{
			zoom = 0.1
		}

		document.getElementById('zoom').value = zoom;
		canvasRender.render(old_zoom);
	}
});