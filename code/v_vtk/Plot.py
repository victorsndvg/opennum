#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import vtk
import vtk.wx.wxVTKRenderWindow
import vtk.wx.wxVTKRenderWindowInteractor
import sys # fs_encoding
import config
import unicodedata
import dialogs
import Menus
import auxSave
import MainBar
import ScaleBar
import TimeBar
import ScalarRange
import TimeManager2
import Player
import PlayerConst
import configPlot
import os.path # para basename ( para nombre de campo )
import math # sqrt
import sourceVTK2
import WindowSearch
import os # para name
import logging


# antes (5.2) imprimia en una ventana, ahora (5.4) imprime en la terminal

# => crash ? parece que si

if os.name == 'nt': # temporal
    vtk.vtkObject.GlobalWarningDisplayOff() # disables warning window



background_color = (0.75, 0.75, 0.75) # background
edges_color = (1.0, 0.6, 1.0) # edges / wireframe : scalar field(s), vector field
mesh_color = (0.0, 1.0, 1.0) # mesh : plot_sub_sel / references: unsel / cut,clip !field
mesh2_color = (0, 0, 1) # mesh2 : plot_faces / references: sel
mesh3_color = (1.0, 0.6, 1.0) # mesh3: references: mesh
unselected_color = (0.3, 0.3, 0.3) # unselected edge references / references: several_unsel
unassigned_color = (0, 0, 0, 1) # PlotMaterials.py face not assigned to material
label_color = (1.0, 1.0, 1.0) # color of labels
legend_color = (0, 0, 0) # legend
outline_color = (0, 0, 0) # outline
axes_color = (0, 0, 0) # scale on axes
arrow_color = (0, 0, 1) # flechas en PlotVectorField
probe_line_color = (1, 1, 0) # probe line
points_color = (1, 0, 0) # points for labels

#edges_color = (0.2, 0.2, 0.2) # edges / wireframe : scalar field
#mesh_color = (0.2, 0.2, 0.2) # mesh : plot_sub_sel
#label_color = (0, 0, 1) # color of labels
#background_color = (0.8, 0.8, 0.8) # background
#legend_color = (0, 0, 0) # legend


# para marxe de legend e appname (0..1)
legendmargin = 0.01

class Plot(wx.Panel):
#class Plot(wx.Window):
#class Plot(wx.Frame):

    def __init__(self, parents):
        wx.Panel.__init__(self, parents[0]) # parents[0] is the book
#        wx.Window.__init__(self, parents[0]) # parents[0] is the book
#        wx.Frame.__init__(self, parents[0]) # parents[0] is the book



        #print 'plotc', self.GetBackgroundColour()
        # se non poño esto, pinta o fondo dela e dos subpaneles gris, non do color por defecto.
        self.SetBackgroundColour(self.GetBackgroundColour())
	# for scale bar
        self.sb_hue = (0.66667,0.0) # blue->red
	self.sv_saturation = (1.0,1.0)
	self.sv_values = (1.0,1.0)
        #print 'plotc', self.GetBackgroundColour()
        

        # significa: | existe timemanager <=> not has_src
        self.has_src = False
        # significa: src e un vtkAssignAttribute
        self.has_assign = False
        self.has_error_ = False

        # para PlotReferences: segrega mallas adicionales (self.src2) de mallas principales (self.src)
        self.additional = False
	self.wireMadd = None
	self.wireAadd = None
	self.additionalAlist = []	#lista de mallas adicionales
        # datos para comprobar se unha fonte ten un campo
        self.fielddata = None
	self.sbA = None

        self.window = parents[1] # to call some methods on it
        self.struct = parents[2] # to use it in constructor. FIX
        self.tracker = parents[3] # now created outside # not None
        self.data1 = parents[4] # now created outside # can be none
        self.revision = -1 # for tracking file modifications
        self.revision_src = -1 # for tracking file modifications
        self.timemanager = None # for temporal series of data

        if self.tracker is None:
            self.has_error_ = True
            return
        
        self.panel_widgets = self.window.panelA
        
        self.widget = None
        self.widget2 = None
	self.window2image = None
	self.moviewriter = None
	self.window2image2 = None
        self.imageappend = None
	self.movie_saving = False
        
        if self.get_options().get(u'split') is True: # excepcional
            
            self.splitter = wx.SplitterWindow(self, -1)
            self.widget = vtk.wx.wxVTKRenderWindowInteractor.wxVTKRenderWindowInteractor( self.splitter , wx.ID_ANY )
            self.widget.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
            self.widget2 = vtk.wx.wxVTKRenderWindowInteractor.wxVTKRenderWindowInteractor( self.splitter , wx.ID_ANY )
            self.widget2.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
            
        elif self.get_options().get(u'interactor') is True:
        
            self.widget = vtk.wx.wxVTKRenderWindowInteractor.wxVTKRenderWindowInteractor( self , wx.ID_ANY )
            self.widget.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
            
        else:
        
            self.widget = vtk.wx.wxVTKRenderWindow.wxVTKRenderWindow( self , wx.ID_ANY )

# test axes
#        self.widget.Enable(1)

        self.rens = []
        ren = vtk.vtkRenderer() # or each plot
        ren.SetBackground(background_color)
        self.rens.append(ren)
        self.add_rens()

        self.boxv = wx.BoxSizer(wx.VERTICAL)

        self.plotbar = MainBar.MainBar(self, self) # before buttons

        self.boxv.Add(self.plotbar, 0, wx.EXPAND)

        self.mesh_names_actors = [] # mesh names actors
        self.mesh_names_pending = [] # pending mesh names

        self.save_as_1()

        self.add_center_1()
        
        self.add_mesh_names_1()
        
        legendon = True
        self.add_legend_1(legendon)
        self.add_legend_2(legendon)

        self.add_appname_2()

        if self.get_options().get(u'split') is True: # excepcional
            self.splitter.SplitVertically(self.widget, self.widget2)
            self.splitter.SetMinimumPaneSize(50)
            self.boxv.Add(self.splitter, 1, wx.EXPAND)
        else:
            self.boxv.Add(self.widget, 1, wx.EXPAND)

        self.option_scale = None # None non aparece, false aparece descativada, true aparece activada
        self.option_scale_abs_rel = None # None non aparece, 0 absoluta 1 relativa
        self.scalarrange = ScalarRange.ScalarRange([self.range_update2, self])
        self.scalebar = ScaleBar.ScaleBar(self, self)
        self.boxv.Add(self.scalebar, 0, wx.EXPAND)
        self.boxv.Hide(self.scalebar, True)

        self.timebar = TimeBar.TimeBar(self, self)
        self.boxv.Add(self.timebar, 0, wx.EXPAND)
        self.boxv.Hide(self.timebar, True)
        
        self.timebar_time_updated_saved = None
        self.timebar_time_updated = 0
        self.timer = None
        self.player = None
        self.is_playing = False

        self.labels_b_value = None

        self.SetSizer(self.boxv)
        
        self.done = False
        
        self.outline = False
        
        #self.SetAutoLayout(True)
        

        cams = []



    def is_done(self):
        return self.done



    def has_error(self):
        return self.has_error_



# <data1 tracker src>


    def call_data1(self, struct):
        if self.data1 is None:
            self.data1 = struct.get_data5() # False: se non se calculan fóra os pointers, non se calculan aquí
        if isinstance(self.data1,basestring):
            self.window.errormsg(u'Error creating plot: '+self.data1)
            return False
        self.update_legend(self.data1)
        self.fieldname = self.data1.get('fieldname') # importante que sea None si non hay field ! modificado: agora pode ser ''
        #self.dim = self.data1.get('dim')
        #self.has_field = self.fieldname is not None and self.fieldname != '' # modificado en call_get_scalars
        self.has_field = self.fieldname is not None
        
        fn = self.data1.get('fieldname')
        fd = self.data1.get('fielddomain')
        ft = self.data1.get('fieldtype')
        
        if fn is not None and ( fd == 'cell' or fd == 'point' ) and ( ft == 'scalar' or ft == 'vector' ):
            self.fielddata = {}
            self.fielddata['name'] = fn
            self.fielddata['domain'] = fd
            #if ft == 'scalar':
            #    self.fielddata['components'] = 1
            #elif ft == 'vector':
            #    self.fielddata['components'] = 3
            #else:
            self.set_additional(True) # ???

#        print 'data1:', self.data1
        return True



    def call_tracker(self, struct):
        result = self.tracker.update()
        self.filename = self.tracker.get_vtkfile()
        self.revision = self.tracker.get_revision()
