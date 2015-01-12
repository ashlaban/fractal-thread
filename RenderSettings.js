RenderSettings = function ()
{
	this.name = "Base";

	this.x = 0.0;
	this.y = 0.0;
	this.zoom   = 1.0;
	this.aspect_ratio = 1.0;

	this.pixel_x = 0;
	this.pixel_y = 0;
	this.pixel_width  = 0;

	this.max_iter = 10;
	this.num_sample_points = 1;

	this.api = "NO_API";

	this.sub_regions = [];

	this.callback = null;

	this.tojson = function()
	{
		// Exclude the callback...
		return JSON.stringify({
			name  : this.name,
			x     : this.x,
			y     : this.y,
			width : this.width,
			zoom  : this.zoom,
			aspect_ratio : this.aspect_ratio,

			pixel_x     : this.pixel_x,
			pixel_y     : this.pixel_y,
			pixel_width : this.pixel_width,

			max_iter         : this.max_iter,
			num_sample_points: this.num_sample_points,

			api: this.api,

			sub_regions: this.sub_regions
		})
	}

	this.copyFrom = function(other)
	{
		// Copy all properties
		for (var prop in other)
		{
			this[prop] = other[prop];
		}

		// Except the tree props
		this. sub_regions = [];

	}

};

RenderSettings.prototype.subdivide = function(n)
{
	if (n <= 0) {return;}

	if (this.sub_regions.length > 0) {this.sub_regions = [];}

	var w  = 1.0/this.zoom;
	var h  = w*this.aspect_ratio;
	var pw = this.pixel_width;
	var ph = Math.floor(this.pixel_width*this.aspect_ratio);
	var NE = {name: "NE", dx:  w/4, dy: -h/4, pixel_dx:  pw/2, pixel_dy:    0};
	var NW = {name: "NW", dx: -w/4, dy: -h/4, pixel_dx:     0, pixel_dy:    0};
	var SW = {name: "SW", dx: -w/4, dy:  h/4, pixel_dx:     0, pixel_dy: ph/2};
	var SE = {name: "SE", dx:  w/4, dy:  h/4, pixel_dx:  pw/2, pixel_dy: ph/2};

	var regions = [NE, NW, SW, SE];

	for (var i = 0; i < regions.length; i++)
	{
		var new_render_settings   = new RenderSettings()
		new_render_settings.copyFrom(this);

		console.log(this.x);

		new_render_settings.name  = this.name + '-' +  regions[i].name;
		new_render_settings.x     = this.x + regions[i].dx;
		new_render_settings.y     = this.y + regions[i].dy;
		new_render_settings.zoom  = this.zoom*2;

		new_render_settings.pixel_x      = this.pixel_x + regions[i].pixel_dx;
		new_render_settings.pixel_y      = this.pixel_y + regions[i].pixel_dy;
		new_render_settings.pixel_width  = pw/2;

		console.log(new_render_settings)
		this.sub_regions.push( new_render_settings )

		if (n > 0)
		{
			new_render_settings.subdivide(n-1);
		}
	}
};

RenderSettings.prototype.default = function()
{
	this.name = "Base"

	this.x = 0.0;
	this.y = 0.0;
	this.zoom   = 1.0;
	this.aspect_ratio = 1.0;

	this.pixel_x = 0;
	this.pixel_y = 0;
	this.pixel_width =  512;

	this.max_iter = 10;
	this.num_sample_points = 1;

	this.api = "NO_API"

	this.sub_regions = [];
	
	return this;
};

RenderSettings.prototype.render = function()
	{
		var callback = this.callback;
		if (this.sub_regions.length <= 0)
		{
			$.post( "", this.tojson(), callback );
		}
		else
		{
			for (var i = 0; i < this.sub_regions.length; i++)
			{
				var region = this.sub_regions[i];
				region.render();
			}
		}
	};