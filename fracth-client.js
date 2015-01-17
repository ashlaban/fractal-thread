
function ViewModel(obj)
{
	for (var property in obj)
	{
		var value = obj[property];
		if (value == null ) continue;
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
function init()
{
	c   = document.getElementById("fracth-canvas");
	ctx = c.getContext("2d");
	ctx.fillStyle = "red";
	ctx.fillRect(10,10,50,50);

	c.width  = 512;
	c.height = 128;

	var controlDrag = false;
	var controlPrevious = {x: 0, y: 0};
	$('#control').mousedown( function(e) {
		if (e.target != this) {return;}
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
		canvasRender.getImage();
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