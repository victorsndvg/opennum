#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os.path
import trees
import config
import Node
import Element



class Leaf(Element.Element):



    def __init__(self):
        Element.Element.__init__(self)



    def set_elements(self, elements):
        self.del_children()
        for element in elements:
            n = Node.Node()
            n.tag = u'element'
            n.set_name(element)
            n.attribs[u'selected'] = u'true'
            self.add_child(n)



    # sets elements but remain unselected
    def set_elements_nosel(self, elements):
        self.del_children()
        for element in elements:
            n = Node.Node()
            n.tag = u'element'
            n.set_name(element)
            self.add_child(n)



    def set_elements_with_source(self, menus, elements, sources=None): # ok +. children with duplicates
        if sources is None:
            sources = self.get_remote_source(menus)
        if (isinstance(sources, list)):
            self.del_children()
            elementsset = set(elements)
            for source in sources:
                if source in elementsset:
                    n = Node.Node()
                    n.tag = u'element'
                    n.set_name(source)
                    n.attribs[u'selected'] = u'true'
                    self.add_child(n)
            return True
        else:
            return sources



    def get_elements_with_source(self, menus, sources=None): # ok +
        if sources is None:
            sources = self.get_remote_source(menus)
        self.clear_elements_not_in_source(menus, sources)
        if (isinstance(sources, list)):
            result = []
            names = set()
            for child in self.children:
                name = child.get_name()
                names.add(name)
            for source in sources:
                if source in names:
                    result.append((source,True))
                else:
                    result.append((source,False))
            return result
        else:
            return sources



    def load(self, submenu):
        Element.Element.load(self,submenu)

        items = submenu.getchildren()
        for item in items:
            if (item.tag==u'element'):
                n = Node.Node()
                n.load(item)
                if item.attrib.get(u'selected') == config.VALUE_TRUE:
                    n.attribs[u'selected'] = config.VALUE_TRUE
                name = item.text
                if name is None:
                    name = u''
                n.set_name(name)
                self.add_child(n)



    def preload(self):
        return []
#        result = self.read_source(True) # error / true / false
#        if result is True or result is False:
#            return []
#        else:
#            return [result]



    def pretest(self, options):
        the_type = self.attribs.get(u'type')
        the_subtype = self.attribs.get(u'subtype')
        if not ( the_type == u'file' and ( the_subtype == u'mesh' or the_subtype == u'field' ) ):
            return []

        menus = self.get_top()
        if menus is None:
            return [u'Error: menus is None in pretest\n']
        window = menus.get_window()

        dim = None
        dimstr = self.attribs.get(u'dim')
        if dimstr is not None:
            try:
                dim = int(dimstr)
            except ValueError:
                return [u'Error: dim: \''+dimstr+'\' in pretest\n']

        filename = self.get_first_name()

        # does not test files with blank names, when options is not True
        if options is not True and ( not isinstance(filename,basestring) or filename == u'' ) :
            return []

# FIX: substituible por FileTrack2.py
        fm = window.filemanager

        tracker = None
        if the_subtype == u'mesh':
            tracker = fm.get_tracker_mesh_file(filename, dim)
        if the_subtype == u'field':
            tracker = fm.get_tracker_file(filename)

        if tracker is not None:
            changed = tracker.is_changed()
        else:
            changed = None

        if changed is None:
            return [u'Warning: ' + the_type + ' \'' + filename + u'\' does not exist']

        return []



    def get_nodes(self, which):
        result = []
        if which == u'leaf':
            result.append(self)
        elif which == u'leaf-file':
            if self.attribs.get(u'type') == u'file':
                result.append(self)
        elif which == u'leaf-file-mesh':
            if self.attribs.get(u'type') == u'file' and self.attribs.get(u'subtype') == u'mesh':
                result.append(self)
        elif which == u'leaf-file-field':
            if self.attribs.get(u'type') == u'file' and self.attribs.get(u'subtype') == u'field':
                result.append(self)
        return result