#        print u'Plot.tracker: vtk_filename', self.filename, u'revision', self.revision, u'result', result
        if result is None:
            self.window.errormsg(u'Error converting mesh to vtk. Not creating plot')
            return False
        # actualiza la dimension a la obtenida del fichero (si no estaba especificada en el menu)
        self.call_dim()
        return True



    # returh whether updated (or would update)
    def call_dim(self, update=True):
        if self.data1.get('dim') is None:
            dim = self.tracker.get_dim()
            if dim is not None:
                self.data1['dim'] = dim
                self.update_legend_data()
                return True
        return False



    def call_config(self, struct):
        result = self.call_data1(struct)
        if not result:
            return result
        result = self.call_tracker(struct)
        return result



    def set_additional(self, value):
        self.additional = value



    def call_src(self):


        #AttributeTypes: SCALARS, VECTORS, NORMALS, TCOORDS, TENSORS
        #Attribute locations: POINT_DATA, CELL_DATA
        fn = self.data1.get('fieldname')
        fd = self.data1.get('fielddomain')
        ft = self.data1.get('fieldtype')
        if fd == 'point':
            pc = 0
        elif fd == 'cell':
            pc = 1
        elif fd is None:
            pc = None
        else:
            self.window.errormsg('Incorrect field domain: '+unicode(fd))
            return False

        if ft == 'scalar':
            sv = 0
        elif ft == 'vector':
            sv = 1
        elif ft is None:
            sv = None
        else:
            self.window.errormsg('Incorrect field type: '+unicode(ft))
            return False
            
        # non pode ser usado con None -> con additional e pvd deu excepción antes de poñer self.set_additional(False)
        self.src2 = None # para .pvd no se inicializa

        if self.tracker.has_series():
            self.timemanager = TimeManager2.TimeManager2()
            self.timemanager.set_interpolation(self.data1.get('interpolation'))
            # workaround: porque vtkInterpolateDataSetAttributes solo interpola atributos activos
            # en algun caso vtkAssignAttribute duplicado
            if pc is not None and sv is not None and fn is not None:
                self.timemanager.set_attributes(fn, sv, pc)
	    #se considera que todos los trackers pueden tener mallas adicionales
#	    self.set_additional(False)
#	    self.has_src = False
	    #si trackernodefiles.is_nodepvd tiene series temporales y mallas adicionales. deprecated
#	    if self.tracker.is_nodepvd:								#añadido
#		self.has_src = True								#añadido
#            	self.set_additional(True)							#añadido
#	    else:										#añadido
#		self.has_src = False
#            	self.set_additional(False) # se non dá excepción ao intentar usar self.src2=None en add_additional_2
        else:
            self.has_src = True

        if pc is not None and sv is not None and fn is not None:

            self.src = vtk.vtkAssignAttribute()
            self.src.Assign(fn, sv, pc) # fn.encode('utf-8') ?
            if self.additional: # PlotReferences and all others
                self.src2a = vtk.vtkAssignAttribute()
                self.src2a.Assign(fn, sv, pc) # fn.encode('utf-8') ?
            self.has_assign = True
        else:
            self.has_assign = False
        
        # aqui tratamos por separado o timemanager porque hai que inicialo (tempo 0).
        if self.timemanager is not None:
            res = self.update_tracker_pvd()
            if isinstance(res,basestring):
                self.window.errormsg(res)
                return False
            res = self.timemanager.recalculate(0) # posicion inicial (tempo 0)
            if isinstance(res,basestring):
                self.window.errormsg(res)
                return False
            res = self.update_source_pvd()
            if isinstance(res,basestring):
                self.window.errormsg(res)
                return False

        # para os pvds ok: self.has_src é false
	if self.has_src and self.timemanager is not None:
	    res = self.update_tracker_source(self.timemanager.indexA)
	else:
            res = self.update_tracker_source()
        if isinstance(res,basestring):
            self.window.errormsg(res)
            return False

        if self.timemanager is not None:
            range = self.timemanager.get_range()
            self.timebar.set_start_time(range[0])
            self.timebar.set_end_time(range[1])
            self.update_time_data_legend()
            self.timebar.put_status(self.get_status())
  
#        print 'self.src.output.range:', self.src.GetOutput().GetScalarRange()

#        print 'Plot sourceVTK2.prints'
#        sourceVTK2.prints(self.src)

        
        return True



    # after call_data1()
    # before call_src()
    def update_field_type(self, fieldtype, force=False): # scalar vector
        if force or self.data1.get('fieldtype') is None:
            self.data1['fieldtype'] = fieldtype
            return True
        return False
    def update_field_domain(self, fielddomain, force=False): # point cell
        if force or self.data1.get('fielddomain') is None:
            self.data1['fielddomain'] = fielddomain
            return True
        return False
    def update_field_name(self, fieldname, force=False):
        if force or self.data1.get('fieldname') is None:
            self.data1['fieldname'] = fieldname
            return True
        return False
    def update_legend_data(self):
        self.update_legend(self.data1)


    def update_time_data_legend(self):
        if self.timemanager is None:
            return
        files = self.timemanager.get_filenames()
        if files is not None:
            self.data1['filenames'] = files

        t = self.timemanager.get_time()
        self.data1['time'] = t
        self.update_time_field(t)
        
        self.update_legend(self.data1)



    def update_time_field(self, time):
        #mirar none ou Null
        self.timebar.set_time(time)
        self.timebar_time_updated += 1



    # responde a la pregunta: se puede actualizar a partir del tracker o de uno nuevo ?
    # si retorna False, no se actualiza el grafico, se crea nuevo ante cualquier cambio
    def updatable_tracker(self):
        return True



    # retorna si el tracker suministrado es nuevo o tiene modificaciones
    def updated_tracker(self, tracker):

        if self.tracker is not tracker:
            return True

        # en get_src se llama a update

        if self.has_src:
	    if tracker.is_nodepvd:					#añadido
		tracker.get_src(None,self.timemanager.indexA)		#añadido
	    else:							#añadido
                tracker.get_src() #				
            if self.revision != tracker.get_revision():
                return True
            if self.revision_src != tracker.get_revision_src():
                return True
        else:
            tracker.update()
            if self.revision != tracker.get_revision():
                return True

        return False



    def update_tracker(self):
        if self.timemanager is not None:
            res = self.update_tracker_pvd()
            if isinstance(res,basestring):
                return res
            res = self.update_source_pvd()
            self.timebar.put_status(self.get_status())
            return res
        else:
            return self.update_tracker_source()



    def update_tracker_pvd(self):
        if self.timemanager is None:
            return True
	#Se captura el error en la actualizacion de trackerpvd vacio o con mallas adicionales	
	try:									#añadido
	    res = self.timemanager.set_tracker(self.tracker)
	except:									#añadido
	    res = True								#añadido

        if isinstance(res,basestring):
            return 'Error initializing for .pvd: '+res

        return True



    def update_source_pvd(self):
        if self.timemanager is None:
            return 'Error: .pvd needed'
            
        ret = self.time_update0({'new':True, 'changed':True}, False)

        return ret
    


    def update_tracker_source(self, index=None): # que fai para os pvds: nada: self.has_src é false

        mnames = []

	#Con trackerformula2 se actualizan las mallas adicionales en add_additional_2
        if not self.has_src:
	    return True
        		
        if self.additional:								#añadido
            src = self.tracker.get_src_group_f(1, self.fielddata, mnames,index)		#añadido
            if src is None or isinstance(src, basestring):				#añadido
                return 'Error obtaining VTK source object (main): ' + unicode(src)	#añadido
            src2 = self.tracker.get_src_group_f(2, self.fielddata, mnames,index) # pode ser None: non ten
            if src2 is None or isinstance(src2, basestring):				#añadido
                return 'Error obtaining VTK source object (additional): ' + unicode(src2)#añadido
        else:
            src = self.tracker.get_src(mnames)
            if src is None or isinstance(src, basestring):
                return 'Error obtaining VTK source object: ' + unicode(src)

        # race condition (hai 2 lecturas de src en additional)
        revision_src = self.tracker.get_revision_src()

        self.clear_mesh_names()
        self.queue_mesh_names(mnames)
        self.test_add_mesh_names()

        if self.revision_src != revision_src:

            # no necesario para primera vez # <- si necesario para inicializar self.src2
            if self.has_assign:
                # self.src.RemoveAllInputs() # non soluciona o problema de conservar Bounds
                self.src.SetInputConnection(src.GetOutputPort())
                self.src.Update()
                if self.additional:
                    self.src2 = self.src2a
                    self.src2.SetInputConnection(src2.GetOutputPort())
                    self.src2.Update()
                    self.src_update0({'new':True, 'changed':True})
                else:
                    self.src_update0({'new':False, 'changed':True})
            else:
                self.src = src
                self.src.Update()
                if self.additional:
                    self.src2 = src2
                    self.src2.Update()
                self.src_update0({'new':True, 'changed':True})
                
            self.revision_src = revision_src

        #print 'plot', src.GetOutput().GetBounds(), '-', self.src.GetOutput().GetBounds()
        
        return True

    

# </data1 tracker src>



    def do_render(self):
    
        self.widget.Render()
        if self.get_options().get(u'split') is True:
            self.widget2.Render()



