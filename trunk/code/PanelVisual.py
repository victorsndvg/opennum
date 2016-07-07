#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
# AUI
import wx.aui
import config
import os
import os.path
from v_vtk import GraphList2
from v_vtk import configPlot
import Menus
import logging


class PanelVisual(wx.Panel):



    def __init__(self, parent, window, path):
        wx.Panel.__init__(self, parent)
        self.window = window
        self.path = path
        self.book = None

        self.plotlist = GraphList2.GraphList2()

        self.titles = {}

#        self.SetBackgroundColour(wx.Colour(0xb4,0xb4,0xb4))
        self.SetBackgroundColour(wx.Colour(0xff,0xff,0xff))
        self.SetMinSize((50,50))

#        self.image = wx.Image(os.path.join(self.path,os.pardir,config.DIR_IMAGES,u'background.jpg'))
        if os.path.isfile(os.path.join(self.path,os.pardir,config.DIR_IMAGES,u'background.'+window.title+u'.png')):
            self.image = wx.Image(os.path.join(self.path,os.pardir,config.DIR_IMAGES,u'background.'+window.title+u'.png'))
        else:
            self.image = wx.Image(os.path.join(self.path,os.pardir,config.DIR_IMAGES,u'background.opennum.png'))
        if not self.image.IsOk(): # fallback
            self.image = wx.EmptyImage(1,1)
        self.bitmap = wx.BitmapFromImage(self.image)
        self.sb = wx.StaticBitmap(self,wx.ID_ANY,self.bitmap)

        self.box = wx.BoxSizer(wx.VERTICAL)

        self.box.AddStretchSpacer(1)
        self.box.Add(self.sb, 0, wx.ALIGN_CENTER_HORIZONTAL )
        self.box.AddStretchSpacer(1)

        self.SetSizer(self.box)

# DeletePage does not fire event
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.page_closed)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.page_close)



    def page_closed( self, event ):
        print 'page_closed'
#        print dir(event)
#        print 'pcd', event.drag_source, event.old_selection, event.selection, event.this, event.thisown
        # event.selection == page deleted ?
#        widget = self.book.GetPage(event.selection) # not that erased
#        print widget
#        self.plotlist.rem_view(widget)
        self.rem_if()



    def page_close( self, event ):
        # non chamado por DeletePage !!!
        print 'page_close'
#        print dir(event)
#        print 'pcg', event.drag_source, event.old_selection, event.selection, event.this, event.thisown
        # event.selection == page deleted ?
        widget = self.book.GetPage(event.selection)
#        print widget

#    to solve crash on close / open
        # non totalmente correcto: un item pode ter varias influencias en varios struct que son do mesmo plot
        self.to_close(widget)
        self.plotlist.rem_view(widget)
#        self.rem_if()



    def to_close(self, widget):
        widget.struct.clear_dependencies(True) # non 100% ok
        widget.to_close()
        


    @staticmethod
    def get_title( num, filename ):
        return '%d: %s' % (num,os.path.basename(filename))



    @staticmethod
    def get_title2( num ):
        return '%d' % num



    def rem_aux(self, force):
        if self.book is not None:
            if force:
# AUI
#                self.book.DeleteAllPages()
                while self.book.GetPageCount() > 0:
                    # necesario porque DeletePage no genera 'PAGE_CLOSE' ni 'PAGE_CLOSED'
                    widget = self.book.GetPage(0)
                    if widget is not None:
                        self.to_close(widget)
                    self.book.DeletePage(0)
                self.plotlist.rem_views()
            if self.book.GetPageCount() == 0:
                self.box.Clear(True)
                self.book = None
                self.box.AddStretchSpacer(1)
                self.box.Add(self.sb, 0, wx.ALIGN_CENTER_HORIZONTAL )
                self.sb.Show()
                self.box.AddStretchSpacer(1)
                self.box.Layout()
                # al cerrar todas las gráficas, se limpia el buffer de títulos para empezar de 0
                self.titles = {}


# close_plots
# removes book
    def rem(self):
        self.rem_aux(True)



    # olvida localizacion de plots, en cado de crearse otros iguales, se crearan nuevos
    # change directory
    def forget(self):
        self.plotlist.rem_views()



# removes book if empty
    def rem_if(self):
        self.rem_aux(False)


    def pre_add(self):
        if self.book is None:
            self.sb.Hide()
            self.box.Clear()
# AUI
# crash on Delete
#                self.book = wx.Notebook(self)
# not crash on Delete
            self.book = wx.aui.AuiNotebook(self,
            style = wx.aui.AUI_NB_TOP | wx.aui.AUI_NB_TAB_MOVE |
                    wx.aui.AUI_NB_SCROLL_BUTTONS | wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB )
            self.box.Add(self.book, 1, wx.EXPAND)
            self.box.Layout()



    def add_p(self):
        self.pre_add()

        b = wx.Button(self.book, wx.ID_ANY , "Pulsar")
        self.book.AddPage(b, 'Display', True)
        self.Layout()



