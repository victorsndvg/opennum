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


aname1 = 'vector_original'
aname2 = 'vector_decimated_factor'
dname = 'vector_arrow_factor'


# ALPHA-vc: para que mostre valor real ao clickar e non mostre (0,0,0) onde non hai frechas (para densidade de frechas < 100%)


class PlotVectorField(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_outline_1()

        choices = [u'Wireframe', u'Surface', u'None']
        self.cbl = wx.Choice(self.plotbar, wx.ID_ANY, choices = choices)
        self.cbl.SetSelection(0) # in windows appears without selection
        self.plotbar.add(self.cbl)
        self.add_opacity_1(selection=0) # Opacity: 100%/75%/50%/25%/0%

        self.Bind(wx.EVT_CHOICE, self.cl, self.cbl)

        self.clicker = None
        if interactive:
            self.clicker = ClickLabel.ClickLabel()
            self.clicker.set_mode('vectors')

        self.esta = None

        self.lastmode = 1.0
        self.lastscale = 1.0



    def get_options(self):
        ops = {u'title':'Vector field'}
        if interactive:
            ops[u'interactor']=True
        return ops



    def cl(self, event):
        if not self.done:
            return

        sel = self.cbl.GetSelection()

        if sel == 0:
            self.wireA2.GetProperty().SetRepresentationToWireframe()
            self.wireA2.SetVisibility(1)
        if sel == 1:
            self.wireA2.GetProperty().SetRepresentationToSurface()
            self.wireA2.SetVisibility(1)
        if sel == 2:
            self.wireA2.SetVisibility(0)

        self.widget.Render()



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        if changes.get('changed'):
            self.esta = None # obliga a recalcular ahora que cambian los datos
            self.ugrid = self.construct_data(self.src)
            self.src_vc.SetInput(self.ugrid)
        return self.src_update1b(changes)



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1b(self, changes):
        if changes.get('changed'):
            self.apply_params()
        if changes.get('changed'):
            self.update_outline(self.src_vc)
#        if changes.get('new'):
#            if self.data1.get('fielddomain') == 'cell':
#                self.cellcenters.SetInputConnection(self.src_vc.GetOutputPort())
#                self.cellcenters_click.SetInputConnection(self.src.GetOutputPort()) # ALPHA-vc
#            else:
#                self.lin.SetInputConnection(self.src_vc.GetOutputPort())
#            self.wireM2.SetInputConnection(self.src_vc.GetOutputPort())
        if changes.get('changed'):
            if self.data1.get('fielddomain') == 'cell':				#añadido
		self.vectors = self.src.GetOutput().GetCellData().GetVectors()	#añadido
	    elif self.data1.get('fielddomain') == 'point':			#añadido
		self.vectors = self.src.GetOutput().GetPointData().GetVectors()	#añadido
            sr = self.vectors.GetRange(-1)					#añadido
	    self.scalarrange.local_set(sr)					#añadido
            #self.wireM2.SetScalarRange(sr)


        # siempre ?
        if self.data1.get('fielddomain') == 'cell':
            self.src_update_clicker(self.clicker, self.cellcenters_click, changes) # necesario ?
        else:
            self.src_update_clicker(self.clicker, self.src, changes) # ALPHA-vc

#        self.data1[dname] = self.lastmode # realizar
#        self.update_legend_data()

        return True



    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        self.update_field_type('vector', True)
        self.update_legend_data()
        
        # creates self.src
        if not self.call_src():
            return


        self.ugrid = self.construct_data(self.src)
        self.src_vc = vtk.vtkAssignAttribute()
        #self.src_vc.Assign(aname, 0, pc) # 0 scalar 1 vector ; 0 point 1 cell
        self.src_vc.SetInput(self.ugrid)
        res = self.apply_data(self.lastmode) # necesario, se non da erro vtk

#        self.wireM = vtk.vtkDataSetMapper()
#        self.wireM.SetInputConnection(self.src.GetOutputPort())

#        print 'rango o:', self.src.GetOutput().GetScalarRange() #test
#        print 'rango d:', self.src.GetOutputAsDataSet().GetScalarRange() #test #so para xml (vtu)
#        self.wireM.SetScalarRange(self.src.GetOutput().GetScalarRange())


# reverse rainbow [red->blue] -> [blue->red]
#        look = self.wireM.GetLookupTable()
#        self.add_scalarbar_2(look)

        self.add_outline_2(self.src_vc)

        if self.data1.get('fielddomain') == 'cell': # vtk does not seem to support cell vectors
            self.cellcenters = vtk.vtkCellCenters()
            self.cellcenters.SetInputConnection(self.src_vc.GetOutputPort())
            self.cellcenters_click = vtk.vtkCellCenters() # ALPHA-vc
            self.cellcenters_click.SetInputConnection(self.src.GetOutputPort()) # ALPHA-vc

        if False:
            # vector
            self.gl = vtk.vtkArrowSource()
        else:
            # simple arrow
            self.gl = vtk.vtkGlyphSource2D()
            self.gl.SetGlyphTypeToArrow()
            self.gl.FilledOff()
            print 'arrow center', self.gl.GetCenter(), '->',
            self.gl.SetCenter(0.5,0,0)
            print self.gl.GetCenter()

#Prueba para representar flechas 3d (descomentar)
#	cyl = vtk.vtkCylinderSource()				#añadido
#	cyl.SetResolution(6)					#añadido
#	cyl.SetRadius(.05)					#añadido
#	cyl.SetHeight(1)					#añadido
	
#	cylTrans = vtk.vtkTransform()				#añadido
#	cylTrans.Identity()					#añadido
#	cylTrans.RotateZ(90)					#añadido
#	cylTrans.Translate(0,-1,0)				#añadido

#	cylTransFilter = vtk.vtkTransformPolyDataFilter()	#añadido
#	cylTransFilter.SetInput(cyl.GetOutput())		#añadido
#	cylTransFilter.SetTransform(cylTrans)			#añadido
#	cone = vtk.vtkConeSource()				#añadido
#	cone.SetResolution(6)					#añadido
#	cone.SetCenter(2,0,0)					#añadido
#	cone.SetAngle(15)					#añadido

#	arrow = vtk.vtkAppendPolyData()				#añadido
#	arrow.AddInput(cylTransFilter.GetOutput())		#añadido
#	arrow.AddInput(cone.GetOutput())			#añadido
#	arrow.Update()						#añadido
#	self.gl = arrow						#añadido
#Prueba para representar flechas 3d

        self.lin = vtk.vtkGlyph3D()
        if self.data1.get('fielddomain') == 'cell': # vtk does not seem to support cell vectors
            self.lin.SetInput(self.cellcenters.GetOutput())#amañar cambio new
            #lutrange = self.src_vc.GetOutput().GetCellData().GetVectors().GetRange(-1)	#añadido
        else:
            self.lin.SetInput(self.src_vc.GetOutput())
            #lutrange = self.src_vc.GetOutput().GetPointData().GetVectors().GetRange(-1)#añadido


	lut = vtk.vtkLookupTable()				#añadido
	lut.SetRampToLinear()					#añadido
	lut.SetScaleToLinear()					#añadido
	# When using vector magnitude for coloring		#añadido
	lut.SetVectorModeToMagnitude()				#añadido
	lut.Build()						#añadido
	# When using a vector component for coloring		#añadido
	#lut.SetVectorModeToComponent()				#añadido
	#lut.SetVectorComponent(1)				#añadido


	if self.vectors is not None:				#añadido
            lutrange = self.vectors.GetRange(-1)		#añadido
            lut.SetTableRange(lutrange)				#añadido

        self.lin.SetSourceConnection(self.gl.GetOutputPort())
        self.lin.SetScaleModeToScaleByVector()
#        self.lin.SetScaleFactor(1.0)
        self.lin.SetColorModeToColorByVector() # flechas de cores
	self.lin.OrientOn()
	self.lin.Update()



        self.pdM = vtk.vtkPolyDataMapper()
        self.pdM.SetInputConnection(self.lin.GetOutputPort())
	#coloreado de vectores
#	self.pdM.SetScalarRange(lutrange)			#añadido
        self.pdM.ScalarVisibilityOn() 				#añadido
	self.pdM.SetLookupTable(lut)				#añadido
	self.pdM.InterpolateScalarsBeforeMappingOff()
#	self.pdM.UseLookupTableScalarRangeOn()
	self.pdM.Update()


      
        self.linA = vtk.vtkActor()
        self.linA.SetMapper(self.pdM)
 #       self.linA.GetProperty().SetColor(Plot.arrow_color)
    
    
#para mostrar surface e wireframe ao mesmo tempo
        self.wireM2 = vtk.vtkDataSetMapper()
        self.wireM2.SetInputConnection(self.src_vc.GetOutputPort())
        self.wireM2.ScalarVisibilityOff()
        self.wireA2 = vtk.vtkActor()
        self.wireA2.SetMapper(self.wireM2)
        self.wireA2.GetProperty().SetRepresentationToWireframe()
        self.wireA2.GetProperty().SetColor(Plot.edges_color)
                
#        self.wireA = vtk.vtkActor()
#        self.wireA.SetMapper(self.wireM)
#        self.wireA.GetProperty().SetRepresentationToSurface()
#        self.wireA.GetProperty().SetColor(Plot.edges_color)


#        self.rens[0].AddActor(self.wireA)
        self.add_opacity_2([self.linA,self.wireA2]) # Opacity: 100%/75%/50%/25%/0%
        self.rens[0].AddActor(self.wireA2)
        self.rens[0].AddActor(self.linA)
       
        if interactive:
            self.set_iren()
            if self.data1.get('fielddomain') == 'cell':
                self.clicker.set_point_cell('point') # así ok
                self.clicker.set_objects(self.cellcenters_click, self.rens[0], self.iren, self.widget) # ALPHA-vc
            else:
                self.clicker.set_point_cell(self.data1.get('fielddomain'))
                self.clicker.set_objects(self.src, self.rens[0], self.iren, self.widget) # ALPHA-vc
            self.clicker.set_props([self.wireA2])
            self.clicker.setup()

        newlast = self.read_params(struct) #####
        if newlast[0] is not None:
            self.lastscale = newlast[0]
        if newlast[1] is not None:
            self.lastmode = newlast[1]
        self.apply_params()

        for ren in self.rens: # WORKAROUND (aparecia non centrada) // + outline
            ren.ResetCamera()

	if self.vectors is not None:				#añadido
            self.scalarrange.local_set(lutrange)		#añadido
            self.add_scalarbar_1()				#añadido
            self.add_scalarbar_2(lut)				#añadido

        self.done = True

    def range_update3(self, range_): # to overwrite in subclasses
        self.pdM.SetScalarRange(range_)

    def read_params(self, struct):

        fail = (None,None)
        scale = None
        density = None

        ch = struct.get_children()

        if len(ch) != 2:
            self.data_error('Incorrect number of children in PlotVectorField options (2 needed)')
            return None

        nums = ch[0].get_elements()
        if len(nums) == 1:
            num = nums[0]
            numf = None
            try:
                numf = float(num)
            except ValueError:
                pass
            if numf is not None:
                scale = numf
            else:
                self.data_error('Error converting \'' + num + '\' to float')
                return fail
        else:
	#Calcula unha escala e escribe o dato no struct
            scale = self.calc_best_scale()                                   #añadido
            ch[0].set_elements([str(scale)])				     #añadido
            self.panel_widgets.update_widget_struct(ch[0])		     #añadido
        #    self.data_error('Incorrect number of elements in scale (1 needed)')
        #    return fail

        nums = ch[1].get_elements()
        if len(nums) == 1:
            num = nums[0]
            numf = None
            try:
                numf = float(num)
            except ValueError:
                pass
            if numf is not None:
                density = numf
            else:
                self.data_error('Error converting \'' + num + '\' to float')
                return fail
        else:
            self.data_error('Incorrect number of elements in density (1 needed)')
            return fail

        return (scale, density/100.0)

    def apply_ini_params(self):                                 #añadido
        if self.lastscale is not None:                          #añadido
            self.bestScale = self.calc_best_scale()             #añadido
            self.lin.SetScaleFactor(self.bestScale)             #añadido
        res = self.apply_data(self.lastmode)                    #añadido

    def calc_best_scale(self):                                  #añadido
	if self.maxNorm is not None:				#añadido
            xdist = (self.bounds[1]-self.bounds[0])             #añadido
            ydist = (self.bounds[3]-self.bounds[2])             #añadido
            zdist = (self.bounds[5]-self.bounds[4])             #añadido
            maxdist = xdist					#añadido
            if maxdist<ydist:					#añadido
		maxdist = ydist					#añadido
            if maxdist<zdist:					#añadido
		maxdist = zdist 				#añadido
            #meddist = (xdist+ydist+zdist)/3			#añadido
            #maxdist = sqrt(((xdist*xdist)+(ydist*ydist)+(zdist*zdist))/3)#añadido
            if self.maxNorm == 0:				#añadido
		return 1.0					#añadido
            else:						#añadido
		return self.round_to_1(maxdist/(self.maxNorm*20))#añadido
	else:
            return 1.0


#redondea al primer digito significativo
    def round_to_1(self,x):					#añadido
	from math import floor, log10				#añadido
	return round(x, -int(floor(log10(x))))			#añadido



    def apply_params(self):
	if self.lastscale is not None:
            self.lin.SetScaleFactor(self.lastscale)
	else:
            self.lin.SetScaleFactor(self.bestscale)
        res = self.apply_data(self.lastmode)



#### vector density ####



    def update(self, struct):
        newlast = self.read_params(struct) #####
        changed = [False,False]
        if newlast[0] is not None:
            if self.lastscale != newlast[0]:
                changed[0] = True
            self.lastscale = newlast[0]
        if newlast[1] is not None:
            if self.lastmode != newlast[1]:
                changed[1] = True
            self.lastmode = newlast[1]
        if changed[1]:
            self.src_update1b({'changed': True})
        elif changed[0]:
            self.lin.SetScaleFactor(self.lastscale)
        if changed[0] or changed[1]:
            self.widget.Render()



    def construct_data(self, src):
        o = src.GetOutput()
        ugrid = vtk.vtkUnstructuredGrid()
        ugrid.SetPoints(o.GetPoints())
        ugrid.SetCells(o.GetCellTypesArray(), o.GetCellLocationsArray(), o.GetCells())
        #ugrid.ShallowCopy(o)
        ##ugrid.DeepCopy(o)
        
        if self.data1.get('fielddomain') == 'cell':
            self.vectors = o.GetCellData().GetVectors()
            pc = 1
        elif self.data1.get('fielddomain') == 'point':
            self.vectors = o.GetPointData().GetVectors()
            pc = 0
        else:
            self.vectors = None


	#Limites dos eixos
	self.bounds = self.src.GetOutput().GetBounds()                  #añadido
	#Maximo tamaño de celda
	#self.cellMaxSize = ugrid.GetMaxCellSize()
	self.maxNorm = None						#añadido
        # engadir aqui os orixinais a ugrid ...
        if self.vectors is not None:
	#Maximo valor da norma dos vectores
            self.maxNorm = self.vectors.GetMaxNorm()                    #añadido
            v = vtk.vtkDoubleArray()
            v.DeepCopy(self.vectors)
            v.SetName(aname1)
            if pc == 1:
                data = ugrid.GetCellData()
            elif pc == 0:
                data = ugrid.GetPointData()
            data.AddArray(v) # replaces if exists


        return ugrid



    def apply_data(self, mode):
    
        if mode is None:
            return False

        if mode > 1.0:
            mode = 1.0

        if mode < 0.0:
            mode = 0.0


        if self.data1.get('fielddomain') == 'cell':
            pc = 1
        elif self.data1.get('fielddomain') == 'point':
            pc = 0
        else:
            return False
        
        if mode == 1.0:
            self.src_vc.Assign(aname1, 1, pc) # 0 scalar 1 vector ; 0 point 1 cell
            self.src_vc.Update() # necesario
            return True

        if mode == self.esta: # xa estaba calculado
            self.src_vc.Assign(aname2, 1, pc) # 0 scalar 1 vector ; 0 point 1 cell
            self.src_vc.Update() # necesario
            return True

        if False: # choose method: sequential or random
            a = PlotVectorField.null_vectors(self.vectors, pc, aname2, mode)
        else:
            a = PlotVectorField.null_vectors_random(self.vectors, pc, aname2, mode)
        
        if a is None:
            return False
        
        if pc == 1:
            data = self.ugrid.GetCellData()
        elif pc == 0:
            data = self.ugrid.GetPointData()

        data.AddArray(a) # replaces if exists


        self.src_vc.Assign(aname2, 1, pc) # 0 scalar 1 vector ; 0 point 1 cell
        
        self.esta = mode
        
        self.src_vc.Update()

        return True



    # factor: 0.0(ningun) ... 1.0(todos)
    @staticmethod
    def null_vectors(vectors, pc, aname, factor):
        if vectors is None:
            return None

        if factor >= 1.0:
            return vectors

        decimated = vtk.vtkDoubleArray()

        decimated.DeepCopy(vectors)

        decimated.SetName(aname)

        tuples = decimated.GetNumberOfTuples()
        components = decimated.GetNumberOfComponents()

        if (factor <= 0.0):
            for i in xrange(tuples*components):
                decimated.SetValue(i, 0.0)
            return decimated

        nonzero = 0

        for i in xrange(tuples):
            if i == 0:
                if factor > 0.0:
                    nonzero = nonzero + 1

                else:
                    for j in xrange(components):
                        decimated.SetValue(i*components+j, 0.0)
            else:
                if float(nonzero)/float(i) <= factor:
                    nonzero = nonzero + 1
                else:
                    for j in xrange(components):
                        decimated.SetValue(i*components+j, 0.0)

        return decimated



    @staticmethod
    def null_vectors_random(vectors, pc, aname, factor):
        if vectors is None:
            return None

        if factor >= 1.0:
            return vectors

        decimated = vtk.vtkDoubleArray()

        decimated.DeepCopy(vectors)

        decimated.SetName(aname)

        tuples = decimated.GetNumberOfTuples()
        components = decimated.GetNumberOfComponents()

        if (factor <= 0.0):
            for i in xrange(tuples*components):
                decimated.SetValue(i, 0.0)
            return decimated

        needed = int(factor * tuples)

        # random sampling without replacement
        to_erase = random.sample(xrange(tuples), tuples-needed)

        # anula vectores marcados para borrar
        for i in to_erase:
            for j in xrange(components):
                decimated.SetValue(i*components+j, 0.0)

        return decimated

	xdist = (self.bounds[1]-self.bounds[0])
