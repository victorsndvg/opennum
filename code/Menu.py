#!/usr/bin/env python
# -*- coding: utf-8 -*-



import trees
import Node
import SubMenu



class Menu(Node.Node):



	def __init__(self):
		Node.Node.__init__(self)



	def load(self,menu):
		Node.Node.load(self,menu)

		items = menu.getchildren()
		for item in items:
			if (item.tag==u'submenu'):
				submenu = SubMenu.SubMenu()
				submenu.load(item)
				self.add_child(submenu)



			
	def save_data(self, parent, parameters=None, transform=None):
		e = trees.ET.Element(self.get_tag())
		e.set(u"name",self.get_name())
		for child in self.get_children():
			child.save_data(e, parameters, transform)
		parent.append(e)



	def prepare(self, menus):
		for child in self.get_children():
			child.prepare(menus)



	def preload(self):
		errors = []
		for child in self.get_children():
			r = child.preload()
			errors.extend(r)
		return errors



	def pretest(self, options):
		errors = []
		for child in self.get_children():
			r = child.pretest(options)
			errors.extend(r)
		return errors



	def get_nodes(self, which):
		result = []
		for child in self.get_children():
			r = child.get_nodes(which)
			result.extend(r)
		return result



	def save_menu(self, parent):
		e = trees.ET.Element(self.get_tag())
		e.attrib = self.get_attribs().copy()
		for child in self.get_children():
			child.save_menu(e)
		parent.append(e)



	def dump(self, index=0):
		print " " * index * 3, u"menu: name:", self.get_name()
		for child in self.get_children():
			child.dump(index + 1)

