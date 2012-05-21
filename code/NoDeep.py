#!/usr/bin/env python
# -*- coding: utf-8 -*-



import copy



class NoDeep():

	def __init__(self, item):
		self.item = item

	def geti(self):
		return self.item

	def seti(self, item):
		self.item = item

	def __copy__(self, memo):
		return NoDeep(self.item)

	def __deepcopy__(self, memo):
		return NoDeep(self.item)

