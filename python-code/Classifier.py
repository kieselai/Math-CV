"""
	Anthony Kiesel
	CS 5600
	Generic SVM Classifier that persists through pickle files
"""
from datetime import datetime
from sklearn import svm
from DataManager import DataManager
from IPython import embed

class SVMClassifier():
	"""
		Generic SVM Classifier that persists through pickle files
	"""
	def __init__(self, export_file, training_set, gamma=1e-8):
		self.gamma = gamma
		self.export_file = export_file
		self.training_set = training_set
		self.svm = None

	def load_classifier(self):
		""" Load a saved classifier from a pickle file """
		self.svm = DataManager.import_pickle_file(self.export_file, self.train_new_classifier)

	def train_new_classifier(self):
		""" Train a new classifier from training data """
		print("STARTING TRAINING: {}".format(datetime.now().time()))
		data = self.training_set.get_training_data()
		labels = self.training_set.get_training_labels()
		classifier = svm.SVC(gamma=self.gamma, kernel='linear')
		classifier.fit(data, labels)
		print("FINISHED: {}".format(datetime.now().time()))
		return classifier

	def get_classifier(self):
		""" Returns the classifier if it has already been loaded, otherwise the classifier is loaded. """
		if self.svm is None:
			self.load_classifier()
		return self.svm

	def predict(self, data_sample):
		""" Returns a prediction from a trained classifier """
		return self.svm.predict(data_sample)