# time

    def time_update0(self, changes, render=True):
        if self.timemanager is None:
            return 'Error: .pvd needed'

        self.update_time_data_legend()
        
        if changes.get('new'):

            mnames = []

            src = self.timemanager.get_src(mnames) # una vez que se obtiene src, no vuelve a ser None

            if src is None:
                return 'Error obtaining source for .pvd'

            if self.has_assign:
		if self.tracker.is_nodepvd:								#añadido
		    if self.src2 is None:								#añadido
			self.src2 = vtk.vtkAssignAttribute()						#añadido
		    src = self.tracker.get_src_group_f(1, self.fielddata, mnames,self.timemanager.indexA)#añadido
	            if src is None or isinstance(src, basestring):					#añadido
        	        return 'Error obtaining VTK source object (main): ' + unicode(src)		#añadido
		    self.src.SetInputConnection(src.GetOutputPort())					#añadido
		    self.src.Update()									#añadido
		    src2 = self.tracker.get_src_group_f(2, self.fielddata, mnames,self.timemanager.indexA)#añadido
	            if src is None or isinstance(src, basestring):					#añadido
        	        return 'Error obtaining VTK source object (additional): ' + unicode(src)	#añadido
		    self.src2.SetInputConnection(src2.GetOutputPort())					#añadido
		    self.src2.Update()									#añadido
		else:											#añadido
                    self.src.SetInputConnection(src.GetOutputPort())					#añadido
		    self.src2 = None
                changes['new'] = False						
            else:
                self.src = src
                
            self.clear_mesh_names()
            self.queue_mesh_names(mnames)
            self.test_add_mesh_names()

        self.src.Update() # para despois getscalarrange dar valores correctos

        ret = self.src_update0(changes)
        
        if render:
	    if self.window2image is not None and self.moviewriter is not None and self.movie_saving:	#añadido
       		if self.get_options().get(u'split'):
		    self.window2image.Modified()								#añadido
		    self.window2image2.Modified()								#añadido
		    self.imageappend.Update()								#añadido			
		else:
		    self.window2image.Modified()								#añadido
		self.moviewriter.Write()								#añadido
            self.do_render() # legend needs this
        
        return True



    def src_update0(self, changes):
        if not self.done:
            return False

        if len(changes) > 0:
#            print 'Plot sourceVTK2.prints'
#            sourceVTK2.prints(self.src)
#            print 'changing plot self.src', changes
            ret = self.src_update1(changes)
            self.check_additional(changes)
            return ret
            


    # new => changed
    def src_update1(self, changes): # redefined in subclasses
        return False



    # helper function
    def src_update_clicker(self, clicker, src, changes):
        if clicker is not None:
            if changes.get('new'):
                clicker.change_src(src) # no imprescindible ?
            elif changes.get('changed'):
                clicker.update_src() # no imprescindible

#/time



# <range>
    def range_update2(self, range):
        #print 'updating range to', range, '...', #code prior version 0.0.1
        logging.debug('updating range to'+str(range)+'...')
        #if not self.is_done(): # mal porque pode ser chamado ben desde o plot()
        #    return
        if range is None:
            #print #code prior version 0.0.1
            return

        self.scalebar.update_range(range)

        self.range_update3(range)

        #print 'updated' #code prior version 0.0.1
        logging.debug('updated')



    def range_update3(self, range): # to overwrite in subclasses
        pass
# </range>



# dictionary with options to overwrite in subclasses do receive subclasses' options
    def get_options(self):
        return {}


# dictionary with options to overwrite in subclasses do receive subclasses' options
# mainly for title
    def get_options_extra(self, data):
        return {}



    def set_iren(self, force=False):
        last = self.widget.GetRenderWindow().GetInteractor()
        if last is None or force:
            self.iren = vtk.vtkRenderWindowInteractor()
            self.widget.GetRenderWindow().SetInteractor(self.iren)
            #self.iren.SetRenderWindow(self.widget.GetRenderWindow())
            #print 'interactor changing' #, last, '->', self.iren #code prior version 0.0.1
            logging.debug('interactor changing')
        else:
            self.iren = last
            #print 'interactor keeping' #, self.iren  #code prior version 0.0.1
            logging.debug('interactor keeping')



#### OPTIONS / BUTTONS / LOGIC


#<mesh names>
    def clear_mesh_names(self):
        for actor in self.mesh_names_actors:
            self.rens[0].RemoveActor( actor )
        del self.mesh_names_actors[:]
        del self.mesh_names_pending[:]



    def queue_mesh_names(self, data):
        self.mesh_names_pending += data



    def test_add_mesh_names(self):
        if self.button_mesh_names.GetValue():
            self.add_mesh_names(self.mesh_names_pending)
            del self.mesh_names_pending[:]



    def add_mesh_names(self, data):
        # self.clear_mesh_names( )
        for d in data:
            if d[0] is None:
                continue
            else:
                coords = d[0]
            if d[1] is None:
                text = '?'
            else:
                text = d[1]
                
            mapper = vtk.vtkTextMapper( )
            mapper.SetInput( text )
            mapper.GetTextProperty().SetColor((1.0,0.9,0.9))
            mapper.GetTextProperty().SetFontSize(18)
            mapper.GetTextProperty().SetJustificationToCentered()
            mapper.GetTextProperty().SetVerticalJustificationToCentered()
            mapper.GetTextProperty().BoldOn()
            mapper.GetTextProperty().ShadowOn()
            actor = vtk.vtkActor2D()
            actor.SetMapper( mapper )
        
            coord = actor.GetPositionCoordinate()
            coord.SetCoordinateSystemToWorld()
            coord.SetValue( coords )

            self.mesh_names_actors.append( actor )
            self.rens[0].AddActor( actor )



    def add_mesh_names_1(self):
        self.button_mesh_names = wx.ToggleButton(self.plotbar, wx.ID_ANY, 'Names', style=wx.BU_EXACTFIT)
        self.button_mesh_names.SetValue(False)
        self.button_mesh_names.Bind(wx.EVT_TOGGLEBUTTON, self.handler_mesh_names)
        self.plotbar.add(self.button_mesh_names)



    def hide_mesh_names_1(self):
        self.button_mesh_names.Hide()



    def handler_mesh_names(self, event):
        self.test_add_mesh_names()
        changes = False
        for actor in self.mesh_names_actors:
            actor.SetVisibility(self.button_mesh_names.GetValue())
            changes = True
        if changes:
            self.do_render()
#</mesh names>


# <additional>
    def add_additional_2(self):
        if self.additional:
	    for actor in self.additionalAlist:					#añadido
		self.rens[0].RemoveActor(actor)					#añadido
	    self.additionalAlist= []
	    try:
		if self.src2 is None and not self.has_src:
		# Mallas adicionales con trackerformula2
		    self.additionaltracker = self.tracker.get_additional_trackers(self.data1['filesmesh2'])		#añadido
		    # Si existen mallas adicionales se añaden a la lista de actores y al render
		    if len(self.additionaltracker) > 0:
			for tr in self.additionaltracker:
			    self.wireMadd = vtk.vtkDataSetMapper()
			    self.wireMadd.SetInputConnection(tr.get_src().GetOutputPort())
			    self.wireMadd.ScalarVisibilityOff()
			    self.wireAadd = vtk.vtkActor()
			    self.wireAadd.SetMapper(self.wireMadd)
			    self.wireAadd.GetProperty().SetRepresentationToWireframe()
			    self.wireAadd.GetProperty().SetColor(mesh3_color)
			    self.rens[0].AddActor(self.wireAadd) # additional meshes
			    self.additionalAlist.append(self.wireAadd)
		else:
		# Mallas adicionales en otros casos
		# Si existen mallas adicionales se añaden a la lista de actores y al render
		    self.wireMadd = vtk.vtkDataSetMapper()
		    self.wireMadd.SetInputConnection(self.src2.GetOutputPort())
		    self.wireMadd.ScalarVisibilityOff()
		    self.wireAadd = vtk.vtkActor()
		    self.wireAadd.SetMapper(self.wireMadd)
		    self.wireAadd.GetProperty().SetRepresentationToWireframe()
		    self.wireAadd.GetProperty().SetColor(mesh3_color)
		    self.rens[0].AddActor(self.wireAadd) # additional meshes
		    self.additionalAlist.append(self.wireAadd)
	    except:
		pass
#		self.set_additional(False)


    def check_additional(self, changes):						#modificado
	self.additionaltracker = []							#añadido
        if self.additional:# and changes.get('new'): # así ?				#modificado
	    if changes.get('new') and self.wireMadd is not None:			#añadido
	        self.wireMadd.SetInputConnection(self.src2.GetOutputPort())		#modificado
	    else:									#añadido
		# Actualización de plots
		self.add_additional_2()							#añadido
		# En el caso de no haber mallas adicionales se borra la lista de sus actores del render
		if self.src2 is None:							#añadido
		    for actor in self.additionalAlist:					#añadido
			self.rens[0].RemoveActor(actor)					#añadido
		    self.additionalAlist = []						#añadido
                    self.wireMadd = None						#añadido
		    self.wireAadd = None						#añadido
		    # Si es un trackerformula se actualizan las mallas adicionales
		    if not self.has_src and len(self.additionaltracker) > 0:		#añadido
			self.add_additional_2()						#añadido

	else: #Si no hay que añadir mallas adicionales, elimina las obsoletas		#añadido
	    if self.wireAadd is not None:						#añadido
		for actor in self.additionalAlist:					#añadido
		    self.rens[0].RemoveActor(actor)					#añadido
		self.additionalAlist = []						#añadido
                self.wireMadd = None							#añadido
		self.wireAadd = None							#añadido
		self.src2 = None							#añadido

