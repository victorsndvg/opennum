#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import wx.lib.newevent
import config
import dialogs



PIXELS_MARGIN = 4
TXT_VALUE = u'Value of '
TXT_CHOOSE = u'Choose '
TXT_CHOOSE_CUSTOMIZE = u'Choose/Add/Del '
TXT_BUTTON_ADD = u'Add'
TXT_BUTTON_DEL = u'Del'
TXT_BUTTON_DOTS = u'...'
TXT_END_LINE = u':'
TXT_MULTIPLE_SEL = u''
TXT_TOOLTIP_BUTTON_ADD = u'Adds an element with the given name'
TXT_TOOLTIP_BUTTON_DEL = u'Deletes selected element'

TXT_BUTTON_TABULAR = u'Show'
TXT_TOOLTIP_BUTTON_TABULAR = u'Open a window with tabular data for these items'
TXT_BUTTON_HELP = u'Help'
TXT_TOOLTIP_BUTTON_HELP = u'Open a window with help for this item'


EventStructChange, EVT_STRUCT_CHANGE = wx.lib.newevent.NewCommandEvent()
#EventStructChange, EVT_STRUCT_CHANGE = wx.lib.newevent.NewEvent()



class Widget(wx.Panel):


    def __init__(self, parent, window, struct, index):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.window = window
        self.menus = window.menus
        self.struct = struct
        self.index = index
        self.SetBackgroundColour(wx.Colour(200,200,200))
        #self.SetBackgroundColour(wx.Colour(12,37,119)) #R:12 G:37 B:119 Azul usc
        #self.SetBackgroundColour(wx.Colour(0,0,6*16+6)) #000066 Azul usc web
        self.errors = []



    def get_struct(self):
        return self.struct



    # actualiza o contido do widget a partir do struct
    def update_from_struct(self):
        pass


    # actualiza o contido do widget a partir dun parametro
    def update_from_param(self, param):
        pass



    def log(self, txt):
        txt2 = txt + u' ' + self.struct.get_path()
        self.window.add_text(txt2+u'\n')



    def end(self):
        self.save_mem()
        self.save_log()



    def save_mem(self):
        pass



    def save_log(self):
        pass



    def has_errors(self):
        return len(self.errors)>0



    def get_errors(self):
        return self.errors



    def check_error(self, result):
        if isinstance(result,list):
            return result
        else:
            error = unicode(result)
            self.errors.append(error)
            self.window.errormsg( error )
            return []


    
    def check_repeated(self, name, struct):
        for child in struct.get_children():
            if child.get_name() == name:
                self.window.errormsg(u'Error: name \'' + name + '\' already exists')
                return True
        return False



    @staticmethod
    def build(struct, parent, window, index):
        tag = struct.get_tag()
        attribs = struct.get_attribs()

        widget = None

        # in the past, there can be hidden elements like this
        #if attribs.get(u'hidden') == u'true':
        #    return widget
        
        # en Node.get_for_source_if_sel_if() hai unha clasificación parella

        if tag==u'struct':

	    #Permite mostrar una matriz desde fichero con WindowTabular
	    if attribs.get(config.AT_SHOW) == config.AT_MATRIX and \
		attribs.get(u'data') is not None:						#añadido
		import WindowTabular								#añadido
		table = WindowTabular.WindowTabular(window, window.tabular_onclose)		#añadido
		table.display(struct,True)							#añadido

            # there can be hidden elements
            if len(struct.get_children()) == 0 and \
                attribs.get(config.AT_SOURCE) is None and \
                attribs.get(config.AT_CUSTOMIZE) != config.VALUE_TRUE and \
                attribs.get(config.AT_SHOWVALUES) != config.VALUE_TRUE:
                return widget

            selection = attribs.get(u'selection')
            
            if (selection is None or selection == "none"):
                widget = WidgetList.WidgetList(0, parent, window, struct, index)
            elif (selection == "single"):
#                widget = WidgetChoice.WidgetChoice(parent, window, struct, index)
                widget = WidgetCombo.WidgetCombo(parent, window, struct, index)
            else:
                window.errormsg(u'Warning: XML menu: struct with selection present, but not one of [\'none\',\'single\']')

        elif tag==u'leaf':

            selection = attribs.get(u'selection')
            type_ = attribs.get(u'type')
            showfile = attribs.get(u'showfile')

            if (type_ == u'folder'):
                widget = WidgetFolderFile.WidgetFolderFile(WidgetFolderFile.FOLDER, parent, window, struct, index)
            elif (type_ == u'file'):
                widget = WidgetFolderFile.WidgetFolderFile(WidgetFolderFile.FILE, parent, window, struct, index)
            elif (type_ == u'float'):
                widget = WidgetEntry.WidgetEntry(0, parent, window, struct, index)
            elif (type_ == u'char'):
                widget = WidgetEntry.WidgetEntry(1, parent, window, struct, index)
            elif (type_ == u'complex'):
                widget = WidgetEntry.WidgetEntry(2, parent, window, struct, index)
            elif (type_ == u'charlist' and showfile is None):
                if (selection is None or selection == "single"):
#                    widget = WidgetChoice.WidgetChoice(parent, window, struct, index)
                    widget = WidgetCombo.WidgetCombo(parent, window, struct, index)
                elif (selection == "multiple"):
                    widget = WidgetList.WidgetList(2, parent, window, struct, index)
                else:
                    window.errormsg(u'Warning: XML menu: leaf of type charlist with selection present, but not one of [\'single\',\'multiple\']')
            elif (type_ == u'charlist' and showfile is not None):
                widget = WidgetText.WidgetText(parent, window, struct, index)
            else:
                window.errormsg(u'Warning: XML menu: leaf of unknown type: ' + unicode(type_))

        return widget

    #Gestion del foco del widget
    #Se sobreescribe en cada uno de los widgets
    def SetFocus(self):					#añadido
	pass						#añadido

#busca nunha cadena (leaf type='float') rangos escritos con los distintos formatos
# formato1= ini:paso:fin
# formato2= ini:fin (paso=1)
# formato3= [ini:paso:fin]. por facer. Admite distintos signos inicial final como () [] ...
#devuelve [nuevacadena,numerodeelementos]
#si numerodeelementos == -1 no es un rango al estilo matlab
    def float_range(self,string):						#añadido
	string2=u' '								#añadido
	num = 0									#añadido
        try:									#añadido
	    array_range = [float(s) for s in string.split(u':')] 		#añadido
            if len(array_range)==3:          					#añadido
		if (array_range[0]>array_range[2] and array_range[1]>0) or \
                   (array_range[2]>array_range[0] and array_range[1]<0):	#añadido
                    print u'ERROR: wrong step in Range('+string+u')'            #añadido		    
		    return[string2, num]					#añadido
		low = array_range[0]						#añadido
                step = array_range[1]						#añadido
                high = array_range[2]						#añadido
                while abs(high)-abs(low)>=0:					#añadido
                	string2 += str(low)+ u'  '				#añadido
                	low+=step						#añadido
			num = num + 1						#añadido
                print u'Range('+string+u')'					#añadido
            elif len(array_range)==2:						#añadido
		if (array_range[0]>array_range[1]):			 	#añadido
                    print u'ERROR: wrong step in Range('+string+u')'            #añadido		    
		    return[string2, num]					#añadido
                low = array_range[0]						#añadido
                step = 1							#añadido
                high = array_range[1]						#añadido
                while high-low>=0:						#añadido
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



import WidgetList
import WidgetChoice
import WidgetCombo
import WidgetEntry
import WidgetFolderFile
import WidgetText
