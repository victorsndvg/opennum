#!/usr/bin/env python
# -*- coding: utf-8 -*-



import FileMrw



class FileMrwScalars(FileMrw.FileMrw):



	def __init__(self, callback=None):
		FileMrw.FileMrw.__init__(self, callback)
		self.array = []



	def gets(self):
		return self.array



# only modifies self if read is successfull
	def read(self, filename, attribs):
		FileMrw.FileMrw.read(self, filename, attribs)

		data = FileMrw.FileMrw.split(self.filename)

		if data[u'error'] is not None:
			return data[u'error']

		result = self.read2(data[u'data'])

		if result is False:
			return False

		self.array = result

		return True



	def read2(self, tokens):
		if len(tokens) < 1:
			return False

		sizea = FileMrw.FileMrw.read_ints(tokens, 0, 1)
		if sizea is False:
			return False

		size = sizea[0]

		if size + 1 > len(tokens):
			return False

		array = FileMrw.FileMrw.read_floats(tokens, 1, size)

		if array is False:
			return False

		return array

