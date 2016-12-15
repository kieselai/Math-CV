"""
	Anthony Kiesel
	CS 5600
	Specialized version of SVMClassifier that loads math symbol training data and classifies
	new symbols according to previous training data
"""
from glob import glob
import re
import numpy as np
from functools import partial


import ImageUtils
from Classifier import SVMClassifier
from CachedTrainingSet import CachedTrainingSet

DATA_EXPORT_FOLDER = "/home/kieselai/python-code/.exported_data/"

class MathSymClassifier(SVMClassifier):
	"""
		Specialized version of SVMClassifier that loads math symbol training data and classifies
		new symbols according to previous training data
	"""
	def __init__(self, image_size=64):
		self.image_size = image_size
		file_end_pattern = "_{0}x{0}.pickle".format(self.image_size)
		training_set = CachedTrainingSet(DATA_EXPORT_FOLDER, file_end_pattern, self.load_new_image_data)
		super().__init__('{0}classifier{1}'.format(DATA_EXPORT_FOLDER, file_end_pattern), training_set)
		self.load_classifier()

	def load_new_image_data(self):
		""" Loads new training labels, human readable text labels, and training data
			(in that order, returned in array) for a training set """
		images, labels, text_labels = [], [], {}
		path_prefix = "/home/kieselai/training-data/reduced_images-{0}x{0}/".format(self.image_size)
		sym_ids = ['0070', '0071', '0072', '0073', '0074', '0075', '0076', '0077', '0078', '0079', '0195', '0196', '0196', '0196', '0514', '0922']
		glob_string = "{}{{}}*_*/[0-9]**.jpg".format(path_prefix)
		filenames = [ glob(glob_string.format(id)) for id in sym_ids ]
		
		for filename in np.concatenate(filenames):
			img_id, img_label, img_data = self.extract_image_data(filename, path_prefix)
			images.append(img_data)
			labels.append(img_id)
			text_labels[img_id] = img_label
		return [np.array(labels), text_labels, ImageUtils.pre_process(images, self.image_size)]

	def extract_image_data(self, filename, path_prefix):
		""" Based on the filename extract image id, label, and load image data """
		short_name = filename.replace(path_prefix, "")
		match = re.match(r'([0-9]{4})_([^/]*)/.*', short_name)
		train_label, text_label = int(match.group(1)), match.group(2)
		image_data = ImageUtils.import_grayscale_image_data(filename)
		return train_label, text_label, image_data


if __name__ == "__main__":
	classifier = MathSymClassifier()
