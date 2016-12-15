"""
	Anthony Kiesel
	CS 5600
	Class Used to load and store training data in pickle files
"""

from IPython import embed

from MathCVExceptions import DataFileNotFoundError
from DataManager import DataManager

class CachedTrainingSet:
	""" Class Used to load and store training data in pickle files """
	def __init__(self, path_prefix, filename_end, calculate_training_set_func):
		self.path_prefix = path_prefix
		self.filename_end = filename_end
		self.recalculate = calculate_training_set_func
		self.training_labels = None
		self.text_labels = None
		self.training_data = None

	def load_training_labels(self, exception_without_file=False):
		""" Load training labels, a numpy array of integer ids used to label classes in classifier """
		try:
			training_labels_file = "{0}training_labels{1}".format(self.path_prefix, self.filename_end)
			self.training_labels = DataManager.import_pickle_file(training_labels_file, exception_without_file=True)
		except DataFileNotFoundError as err:
			if exception_without_file:
				raise err
			else:
				self.load_training_data()

	def load_text_labels(self, exception_without_file=False):
		""" Loads text labels, a dictionary using the training label ids as a key,
			and a human readable string as the value """
		try:
			text_labels_file = "{0}text_labels{1}".format(self.path_prefix, self.filename_end)
			self.text_labels = DataManager.import_pickle_file(text_labels_file, exception_without_file=True)
		except DataFileNotFoundError as err:
			if exception_without_file:
				raise err
			else:
				self.load_training_data()

	def load_training_data(self, exception_without_file=False):
		""" Load training data.  This is a numpy array of numpy arrays containing training features """
		template_filename = "{pre}{{}}{end}".format(pre=self.path_prefix, end=self.filename_end)
		files = [template_filename.format(mid) for mid in ["training_labels", "text_labels", "training_data"]]
		loaded_data = DataManager.import_pickle_file(files, self.recalculate, exception_without_file)
		self.training_labels, self.text_labels, self.training_data = loaded_data[0:3]

	def get_training_labels(self):
		""" Load training labels if they do not exist and then return them. """
		if self.training_labels is None:
			self.load_training_labels()
		return self.training_labels

	def get_text_labels(self):
		""" Load text labels if they do not exist and then return them. """
		if self.text_labels is None:
			self.load_training_labels()
		return self.text_labels

	def get_training_data(self):
		""" Load training data if it does not exist and then return the data. """
		if self.training_data is None:
			self.load_training_data()
		return self.training_data
