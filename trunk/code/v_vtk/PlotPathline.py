#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
import Plot
import wx_version
import wx
import vtk
import ClickLabel3 as ClickLabel
import random
import Element

# mostrar etiquetas con el valor del campo en los puntos donde se hace 'doble click'
interactive = True

# ALPHA-vc: para que mostre valor real ao clickar e non mostre (0,0,0) onde non hai frechas (para densidade de frechas < 100%)

class PlotPathline(Plot.Plot):
#### Constructor ###############################################################
# Inicializa la clase
    def __init__(self, parent):
    	#usa el constructor del padre
        Plot.Plot.__init__(self, parent)

        # Primera parte para incliur el visor
        # Asigna button_outline a plotbar
        self.add_outline_1()

        # anade cbl en plotbar
        choices = [u'Wireframe', u'Surface', u'None']
        self.cbl = wx.Choice(self.plotbar, wx.ID_ANY, choices = choices)
        self.cbl.SetSelection(0) # in windows appears without selection
        self.plotbar.add(self.cbl)
        self.add_opacity_1(selection=0) # Opacity: 100%/75%/50%/25%/0%
        self.Bind(wx.EVT_CHOICE, self.cl, self.cbl) #enlaza el evento con cl y cbl

        # configura el clicker
        self.clicker = None
        if interactive:
            self.clicker = ClickLabel.ClickLabel()
            self.clicker.set_mode('vectors')

        # variables cambiantes a traves del xml
        self.lastnlin = 300
        self.lastancho = 5e-4
        self.lastradio = 2e-3
        self.lastcenter = [0.0, 0.0, 0.0]
        self.lastinteg = "4"
        print '====>__inti__',self.lastcenter[0],',',self.lastcenter[1],',',self.lastcenter[2]

#### get_options ###############################################################
# Asigna el titulo y la opcion de interaccion
# Motodo sobrecargado
    def get_options(self):
    	ops = {u'title':'Pathline'}
        if interactive:
            ops[u'interactor'] = True
        return ops



#### cl ########################################################################
# Cambia la representacion en funcion de la opcion escogida (wireframe, surface, ...)
    def cl(self, event):
    	if not self.done:
            return

        sel = self.cbl.GetSelection()

        if sel == 0:
            self.wireA2.GetProperty().SetRepresentationToWireframe()
            self.wireA2.SetVisibility(1)
        elif sel == 1:
            self.wireA2.GetProperty().SetRepresentationToSurface()
            self.wireA2.SetVisibility(1)
        elif sel == 2:
            self.wireA2.SetVisibility(0)

        self.widget.Render()
        


#### src_update1 ###############################################################
# para cuando cambia el tiempo y por tanto, self.src
# al finalizar invoca a src_update1b
# metodo sobrecargado
    def src_update1(self, changes):
    	if changes.get('changed'):
            self.ugrid = self.construct_data(self.src)
            self.src_vc.SetInput(self.ugrid)
        return self.src_update1b(changes)



#### src_update1b ##############################################################
# para cuando cambia el tiempo y por tanto, self.src
    def src_update1b(self, changes): 
    	if changes.get('changed'):
            # Actualiza los datos referentes al plot
            self.apply_params()
        if changes.get('changed'):
            # Actualiza las medidas del visor
            self.update_outline(self.src_vc)

            # Actualiza los vectores y su rango
            if self.vectors is not None:
                if self.data1.get('fielddomain') == 'cell':
                    self.vectors = self.src.GetOutput().GetCellData().GetVectors()
                elif self.data1.get('fielddomain') == 'point':
                    self.vectors = self.src.GetOutput().GetPointData().GetVectors()
                self.lutrange = self.vectors.GetRange(-1)
                self.scalarrange.local_set(self.lutrange)
                self.lut.SetTableRange(self.lutrange)

        # siempre ?
        # Actualiza el clicker en funcion del tipo de elemento
        if self.data1.get('fielddomain') == 'cell':
            self.src_update_clicker(self.clicker, self.cellcenters_click, changes) # necesario ?
        else:
            self.src_update_clicker(self.clicker, self.src, changes) # ALPHA-vc

        return True

   

#### plot ######################################################################
# Metodo principal para dibujar la representacion
    def plot(self, struct):
    	# Crea self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        # Actualiza campos
        self.update_field_type('vector', True)
        self.update_legend_data()

        # Crea self.src
        if not self.call_src():
            return

        # Obtenemos los vectores
        self.ugrid = self.construct_data(self.src)
        self.src_vc = vtk.vtkAssignAttribute()
        self.src_vc.SetInput(self.ugrid)
        
        # Segunda parte para incluir el visor
        # Pinta los elementos

  
        # Obtiene los centros de las celdas si se usa dicho tipo de elemento
        if self.data1.get('fielddomain') == 'cell': # vtk does not seem to support cell vectors
            self.cellcenters = vtk.vtkCellCenters()
            self.cellcenters.SetInputConnection(self.src_vc.GetOutputPort())
            self.cellcenters_click = vtk.vtkCellCenters() # ALPHA-vc
            self.cellcenters_click.SetInputConnection(self.src.GetOutputPort()) # ALPHA-vc

        self.ini_params()