# </additional>


# <time>
    def add_time_1(self):
        name = self.data1.get('evolution_upper')
        self.timebutton = wx.ToggleButton(self.plotbar, wx.ID_ANY, name + ' bar', style=wx.BU_EXACTFIT)
        self.timebutton.Bind(wx.EVT_TOGGLEBUTTON, self.handler_time)
        self.plotbar.add(self.timebutton)



    def handler_time(self, event):
        if self.timebar is None:
            self.timebutton.SetValue(False)
            return
        if self.timebutton.GetValue():
            self.boxv.Show(self.timebar, True)
            self.boxv.Layout()
        else:
            self.boxv.Hide(self.timebar, True)
            self.boxv.Layout()
# </time>



# <scale>
    def add_scale_1(self):
        self.scale_button = wx.ToggleButton(self.plotbar, wx.ID_ANY, u'Scale bar', style=wx.BU_EXACTFIT)
        self.scale_button.Bind(wx.EVT_TOGGLEBUTTON, self.handler_scale)
        self.plotbar.add(self.scale_button)



    def handler_scale(self, event):
        if self.scalebar is None:
            self.scale_button.SetValue(False)
            return
        if self.scale_button.GetValue():
            self.boxv.Show(self.scalebar, True)
            self.boxv.Layout()
        else:
            self.boxv.Hide(self.scalebar, True)
            self.boxv.Layout()
# <scale>



# <scalarbar>
    def add_scalarbar_1(self, visible=True):
        self.option_scale = visible
        # None: non aparece barra, False: non aparece escala, True: aparece escala



    # corrects scale [blue->red]
    def add_scalarbar_2(self, look):
        # reverse rainbow [red->blue] -> [blue->red]
        look.SetHueRange(self.sb_hue)
	look.SetSaturationRange(self.sv_saturation)
	look.SetValueRange(self.sv_values)
        
        self.sbA = vtk.vtkScalarBarActor()
        self.sbA.SetLookupTable(look)
        self.sbA.SetNumberOfLabels(7)
        if vtk.vtkVersion.GetVTKMajorVersion() == 6:
            self.sbA.SetTitle(' ')
        else:
            self.sbA.SetTitle('')
        #print 'sbA.Pos1', self.sbA.GetPositionCoordinate()
        #print 'sbA.Pos2', self.sbA.GetPosition2Coordinate()
        #print 'sbA.GetWidth', self.sbA.GetWidth()
        self.sbA.SetPosition(0.86, 0.1)
        self.sbA.SetPosition2(0.12, 0.8) # relative # default: (0.17, 0.8)
        self.sbA.SetVisibility(self.option_scale)
        self.rens[0].AddActor(self.sbA)



    def scalarbar_change(self, value):
        if not self.done:
            return
        self.sbA.SetVisibility(value)
        self.do_render()
# </scalarbar>

    def scalarbar_change_color(self, hue=None, sat=None, val=None, style=None):
        if not self.done:
            return
	look = self.sbA.GetLookupTable()
	if style is not None:
	    if style == u'Linear':
		look.SetRampToLinear()
	    elif style == u'Curve':
		look.SetRampToSCurve()
	    elif style == u'Sqrt':
		look.SetRampToSQRT()
	if hue is not None:
	    self.sb_hue = hue
	    look.SetHueRange(self.sb_hue)
	if sat is not None:
	    self.sb_saturation = sat
	    look.SetSaturationRange(self.sb_saturation)
	if val is not None:
	    self.sb_values = val
	    look.SetValueRange(self.sb_values)
	look.Build()
	self.do_render()



# # # # scale absolute / relative (to visible region) # -> scalebar

    # public
    def add_abs_rel_1(self, selection=0):
        if selection == 0:
            self.option_scale_abs_rel = 0
        elif selection == 1:
            self.option_scale_abs_rel = 1
        else:
            self.option_scale_abs_rel = None

        self.abs_rel_pos = self.option_scale_abs_rel



    def set_abs_rel_pos(self, pos):
        self.abs_rel_pos = pos



    # public
    def add_abs_rel_2(self,src,cutter):
        self.abs_rel_data = [src,cutter]



    # public
    def change_abs_rel(self, src):
        self.abs_rel_data[0] = src



    # public
    # for changes in type of range
    def adjust_abs_rel(self):
        if self.abs_rel_pos == 0:
            self.scalarrange.local_set(self.abs_rel_data[0].GetOutput().GetScalarRange())
        elif self.abs_rel_pos == 1:
            self.abs_rel_data[1].Update()
            self.scalarrange.local_set(self.abs_rel_data[1].GetOutput().GetScalarRange())



    # public
    # for changes in range
    def update_abs_rel(self):
        if self.abs_rel_pos == 0:
            pass # do not update because src is always the same
        elif self.abs_rel_pos == 1:
            self.abs_rel_data[1].Update()
            self.scalarrange.local_set(self.abs_rel_data[1].GetOutput().GetScalarRange())
        # render called outside if needed
        
# # # # /scale absolute / relative (to visible region)



### <outline>
    def add_outline_1(self):
        self.button_outline = wx.ToggleButton(self.plotbar, wx.ID_ANY, 'Outline', style=wx.BU_EXACTFIT)
        self.button_outline.SetValue(False) #modificado: por defecto boton outline off
        self.button_outline.Bind(wx.EVT_TOGGLEBUTTON, self.handler_outline)
        self.plotbar.add(self.button_outline)

        
        
    def add_outline_2(self, src):

        self.outF = vtk.vtkOutlineFilter()
        self.outF.SetInputConnection(src.GetOutputPort())
        
        self.outM = vtk.vtkPolyDataMapper()
        self.outM.SetInputConnection(self.outF.GetOutputPort())
        
        self.outA = vtk.vtkActor()
        self.outA.SetMapper(self.outM)
        self.outA.GetProperty().SetColor(outline_color)
        
        self.rens[0].AddActor(self.outA)

        self.cubeA = vtk.vtkCubeAxesActor()
        self.cubeA.SetBounds(src.GetOutput().GetBounds())
        self.cubeA.SetCamera(self.rens[0].GetActiveCamera())
        self.cubeA.SetFlyModeToOuterEdges()
        self.cubeA.GetProperty().SetColor(axes_color)

#void     SetFlyModeToOuterEdges ()
#void     SetFlyModeToClosestTriad ()
#void     SetFlyModeToFurthestTriad ()
#void     SetFlyModeToStaticTriad ()
#void     SetFlyModeToStaticEdges ()
        # necesario: 2010-05-10
        for ren in self.rens: # WORKAROUND (aparecia non centrada)
            ren.ResetCamera()
#        print 'resetearia'

        self.rens[0].AddActor(self.cubeA)


	#Añadido: por defecto outline oculto
        state = self.button_outline.GetValue()		#añadido
        self.outA.SetVisibility(state)			#añadido
        self.cubeA.SetVisibility(state)			#añadido


# debuxa tres eixos coloreados en (0,0) pareceme
#        self.axesA = vtk.vtkAxesActor()
#        self.rens[0].AddActor(self.axesA)
        
        self.outline = True



    def update_outline(self, src):
        if self.done and self.outline is True:
            self.outF.SetInputConnection(src.GetOutputPort())
            #self.outF.Update()
#            print 'update outline bounds', src.GetOutput().GetBounds()
            self.cubeA.SetBounds(src.GetOutput().GetBounds())



    def handler_outline(self, event):
        if not self.done:
            return
        state = self.button_outline.GetValue()
        self.outA.SetVisibility(state)
        self.cubeA.SetVisibility(state)
        self.widget.Render()
### </outline>




# # # # <labels b>



    def add_labels_b_1(self):
        labels_b_choices = [u'No labels', u'Selected', u'All']
        self.labels_b_choice = wx.Choice(self.plotbar, wx.ID_ANY, choices = labels_b_choices)
        self.labels_b_choice.SetSelection(0) # in windows appears without selection
        self.plotbar.add(self.labels_b_choice)
        self.labels_b_choice.Bind(wx.EVT_CHOICE, self.labels_b_handler, self.labels_b_choice)
