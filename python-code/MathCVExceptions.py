"""
	Anthony Kiesel, CS 5600
	Module containing error classes for MathCV
"""

class DataFileNotFoundError(Exception):
	""" Exception used when a training data file
		can't be found and exceptions are enabled
		on import.
	"""
	pass

class ObjectNotCallable(Exception):
	""" Raised when an object isn't callable """
	pass
