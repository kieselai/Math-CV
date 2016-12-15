#!/usr/bin/python3
"""
	Anthony Kiesel
	CS 5600
	Provides utilities to work with images for pre-processing, etc
"""
import numpy as np
import cv2
from PIL import Image, ImageChops
import skimage.feature
import argparse
import uuid


def import_grayscale_image_data(filepath):
	""" loads an image, converts it to grayscale, and returns a flattened array of the pixel matrix """
	return cv2.cvtColor(cv2.imread(filepath), cv2.COLOR_BGR2GRAY)

def pre_process(images_np_arr, img_size):
	""" Runs full pre-processing on each img_size x img_size array of images and returns a flattened feature descriptor for each image """
	data = np.array([deskew_image(img, img_size) for img in images_np_arr])
	data = np.array([calculate_hog(img, img_size) for img in data])
	return data

def flatten_images_array(images_arr, img_size):
	""" Flattens each image in the images_arr to a flat array.  """
	return np.array(images_arr).reshape(len(images_arr), img_size * img_size)

def deskew_image(img, dim):
	""" 
		Original Code at: http://docs.opencv.org/trunk/dd/d3b/tutorial_py_svm_opencv.html 

		Rotates an image into a straigtened orientation.

		This code takes advantage of image moments, which are a way of using the 
		average intensity of pixel values to describe different properties of the image.
		In this particular case, covariance of these moments can be used to determine 
		the orientation of the image. 
		https://en.wikipedia.org/wiki/Image_moment#Examples_2

		img is a dim x dim numpy matrix
	"""
	moment = cv2.moments(img)
	if abs(moment['mu02']) < 1e-2:
		return img.copy()
	img_skew = moment['mu11'] / moment['mu02']
	rot_matrix = np.float32([[1, img_skew, -0.5*dim*img_skew], [0, 1, 0]])
	return cv2.warpAffine(img, rot_matrix, (dim, dim), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)

def calculate_hog(img, img_size):
	""" Calculate hog value as feature set """
	num_cells = 4
	num_pixels = img_size / num_cells
	per_cell=(num_pixels, num_pixels)
	per_block=(num_cells, num_cells)
	return skimage.feature.hog(img, pixels_per_cell=per_cell, cells_per_block=per_block, orientations=8)

def resize_image(image_filepath, destination_filepath, new_size=64, do_crop_whitespace=True, do_center_and_pad=True):
	""" Resize an image and save at destination path """
	size = (new_size, new_size)
	image = Image.open(image_filepath)
	if do_crop_whitespace:
		image = crop_whitespace(image)
	image.thumbnail(size, Image.ANTIALIAS)
	if do_center_and_pad:
		image = center_and_pad(image, size)
	image.save(destination_filepath)

def resize_image_data(img):
	""" 
		Resize a cv2 format image to a square 64x64 size.
		The image is padded equally on opposite sides if one dimension doesn't equally fit.
	"""
	size = (64,64)
	temp_file = "/tmp/" + str(uuid.uuid4())+".jpg"
	cv2.imwrite(temp_file, img)
	image = Image.open(temp_file)
	image.thumbnail(size, Image.ANTIALIAS)
	image = center_and_pad(image, size)
	return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

def crop_whitespace(image):
	"""
		Crop a PIL format image.  Compares to a white background and saves where
		the image is different.
	"""
	background = Image.new("RGB", image.size, color=(255, 255, 255))
	diff = ImageChops.difference(image, background)
	bbox = diff.getbbox()
	if bbox:
		return image.crop(bbox)
	else:
		return image.copy() # If the image is completely whitespace

def center_and_pad(image, size):
	""" 
		Centers an image on a white background.  
		If the original image isn't square, this will
		make the image squared at the center of the image.
	"""
	background = Image.new("RGB", size, (255, 255, 255))
	x_pad = (size[0] - image.size[0]) // 2
	y_pad = (size[1] - image.size[1]) // 2
	offset = (x_pad, y_pad)
	background.paste(image, offset)
	return background;