# en init
#        self.labels_b_value = None



    def add_labels_b_2(self, data):
        self.labels_b_data = data
        self.labelsbT = vtk.vtkThresholdPoints()
        self.labelsbT.SetInputConnection(self.labels_b_data[0].GetOutputPort())
        self.labelsbT.ThresholdBetween(-1,-2)
        
        self.labelsbM = vtk.vtkLabeledDataMapper()
        self.labelsbM.SetInputConnection(self.labelsbT.GetOutputPort())
        # self.labelsbM.SetLabelFormat("%g")
        self.labelsbM.SetLabelModeToLabelScalars()
        self.labelsbM.GetLabelTextProperty().SetColor(label_color)

        self.labelsbA = vtk.vtkActor2D()
        self.labelsbA.SetMapper(self.labelsbM)
        self.labelsbA.SetVisibility(0)
        self.rens[0].AddActor(self.labelsbA)



    def labels_b_data_change(self, data):
        self.labels_b_data = data
        # conecta objeto nuevo
        if self.labels_b_choice.GetSelection() == 2:
            # igual que en labels_b_call
            self.labelsbM.SetInputConnection(self.labels_b_data[0].GetOutputPort())



    def labels_b_handler(self, event):
        if not self.done:
            return

        sel = self.labels_b_choice.GetSelection()

        self.labels_b_call(sel)

        self.widget.Render()



    def labels_b_call(self, num): # to overwrite
        if num == 0:
            self.labelsbA.SetVisibility(0)
        elif num == 1:
            if self.labels_b_value is not None:
                self.labelsbT.ThresholdBetween(self.labels_b_value, self.labels_b_value)
            else:
                self.labelsbT.ThresholdBetween(-1, -2)
            self.labelsbM.SetInputConnection(self.labelsbT.GetOutputPort())
            self.labelsbA.SetVisibility(1)
        elif num == 2:
            self.labelsbM.SetInputConnection(self.labels_b_data[0].GetOutputPort())
            self.labelsbA.SetVisibility(1)
        self.widget.Render()



    def labels_b_update(self, value):
        self.labels_b_value = value
        if self.labels_b_value is not None:
            self.labelsbT.ThresholdBetween(self.labels_b_value, self.labels_b_value)
        else:
            self.labelsbT.ThresholdBetween(-1, -2)
        self.widget.Render()

        
        
# # # # </labels b>



# # # # plane on / off
    def add_plane_1(self, selection=0):
        self.plane_widget = wx.ToggleButton(self.plotbar, wx.ID_ANY, 'Plane', style=wx.BU_EXACTFIT)
        self.plotbar.add(self.plane_widget)
        self.plane_widget.SetValue(selection==0)
        self.plane_widget.Bind(wx.EVT_TOGGLEBUTTON, self.handler_plane)



    def add_plane_2(self,planeI):
        self.plane_data = [planeI]



    def handler_plane(self, event):
        if not self.done:
            return    
        self.adjust_plane()
        self.widget.Render()



    def adjust_plane(self):
        if self.plane_widget.GetValue():
            self.plane_data[0].On()
        else:
            self.plane_data[0].Off()
# # # # /plane on / off



# # # # surface / wireframe
    def add_sw_1(self, button=True, selection=1):
        self.sw_button = button
        self.sw_pos = selection
        self.sw_choices = [u'Wireframe', u'Surface']
        if self.sw_button:
            self.sw_widget = wx.Button(self.plotbar, wx.ID_ANY, self.sw_choices[self.sw_pos], style=wx.BU_EXACTFIT)
            self.sw_widget.Bind(wx.EVT_BUTTON, self.handler_sw)
        else:
            self.sw_widget = wx.Choice(self.plotbar, wx.ID_ANY, choices = self.sw_choices)
            self.sw_widget.SetSelection(self.sw_pos) # in windows appears without selection
            self.sw_widget.Bind(wx.EVT_CHOICE, self.handler_sw)
        self.plotbar.add(self.sw_widget)


    def add_sw_2(self, obj):
        self.sw_data = [obj]


    def handler_sw(self, event):
        if not self.done:
            return
        if self.sw_button:
            self.sw_pos = (self.sw_pos + 1) % 2
            self.sw_widget.SetLabel(self.sw_choices[self.sw_pos])
            self.plotbar.layout() # ko: seguintes na beira da ventaa: ko ao aumentar ko. ko tamen sin tar na beira
        else:
            self.sw_pos = self.sw_widget.GetSelection()
        self.adjust_sw()
        self.widget.Render()


    def adjust_sw(self):
        if self.sw_pos == 0:
            self.sw_data[0].GetProperty().SetRepresentationToWireframe()
        elif self.sw_pos == 1:
            self.sw_data[0].GetProperty().SetRepresentationToSurface()
# # # # /surface / wireframe



# # # # wireframe / surface / surface+edges
    def add_swe_1(self, selection=1):
        self.swe_pos = selection
        self.swe_choices = [u'Wireframe', u'Surface', u'Surface+Edges']
        self.swe_widget = wx.Choice(self.plotbar, wx.ID_ANY, choices = self.swe_choices)
        self.swe_widget.SetSelection(self.swe_pos) # in windows appears without selection
        self.swe_widget.Bind(wx.EVT_CHOICE, self.handler_swe)
        self.plotbar.add(self.swe_widget)


    def add_swe_2(self, obj):
        self.swe_data = [obj]


    def handler_swe(self, event):
        if not self.done:
            return
        self.swe_pos = self.swe_widget.GetSelection()
        self.adjust_swe()
        self.widget.Render()


    def adjust_swe(self):
        if self.swe_pos == 0:
#            self.swe_data[1].SetVisibility(False)
            self.swe_data[0].GetProperty().SetRepresentationToWireframe()
            self.swe_data[0].GetProperty().EdgeVisibilityOff()

        elif self.swe_pos == 1:
            #self.swe_data[1].SetVisibility(False)
            self.swe_data[0].GetProperty().SetRepresentationToSurface()
            self.swe_data[0].GetProperty().EdgeVisibilityOff()
        elif self.swe_pos == 2:
            #self.swe_data[1].SetVisibility(True)
            self.swe_data[0].GetProperty().SetRepresentationToSurface()
            self.swe_data[0].GetProperty().EdgeVisibilityOn()
# # # # /wireframe / surface / surface+edges



# # # # <save image as>
    def save_as_1(self):
        self.save_as_text = u'Save...'
        self.save_as_button = wx.Button(self.plotbar, wx.ID_ANY, self.save_as_text, style=wx.BU_EXACTFIT)
        self.save_as_button.Bind(wx.EVT_BUTTON, self.save_as_call)
        self.plotbar.add(self.save_as_button)



    def save_as_call(self, event,movie=False):
        if not self.done:
            return

	if movie:
            return self.save_movie_from_window(self.widget.GetRenderWindow())
	else:
            if self.get_options().get(u'split') is True: # excepcional
            	self.save_from_window(self.widget.GetRenderWindow(), u'Select a file to save the scene on the left')
            	self.save_from_window(self.widget2.GetRenderWindow(), u'Select a file to save the scene on the right')
            else:
            	self.save_from_window(self.widget.GetRenderWindow())
	return None



    def save_from_window(self, renderwindow, title=None):
        auxSave.save_renderwindow(self.window, renderwindow, title)
# # # # </save image as>

    def save_movie_from_window(self, renderwindow, title=None):
	return auxSave.save_movie_renderwindow(self.window, renderwindow, title)

# # # # <center>
# center despois de quitar mallas adicionais, considéraas ainda para calcular o centro... => hide / delete
    def add_center_1(self):
        self.center_button = wx.Button(self.plotbar, wx.ID_ANY, 'Center', style=wx.BU_EXACTFIT)
        self.center_button.Bind(wx.EVT_BUTTON, self.center_event)

        self.orient_choices = ['XY view', 'XZ view', 'YZ view', 'iso view']
        self.orient_widget = wx.Choice(self.plotbar, wx.ID_ANY, choices = self.orient_choices)
        self.orient_widget.SetSelection(0) # in windows appears without selection
        self.orient_widget.Bind(wx.EVT_CHOICE, self.orient_event)

        self.plotbar.add(self.orient_widget)
        self.plotbar.add(self.center_button)

    def hide_center_1(self):
        self.center_button.Hide()
        self.orient_widget.Hide()
	self.legend_button.Hide()
        
# restore cam: center
    def center_event(self, event):
        if not self.done:
            return

        #self.printcam()

        for ren in self.rens:
            ren.ResetCamera() # posicion, tamanho

        #self.printcam()

        #self.loadcam()

        # sen loadcam, resetea a posicion e o tamanho, pero non a orientacion/direccion

        self.widget.Render()
        
    def orient_event(self, event):
        if not self.done:
            return
        pos = self.orient_widget.GetSelection()
        self.orient_inter(pos)
        self.widget.Render()

    def orient_inter(self, pos):
        if pos == 0:
            self.orient_handler((0.0,0.0,1.0))
        elif pos == 1:
            self.orient_handler((0.0,1.0,0.0),(0,0,1)) # necesario cambiar ViewUp
        elif pos == 2:
            self.orient_handler((1.0,0.0,0.0))
        elif pos == 3:
            v = math.sqrt(1.0/3.0)
            self.orient_handler((v,v,v))

    def orient_handler(self, unit, up=(0.0,1.0,0.0)):
        if not self.done:
            return

        for ren in self.rens:
            ren.ResetCamera() # posicion, tamanho
            fp = ren.GetActiveCamera().GetFocalPoint()
            p = ren.GetActiveCamera().GetPosition()
            dist = math.sqrt( (p[0]-fp[0])**2 + (p[1]-fp[1])**2 + (p[2]-fp[2])**2 )
            ren.GetActiveCamera().SetPosition(fp[0]+dist*unit[0], fp[1]+dist*unit[1], fp[2]+dist*unit[2])
            ren.GetActiveCamera().SetViewUp(up)