#I##############################################################################
####### Inicializamos el dibujante #############################################
        # Create source for streamtubes   
        self.seeds = vtk.vtkPointSource()   
        self.seeds.SetRadius(self.lastradio) # zona que abarca la salida de puntos  
        self.seeds.SetCenter(self.lastcenter)   
        print '====>plot ->> self.seeds.SetCenter',self.lastcenter[0],',',self.lastcenter[1],',',self.lastcenter[2]
        self.seeds.SetNumberOfPoints(self.lastnlin)   

        self.lin = vtk.vtkStreamTracer()
        self.lin.SetInputConnection(self.src.GetOutputPort())
        self.lin.SetSource(self.seeds.GetOutput())  
        
####### Configuramos el dibujante ##############################################
        self.lin.SetStartPosition(self.lastcenter)
        print '====>plot ->> self.lin.SetStartPosition',self.lastcenter[0],',',self.lastcenter[1],',',self.lastcenter[2]
        self.lin.SetMaximumPropagation(500)
        self.lin.SetInitialIntegrationStep(0.5)
        #self.lin.SetIntegrationStepUnit(2)	# 2 = CELL_LENGTH_UNIT
        self.lin.SetIntegrationDirectionToBoth()
        
        integ = vtk.vtkRungeKutta4()
        self.lin.SetIntegrator(integ)

####### Configuramos el filtro #################################################
        self.streamTube = vtk.vtkTubeFilter()
        self.streamTube.SetInputConnection(self.lin.GetOutputPort())
        self.streamTube.SetInputArrayToProcess(1, 0, 0, 0, 1)
        self.streamTube.SetRadius(self.lastancho)
        self.streamTube.SetNumberOfSides(12)
        self.streamTube.SetVaryRadiusToVaryRadiusByVector()
        
#F###### Configuramos la tabla de colores ######################################
        # Iniicializamos la tabla de asignacion de colores
        self.lut = vtk.vtkLookupTable()
        self.lut.SetRampToLinear()
        self.lut.SetScaleToLinear()
        self.lut.SetVectorModeToMagnitude()# When using vector magnitude for coloring
        self.lut.Build()

        if self.vectors is not None:
            self.lutrange = self.vectors.GetRange(-1)
            self.lut.SetTableRange(self.lutrange)

####### Configuramos el mapper #################################################
        self.pdM = vtk.vtkPolyDataMapper()
        self.pdM.SetInputConnection(self.streamTube.GetOutputPort())
        #Definicion del campo y el rango para colorear
        if self.vectors is not None:
            self.pdM.SelectColorArray(self.vectors.GetName())
            self.pdM.SetScalarRange(self.lutrange)
            if self.data1.get('fielddomain') == 'cell':
                self.pdM.SetScalarModeToUseCellFieldData()
            else:
                self.pdM.SetScalarModeToUsePointFieldData()
            self.pdM.SetColorModeToMapScalars()
            self.pdM.InterpolateScalarsBeforeMappingOff()
            self.pdM.ScalarVisibilityOn()
        self.pdM.SetLookupTable(self.lut)
        self.pdM.UseLookupTableScalarRangeOn()
        self.pdM.Update()
    
####### Configuramos el actor ##################################################
        self.linA = vtk.vtkActor()
        self.linA.SetMapper(self.pdM)
        self.linA.VisibilityOn()
        self.linA.GetProperty().SetAmbient(1.0)
        self.linA.GetProperty().SetDiffuse(0.0)
        self.linA.GetProperty().SetSpecular(0.0)

