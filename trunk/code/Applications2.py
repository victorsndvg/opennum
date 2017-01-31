#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os
import Menu
import SubMenu
import Struct_
import config



# temporal
def name_split(name):
    out1 = u''
    out2 = name
    i = name.find(u'-')
    if i >= 0:
        out1 = name[0:i]
        out2 = name[i+1:]
    return (out1,out2)

    
    
def compare_names(x , y):
    xx = x[0]
    yy = y[0]
    if xx < yy:
        return -1
    if xx > yy:
        return 1
    return 0

    
    
def get_dirnames(dir):
    try:
        # lista de ficheiros 
        names1 = os.listdir(dir)

        # filtra os non directorios
        # debera flitrar os ocultos tamÃ©n [. ...]
        names2 = []
        for name in names1:
            # se non é oculto (.) e e un directorio, gárdao
            if (not (len(name) > 0 and name[0]==u'.')) and os.path.isdir(os.path.join(dir, name)):
                names2.append(name)

    except OSError:
        return False

    names3 = []

    for name in names2:
        tuple1 = name_split(name)
        list2 = [tuple1[0],tuple1[1],name]
        names3.append(list2)

    # ordena o resultado
    names3.sort(compare_names)

    return names3 # "abc" - "def" - "abc-def"



class Applications2():
    
    def __init__(self):
        self.dirname = None
        self.tree = []

    # retorna True se leu ben e False se leu mal
    def read(self, dirname):
        self.dirname = dirname
        self.tree = []
        dir1 = get_dirnames(self.dirname)
        if dir1 is False:
            return False
        for dir in dir1:
            dirnext = get_dirnames(os.path.join(self.dirname,dir[2]))
            if dirnext is False:
                return False
            dir.append(dirnext)    # pos 3
        # 0: before - ; 1: after - ; 2: complete dirname ; 4: children
        self.tree = dir1
        return True


    def get(self):
        return self.tree


    def build_menu(self):
        menu = Menu.Menu()
        menu.tag = u'menu'
        menu.get_attribs()[config.AT_SAVETHIS] = config.VALUE_FALSE
        menu.set_name(u'Application')
        for app in self.tree:
            submenu = SubMenu.SubMenu()
            submenu.tag = u'submenu'
            submenu.set_name(app[1])
            
# submenu conten só un elemento non-action
            #Mostrar las aplicaciones en structs
            struct = Struct_.Struct()
            struct.tag = u'struct'
            struct.set_name('Example to Load')
            struct.set_title(app[1] + ', select case:')
#            struct.get_attribs()[config.AT_TITLE] = u''
            
            for example in app[3]:
                #Mostrar las aplicaciones en structs
                str = Struct_.Struct()
                str.tag = u'struct'
                str.set_name(example[1])
                str.get_attribs()[config.AT_COPY] = os.path.join(app[2], example[2])
                struct.add_child(str)
                #Comentado.Mostrar las aplicaciones en submenus
                #str = SubMenu.SubMenu()
                #str.tag = u'submenu'
                #str.set_name(example[1])
                #str.get_attribs()[config.AT_COPY] = os.path.join(app[2], example[2])
                #submenu.add_child(str)

            submenu.add_child(struct) #Mostrar las aplicaciones en structs
            menu.add_child(submenu)
        
#        menu.dump()
        
        return menu

#################################################
# Nuevos menus Application y Sample data
    def has_app(self,title=None):

        for app in self.tree:
            if title is not None and title == app[1]:
                return True
        return False

#################################################
# Nuevos menus Application y Sample data
    def build_sampledata(self,title=None):

        submenu = SubMenu.SubMenu()

        submenu.tag = u'menu'
        submenu.get_attribs()[config.AT_SAVETHIS] = config.VALUE_FALSE
        submenu.set_name(u'Application')
        for app in self.tree:
            submenu2 = SubMenu.SubMenu()
            submenu2.tag = u'submenu'
            submenu2.set_name(app[1])
            
            if submenu2.get_name().lower() == u'separator' and app[1] != app[2] and app[0] != u'':
                submenu2.get_attribs()['separator'] = config.VALUE_TRUE
                submenu.add_child(submenu2)
                continue

            for example in app[3]:
                submenu3 = SubMenu.SubMenu()
                submenu3.tag = u'submenu'
                submenu3.set_name(example[1])
                if submenu3.get_name().lower() == u'separator' and example[1] != example[2] and example[0] != u'':
                    submenu3.get_attribs()['separator'] = config.VALUE_TRUE
                    submenu2.add_child(submenu3)
                    continue
                submenu3.get_attribs()[config.AT_COPY] = os.path.join(app[2], example[2])
                submenu2.add_child(submenu3)

            if title is not None and title == app[1]:
                return submenu2

            submenu.add_child(submenu2)
        
        return submenu

#################################################
# Nuevos menus Application y Sample data
    def build_application(self):
        submenu = SubMenu.SubMenu()
        submenu.tag = u'menu'
        submenu.get_attribs()[config.AT_SAVETHIS] = config.VALUE_FALSE
        submenu.set_name(u'Application')
        for app in self.tree:
            submenu2 = SubMenu.SubMenu()
            submenu2.tag = u'submenu'
            submenu2.set_name(app[1])

            if submenu2.get_name().lower() == u'separator' and app[1] != app[2] and app[0] != u'':
                submenu2.get_attribs()['separator'] = config.VALUE_TRUE
                submenu.add_child(submenu2)
                continue

            examples = app[3]
            if len(examples)>=1:
                submenu2.get_attribs()[config.AT_COPY] = os.path.join(app[2], examples[0][2])
                submenu.add_child(submenu2)
        
        return submenu


#################################################
# Nuevos menus Application y Sample data
    def build_help(self):
        submenu = SubMenu.SubMenu()
        submenu.tag = u'menu'
        submenu.get_attribs()[config.AT_SAVETHIS] = config.VALUE_FALSE
        submenu.get_attribs()[config.AT_HELP] = config.VALUE_TRUE
        submenu.set_name(u'Help')
        for app in self.tree:
            submenu2 = SubMenu.SubMenu()
            submenu2.tag = u'submenu'
            submenu2.set_name(app[1])

            if submenu2.get_name().lower() == u'separator' and app[1] != app[2] and app[0] != u'':
                submenu2.get_attribs()['separator'] = config.VALUE_TRUE
            else:
                submenu2.get_attribs()[config.AT_SOURCE] = app[2]
                submenu2.get_attribs()[config.AT_HELP] = config.VALUE_TRUE
            submenu.add_child(submenu2)
    
        
        return submenu
