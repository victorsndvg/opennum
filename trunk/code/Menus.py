#!/usr/bin/env python
# -*- coding: utf-8 -*-



import shutil
import trees
import NoDeep
import Node
import Menu
import SubMenu     #añadido subsubmenus
import Leaf
import config



class Menus(Node.Node):



    def __init__(self, window):
        Node.Node.__init__(self)
        self.tag = None
        self.indexed = {} # num: submenu
        self.window = NoDeep.NoDeep(window)



    def get_window(self):
        return self.window.geti()



    def is_loaded(self):
        return self.get_tag() is not None



    def to_save(self):
        return self.get_tag() is not None and self.get_attribs().get(u'save') != u'false'



# load menu
    def load_file(self, filename=None):
	print filename
        if filename is None:
            filename = config.FILE_MENULOCAL
        try:
            tree = trees.ET.parse(filename)
        except Exception , x:
	    if filename == config.FILE_MENULOCAL:
        	self.get_window().errormsg(u'Error loading menu file: \'' + filename + '\': ' + repr(x))
            return False

        # this way, we do not discard data in case of error
        Node.Node.__init__(self)
        self.indexed = {}

        root = tree.getroot()

        Node.Node.load(self, root)

        items = root.getchildren()

        num = 0
        for item in items:
            if item.tag == u'menu':
                menu = Menu.Menu()
                menu.load(item)
                self.add_child(menu)
                # build a dictionary with indexes
                for submenu in menu.get_children():
                    self.indexed[num] = submenu
                    submenu.set_index(num)
                    num = num + 1
                    #Debemos asignar un indice a los subsubmenus para poder identificar sus eventos
                    #-------------------------------------------------------------------------------------------------------------------------------------
                    for subsubmenu in submenu.get_children():                                                                 #añadido
                        if isinstance(subsubmenu, SubMenu.SubMenu):                                                           #añadido
                            self.indexed[num] = subsubmenu                                                                    #añadido
                            subsubmenu.set_index(num)                                                                         #añadido
                            num = num + 1                                                                                     #añadido
                    #-------------------------------------------------------------------------------------------------------------------------------------
        return True



#calculates unique numbers for submenu calls. podese reescribir o anterior
#modificado para permitir recibir un indice de partida
    def reindex(self, n=None):										
	if n is None:
	    num = 0
	else:
	    num = n
        self.indexed.clear()
        for menu in self.get_children():
            for submenu in menu.get_children():
                self.indexed[num] = submenu
                submenu.set_index(num)
                num = num + 1
                #Debemos reasignar un indice a los subsubmenus para poder identificar sus eventos
                #---------------------------------------------------------------------------------------------------------------------
                for subsubmenu in submenu.get_children():                                                                 #añadido
                    if isinstance(subsubmenu, SubMenu.SubMenu):                                                           #añadido
                        self.indexed[num] = subsubmenu                                                                    #añadido
                        subsubmenu.set_index(num)                                                                         #añadido
                        num = num + 1                                                                                     #añadido
	return num
                    #-------------------------------------------------------------------------------------------------------------------------------------



# save data
    def save_data(self, filename=None, parameters=None, extras=[], force=False, transform=None, transformextra=None):
        # temporal
        if not self.is_loaded():
            return
            
        e = trees.ET.Element(u'data')
        tree = trees.ET.ElementTree(e)

        root = tree.getroot()
        for extra in extras: # para permitir nome de ficheiro ou outras cousas
            extra.save_data(root, parameters, transformextra)
        for menu in self.get_children():
            if force or menu.get_attribs().get(config.AT_SAVETHIS) != config.VALUE_FALSE:
                menu.save_data(root, parameters, transform)

        Menus.indent_data(root)

        if filename is None:
            filename = self.get_datafile()

        if filename is not None:
            # cp file file.bak
            print 'save_data', filename
            tree.write(filename,"iso-8859-15") # utf-8



    def get_parameters(self):
        data = {}
        for child in self.get_children():
            child.add_parameters(data)
        return data



    def prepare(self):
        for child in self.get_children():
            child.prepare(self)



    def preload(self):
        errors = []
        for child in self.get_children():
            r = child.preload()
            errors.extend(r)
        return errors



