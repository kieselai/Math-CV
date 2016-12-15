import socket
import os
import subprocess
import re
import time
import ImageUtils
from MathSymClassifier import MathSymClassifier

HOST="127.0.0.1"
PORT = 12000
BUFFER_SIZE=1024

# Load the existing classifier
classifier = MathSymClassifier() 

def launch_listener():
	"""
		This function can be used to launch a TCP server that receives the path
		to an image file and responds with classification of the digits in that file.
		If the port is already in use, it's likely because this application was previously
		using it, so I scripted a few commands to find the pid of the open process
		and kill it so the port can be reused. This probably isn't the best method,
		but it's pretty unlikely that other processes would use this specific port.
	"""
	netstat = subprocess.Popen(['netstat', '-lpn'], shell=False, stdout=subprocess.PIPE)
	(out, err) = netstat.communicate()
	regx=re.compile("^tcp.*127\.0\.0\.1:12000.*LISTEN[ ]*(?P<pid>[0-9]*)/.*$")
	for line in out.decode('utf-8').split("\n"):
		match=regx.match(line)
		if match:
			subprocess.Popen(["kill", "-9", match.group("pid")])
			time.sleep(1)
	# Create the listener
	listener=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listener.bind((HOST, PORT))
	listener.listen(1);
	# Listen and return results
	while(True):
		(connection, address) = listener.accept()
		try:
			filename = connection.recv(BUFFER_SIZE).decode('utf-8').strip()
			print(filename)
			prediction_str = process_input_and_predict(filename)
			print(prediction_str)
			connection.send(str.encode(prediction_str))
		except Exception as err:
			connection.send(str.encode("ERROR"))
	connection.close()

def process_input_and_predict(filename):
	"""
		Check if the file exists and use the classifier to predict what symbols
		the image contains. 
	"""
	if os.path.isfile(filename):
		symbol_images = ImageUtils.get_split_images_ordered(filename)
		resized = [ ImageUtils.resize_image_data(img) for img in symbol_images ]
		features = ImageUtils.pre_process(resized, 64)
		prediction_str = ",".join([ str(p) for p in classifier.predict(features)])
		return prediction_str;
	else:
		return "ERROR";


if __name__ == "__main__":
	launch_listener()