# # # # </center>



#<search>
    def add_search_1(self, callback, callback_coords=None):
        self.search_callback = callback
        self.search_callback_coords = callback_coords
        self.search_button = wx.Button(self.plotbar, wx.ID_ANY, 'Search...', style=wx.BU_EXACTFIT)
        self.search_button.Bind(wx.EVT_BUTTON, self.search_event)
        self.plotbar.add(self.search_button)

    def search_event(self, event):
        # <dialog>
        if self.search_callback_coords is not None:
            xyz = self.search_callback_coords()
        else:
            xyz = {}
        dialog = WindowSearch.WindowSearch(self.window, xyz) # pasar coordenadas do nodo actual ?
        r = dialog.ShowModal()
        if r == wx.ID_OK:
            datanew = dialog.get_data()
        dialog.Destroy()
        dialog = None
        # </dialog>
        if r == wx.ID_OK:
            coords = []
            coord = None
            try:
                coord = datanew.get('x')
                coords.append(float(coord))
                coord = datanew.get('y')
                coords.append(float(coord))
                coord = datanew.get('z')
                coords.append(float(coord))
            except ValueError:
                self.window.errormsg('Error converting coordinate \''+coord+'\' to floating point number')
            else:
                self.search_callback(coords)
#</search>



#<app name>
    def add_appname_2(self):
        self.textActorApp = vtk.vtkTextActor()
        self.textActorApp.SetInput(self.window.get_appname())

        pc = self.textActorApp.GetPositionCoordinate()
        pc.SetCoordinateSystemToNormalizedDisplay()
        pc.SetValue(1.0 - legendmargin, 0.0 + legendmargin)

        tprop = self.textActorApp.GetTextProperty()
        tprop.SetFontSize(13)
        tprop.SetFontFamilyToArial()
        tprop.SetJustificationToRight()
        tprop.SetColor(legend_color)

        self.rens[0].AddActor2D(self.textActorApp)
        self.textActorApp.SetVisibility(True)
#</app name>



# # # # <legend>    
    def add_legend_1(self, visible=False):
        self.legend_button = wx.ToggleButton(self.plotbar, wx.ID_ANY, 'Legend', style=wx.BU_EXACTFIT)
        self.legend_button.SetValue(visible)
        self.plotbar.add(self.legend_button)
        self.legend_button.Bind(wx.EVT_TOGGLEBUTTON, self.legend_event)

    def legend_event(self, event):
        if not self.done:
            return

        self.textActor.SetVisibility(self.legend_button.GetValue())
        self.widget.Render()

    def add_legend_2(self, visible=False):
        self.textActor = textActor = vtk.vtkTextActor()
        textActor.SetInput(u'')

        tprop = textActor.GetTextProperty()
        tprop.SetFontSize(13)
        tprop.SetFontFamilyToArial()
        tprop.SetJustificationToLeft()
        tprop.SetColor(legend_color)

# para poñela arriba
        tprop.SetVerticalJustificationToTop()
        pc = textActor.GetPositionCoordinate()
        pc.SetCoordinateSystemToNormalizedDisplay()
        pc.SetValue(0.0 + legendmargin, 1.0 - legendmargin)

        self.textActor.SetVisibility(visible)
        
        self.rens[0].AddActor2D(textActor)

    def update_legend(self, data1):
        filenames = []
        filenames = data1.get('filenames')
        dim = data1.get('dim')
        fieldname = data1.get('fieldname')
        fieldtype = data1.get('fieldtype')
        fielddomain = data1.get('fielddomain')
        component = data1.get('vector_component')
        time = data1.get('time')
        evolution = data1.get('evolution_upper')

        txt = u''
# Muestra los nombres de ficheros que se muestran en el plot
#        if filenames is not None:
#            fnset = set()
#            for f in filenames:
#                if f not in fnset:
#                    fnset.add(f)
#                    try:
#                        temp = unicode(f)
#                    except UnicodeDecodeError:
#                        temp = unicode(f.encode('string_escape')) # solucion alternativa a NFKD-ignore máis abaixo
#                    txt += u'File: ' + temp + u'\n'
        if dim is not None:
            txt += 'Dim: ' + unicode(dim) + 'D\n'

        #if fieldname is not None and fieldname != '':
        #    txt += 'Field: ' + fieldname + '\n'
        
        if fieldname is not None:
            txt1 = 'Field: ' + fieldname
            if fieldtype is not None or fielddomain is not None:
                txt2 = '('
                if fielddomain is not None and fieldtype is not None:
                    txt2 += fielddomain + ' ' + fieldtype
                else:
                    if fielddomain is not None:
                        txt2 += fielddomain
                    if fieldtype is not None:
                        txt2 += fieldtype
                txt2 += ')'
            if fieldtype is not None:
                txt1 += ' ' + txt2
            txt += txt1 + '\n'

        if component is not None:
            txt1 = 'Field component: '
            if isinstance(component, basestring):
                txt1 += component
            txt += txt1 + '\n'
            
        if time is not None:
            txt += evolution + ': ' + unicode(time) + '\n'

        txt2 = unicodedata.normalize('NFKD', txt).encode('ascii','ignore') # cuestionable º -> o
        if txt != txt2:
            #print u'Warning: unicode to ascii has changed some chars : \'' + txt + '\' -> \'' + txt2 + '\'' #code prior version 0.0.1
            logging.warning(u'Warning: unicode to ascii has changed some chars : \'' + txt + '\' -> \'' + txt2 + '\'')
        self.textActor.SetInput(txt2)

    def show_legend(self, tf):
        self.textActor.SetVisibility(tf)
# # # # </legend>

# # # # Opacity: 100%/Opacity: 75%/Opacity: 50%/Opacity: 25%/Opacity: 0%
    def add_opacity_1(self, selection=1):								#añadido
        self.opacity_pos = selection									#añadido
        self.opacity_choices = [u'Opacity: 100%', u'Opacity: 90%', u'Opacity: 80%', u'Opacity: 70%',\
u'Opacity: 60%', u'Opacity: 50%', u'Opacity: 40%', u'Opacity: 30%', u'Opacity: 20%', u'Opacity: 10%']	#añadido
        self.opacity_widget = wx.Choice(self.plotbar, wx.ID_ANY, choices = self.opacity_choices)	#añadido
        self.opacity_widget.SetSelection(self.opacity_pos) # in windows appears without selection	#añadido
        self.opacity_widget.Bind(wx.EVT_CHOICE, self.handler_opacity)					#añadido
        self.plotbar.add(self.opacity_widget)								#añadido


    def add_opacity_2(self, obj):									#añadido
        self.opacity_data = obj # Actor array!								#añadido


    def handler_opacity(self, event):									#añadido
        if not self.done:										#añadido
            return											#añadido
        self.opacity_pos = self.opacity_widget.GetSelection()						#añadido
        self.adjust_opacity()										#añadido
        self.widget.Render()										#añadido


    def adjust_opacity(self):										#añadido
	#Se añade el actor de la barra de escala
	if self.sbA is not None:
	    self.opacity_data.append(self.sbA)								#añadido
	for actor in self.opacity_data:									#añadido
            if self.opacity_pos == 0:									#añadido
		actor.GetProperty().SetOpacity(1.)							#añadido
            elif self.opacity_pos == 1:									#añadido
		actor.GetProperty().SetOpacity(0.9)							#añadido
            elif self.opacity_pos == 2:									#añadido
		actor.GetProperty().SetOpacity(0.8)							#añadido
            elif self.opacity_pos == 3:									#añadido
		actor.GetProperty().SetOpacity(0.7)							#añadido
	    elif self.opacity_pos == 4:									#añadido
		actor.GetProperty().SetOpacity(0.6)							#añadido
	    elif self.opacity_pos == 5:									#añadido
		actor.GetProperty().SetOpacity(0.5)							#añadido
	    elif self.opacity_pos == 6:									#añadido
		actor.GetProperty().SetOpacity(0.4)							#añadido
	    elif self.opacity_pos == 7:									#añadido
		actor.GetProperty().SetOpacity(0.3)							#añadido
	    elif self.opacity_pos == 8:									#añadido
		actor.GetProperty().SetOpacity(0.2)							#añadido
	    elif self.opacity_pos == 9:									#añadido
		actor.GetProperty().SetOpacity(0.1)							#añadido
# # # # Opacity: 100%/Opacity: 75%/Opacity: 50%/Opacity: 25%/Opacity: 0%

