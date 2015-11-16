#!/usr/bin/env python
# -*- coding: utf-8 -*-



import trees
import Node
import Element



class SubMenu(Node.Node):



    def __init__(self):
        Node.Node.__init__(self)
	self.indexed = {}
        self.actions = []
        self.num = -1


#Ahora tambien funciona para el control de eventos desde Window
    def get_index(self, num=None):
	if num is None:					#añadido
	    return self.num
        if (num in self.indexed):			#añadido
            return self.indexed[num]			#añadido
        else:						#añadido
            return None					#añadido



    def set_index(self, num):
        self.num = num




    def load(self,submenu):
        Node.Node.load(self,submenu)

        items = submenu.getchildren()
        for item in items:
            if (item.tag==u'action'):
                
                # item é unha clase das de elementtree
                action = {}
                action[u'source'] = item.attrib.get(u'source') # unused
                action[u'name'] = item.get(u'name')
                action[u'title'] = item.get(u'title')		#añadido
                action[u'data'] = item.get(u'data')		#añadido
                action[u'reload'] = item.get(u'reload')		#añadido
                
                params = [] # one action: [param0, param1, ...]
                subitems = item.getchildren()
                for subitem in subitems:
                    if (subitem.tag==u'param'):

                        text = subitem.text
                        if text is None:
                            text = u''

                        param={'text':text, 'attrib':subitem.attrib.copy()}
                        
                        params.append(param)
                
                action[u'params'] = params
                
                self.actions.append(action)
            else:
                elem = Element.Element.build(item)
                if (elem is not None):
                    self.add_child(elem)
                else:
                    print 'Warning: unknown element'
# agora cargaos todos. antes so cargaba un:
#                if (len(self.children)==0): # only 1 'struct' child
#                    elem = Element.Element.build(item)
#                    if (elem is not None):
#                        self.add_child(elem)
#                    else:
#                        print 'Warning: unknown element'
#                else:
#                    print 'Warning: only one non-action child of submenu allowed'



    def get_actions(self):
        return self.actions



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

        for action in self.actions:
            a = trees.ET.Element(u'action')
            name = action.get('name')
            if name is not None:
                a.set(u'name',name)
####################################################################
# Atributos de custom exec. title:titulo de la ventana, data:comando
####################################################################
            title = action.get('title')			#añadido
            if title is not None:			#añadido
                a.set(u'title',title)			#añadido
            data = action.get('data')			#añadido
            if data is not None:			#añadido
                a.set(u'data',data)			#añadido
            reload_menu = action.get('reload')		#añadido
            if reload_menu is not None:			#añadido
                a.set(u'reload',reload_menu)		#añadido

            source = action.get('source') # unused
            if source is not None:
                a.set(u'source',source)
            for param in action.get('params'):
                p = trees.ET.Element(u'param')
                p.text = param.get('text')
                p.attrib = param.get('attrib').copy()
                a.append(p)
            e.append(a)
        for child in self.get_children():
            child.save_menu(e)
        parent.append(e)



    def dump(self, index=0):
        print " " * index * 3, u"submenu: name:", self.get_name(), u"#actions:", len(self.actions)
        for child in self.get_children():
            child.dump(index + 1)


    def reindex(self, n=None):
	if n is None:
	    num = 0
	else:
	    num = n
        self.indexed.clear()
        if True:
            for submenu in self.get_children():
                self.indexed[num] = submenu
                submenu.set_index(num)
                num = num + 1
                #Debemos reasignar un indice a los subsubmenus para poder identificar sus eventos
                #-------------------------------------------------------------------------------------------------------------------------------------
                for subsubmenu in submenu.get_children():                                                                   #añadido
                    if isinstance(subsubmenu, SubMenu):                                                           #añadido
                        self.indexed[num] = subsubmenu                                                                              #añadido
                        subsubmenu.set_index(num)                                                                                      #añadido
                        num = num + 1                                                                                                           #añadido
	return num
                    #-------------------------------------------------------------------------------------------------------------------------------------
