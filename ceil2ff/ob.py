"""
	ob module creates an observation object for use with profiles
	should hold necessary height information, values in the profile, and metadata
	
	should use numpy for all possible operations.

"""

import matplotlib.pyplot as plt
from numpy import array
from tools import flip2d


class Ob:
	def __init__(self, raw):
		"""
		Create an observation object 
		Inputs:
			raw = the text of the observation
		"""
		self.raw = raw
		# that's it.
		
	def flip(self, array):
		"""
		Flip the indeces of an array, to be used internally or externally
		"""
		return flip2d(array)