## axes indicator
    def add_axes_2(self):
        #return

	#print 'AXES2AXES2AXES2AXES2AXES2AXES2AXES2AXES2AXES2'
	#print 'AXES2AXES2AXES2AXES2AXES2AXES2AXES2AXES2AXES2'
	#print 'AXES2AXES2AXES2AXES2AXES2AXES2AXES2AXES2AXES2'

        renai = self.add_ren() 
	renai.InteractiveOff()
	a = vtk.vtkBorderWidget()
	#dist = self.rens[0].GetActiveCamera().GetDistance()
	renai.SetActiveCamera(self.rens[0].GetActiveCamera())
	#renai.GetActiveCamera().SetPosition(self.rens[0].GetActiveCamera().GetPosition())
	#renai.GetActiveCamera().SetFocalPoint(self.rens[0].GetActiveCamera().GetFocalPoint())
	#renai.GetActiveCamera().SetViewUp(self.rens[0].GetActiveCamera().GetViewUp())
	renai.GetActiveCamera().SetDistance(self.rens[0].GetActiveCamera().GetDistance())	
	renai.GetActiveCamera().SetFocalPoint(self.rens[0].GetActiveCamera().GetDirectionOfProjection())
	renai.SetBackground(background_color)
        #self.widget.GetRenderWindow().AddRenderer(renai)
        renai.SetViewport(0.0, 0.0, 0.15, 0.2)
        self.axesIndicator = vtk.vtkAxesActor()
	self.axesIndicator.SetTotalLength(3.5,3.5,3.5)
        vomw = vtk.vtkOrientationMarkerWidget()
	self.set_iren()
	vomw.SetInteractor( self.iren )
        vomw.SetOutlineColor( 0.9300, 0.5700, 0.1300 )
        vomw.SetOrientationMarker( self.axesIndicator )
	vomw.InteractiveOn( )


        renai.AddActor(self.axesIndicator)

## /axes indicator


    def get_revision(self):
        return self.revision



    def get_tracker_(self):
        return self.tracker



    def set_tracker_(self, tracker):
        self.tracker = tracker
        self.revision = -1
        self.revision_src = -1
        self.filename = self.tracker.get_vtkfile()



    # 1º set_tracker_ 2º set_data [dim calculada]
    def set_data(self, data):
        self.data1['filenames'] = data.get('filenames')
        self.data1['dim'] = data.get('dim')
	# Necesario para las mallas adicionales en trackerformula2
        self.data1['filesmesh2'] = data.get('filesmesh2')			#añadido
        self.call_dim(False) # calculates dim to show # uses self.tracker
        self.update_legend_data()



# avoid crash when opening closing exiting (wx/vtk BUG) - does not solve it
    # called after constructor or after plot_top
    def to_close(self):
        #self.widget.GetRenderWindow().WindowRemap()
        #self.widget.GetRenderWindow().Destroy()
        self.widget = None
        self.widget2 = None
        self.src = None

        if self.timer is not None:
            self.timer.Stop()
            self.timer = None
            
        #print 'Plot closed' # non entra ao cerrar a aplicación ! xa entra #code prior version 0.0.1
        logging.debug('Plot closed')



    def add_rens(self):
        for ren in self.rens:
            self.widget.GetRenderWindow().AddRenderer(ren)



    def add_ren(self):
        ren = vtk.vtkRenderer()
        self.widget.GetRenderWindow().AddRenderer(ren)
        self.rens.append(ren)
        return ren



    #debug
    def printcam(self):
        #print 'printcam'
        #print 'gfp', ren.GetActiveCamera().GetFocalPoint()
        #print 'gp', ren.GetActiveCamera().GetPosition()
        #print 'gvu', ren.GetActiveCamera().GetViewUp()  #code prior version 0.0.1
        logging.debug('printcam')
        logging.debug(ren.GetActiveCamera().GetFocalPoint())  
        logging.debug(ren.GetActiveCamera().GetPosition())
        logging.debug(ren.GetActiveCamera().GetViewUp())

    #debug
    def savecam(self):
        cams = []
        for ren in self.rens:
            cam = []
            cam.append(ren.GetActiveCamera().GetFocalPoint())
            cam.append(ren.GetActiveCamera().GetPosition())
            cam.append(ren.GetActiveCamera().GetViewUp())
            cams.append(cam)
        #print 'cam:', cams #code prior version 0.0.1
        logging.debug('cams')
        logging.debug(cams)
        self.cams = cams



    #debug
    def loadcam(self):
        i = 0
        for ren in self.rens:
            if i >= len(self.cams):
                break
            cam = self.cams[i]
            ren.GetActiveCamera().SetFocalPoint(cam[0])
            ren.GetActiveCamera().SetViewUp(cam[2])
            i += 1



# plot called from PanelVisual
    def plot_top(self, struct):
        # necessary to specify to avoid subclasses doing it multiple times
        self.struct = struct

        # self.plot_pre ou dentro

        self.plot(struct)

        if not self.is_done() or self.has_error():
            return

        self.add_additional_2()

        #self.printcam()
        #self.savecam()

#        self.add_axes_2()
        
        if self.option_scale is not None: # solo cuando se indica
            self.add_scale_1()
            self.scalebar.set_scale_visible(self.option_scale)
            self.scalebar.set_scale_abs_rel(self.option_scale_abs_rel)
            self.scalebar.set_is_temporal(self.timemanager is not None)
            self.scalebar.init()
        
        if self.timemanager is not None: # solo en .pvd
            self.add_time_1()

        self.plotbar.actual_add() # adds widgets from queue to MainBar

        #self.boxv.Show(self.plotbar, True, True) # recursive
        
        self.plotbar.layout()
        self.boxv.Layout()
        


# plot, to be overwritten
    def plot(self, struct):
        pass



# update plot called from PanelVisual
    def update_top(self, struct):
        # necessary to update in case of several structs pointing to the same plot
        self.struct = struct
        self.update(struct)



# update plot, to be overwritten
    def update(self, struct):
        pass
        # self.widget.Render()



    def data_error(self, error=None):
        txt = "Error: Cannot update plot with incorrect data"
        if error is not None:
            txt += ": " + error
        self.window.errormsg(txt)



    def read_2_vectors(self, struct, names=None): # names None or len = 3
        strA = ""
        strB0 = ""
        strB1 = ""
        if names is not None and len(names)>=3:
            strA = names[0]
            strB0 = names[1]
            strB1 = names[2]

        ch = struct.get_children()

        if len(ch) != 2:
            self.data_error('Incorrect number of children' + strA + ' (2 needed)')
            return None
        
        nums0 = ch[0].get_elements()
        nums1 = ch[1].get_elements()
        
        if len(nums0) != 3:
            self.data_error('Incorrect number of elements (3 needed)' + strB0)
            return None

        if len(nums1) != 3:
            self.data_error('Incorrect number of elements (3 needed)' + strB1)
            return None
        
        numsf0 = []
        for num in nums0:
            try:
                numsf0.append(float(num))
            except ValueError:
                self.data_error('Error converting \'' + num + '\' to float' + strB0)
                return None

        numsf1 = []
        for num in nums1:
            try:
                numsf1.append(float(num))
            except ValueError:
                self.data_error('Error converting \'' + num + '\' to float' + strB1)
                return None
    
        return [numsf0, numsf1]



    # update here or call from self.timemanager ?
    def time_first(self):
        if self.timemanager is None:
            return False
        self.timemanager.changes_clear()
        res = self.timemanager.action_first()
        if res is not True:
            self.window.errormsg(res)
        else:
            changes = self.timemanager.changes_get()
            res = self.time_update0(changes)
            if isinstance(res,basestring):
                self.window.errormsg(res)
        
    def time_last(self):
        if self.timemanager is None:
            return False
        self.timemanager.changes_clear()
        res = self.timemanager.action_last()
        if res is not True:
            self.window.errormsg(res)
        else:
            changes = self.timemanager.changes_get()
            res = self.time_update0(changes)
            if isinstance(res,basestring):
                self.window.errormsg(res)
            
    def time_previous(self):
        if self.timemanager is None:
            return False
        self.timemanager.changes_clear()
        res = self.timemanager.action_previous()
        if res is not True:
            self.window.errormsg(res)
        else:
            changes = self.timemanager.changes_get()
            res = self.time_update0(changes)
            if isinstance(res,basestring):
                self.window.errormsg(res)

    def time_next(self):
        if self.timemanager is None:
            return False
        self.timemanager.changes_clear()
        res = self.timemanager.action_next()
        if res is not True:
            self.window.errormsg(res)
        else:
            changes = self.timemanager.changes_get()
            res = self.time_update0(changes)
            if isinstance(res,basestring):
                self.window.errormsg(res)
            
    def time_goto(self, time):
        if self.timemanager is None:
            return False
        self.timemanager.changes_clear()
        res = self.timemanager.action_goto_time(time)
        if res is not True:
            self.window.errormsg(res)
        else:
            changes = self.timemanager.changes_get()
            res = self.time_update0(changes)
            if isinstance(res,basestring):
                self.window.errormsg(res)

    def time_goto_step(self, step):
        if self.timemanager is None:
            return False
        self.timemanager.changes_clear()
        res = self.timemanager.action_goto_index(step)
        if res is not True:
            self.window.errormsg(res)
        else:
            changes = self.timemanager.changes_get()
            res = self.time_update0(changes)
            if isinstance(res,basestring):
                self.window.errormsg(res)


