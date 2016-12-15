var express    = require('express');
var helmet = require('helmet');
var bodyParser = require('body-parser');
var fs = require("fs");
var temp = require('temp');
var spawn = require('child_process').spawn;
var app = express();
var net = require('net');
app.use(helmet());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

app.disable('x-powered-by');

app.use(express.static(__dirname + '/static'));

var path = require('path');

app.get('/', function(req, res) { 
  res.sendFile(path.join(__dirname + '/static/index.html'));
});

var save_image_file = function(img_data, ext, sym){
    var data_uri = img_data.replace(/^data:image\/(jpeg|png);base64,/, "");
    if(ext == 'jpeg') ext = 'jpg';
	sym = "" + sym;
	var symbols = {
		"0": "0070_0",
		"1": "0071_1",
		"2": "0072_2",
		"3": "0073_3",
		"4": "0074_4",
		"5": "0075_5",
		"6": "0076_6",
		"7": "0077_7",
		"8": "0078_8",
		"9": "0079_9",
		"-": "0195_SYM_minus",
		"+": "0196_SYM_plus",
		"*": "0514_ast",
		"/": "0922_SYM_forward_slash"
	}
	sym = symbols[ sym ] || ""
    var file_name = temp.path({ prefix: sym + "___zzz___", suffix: '.' + ext});
    fs.writeFile(file_name, data_uri, 'base64', function(error){
        console.log(error);
    });
	return file_name;
}


app.post('/process_image', function(req, res){
	var file_name = save_image_file(req.body.img_data, req.body.ext) 
	var symbols = {
        "70" : "0",
        "71" : "1",
        "72" : "2",
        "73" : "3",
        "74" : "4",
        "75" : "5",
        "76" : "6",
        "77" : "7",
        "78" : "8",
        "79" : "9",
        "195" : "-",
        "196" : "+",
        "514" : "*",
        "922" : "/",
	};

	var client = new net.Socket();
	client.connect(12000, '127.0.0.1', function() {
		console.log(file_name);
		client.write(file_name);
	});
	client.on('data', function(data){
		var s = data.toString().replace("\n", "").split(",");
		var eq = ""
		for (i = 0; i< s.length; i++){
			eq += symbols[s[i].replace(" ","")]
		}
		var result;
		try {
			result = eval(eq);
		}
		catch(err){
			result = "UNKNOWN";
		}
		res.json({ equation: eq, solution: result })
		client.destroy()
	});
});

/*
Originally Used to make training images.
Disabled for now.
app.post('/training_image', function(req, res){
	var sym = req.body.sym || -1;
	if (sym != -1){
		file_name = save_image_file(req.body.img_data, req.body.ext, req.body.sym)
		res.json({ result: "SUCCESS"});
	}
});
*/

app.listen(8080, function(){
  console.log('Express server listening on port 8080')
});
