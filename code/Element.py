#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os.path
import trees
import config
import Node
import SubMenu #añadido subsubmenu
from v_vtk import configPlot



class Element(Node.Node):

    def __init__(self):
        Node.Node.__init__(self)



    # merges two Element
    # now replaces children
    def combine(self, element):
        Node.Node.combine(self, element)



    def plot_do(self, path_exe):
        plot_type = self.get_attribs().get(config.PLOT) # cambiado de PLOT_TYPE a PLOT
        if plot_type is not None:
            alias = configPlot.get_alias(plot_type)
            needs = configPlot.get_needs_plot(alias)
            if needs is True:
                filename = alias + u'.plot.xml'
                print 'loading', filename
                path = os.path.join(path_exe, os.pardir, u'plots', filename)
                if isinstance(self, Leaf.Leaf):
                    newstruct = Leaf.Leaf()
                else:
                    newstruct = Struct_.Struct()
                result = newstruct.load_file(path)
                if result:
                    self.combine(newstruct)
                    self.get_attribs()[config.PLOTTED] = config.VALUE_TRUE
                    self.set_children_parents()
                    return True
                else:
                    return u'Error: can not load plot XML configuration file: \'' + filename + '\''
            elif needs is False:
                self.get_attribs()[config.PLOTTED] = config.VALUE_TRUE
                return True
            elif needs is None:
                return u'Error: unknown plot type'
                # 'it is undefined whether the plot needs a configuration XML file'
            else:
                return u'Error: unknown return value of get_needs_plot'
        else:
            return u'Error: unknown plot type'



    def load(self,item):
        Node.Node.load(self,item)


# load file
    def load_file(self, filename):
        try:
            tree = trees.ET.parse(filename)
        except Exception , x:
            print repr(x)
            return False

        root = tree.getroot()
        self.load(root)

        return True



    def save_data(self, parent, parameters=None, transform=None):
        e = trees.ET.Element(self.get_tag())
#        e.attrib = self.attribs.copy()
        e.attrib = Node.Node.filter_attribs(self.attribs)
        for child in self.get_children():
            child.save_data(e, parameters, transform)
        parent.append(e)



    def prepare(self, menus):
        sources = self.get_remote_source(menus)
        self.clear_elements_not_in_source(menus, sources)
        self.create_elements_from_source(menus, sources)
        if not isinstance(self,Leaf.Leaf):
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



    @staticmethod
    def build(item):
        if (item.tag==u'leaf'):
            e = Leaf.Leaf()
            e.load(item)
            return e
        if (item.tag==u'struct'):
            e = Struct_.Struct()
            e.load(item)
            return e
            
        #---------------------------------------------------
        #Detecta el tag submenu (de 2ndo nivel) y lo añade a la jerarquia
        if (item.tag==u'submenu'):
            e = SubMenu.SubMenu()
            e.load(item)
            return e
        #*-------------------------------------------------
        
        return None



    def dump(self, index=0):
        print " " * index * 3, u"element(",self.tag,"): name:", self.get_name(), ";",
        for key in self.attribs:
            print key, ":", self.attribs[key], " ",
        print
        for child in self.get_children():
            child.dump(index + 1)



#### #element ~ child / child with (name,selected)
    def get_elements_selected(self): # +ok. leafs with source, have not selected elements missing
        elements = []
        for element in self.children:
            if element.attribs.get(u'selected') == u'true':
                elements.append(element.get_name())
        return elements

    def get_elements(self): # +ok. leafs with source, have not selected elements missing
        elements = []
        for element in self.children:
            elements.append(element.get_name())
        return elements

    def set_elements(self, elements):
        pass

    # sets elements but remain unselected
    def set_elements_nosel(self, elements):
        pass

    def set_elements_with_source(self, menus, elements):
        pass

    def get_elements_with_source(self, menus):
        pass

    def clear_elements_not_in_source(self, menus, sources=None): # ok+
        if sources is None:
            sources = self.get_remote_source(menus)
        if not isinstance(sources,list):
            return sources
        sourcesset = set(sources)
        integer = 0
        for integer in range(len(self.children)-1,-1,-1):
            child = self.children[integer]
            name = child.get_name()
            if name not in sourcesset:
                self.del_child(integer)
        return True

    def create_elements_from_source(self, menus, sources=None):
        pass



import Struct_
import Leaf