#busca nunha cadena (leaf type='float') rangos escritos con los distintos formatos
# formato1= ini:paso:fin
# formato2= ini:fin (paso=1)
# formato3= [ini:paso:fin]. por facer. Admite distintos signos inicial final como () [] ...
#devuelve [nuevacadena,numerodeelementos]
#si numerodeelementos == -1 no es un rango al estilo matlab
    def float_range(self,string):						#añadido
	string2=u' '								#añadido
	num = 0
        try:									#añadido
	    array_range = [float(s) for s in string.split(u':')] 		#añadido
            if len(array_range)==3:          					#añadido
                low = array_range[0]						#añadido
                step = array_range[1]						#añadido
                high = array_range[2]						#añadido
                while low<=high:						#añadido
                	string2 += str(low)+ u'  '				#añadido
                	low+=step						#añadido
			num = num + 1						#añadido
                print u'Range('+string+u')'					#añadido
            elif len(array_range)==2:						#añadido
                low = array_range[0]						#añadido
                step = 1							#añadido
                high = array_range[1]						#añadido
                while low<=high:						#añadido
                	string2 += str(low)+ u'  '				#añadido
                	low+=step						#añadido
			num = num + 1						#añadido
                print u'Range('+string+u')'              			#añadido
            elif len(array_range)==1:						#añadido
                string2 = string						#añadido
		num = -1							#añadido
        except:									#añadido
            string2 = string							#añadido
	    num = -1								#añadido
	return [string2,num]							#añadido


    def save_data(self, parent, parameters=None, transform=None):
        e = trees.ET.Element(u"leaf")
#        e.attrib = self.attribs.copy()
        e.attrib = Node.Node.filter_attribs(self.attribs)

#        for child in self.get_elements():
#            v = trees.ET.Element(u"element")
#            v.text = child
#            e.append(v)

        if e.attrib.get(u'type') == u'float':
            glue = u' '
        else:
            glue = u'\n'
        
        trfunction = None
        if transform is not None:
            if e.attrib.get(u'type') == u'file':
                trfunction = transform.add_get_file
            if e.attrib.get(u'type') == u'folder':
                trfunction = transform.add_get_dir

        # do not save passwords' content
        #if self.get_attribs().get(u'subtype')==u'password':
        #    elements = []
        #else:
        if parameters is None or self not in parameters:
#            if u'source' in self.get_attribs(): # leafs with source, have not selected elements missing
#                elements = self.get_elements() # x
#            else:
#                elements = self.get_elements_selected() # this would be ok for both cases (x and this)

            # ahora hay 'source' y 'mesh' en vez de antes 'source'
            if self.get_attribs().get(u'type') == 'charlist':
                elements = self.get_elements_selected()
            else:
                elements = self.get_elements()
        else:
            elements = [parameters[self]]

        e.attrib[u'totalnum'] = unicode(len(elements))

        v = trees.ET.Element(u"elements")
        text = u''
        i = 0
        for elem in elements:
            if trfunction is not None:
                text += trfunction(elem)
            else:
                if e.attrib.get(u'type') == u'float':
			# Admite rangos al estilo matlab en leaf-float
			float_range = self.float_range(elem)				#añadido
			# Si es un rango modificar totalnum
			if float_range[1] != -1:					#añadido
			    e.attrib[u'totalnum'] = unicode(float_range[1])		#añadido
			text += float_range[0]						#añadido
		else:
                	text += elem
                
#            if (i+1 != len(elements)):
#                text += glue
            text += glue
            i = i + 1
        v.text = text
        e.append(v)

        parent.append(e)



    def add_parameters(self, data):
        if self.get_attribs().get(config.AT_PARAM) == config.VALUE_TRUE:
            if self.has_source():
                elements = self.get_elements() # por que ? # leafs with source, have not selected elements missing
            else:
                elements = self.get_elements_selected()
            data[self] = elements



    def save_menu(self, parent):
        e = trees.ET.Element(self.get_tag())
        e.attrib = self.get_attribs().copy()
        
        # do not save passwords' content
        #if self.get_attribs().get(u'subtype') != u'password':
        
        for child in self.get_children():
            element = trees.ET.Element(child.get_tag())
            element.text = child.get_name()
            element.attrib = child.get_attribs().copy()
            if u'name' in element.attrib:
                del element.attrib[u'name']
            e.append(element)
                
        parent.append(e)



    def dump(self, index=0):
        print " " * index * 3, u"leaf: name:", self.get_name(), ";",
        for key in self.attribs:
            print key, ":", self.attribs[key], " ",
        print
        for child in self.get_elements():
            print " " * (index + 1) * 3, u"element:", child