############### clean !



# adds a plot always
    def add(self, struct):
        return self.internal(struct, 0)



# adds a plot if it does not exist, or does nothing if it exists
    def add_only(self, struct):
        return self.internal(struct, 1)



# adds a plot if it does not exist, or updates it if exists
    def add_update(self, struct):
        return self.internal(struct, 2)



# este tamen se chama, cando hai cambios no formulario [ parámetros para o gráfico, etc ]
# chamase desde os widgets, e agora desde panelWidgets
# updates a plot if it exists, or does nothing it if does not exist
    def update(self, struct):
        return self.internal(struct, 3)



# selects page of that plot
    def select(self, struct):
        return self.internal(struct, 4)



# hai dous usados, este e outro
# este chamase desde PanelWidgets
# non fai update [facíao, non o fai, e podese volver a facer se se controla na grafica os render innecesarios]
# xa fai update outra vez.
# adds a plot if the file changed or if the plot does not exist
    def add_only_changed(self, struct):
        return self.internal(struct, 5)



    # usado tamen
    # actualiza un plot se existe. non cambia a selección
    # struct un dos titulares do grafico [influencia de item]
    # item foi o actualizado
    def update_from_dependency(self, struct, item):
        return self.internal(struct, 6, item)



# mode: ...
    def internal(self, struct, mode, item=None):
#        print 'PanelVisual: internal:', struct.get_tag(), struct.get_name(), mode
    
# rethink: add (plot=!="true") != update (plot ="true")
        
        data = struct.get_data5(True) # true: calculates pointers

        if isinstance(data, basestring):
            self.window.errormsg(u'Error creating/updating plot: ' + data)
            return False

        # re-chequea se é unha dependencia actualmente
        if mode == 6 and (item is None or not struct.is_dependency(item)):
            return False
        
        filenames = tuple(data.get('filenames'))
        fieldname = data.get('fieldname') # may be None here and inside plot get a value
        # fieldtype may be changed in Plot...
        if fieldname is not None:
            domain = data.get('fielddomain')
            if domain is not None:
                # hacemos esto para los ficheros que tienen campos cell y point con el mismo nombre
                # se representen correctamente en distintas pestañas
                fieldname = domain + ':' + fieldname
            else:
                fieldname = ':' + fieldname

        temp = struct.get_attribs().get(config.PLOT) # cambiado de PLOT_TYPE a PLOT
	#Si la representacion viene del boton show en lugar del atributo plot
	if temp is None:							#añadido
	    typename = u'2d_graph'						#añadido
	else:									#añadido
            typename = configPlot.get_alias(temp)				#añadido
        extra = u'¬' # para abrir, en distintas graficas, structs con igual ficheiro pero distinta configuracion de tempo/frecuencia...
        if not data.get('interpolation'):
            extra += unicode(data.get('interpolation'))
        extra += u'¬'
        if struct.get_attribs().get(config.PLOT_EVOLUTION) is not None:
            extra += struct.get_attribs().get(config.PLOT_EVOLUTION)
        extra += u'¬'

        if data.get('formula_is') is True: # para as fórmulas, non comparte visualizacións entre distintos nodos
            view = self.plotlist.get_from_node(struct)
        else:
            # si es el mismo struct, devuelve siempre uno si hay
            # si no, devuelve uno que coindida en el resto de los datos, si hay
            # si no, None
            view = self.plotlist.get(struct, filenames, fieldname, typename, extra)
            # non se modifica se cambia o numero de ficheiros seleccionados para o plot

        if view is None:
            was = None
        else:
            was = False
	

#        print 'plotlist was', was is not None, filenames, fieldname, typename, extra, struct
        
        filemanager = self.window.filemanager

        add = False
        update = False
        select = False
        if mode == 0:
            add = True
        if mode == 1 and was is None:
            add = True
        if mode == 2 and was is None:
            add = True
        if mode == 2 and was is not None:
            update = True
        if mode == 3 and was is not None:
            update = True
        if mode == 4 and was is not None:
            select = True
        if mode == 5 and was is None:
            add = True
        if mode == 5 and was is not None:
            update = True
        if mode == 5 and was is not None and add is not True:
            # parece ser necesario para que actualice el plot si hay cambio de struct asociado
            update = True
        if mode == 6 and was is not None:
            update = True

        add_ok = False

        if add:
            #self.window.add_text(u'Adding visualization start ...\n') #code prior version 0.0.1
            logging.debug(u'Adding visualization start ...')
            tracker = struct.get_tracker5( filemanager, data )
            if isinstance(tracker, basestring):
                self.window.errormsg(u'Error creating plot: ' + tracker)
            elif tracker is None:
                self.window.errormsg(u'Error creating plot: Undefined plot files')
	    # si añadimos un nuevo tracker vacio
            elif tracker.is_void:		#añadido
                self.window.errormsg(u'Error creating plot: No mesh or chart has been selected') #añadido
            else:
                if tracker.is_changed() is not None:
                    if tracker.update() is not None:
                        ok = self.add(filenames, fieldname, typename, extra, struct, tracker, data)
                    else: # tracker.update() is None
                        self.window.errormsg(u'Error converting mesh to vtk. Not creating plot')
                else: # tracker.is_changed() is Non