################################################################################################
# establecemos el escritor de video
    def set_movie_writer(self, codec,filename,rate):

	self.moviewriter = None							#añadido
        codecs = [u'AVI',u'FFMPEGHQ',u'FFMPEGLQ',u'OGGTHEORA',u'MPEG2']		#añadido
	#print codec  #code prior version 0.0.1
        logging.debug(codec)
	index = codecs.index(codec)						#añadido
        if codec in codecs:							#añadido
	    try:								#añadido
	    	if index == 0:		#AVI					#añadido
		    self.moviewriter = vtk.vtkAVIWriter()			#añadido
		    self.moviewriter.SetRate(rate)				#añadido
		    self.moviewriter.SetQuality(2)				#añadido
	    	elif index == 1:	#FFMEPGHQ				#añadido
		    self.moviewriter = vtk.vtkFFMPEGWriter()			#añadido
		    self.moviewriter.SetRate(rate)				#añadido		
		    self.moviewriter.SetBitRate(1024*1024*30)			#añadido
		    self.moviewriter.SetBitRateTolerance(1024*1024*30)		#añadido
		    self.moviewriter.SetQuality(2)				#añadido	
	    	elif index == 2:	#FFMEPGLQ				#añadido
		    self.moviewriter = vtk.vtkFFMPEGWriter()			#añadido
		    self.moviewriter.SetRate(rate)				#añadido		
		    self.moviewriter.SetBitRate(800*800*30)			#añadido
		    self.moviewriter.SetBitRateTolerance(800*800*30)		#añadido
		    self.moviewriter.SetQuality(2)				#añadido	
	    	elif index == 3:	#OGGTHEORA				#añadido
		    self.moviewriter = vtk.vtkOggTheoraWriter()			#añadido
		    self.moviewriter.SetRate(rate)				#añadido
		    self.moviewriter.SetQuality(2)				#añadido
	    	elif index == 4:	#MPEG2					#añadido
		    self.moviewriter = vtk.vtkMPEG2Writer()			#añadido
		    #self.moviewriter.SetRate(rate)				#añadido
		    #self.moviewriter.SetQuality(2)				#añadido
		self.moviewriter.SetFileName(filename)				#añadido
	    except:								#añadido
		return u'ERROR: '+codec+ ' codec not found'			#añadido
	else:
	    return u'ERROR: '+codec+ ' not yet supported'			#añadido


################################################################################################
# establecemos el capturador de la ventana de render
    def set_image_filter(self,moviewriter):

	self.window2image = None						#añadido
	self.window2image2 = None						#añadido

	self.window2image = vtk.vtkWindowToImageFilter()			#añadido
	self.window2image.SetInput(self.widget.GetRenderWindow())		#añadido

	if self.get_options().get(u'split'):
	    self.window2image2 = vtk.vtkWindowToImageFilter()			#añadido
	    self.window2image2.SetInput(self.widget2.GetRenderWindow())		#añadido
	    self.imageappend = vtk.vtkImageAppend()				#añadido
	    self.imageappend.PreserveExtentsOff()				#añadido
	    self.imageappend.SetAppendAxis(0)					#añadido	
	    if vtk.vtkVersion.GetVTKMajorVersion() < 6:
	        self.imageappend.SetInput(0,self.window2image.GetOutput())		#añadido
	        self.imageappend.SetInput(1,self.window2image2.GetOutput())		#añadido
	    else:
	        self.imageappend.SetInputData(0,self.window2image.GetOutput())		#añadido
	        self.imageappend.SetInputData(1,self.window2image2.GetOutput())		#añadido
	    self.imageappend.Update()						#añadido
	    moviewriter.SetInputConnection(self.imageappend.GetOutputPort())#añadido
	else:									#añadido
	    moviewriter.SetInputConnection(self.window2image.GetOutputPort()) #añadido

################################################################################################
# Exportar animación de la ventana de render a video
    def start_movie_saving(self, movie_opt=None):
        if movie_opt is not None:							#añadido
	    #Calculo de frames por segundo
	    num_times = len(self.tracker.get_times())						#añadido
	    ini_time_index = self.tracker.search_time_pos(movie_opt.get(u'start_time'))	#añadido
	    end_time_index = self.tracker.search_time_pos(movie_opt.get(u'end_time'))	#añadido
	    movie_opt[u'num_times'] = end_time_index - ini_time_index			#añadido
	    rate = movie_opt.get(u'num_times')//movie_opt.get(u'duration')		#añadido
	    if rate == 0:								#añadido
		rate = 1								#añadido
	    #Creamos movie writer e image filter
	    res =  self.set_movie_writer(movie_opt.get(u'codec'),movie_opt.get(u'file'),rate)#añadido
	    if isinstance(res,basestring):
		self.window.errormsg(res)
		return False
	    else:
		self.set_image_filter(self.moviewriter)							#añadido
	    	self.movie_saving = movie_opt.get(u'movie')				#añadido
		self.moviewriter.Start()						#añadido
		return True								#añadido
################################################################################################

    def time_play(self):

        if self.timemanager is None:
            return False

        if self.timer is None:
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        if self.player is None:
            if self.data1.get('interpolation'):
                self.player = Player.Player(self, self.timemanager) # player de tempo proporcional
            else:
                self.player = PlayerConst.PlayerConst(self, self.timemanager) # player de tempo constante / frecuencia
        
        rango = self.timebar.get_time_range()
        if rango[0] is None or rango[1] is None:
            return
        dur = self.timebar.get_duration()
        if dur is None:
            return
        
        if self.is_playing:
            self.window.add_text('Play: pausing ...\n')
            self.player.pause()
            self.timer.Stop()
            self.is_playing = False
            self.timebar.set_is_playing(False)
            self.timebar_time_updated_saved = self.timebar_time_updated
            return

        self.is_playing = True
        self.timebar.set_is_playing(True)
        # se non houbo cambios de tempo, empeza onde estaba (se non houbo cambios de rango e duración)
        # e se non, empeza de novo
        if self.timebar_time_updated_saved == self.timebar_time_updated:
            res = self.player.start_or_continue(rango[0], rango[1], dur, self.timemanager.get_times())
            if res == 0:
                self.window.add_text('Play: starting ...\n')
            elif res == 1:
                self.window.add_text('Play: continuing ...\n')
        else:
            self.player.start(rango[0], rango[1], dur, self.timemanager.get_times())
            self.window.add_text('Play: starting ...\n')
        self.timer.Start(20) # tarda o intervalo en empezar
        self.timer_action() # 0




    def on_timer(self, event):
        self.timer_action()



    def timer_action(self):
        res = self.player.step()
        if res is False:
            self.timer.Stop()
            self.is_playing = False
            self.timebar.set_is_playing(False)
            self.window.add_text('Play: stopping ...\n')
	    if self.moviewriter is not None and self.movie_saving:				#añadido
		self.moviewriter.End()								#añadido
		self.movie_saving = False							#añadido
        self.timebar.put_status(self.get_status())



    def get_status(self):
        if self.timemanager is None:
            return {}
        else:
            return self.timemanager.get_status()



    @staticmethod
    def build(typename, parent):
        
        alias = configPlot.get_alias(typename)
        if alias != typename:
            #print 'building plot:', typename, '->', alias  #code prior version 0.0.1
            logging.debug('building plot:'+str(typename)+'->'+str(alias))
        else:
            #print 'building plot:', typename #code prior version 0.0.1
            logging.debug('building plot:'+str(typename))
        typeobj = Plot.get_type_type(alias)
        if typeobj is not None:
            return typeobj(parent) # constructor
        else:
            return None



    @staticmethod
    def get_type_type(typename):
        if typename == u'mesh':
            return PlotMesh.PlotMesh
        elif typename == u'references':
            return PlotReferences.PlotReferences
        elif typename == u'numbering':
            return PlotNumbering.PlotNumbering
        elif typename == u'materials':
            return PlotMaterials.PlotMaterials
        elif typename == u'filled':
            return PlotFilled.PlotFilled
        elif typename == u'threshold':
            return PlotThreshold.PlotThreshold
        elif typename == u'contour':
            return PlotContour.PlotContour
        elif typename == u'scalar_deformed':
            return PlotScalarDeformed.PlotScalarDeformed
        elif typename == u'vector_deformed':
            return PlotVectorDeformed.PlotVectorDeformed
        elif typename == u'plot_over_line':
            return PlotOverLine.PlotOverLine
        elif typename == u'slice':
            return PlotSlice.PlotSlice
        elif typename == u'cut':
            return PlotCut.PlotCut
        elif typename == u'rough_cut':
            return PlotRoughCut.PlotRoughCut
        elif typename == u'vector_field':
            return PlotVectorField.PlotVectorField
        elif typename == u'2d_graph':
            return Plot2DGraph.Plot2DGraph
        elif typename == u'vector_components':
            return PlotVectorComponents.PlotVectorComponents
        elif typename == u'streamline':
        	return PlotStreamline.PlotStreamline 
        elif typename == u'image':
        	return PlotPicture.PlotPicture
        else:
            return None



import PlotMesh
import PlotReferences
import PlotNumbering
import PlotMaterials
import PlotFilled
import PlotThreshold
import PlotContour
import PlotScalarDeformed
import PlotVectorDeformed
import PlotOverLine
import PlotSlice
import PlotCut
import PlotRoughCut
import PlotVectorField
import Plot2DGraph
import PlotVectorComponents
import PlotStreamline
import PlotPicture
