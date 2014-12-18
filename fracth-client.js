function RenderSettings()
{
	this.name = "Base";

	this.x = 0.0;
	this.y = 0.0;
	this.width  = 0.0;
	this.height = 0.0;
	this.zoom   = 0.0;

	this.pixel_x = 0;
	this.pixel_y = 0;
	this.pixel_width  = 0;
	this.pixel_height = 0;

	this.max_iter = 10;
	this.num_sample_points = 1;

	this.api = "python";

	this.sub_regions = [];
}

function ViewModel(obj)
{
	for (var property in obj)
	{
		var value = obj[property];
		switch (value.constructor)
		{
			case Array:
				this[property] = ko.observableArray(value);
				break;
			default:
				this[property] = ko.observable(value);
				break;
		}
	}
}

function RenderSettingsVMMV()
{
	console.log("New RenderSettingsVMMV");

	var render_settings = new RenderSettings();
	return new ViewModel(render_settings)
}

function defaultRenderSettings()
{
	obj = new RenderSettings();
	obj.name = "Base"

	obj.x = -1.0;
	obj.y = -0.25;
	obj.width  = 2.0;
	obj.height = 2.0;
	obj.zoom   = 1.0;

	obj.pixel_x = 0;
	obj.pixel_y = 0;
	obj.pixel_width =  512;
	obj.pixel_height = 512;

	obj.max_iter = 10;
	obj.num_sample_points = 1;

	obj.api = "python"

	obj.sub_regions = [];
	
	return obj
}

function normaliseRenderSettings( render_settings )
{
	render_settings.width  /= render_settings.zoom;
	render_settings.height /= render_settings.zoom;
	render_settings.zoom = 1.0;
}

// TODO: function inheritance etc.
function subdivideRenderSettings( render_settings, n )
{
	// if (render_settings.sub_regions.length > 0)
	// {
	// 	for (var i = 0; i < render_settings.sub_regions.length; i++)
	// 	{
	// 		subdivideRenderSettings(render_settings.sub_regions[i], n);
	// 	}
	// }
	if (n <= 0) {return;}

	var w  = render_settings.width;
	var h  = render_settings.height;
	var pw = render_settings.pixel_width;
	var ph = render_settings.pixel_height;
	var NE = {name: "NE", dx:  w/4, dy: -h/4, pixel_dx:  pw/2, pixel_dy:    0};
	var NW = {name: "NW", dx: -w/4, dy: -h/4, pixel_dx:     0, pixel_dy:    0};
	var SW = {name: "SW", dx: -w/4, dy:  h/4, pixel_dx:     0, pixel_dy: ph/2};
	var SE = {name: "SE", dx:  w/4, dy:  h/4, pixel_dx:  pw/2, pixel_dy: ph/2};

	var regions = [NE, NW, SW, SE];

	for (var i = 0; i < regions.length; i++)
	{
		var new_render_settings = defaultRenderSettings()
		new_render_settings.name   = render_settings.name + '-' +  regions[i].name;
		new_render_settings.x      = render_settings.x + regions[i].dx;
		new_render_settings.y      = render_settings.y + regions[i].dy;
		new_render_settings.width  = render_settings.width/2;
		new_render_settings.height = render_settings.height/2;

		new_render_settings.pixel_x      = render_settings.pixel_x + regions[i].pixel_dx;
		new_render_settings.pixel_y      = render_settings.pixel_y + regions[i].pixel_dy;
		new_render_settings.pixel_width  = render_settings.pixel_width/2;
		new_render_settings.pixel_height = render_settings.pixel_height/2;

		new_render_settings.max_iter = render_settings.max_iter;
		new_render_settings.num_sample_points = render_settings.num_sample_points;

		if (n > 0)
		{
			subdivideRenderSettings(new_render_settings, n-1);
		}

		render_settings.sub_regions.push( new_render_settings )
	};
}

function render( render_settings )
{
	console.log(render_settings);
	if (render_settings.sub_regions.length <= 0)
	{
		$.post( "", render_settings, function(data){putFractalPiece(data);} )
	}
	else
	{
		for (var i = 0; i < render_settings.sub_regions.length; i++)
		{
			render(render_settings.sub_regions[i]);
		}
	}
}

function getImage()
{
	var render_settings;
	render_settings = defaultRenderSettings();
	render_settings.x = parseFloat(document.getElementById('x').value);
	render_settings.y = parseFloat(document.getElementById('y').value);
	render_settings.pixel_width  = parseInt(document.getElementById('pixel_width').value);
	render_settings.pixel_height = parseInt(document.getElementById('pixel_height').value);
	render_settings.zoom     = parseFloat(document.getElementById('zoom').value);
	render_settings.max_iter = parseFloat(document.getElementById('max-iter').value);
	render_settings.num_sample_points = parseInt(document.getElementById('num-sample-points').value);
	render_settings.api = document.getElementById('api').value;
	normaliseRenderSettings( render_settings );

	var c = document.getElementById("fracth-canvas");
	c.width  = render_settings.pixel_width;
	c.height = render_settings.pixel_height;

	var n = Math.log2(render_settings.pixel_width) - 8;
	subdivideRenderSettings( render_settings, n );
	render( render_settings );
}

function putFractalPiece( data )
{
	console.log('Fractal received.');
	console.log(data)

	var c = document.getElementById("fracth-canvas");
	var ctx = c.getContext("2d");

	var x, y;
	switch (name)
	{
		case "NE":
		case "NW":
		case "SW":
		case "SE":
	}

	x = data.pixel_x;
	y = data.pixel_y;
	var width = data.pixel_width;
	var height = data.pixel_height;
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
function init()
{
	c   = document.getElementById("fracth-canvas");
	ctx = c.getContext("2d");
	ctx.fillStyle = "red";
	ctx.fillRect(10,10,50,50);

	c.width  = 512;
	c.height = 512;

	var controlDrag = false;
	var controlPrevious = {x: 0, y: 0};
	$('#control').mousedown( function(e) {
		controlDrag = true;
		controlPrevious.pageX = e.pageX;
		controlPrevious.pageY = e.pageY;
	});
	$('#control').mouseup( function(e) {
		controlDrag = false;
	});
	$(document).mousemove( function(e) {
		var el = $('#control');

		if (controlDrag)
		{
			var x = el.offset().left;
			var y = el.offset().top;

			el.offset({
				top : y + (e.pageY - controlPrevious.pageY),
				left: x + (e.pageX - controlPrevious.pageX)
			});
			controlPrevious.pageX = e.pageX;
			controlPrevious.pageY = e.pageY;
		}
	});

}

$(window).on( 'keydown', function(e) {
	var key = e.keyCode ? e.keyCode : e.which;
	
	switch (key)
	{
	case 13: // Enter
		getImage();
		break;
	case 27: // Esc
		e.preventDefault();
		$('#control').toggle(150);
		break;
	default:
		console.log('Key pressed ' + key)
	}
});

$(document).ready( init );

var vm = new RenderSettingsVMMV();