#		    print filenames, fieldname, typename, extra, struct, tracker, data
                    self.window.errormsg(u'Unable to access file(s) to create plot')

            #self.window.add_text(u'Adding visualization end ...\n') #code prior version 0.0.1
            logging.debug(u'Adding visualization end ...')
            
        if update:
        
            print u'Updating visualization start ...'

            tracker = struct.get_tracker5( filemanager, data )

            if isinstance(tracker, basestring):
                self.window.errormsg(u'Error updating plot: ' + tracker)
            elif tracker is None:
                self.window.errormsg(u'Error updating plot: Undefined plot files')
            else:
                # reformar: unha soa funcion update_tracker_data fará todo
                if tracker.is_changed() is not None:
                    if tracker.update() is not None:
                        if view.updated_tracker(tracker):
                            if view.updatable_tracker():
                                if tracker is not view.get_tracker_():
                                    view.set_tracker_(tracker)
				# Si es nodepvd se permite por defecto que tenga mallas adicionales
				# En caso de que no las tenga se compruba en plot.check_additional. deprecated
				# Todos los trackers tienen la posibilidad de tener mallas adicionales.
				    if True:#tracker.is_nodepvd:							#añadido
			            	view.set_additional(True)							#añadido
				# Si el tracker esta vacio no se actualiza nada
				    elif tracker.is_void:								#añadido
					return										#añadido

                                view.set_data(data)
                                    
                                res = view.update_tracker()
                                if isinstance(res, basestring):
                                    self.window.errormsg(u'Error updating plot with new data files: ' + res)
                                
                            else:
                                add = True
                                ok = self.add(filenames, fieldname, typename, extra, struct, tracker, data)
                        else:
                            pass

                    else: # tracker.update() is None
                        self.window.errormsg(u'Error converting mesh to vtk. Not updating plot')
                else: # tracker.is_changed() is None
                    self.window.errormsg(u'Unable to access file(s) to update plot')


            if not add:

                struct.add_dependencies(data.get('dependencies'), True)

                # self.window.process_pending() # innecesario ?
                view.update_top(struct) # render

                # considerar eliminar os Render de update_top
                view.do_render() # pode estar duplicado

            print u'Updating visualization end ...'

        if was is not None and not add and mode != 6:
        
            print u'Selecting visualization start ...'
            next = self.book.GetPageIndex(view)
            previous = self.book.GetSelection()
            if next != previous:
                self.book.SetSelection(next)
            print u'Selecting visualization end ...'

        return ( add and add_ok ) or update or select



    def add(self, filenames, fieldname, typename, extra, struct, tracker, data):
        self.window.process_pending() # necesario ?
        self.pre_add() # self.book
        # reports error inside
        # trick to avoid passing 3 args

        from v_vtk import Plot as Plot #### arriba manda tempo !!!
                        
        newview = Plot.Plot.build( typename ,
                    [self.book, self.window, struct, tracker, data] )

        if newview is not None and newview.has_error():
            self.to_close(newview)
            newview.Destroy()
            newview = None
            # error in else:
        if newview is not None:
            #num = self.plotlist.num
            #self.book.AddPage(newview, PanelVisual.get_title2(num), True)
            title = newview.get_options_extra(data).get('title')
            if title is None:
                title = newview.get_options().get('title')
            if title is None:
                title = typename

            # numerar títulos repetidos
            oldnum = self.titles.get(title)
            if oldnum is None:
                title2 = title
                self.titles[title] = 2
            elif oldnum < 2:
                title2 = title
                self.titles[title] = oldnum + 1
            else:
                title2 = title + ' (' + unicode(oldnum) + ')'
                self.titles[title] = oldnum + 1

            self.book.AddPage(newview, title2, True)
            newview.plot_top(struct) # o antes para asegurar
            add_ok = newview.is_done() and not newview.has_error() # reports error
            if add_ok:
                self.plotlist.add(struct, newview, filenames, fieldname, typename, extra)

                struct.clear_dependencies(True)
                struct.add_dependencies(data.get('dependencies'), True)

                return True
            else:
                # failed: now we delete erroneous Plot

                # numerar títulos repetidos
                self.titles[title] = oldnum
                
                index = self.book.GetPageCount()
                if index > 0:
                    self.to_close(newview)
                    self.book.DeletePage(index-1)
                self.window.errormsg('Error completing plot')
                self.rem_if() # undo self.pre_add()
                return False
        else: # newview is None
            self.window.errormsg('Error creating plot of type: '+typename)
            self.rem_if() # undo self.pre_add()
            return False

        return False
