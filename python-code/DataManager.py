"""
	Anthony Kiesel, CS 5600
	This module contains the DataManager class, which is used to save and load pickle files
"""
import os
import pickle
from functools import partial
from IPython import embed
from MathCVExceptions import DataFileNotFoundError, ObjectNotCallable

class DataManager():
	""" Manages Pickle data files and provides file utility functions """
	@staticmethod
	def import_pickle_file(exported_filename, recalculate_function=None, exception_without_file=False):
		""" Loads data from a pickle file provided that the file exists,
			otherwise the data is recalculated or an error is returned """
		# if a list of file names is provided, load each data file if the file exists
		if isinstance(exported_filename, (list, tuple)) and not isinstance(exported_filename, str):
			if all([os.path.isfile(x) for x in exported_filename]):
				return [DataManager.open_file(file_name, 'rb', pickle.load) for file_name in exported_filename]
		# if a single file name is provided, load that file if it exists
		elif os.path.isfile(exported_filename):
			return DataManager.open_file(exported_filename, 'rb', pickle.load)
		# if the file doesn't exist and we want to throw an exception rather than try to load the data, throw an exception
		if exception_without_file:
			raise DataFileNotFoundError(exported_filename)
		# if the recalculate function is callable, recalculate the data and export the data to a pickle file
		elif hasattr(recalculate_function, '__call__'):
			export_data = recalculate_function()
			DataManager.export_pickle_file(exported_filename, export_data)
			return export_data
		# If no recalculate function is given, or it is invalid, throw an exception
		else:
			raise ObjectNotCallable("File not found, and recalculate_function parameter is not callable. ")

	@staticmethod
	def export_pickle_file(exported_filename, export_data):
		""" Exports an object or multiple objects to the specified pickle file(s) """
		# if a list of file names are provided, save each element in the export data list to the corresponding file
		if isinstance(exported_filename, (list, tuple)) and not isinstance(exported_filename, str):
			for file_name, val in zip(exported_filename, export_data):
				DataManager.open_file(file_name, "wb", partial(pickle.dump, val))
		else: # otherwise save to a single file
			DataManager.open_file(exported_filename, 'wb', partial(pickle.dump, export_data))

	# Helper method to open a file, call a function on the file handle, and return any values produced
	@staticmethod
	def open_file(file_name, open_mode, action_func):
		""" Opens a file in the specified mode and performs some action on the file handle
			before closing and returning the handle """
		if hasattr(action_func, '__call__'):
			with open(file_name, open_mode) as file_handle:
				return action_func(file_handle)
		else:
			raise ObjectNotCallable("ERROR: File open action is not callable.")
