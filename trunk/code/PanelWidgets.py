#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import config
import Widget



PIXELS_MARGIN = 6



class PanelWidgets(wx.ScrolledWindow): #Panel):
    def __init__(self, parent, window):
#        wx.Panel.__init__(self, parent)
        wx.ScrolledWindow.__init__(self, parent)
        self.window = window

        self.box = wx.BoxSizer(wx.VERTICAL)
#        self.SetAutoLayout(True)
#        self.SetSizerAndFit(self.box)
        self.SetSizer(self.box)

        self.SetScrollRate(1,1)
	#contador de widgets en panelWidgets
	self.widgetcounter = 0					#añadido

        self.widgets = []

        self.Bind(Widget.EVT_STRUCT_CHANGE, self.event_struct_change)



    def display_set(self, struct):
#        print 'ds0'
        for a in range(len(self.widgets)-1,-1,-1):
            self.widgets[a].end()
#        print 'ds1'
        del self.widgets[:]
#        print 'ds2'
        self.box.Clear(True)

	self.widgetcounter = 0					#añadido

#        print 'ds3'
        self.Scroll(0,0)

#        print 'ds4'
        self.add_widget(struct)
#        print 'ds5'



    def display_add(self, struct, index):
        # destroys widgets with index >= 'index'
        for a in range(len(self.widgets)-1,index-1,-1):
            self.widgets[a].end()
            self.box.Detach(a)
            self.widgets[a].Destroy()
	    self.widgetcounter = self.widgetcounter - 1		#añadido
        del self.widgets[index:]

        self.add_widget(struct)

	# poner alguna condición para no evaluar constantemente
#	self.window.apply_config() #actualiza la configuracion en tiempo real

	#Scroll automatico para cada widget añadido.
	w,h = self.GetVirtualSizeTuple()			#añadido
	self.Scroll(0,h)					#añadido



    def add_widget(self, struct):
        if struct is not None:

            continuar = True
            
            # se hai que facer un menu reload, faino ou manda facelo !!!
            copyvalue = struct.get_attribs().get(config.AT_COPY)
            if copyvalue is not None:
                #print 'bbb'
                self.window.menu_copy_load(copyvalue)
                #print 'ccc'
                #self.display_set(None) # limpa widget que hai # CAUSA CRASH
                #print 'ddd'
                continuar = False
                # CRASH !!!
                #return # causaba crash? quitalo non o solucionou

            if continuar:
            
                if struct.plot_able():
                    ok = struct.plot_do(self.window.path_exe)
                    if ok is not True:
                        self.window.errormsg(ok)


                # este bloque y el anterior podrian ir debajo de la creación de widget ?
                # applies functions to all plots [parents and self]
                if struct.plot_has():
                    resultado = self.window.panelB.add_only_changed(struct)
                    #print 'resultado grafica', resultado
                struct.apply_to_parent_plots(self.window.panelB.update)
            
            if continuar:

                widget = Widget.Widget.build(struct, self, self.window, len(self.widgets))

                if widget is not None and widget.has_errors():
                    #print 'widget errors:', widget.get_errors()
                    widget.Destroy()
                    widget = None
                if widget is not None:
		    #Se fuerza a que panelWidgets consiga el foco en primer lugar
		    self.SetFocus()						#añadido
                    self.box.Add(widget , 0 , wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT , PIXELS_MARGIN)
                    self.widgets.append(widget)
		    self.widgetcounter = self.widgetcounter + 1			#añadido
		#Gestion del foco del primer widget en panelWidgets
		if self.widgetcounter == 1 and widget is not None:		#añadido
		    widget.SetFocus()					#añadido
                    
#        for a in self.widgets:
            #a.Fit()
            #a.Layout()

# estas dúas fanlle mal en windows xp.
#        self.box.Layout()
#        self.Layout()

#    scrolledwindow
        self.FitInside() # ok case



#    updates widget with struct contents
    def update_widget_struct(self, struct):
        yes = False
        for w in self.widgets:
            if w.get_struct() is struct:
                yes = True
                w.update_from_struct()
        if not yes:
            # parece que non fai falta notificar,
            # xa queda modificado o struct para a próxima vez que se mostre
            #print 'missing struct update'
            pass



#    updates widget with param contents
# chámase dende plot edges/faces/subsel interactive. recíbeo widget list
# poderíase eliminar e pasar todo a widget struct ?
    def update_widget_param(self, struct, param):
        yes = False
        for w in self.widgets:
            if w.get_struct() is struct:
                yes = True
                # reactivo: chama a actualizar plot
                w.update_from_param(param)

        # se non hai widget para o struct
        if not yes:
            print 'missing param update'
            has_source = struct.has_source()
            if has_source:
                elements = struct.get_elements_with_source(self.window.menus)
                if not isinstance(elements,list):
                    print 'get_elements_with_source PanelWidgets error: ' + unicode(elements)
                else:
                    names = []
                    for element in elements:
                        if element[1]:
                            if param != element[0]:
                                names.append(element[0])
                        else:
                            if param == element[0]:
                                names.append(element[0])
                    struct.set_elements(names)
            else:
                children = struct.get_children()
                for child in children:
                    if child.get_name() == param:
                        attribs = child.get_attribs()
                        if u"selected" in attribs:
                            del attribs[u"selected"]
                        else:
                            attribs[u"selected"] = u"true"

            struct.apply_to_all_plots(self.window.panelB.update)



    # chamado a traves de sinais, polos widgets
    def event_struct_change(self, event):
        #print 'pulsou', event.struct, event.index
        self.display_add(event.struct, event.index)
	self.window.apply_config()