def find_connected_paths(img):
	"""
		This is used for finding each digit or symbol.  
		Here are the processing steps:
		01: Since images submitted tend to have broken segments in each digit,
		    First a blur is applied to the image, 
			Second, and more importantly, a dilation is applied to hopefully 
			reconnect lines that are very close together.
			Attempts were made to combine these segments by looking at the
			coordinates they were in, but I finally settled on this pre-processing
			step as the most concise way to achieve results. 
		02: A reverse threshold is applied after blur and dilation.  I had 
			originally thought this step could be skipped, since it is mostly used 
			to clean up poor image quality, erasing artifacts that are present due
			to poor lighting, picture quality or in handwriting it might be an 
			accidental pencil stroke that is not dark enought to be considered
			as a written character.  In my case, this is a digital image, so I
			don't believe there should be any of those issues. Unfortunately the
			next step would not work until I applied this thresholding.  I don't
			know exactly if this is a requirement to finding contours, but the code
			works, so the current implementation does include this step. 
		03: Find the contours.  This is the overall goal, and it works quite nicely
			following all of the previously mentioned pre-processing. The cv2.RETR_EXTERNAL 
			parameter tells the findContours function that it should return the
			outermost contour of a detected contour. Other options are to return a tree,
			a simple list, or to return all boundaries including inner and outer
			contours.  So if the image was of say a 0, there would be an inner and outer
			contour specified.  This option just gives the outer-most contour. The 
			cv2.CHAIN_APPROX_SIMPLE option simply allows us to save memory by giving
			sampled endpoints of contours, rather than every point inbetween.
	"""
	if isinstance(img, str): # If the provided image is a string, go ahead and open the file that is specified.
		img = import_grayscale_image_data(img)
	blur = cv2.GaussianBlur(img,(5,5),0)
	di = cv2.dilate(blur, (3,3))
	retVal, thresh=cv2.threshold(blur, 125, 255, cv2.THRESH_BINARY_INV)
	img2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	return img, contours, hierarchy

def get_split_images_ordered(img):
	"""
		Use the connected contours of an image to find bounding rectangles, 
		which can then be ordered by the left-most x-axis value of each contour. 
		A mask is created for each connected section, and all other values are
		removed from a copy of the original image. The remaining image is the
		inner portion of an outer contour line, which should be an individual
		character if no two characters are connected.
	"""
	img, contours, hierarchy = find_connected_paths(img)
	rects = []
	images = []
	for i, c in enumerate(contours):
	   r = cv2.boundingRect(c)
	   rects.append(r) # Save the area of the image the current symbol is located at
	   mask = np.zeros([len(img), len(img[0])], dtype=np.uint8) # Create a blank copy of img
	   mask.fill(255)
	   # Use outer contour line to create a mask of the area of interest	   
	   img3=cv2.drawContours(mask, contours, i, (0,255,0), cv2.FILLED)
	   # Flatten the mask and original image and copy any pixel that black in both images to the new image.
	   m_flat = mask.reshape(1, -1)
	   im_flat = img.copy().reshape(1, -1)
	   for j in range(0, len(m_flat[0])):
	       if m_flat[0][j] != 0:
	           im_flat[0][j] = 255
	   img4 = im_flat.reshape(len(img), len(img[0])) #resize new image to correct size
	   x, y, w, h = cv2.boundingRect(c)
	   crop = img[y:y+h, x:x+w] # crop image to boundary
	   images.append(crop.copy())
	x = [ r[0] for r in rects ] # get x-vals of each symbol
	mins = []
	for j in range(0, len(x)):
	    mins.append(x.index(min(x)))
	    x[ x.index(min(x)) ] = 99999999
	sorted_imgs = [ images[j] for j in mins ] # sort images according to minimum-x indices
	return sorted_imgs


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Image Utilities')
	parser.add_argument('-r', '--resize', action='store_true', help='Crop and resize image to fit width specified')
	parser.add_argument('-i', '--infile', action='store', default='', help="The image file to use")
	parser.add_argument('-o', '--outfile', action='store', default="", help="The output file to write to")
	parser.add_argument('-s', '--size', action='store', default=64, type=int, help="Square image size to use")
	args = parser.parse_args()
	if args.resize and args.infile.strip() != '' and args.outfile.strip() != '':
		resize_image(args.infile.strip(), args.outfile.strip(), args.size)