#F##############################################################################

        #para mostrar surface e wireframe ao mesmo tempo
        self.wireM2 = vtk.vtkDataSetMapper()
        self.wireM2.SetInputConnection(self.src_vc.GetOutputPort())
        self.wireM2.ScalarVisibilityOff()
        self.wireA2 = vtk.vtkActor()
        self.wireA2.SetMapper(self.wireM2)
        self.wireA2.GetProperty().SetRepresentationToWireframe()
        self.wireA2.GetProperty().SetColor(Plot.edges_color)
        self.add_opacity_2([self.linA,self.wireA2]) # Opacity: 100%/75%/50%/25%/0%
        # Incluimos los actores en el renderer        
        self.rens[0].AddActor(self.wireA2)
        self.rens[0].AddActor(self.linA)

        # Si estamos en modo interactivo configuramos el clicker
        if interactive:
            self.set_iren()    # Configura el interactor
            if self.data1.get('fielddomain') == 'cell':
                self.clicker.set_point_cell('point') # así ok
                self.clicker.set_objects(self.cellcenters_click, self.rens[0], self.iren, self.widget) # ALPHA-vc
            else:
                self.clicker.set_point_cell(self.data1.get('fielddomain'))
                self.clicker.set_objects(self.src, self.rens[0], self.iren, self.widget) # ALPHA-vc
            self.clicker.set_props([self.wireA2])
            self.clicker.setup()
         
        # Obtenemos los datos si los hay en el xml
        newlast = self.read_params(struct)
        changed = self.test_params(newlast)
        if changed:
        	self.apply_params()
           
        # Reseteamos las camaras de todos los renderers
        for ren in self.rens: # WORKAROUND (aparecia non centrada) // + outline
            ren.ResetCamera()

        # Incluye la barra de escala si tenemos vectores
        if self.vectors is not None:
            self.scalarrange.local_set(self.lutrange)
            self.add_scalarbar_1()
            self.add_scalarbar_2(self.lut)

        self.add_outline_2(self.src_vc)

        self.done = True
        


#### range_update3 #############################################################
# Asigna el rango de la escala
# Motodo sobrecargado
    def range_update3(self, range_): # to overwrite in subclasses
    	self.pdM.SetScalarRange(range_)        


#### read_params ###############################################################
# Obtiene los parametros que se pasan desde el xml
    def read_params(self, struct):
    	fail = [None,None,None,None,None]
        nlin = None
        ancho = None
        radio = None
        centro = [None,None,None]
        integ = None

        ch = struct.get_children()

        if len(ch) == 0:
            print '====>read_params ->> return len(ch)==0',self.lastcenter[0],',',self.lastcenter[1],',',self.lastcenter[2]
            return [self.lastnlin, self.lastancho, self.lastradio, self.lastcenter, self.lastinteg]

        if len(ch) != 5:
            self.data_error('Incorrect number of children in PlotPathline options (5 needed)')
            return fail

        # Obtenemos el primer dato (nlin)
        nums = ch[0].get_elements()
        if len(nums) == 0:
            ch[0].set_elements([str(self.lastnlin)])
            self.panel_widgets.update_widget_struct(ch[0])
        elif len(nums) == 1:
            num = nums[0] 
            if num == None:
                self.data_error('Null parameter')
                return fail
            
            numf = None
            try:
                numf = int(num)
            except ValueError:
                pass
            if numf is not None:
                nlin = numf
            else:
                self.data_error('Error converting \'' + num + '\' to int')
                return fail
        else:
            self.data_error('Incorrect number of elements in number of lines (1 needed)')
            return fail

        # Obtenemos el segundo dato (ancho)
        nums = ch[1].get_elements()
        if len(nums) == 0:
            ch[1].set_elements([str(self.lastancho)])
            self.panel_widgets.update_widget_struct(ch[1])
        elif len(nums) == 1:
            num = nums[0] 
            if num == None:
                self.data_error('Null parameter')
                return fail
            
            numf = None
            try:
                numf = float(num)
            except ValueError:
                pass
            if numf is not None:
                ancho = numf
            else:
                self.data_error('Error converting \'' + num + '\' to float')
                return fail
        else:
            self.data_error('Incorrect number of elements in line size (1 needed)')
            return fail

        # Obtenemos el tercer dato (radio)
        nums = ch[2].get_elements()
        if len(nums) == 0:
            ch[2].set_elements([str(self.lastradio)])
            self.panel_widgets.update_widget_struct(ch[2])
        elif len(nums) == 1:
            num = nums[0] 
            if num == None:
                self.data_error('Null parameter')
                return fail
            
            numf = None
            try:
                numf = float(num)
            except ValueError:
                pass
            if numf is not None:
                radio = numf
            else:
                self.data_error('Error converting \'' + num + '\' to float')
                return fail
        else:
            self.data_error('Incorrect number of elements in seeds radius (1 needed)')
            return fail

        # Obtenemos el cuarto dato (centro)
        nums = ch[3].get_elements()
        if len(nums) == 0:
            ch[3].set_elements([str(self.lastcenter[0]),str(self.lastcenter[1]),str(self.lastcenter[2])])
            print '====>read_params ->> if len(nums) == 0',self.lastcenter[0],',',self.lastcenter[1],',',self.lastcenter[2]
            self.panel_widgets.update_widget_struct(ch[3])
        elif len(nums) == 3:
            for i in [0, 1, 2]:
                num = nums[i]
                if num == None:
                    self.data_error('Null parameter')
                    return fail
            
                numf = None
                try:
                    numf = float(num)
                except ValueError:
                    pass
                if numf is not None:
                    centro[i] = numf
                else:
                    self.data_error('Error converting \'' + num + '\' to float')
                    return fail
        else:
            self.data_error('Incorrect number of elements in seeds center (3 needed)')
            return fail
            
        # Obtenemos el quinto dato (integ)
        nums = ch[4].get_elements_selected()
        if len(nums) == 0:
            ch[4].set_elements([self.lastinteg])
            self.panel_widgets.update_widget_struct(ch[4])
        elif len(nums) == 1:
            integ = nums[0]
            if integ == None:
                self.data_error('Null parameter')
                return fail
        else:
            self.data_error('Incorrect number of elements in Runge-Kutta Method order (1 needed)')
            return fail
            
        return [nlin,ancho,radio,centro,integ]



