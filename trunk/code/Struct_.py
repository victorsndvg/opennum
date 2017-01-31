#!/usr/bin/env python
# -*- coding: utf-8 -*-



import copy
import trees
import Node
import Element



class Struct(Element.Element):



    def __init__(self):
        Element.Element.__init__(self)
        self.defaults = []



    # merges two Struct
    # now replaces children
    def combine(self, struct):
        Element.Element.combine(self, struct)
        self.defaults = struct.defaults[:]
        #self.defaults.extend(struct.defaults)



    def get_defaults(self):
        return self.defaults



    def create_defaults(self, name):
        result = []
        # Looks for defaults (with name)
        for default in self.defaults:
            if default.get_attribs().get(u'name')==name:
                default_copy = copy.deepcopy(default) # important
                default_copy.set_children_parents()
                attribs = default_copy.get_attribs()
                if attribs.get(u"default")==u"true":
                    del attribs[u"default"]
                default_copy.set_name(name)
                result.append(default_copy)
        # If no defaults (with name), looks for defaults (without name)
        if len(result) == 0:
            for default in self.defaults:
                if default.get_attribs().get(u'name') is None:
                    default_copy = copy.deepcopy(default) # important
                    default_copy.set_children_parents()
                    attribs = default_copy.get_attribs()
                    if attribs.get(u"default")==u"true":
                        del attribs[u"default"]
                    default_copy.set_name(name)
                    result.append(default_copy)
        # If no defaults (with or without name), creates a generic struct
        if len(result) == 0:
            default_copy = Struct()
            default_copy.tag = u'struct'
            default_copy.set_name(name)
            default_copy.set_children_parents()
            result.append(default_copy)
        return result



    def set_elements(self, elements):
        elementsset = set(elements)
        for child in self.children:
            attribs = child.get_attribs()
            if child.get_name() in elementsset:
                attribs[u"selected"] = u'true'
            else:
                if u"selected" in attribs:
                    del attribs[u"selected"]



    # sets elements but remain unselected
    # here unselects every one... is it logical?
    def set_elements_nosel(self, elements):
        for child in self.children:
            if u"selected" in attribs:
                del attribs[u"selected"]



    def set_elements_with_source(self, menus, elements, sources=None): # ok +. children with duplicates. does not remove duplicates
        if sources is None:
            sources = self.get_remote_source(menus)
        self.clear_elements_not_in_source(menus, sources)
        self.create_elements_from_source(menus, sources)
        if (isinstance(sources, list)):
            elementsset = set(elements)
            for child in self.children:
                attribs = child.get_attribs()
                if child.get_name() in elementsset:
                    attribs[u"selected"] = u'true'
                else:
                    if u"selected" in attribs:
                        del attribs[u"selected"]
            return True
        else:
            return sources



    def get_elements_with_source(self, menus, sources=None): # ok. result must match children [WidgetList.subselect]
        if sources is None:
            sources = self.get_remote_source(menus)
        self.clear_elements_not_in_source(menus, sources)
        self.create_elements_from_source(menus, sources)
        if (isinstance(sources, list)):
            result = []
            for child in self.children:
                name = child.get_name()
                if (child.get_attribs().get(u'selected')==u'true'):
                    result.append((name,True))
                else:
                    result.append((name,False))
            return result
        else:
            return sources



    def create_elements_from_source(self, menus, sources=None): # ok+. does not remove duplicates. does not add duplicates
        if sources is None:
            sources = self.get_remote_source(menus)
        if not isinstance(sources,list):
            return sources
        else:
            names = set()
            for child in self.children:
                name = child.get_name()
                names.add(name)
            for source in sources:
                if source not in names:
                    defaults = self.create_defaults(source)
                    for default in defaults:
                        self.add_child(default)
            return True



    def load(self,struct):
        Element.Element.load(self, struct)

        items = struct.getchildren()
        for item in items:
            element = Element.Element.build(item)
            if (element is not None):
                attribs = element.get_attribs()
                if (attribs.get(u"default")==u"true"):
                    self.defaults.append(element)
                else:
                    self.add_child(element)
            else:
                print 'Warning: unknown element'



    def save_data(self, parent, parameters=None, transform=None):
        e = trees.ET.Element(self.get_tag())
        selection_single = self.attribs.get(u'selection') == u'single'
#        e.attrib = self.attribs.copy()
        e.attrib = Node.Node.filter_attribs(self.attribs)
        for child in self.get_children():
            if not selection_single or child.get_attribs().get(u'selected')==u'true':
                child.save_data(e, parameters, transform)
        parent.append(e)



    def add_parameters(self, data):
        selection_single = self.attribs.get(u'selection') == u'single'
        for child in self.get_children():
            if not selection_single or child.get_attribs().get(u'selected')==u'true':
                child.add_parameters(data)



    def save_menu(self, parent):
        e = trees.ET.Element(self.get_tag())
        e.attrib = self.get_attribs().copy()
        for child in self.get_defaults():
            child.save_menu(e)
        for child in self.get_children():
            child.save_menu(e)
        parent.append(e)



    def dump(self, index=0):
        print " " * index * 3, u"struct: name:", self.get_name(), ";",
        for key in self.attribs:
            print key, ":", self.attribs[key], " ",
        print
        for child in self.get_children():
            child.dump(index + 1)

