
var canvas = $("#notebook");
var ctx = canvas.get(0).getContext("2d");
var draw_flag = false;
var prev = { x: 0, y: 0 };
reset_canvas();
var set_flag = (value) => { draw_flag = value; }
$(document).on("mousedown", "*", (e) => { set_flag(true); });
$(document).on("mouseup", "*", (e) => { set_flag(false); });
var prevent_scroll_on_touchscreen_canvas = (e) => {
	if (e.target == canvas.get(0)){
		e.preventDefault();
	}
}
$(document).on("touchstart", "*", prevent_scroll_on_touchscreen_canvas);
$(document).on("touchmove", "*", prevent_scroll_on_touchscreen_canvas);
$(document).on("touchend", "*", prevent_scroll_on_touchscreen_canvas);

canvas.on({
	"mouseenter": (e) => prev=get_position(e, canvas.offset()),
	"mousemove": (e) => draw(e),
	"mousedown": (e) => draw(e),
	"mouseout": (e)=> draw(e),
	// Touchscreen
	"touchstart": (e) => {
		set_flag(true)
		prev=get_position(e.touches[0], canvas.offset());	
	},
	"touchmove": (e) => draw(e.touches[0]),
	"touchend": (e) => set_flag(false)
});
var get_position=(e, offset) => {
	var mouse_x = (e.pageX || e.clientX || 0);
	var mouse_y = (e.pageY || e.clientY || 0);
	return { x: mouse_x - offset.left, y: mouse_y - offset.top }; 
};

function draw(e) {
	var curr = get_position(e, canvas.offset());
	if(draw_flag){
		draw_line(prev.x, prev.y, curr.x, curr.y);
	}
	prev = curr;
}

function draw_line(x1, y1, x2, y2){
	ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = "black";
    ctx.lineWidth = 5;
    ctx.stroke();
    ctx.closePath();
}

function reset_canvas() {
	var fill_style = ctx.fillStyle;
    ctx.clearRect(0, 0, canvas.width(), canvas.height());
	ctx.beginPath();
	ctx.rect(0, 0, canvas.width(), canvas.height());
	ctx.fillStyle = "white";
	ctx.fill();
	ctx.fillStyle = fill_style;	
}

function submit_image(){
	$.ajax({	
		type: "POST",
		url: "process_image",
		data: { img_data: canvas.get(0).toDataURL('image/jpeg'), ext: 'jpg' },
		success: function(result){
			console.log(result);
			$("#equation").val(result.equation);
			$("#solution").val(result.solution);
		}
	});		
}

/*
Training images disable for now
function submit_training_image(){
	var sym = $("#sym_field").val();
	if (sym !== ""){
   		$.ajax({
   		    type: "POST",
   		    url: "training_image",
   		    data: { 
   				img_data: canvas.get(0).toDataURL('image/jpeg'),
   				ext: 'jpg',
   				sym: $("#sym_field").val()
   			},
   		    success: function(result){
   		        console.log(result);
   		    }
   		});
	}
	else {
		alert( "What Symbol is this image?" )
	}
}
*/


$("#reset_button").click(()=>reset_canvas());
$("#submit_button").click(()=> submit_image());
/*
Training images disabled for now
$("#submit_training").click(()=>{
	submit_training_image();
	reset_canvas();
})
*/