#### mod_integ #################################################################
# Modifica el integrador en funcion del orden escogido
    def mod_integ(self, lastinteg):
    	if lastinteg == "2":
            integ = vtk.vtkRungeKutta2()
        elif lastinteg == "4":
            integ = vtk.vtkRungeKutta4()
        elif lastinteg == "4-5":
            integ = vtk.vtkRungeKutta45()
        else:
            integ = None
            self.data_error('Runge-Kutta Method order not selected')
        if integ is not None:
            self.lin.SetIntegrator(integ)
   
   

#### apply_params ##############################################################
    def apply_params(self):
    	if self.lastradio is not None:
            self.seeds.SetRadius(self.lastradio)
        if self.lastnlin is not None:
            self.seeds.SetNumberOfPoints(self.lastnlin)
        if self.lastancho is not None:
            self.streamTube.SetRadius(self.lastancho)
        if self.lastcenter is not None:
            self.seeds.SetCenter(self.lastcenter)
            print '====>apply_params',self.lastcenter[0],',',self.lastcenter[1],',',self.lastcenter[2]
        if self.lastinteg is not None:
            self.mod_integ(self.lastinteg)
       
       

#### test_params ##############################################################
    def test_params(self, newlast): 
    	changed = False
        
        if (newlast[0] is not None) & (self.lastnlin != newlast[0]):
            changed = True
            self.lastnlin = newlast[0]
        if (newlast[1] is not None) & (self.lastancho != newlast[1]):
            changed = True
            self.lastancho = newlast[1]
        if (newlast[2] is not None) & (self.lastradio != newlast[2]):
            changed = True
            self.lastradio = newlast[2]
        if (newlast[3] is not None) & (newlast[3][0] is not None) & (newlast[3][1] is not None) & (newlast[3][2] is not None) & (self.lastcenter != newlast[3]):
            print '====>test_params',self.lastcenter[0],',',self.lastcenter[1],',',self.lastcenter[2]
            print '====>test_params',newlast[3][0],',',newlast[3][1],',',newlast[3][2]
            changed = True
            self.lastcenter = newlast[3]
        if (newlast[4] is not None) & (self.lastinteg != newlast[4]):
            changed = True
            self.lastinteg = newlast[4]
                  
        return changed
          



#### update ####################################################################
# Actualiza el estado de la representacion
# Metodo sobrecargado
    def update(self, struct):   
    	newlast = self.read_params(struct)
        changed = self.test_params(newlast)

        if changed:
            self.apply_params()
            self.widget.Render()
        


#### construct_data ############################################################
# Inicializacion de la lectura del archivo?
    def construct_data(self, src):
    	# Construimos el grid
        o = src.GetOutput()
        ugrid = vtk.vtkUnstructuredGrid()
        ugrid.SetPoints(o.GetPoints())
        ugrid.SetCells(o.GetCellTypesArray(), o.GetCellLocationsArray(), o.GetCells())
        
        # Obtenemos los vectores en funcion del tipo de elemento
        if self.data1.get('fielddomain') == 'cell':
            self.vectors = o.GetCellData().GetVectors()
            pc = 1
        elif self.data1.get('fielddomain') == 'point':
            self.vectors = o.GetPointData().GetVectors()
            pc = 0
        else:
            self.vectors = None

        # Limites dos eixos
        self.bounds = self.src.GetOutput().GetBounds()
        return ugrid
        
    def ini_params(self):
    	
        # Centro ("Inicializacion")
        x = (self.bounds[1]+self.bounds[0])/2.0
        y = (self.bounds[3]+self.bounds[2])/2.0
        z = (self.bounds[5]+self.bounds[4])/2.0
        self.lastcenter = [x, y, z]
        print '====>ini_params',self.lastcenter[0],',',self.lastcenter[1],',',self.lastcenter[2]


        # Maximo radio sen sairse dos eixos ("Inicializacion")
        self.lastradio = (self.bounds[1]-self.bounds[0])/2.0
        otro = (self.bounds[3]-self.bounds[2])/2.0
        if (self.lastradio < 0):
            self.lastradio = self.lastradio * (-1.0)
        if (otro < 0):
            otro = otro * (-1.0)
        if (self.lastradio > otro):
            self.lastradio = otro