# options: True: test all files ; False: test only files != ''
    def pretest(self, options=False):
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



    def save_menu(self, filename=None, force=False):
        if not self.is_loaded() or not self.to_save(): # not to save
            return

        # for what ?
#        self.prepare() ###

        e = trees.ET.Element(self.get_tag())
        tree = trees.ET.ElementTree(e)

        root = tree.getroot()
        root.attrib = self.get_attribs().copy()
        for child in self.get_children():
            if force or child.get_attribs().get(config.AT_SAVETHIS) != config.VALUE_FALSE:
                child.save_menu(root)

        Menus.indent_menu(root)

        if filename is None:
            filename = config.FILE_MENULOCAL

        #filename = filename + u'._.xml'
        # cp file file.bak
        print 'save_menu', filename
        try:
            shutil.copy2( filename , filename+'~' )
        except IOError:
            pass
        tree.write(filename, "utf-8")



    def get_index(self, num):
        if (num in self.indexed):
            return self.indexed[num]
        else:
            return None



    def get_datafile(self):
        #return self.get_attribs().get(u'datafile')
        return config.FILE_MENULOCALSOLVER



    def dump1(self, obj=None, index=0):
        obj2 = obj
        if (obj is None):
            obj2 = self
            print " " * index * 2, u"menus: datafile:", obj2.get_datafile()
        else:
            print " " * index * 2, obj2.get_name()
        for child in obj2.get_children():
            self.dump(child, index + 1)



    def dump(self, index=0):
        print " " * index * 3, u"menus: datafile:", self.get_datafile()
        for child in self.get_children():
            child.dump(index + 1)



    @staticmethod
    def indent_data(element, level=0, last=False):
        children = element.getchildren()

        l = level
        if (last):
            l = l - 1
        if (l<0):
            l = 0
        element.tail = u'\n' + (u'\t' * l)

        string1 = u''
        string2 = u''
        string3 = u''
        if (element.tag == u'elements'):
            string1 = u'\n' + (u'\t' * level)
        if (True):
            if len(children)==0:
                string2 = u'\n' + (u'\t' * level)
                string3 = u''
            else:
                string2 = u'\n' + (u'\t' * (level+1))
                string3 = u'\t'
        if (isinstance(element.text,basestring)):
            if (len(element.text)==0):
                element.text = string2
            else:
                text = element.text.replace( u'\n' , u'\n' + (u'\t' * level) )
                if '\n' in element.text:
                    element.text = string1 + text + string3
                else:
                    element.text = string1 + text + string2
        else:
            element.text = string2

        i = 0
        for child in children:
            is_last = i + 1 == len(children)
            Menus.indent_data(child, level+1, is_last)
            i = i + 1



    @staticmethod
    def indent_menu(element, level=0, last=False):
        children = element.getchildren()

        l = level
        if (last):
            l = l - 1
        if (l<0):
            l = 0
        element.tail = u'\n' + (u'\t' * l)

        string1 = u''
        string2 = u''
        if (True):
            if len(children)==0:
                string2 = u'\n' + (u'\t' * level)
            else:
                string2 = u'\n' + (u'\t' * (level+1))

        tags = set()
        tags.add(u'menus')
        tags.add(u'menu')
        tags.add(u'submenu')
        tags.add(u'action')
        tags.add(u'struct')
        tags.add(u'leaf')
        #param
        #element

        if element.tag in tags:
            if (isinstance(element.text,basestring)):
                if (len(element.text)==0):
                    element.text = string2
                else:
                    element.text = string1 + text + string2
            else:
                element.text = string2

        i = 0
        for child in children:
            is_last = i + 1 == len(children)
            Menus.indent_menu(child, level+1, is_last)
            i = i + 1

