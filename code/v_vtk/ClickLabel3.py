#!/usr/bin/env python
# -*- coding: utf-8 -*-



import vtk
import Plot



# mostrar puntos y etiquetas con el valor del campo en los puntos donde se hace 'doble click'



class ClickLabel():



    def __init__(self):
        self.src = None
        self.renderer = None
        self.iren = None
        self.widget = None
        self.props = None
        
        self.CLselF = None
        
        self.locator = None
        self.locator_pending = True
        
        self.mode = 0 # 0 scalars 1 vectors
        self.pointcell = 0 # 0 point 1 cell
        self.click = 1 # 'double' click



    # si llamar, antes de setup()
    def set_point_cell(self, pointcell):
        if pointcell == 'point':
            self.pointcell = 0
        elif pointcell == 'cell':
            self.pointcell = 1
        else:
            print 'ClickLabel3.py: field domain out of range'



    # si llamar, antes de setup()
    def set_mode(self, mode):
        if mode == 'scalars':
            self.mode = 0
        elif mode == 'vectors':
            self.mode = 1
        else:
            print 'ClickLabel3.py: field type out of range'



    # llamar en cualquier momento:
    def set_click(self, mode):
        if mode == 0: # single left click
            self.click = 0
        elif mode == 1: # tricky double click - Windows
            self.click = 1
        else:
            print 'ClickLabel3.py: click mode out of range'




    # llamar en cualquier momento
    def set_props(self, props):
        if props is None:
            self.props = None
        else:
            self.props = vtk.vtkPropCollection()
            for prop in props:
                self.props.AddItem(prop)



    # llamar antes de setup()
    def set_objects(self, source, renderer, iren, widget):
        self.src = source
        self.renderer = renderer
        self.iren = iren
        self.widget = widget



    # src object changes: another object
    def change_src(self, source):
        self.src = source
        self.CLselF.SetInputConnection(self.src.GetOutputPort())
        self.locator_pending = True
        self.clear(False)



    # src object is updated: same object, different data
    def update_src(self):
        self.locator_pending = True
        self.clear(False)



    # limpia los puntos
    def clear(self, render=True):
        self.CLselS.RemoveAllIDs()
        if render:
            self.widget.Render()



    # inicializa el objeto
    def setup(self):
        
        # temporal HACK does not work
        #self.cellcenters = None
        #if self.pointcell == 1:
        #    self.cellcenters = vtk.vtkCellCenters()
        #    self.cellcenters.SetInputConnection(self.src.GetOutputPort())
        #    self.pointcell = 0
    
        self.CLselS = vtk.vtkSelectionSource()
        self.CLselS.SetContentType(4) # vtkSelection:: #1 GLOBALIDS(nada) #3 VALUES(nada) #4 INDICES(varios)
        if self.pointcell == 0:
            self.CLselS.SetFieldType(1) # vtkSelection:: #0 CELL #1 POINT
            self.CLselS.SetContainingCells(0) # para non extraer tamén as celdas que conteñen o punto dado
        elif self.pointcell == 1:
            self.CLselS.SetFieldType(0) # vtkSelection:: #0 CELL #1 POINT

        self.CLselF = vtk.vtkExtractSelectedIds()
#        if self.cellcenters is not None:
#            self.CLselF.SetInputConnection(self.cellcenters.GetOutputPort())
#        else:
#            self.CLselF.SetInputConnection(self.src.GetOutputPort())
        
        self.CLselF.SetInputConnection(self.src.GetOutputPort())
        self.CLselF.SetSelectionConnection(self.CLselS.GetOutputPort())
        
        if self.pointcell == 1:
            self.cellcenters = vtk.vtkCellCenters()
            self.cellcenters.VertexCellsOn() # que ?
            self.cellcenters.SetInputConnection(self.CLselF.GetOutputPort())
            
        
# marcar puntos
        if True:
            # puntos. tamanho en pantalla constante
#            self.CLPointsV = vtk.vtkVertexGlyphFilter()
#            self.CLPointsV.SetInputConnection(self.CLselF.GetOutputPort())
#            self.CLPointsM = vtk.vtkPolyDataMapper()
#            self.CLPointsM.SetInputConnection(self.CLPointsV.GetOutputPort())
#            self.CLPointsM.ScalarVisibilityOff()
            self.CLPointsM = vtk.vtkDataSetMapper()
            if self.pointcell == 1:
                self.CLPointsM.SetInputConnection(self.cellcenters.GetOutputPort())
            else:
                self.CLPointsM.SetInputConnection(self.CLselF.GetOutputPort())
            self.CLPointsM.ScalarVisibilityOff()
            self.CLPointsA = vtk.vtkActor()
            self.CLPointsA.SetMapper(self.CLPointsM)
            self.CLPointsA.GetProperty().SetRepresentationToPoints()
            self.CLPointsA.GetProperty().SetPointSize(3.0)
            self.CLPointsA.GetProperty().SetColor(Plot.points_color)
            self.renderer.AddActor(self.CLPointsA)
        else:
            # esferas. tamanho en pantalla variable
            self.CLglyph = vtk.vtkSphereSource()
            self.CLPointsG = vtk.vtkGlyph3D()
            self.CLPointsG.SetInputConnection(self.CLselF.GetOutputPort())
            self.CLPointsG.SetSourceConnection(self.CLglyph.GetOutputPort())
            self.CLPointsG.ScalingOff()
            #self.CLPointsG.SetScaleModeToDataScalingOff()
            self.CLPointsM = vtk.vtkPolyDataMapper()
            self.CLPointsM.SetInputConnection(self.CLPointsG.GetOutputPort())
            self.CLPointsM.ScalarVisibilityOff()
            self.CLPointsA = vtk.vtkActor()
            self.CLPointsA.SetMapper(self.CLPointsM)
            self.CLPointsA.GetProperty().SetColor(Plot.points_color)
            self.renderer.AddActor(self.CLPointsA)
        
# labels
        # protesta por que:
        # ..\archive\VTK\Rendering\vtkLabeledDataMapper.cxx, line 377
        # vtkLabeledDataMapper (094D4C80): Could not find label array (index 0) in input.        
        self.CLlabelsbM = vtk.vtkLabeledDataMapper()

#FIX FIX FIX
        if self.pointcell == 1:
            #self.cellcenters = vtk.vtkCellCenters()
            #self.cellcenters.SetInputConnection(self.CLselF.GetOutputPort())
            #self.CLlabelsbM.SetInputConnection(self.cellcenters.GetOutputPort())
            
            self.CLlabelsbM.SetInputConnection(self.cellcenters.GetOutputPort())
        else:
            self.CLlabelsbM.SetInputConnection(self.CLselF.GetOutputPort())
            
        # self.CLlabelsbM.SetLabelFormat("%g")
        if self.mode == 0:
            self.CLlabelsbM.SetLabelModeToLabelScalars()
        elif self.mode == 1:
            self.CLlabelsbM.SetLabelModeToLabelVectors()
        self.CLlabelsbM.GetLabelTextProperty().SetColor(Plot.label_color)

        self.CLlabelsbA = vtk.vtkActor2D()
        self.CLlabelsbA.SetMapper(self.CLlabelsbM)
#        self.CLlabelsbA.SetVisibility(0)
        self.renderer.AddActor(self.CLlabelsbA)
        
        # point locator
        if self.pointcell == 0:
            self.locator = vtk.vtkPointLocator()
        elif self.pointcell == 1:
            self.locator = vtk.vtkCellLocator()

        self.locator_pending = True

        if self.click == 0:
            self.iren.AddObserver("LeftButtonPressEvent", self.ButtonPress1)
        elif self.click == 1:
            self.iren.AddObserver("LeftButtonPressEvent", self.ButtonPress2)
            self.iren.AddObserver("LeftButtonReleaseEvent", self.ButtonRelease2)

        self.picker = vtk.vtkPropPicker()
#        picker.SetTolerance(0.005)
        self.picker.AddObserver("EndPickEvent", self.EndPick)
        self.iren.SetPicker(self.picker)



    def ButtonPress1(self, obj, event):
        xypos = self.iren.GetEventPosition()
        print 'leftPress', event, 'repeat', self.iren.GetRepeatCount(), xypos
        self.do_pick(xypos)



    def ButtonPress2(self, obj, event):
        xypos = self.iren.GetEventPosition()
        print 'leftPress', event, 'repeat', self.iren.GetRepeatCount(), xypos



    # funciona en Windows ( se llama a LeftButtonReleaseEvent sólo para double click )
    def ButtonRelease2(self, obj, event):
        xypos = self.iren.GetEventPosition()
        print 'leftRel', event, 'repeat', self.iren.GetRepeatCount(), xypos
        self.do_pick(xypos)



    def do_pick(self, xypos=None, do_print=False):
        if xypos is None:
            xypos = self.iren.GetEventPosition()
        if do_print:
            print xypos
        if self.props is None:
            self.picker.Pick(xypos[0], xypos[1], 0, self.renderer)
        else:
            self.picker.PickProp(xypos[0], xypos[1], self.renderer, self.props)



    def EndPick(self, obj, event):
        a = self.picker.GetActor()
        #print a
        pos = self.picker.GetPickPosition()
        prop = self.picker.GetViewProp()
        there_is = prop is not None
        print 'pos', pos, 'there is', there_is
        
        if not there_is:
            self.clear()
            return

#        print self.locator
        
        if self.locator_pending: # así no inicializa varias veces innecesariamente
            self.locator.SetDataSet(self.src.GetOutput())
            self.locator_pending = False

        if self.pointcell == 0: # point
            point_id = self.locator.FindClosestPoint(pos)
            print 'point_id', point_id
            
            if point_id < 0:
                return
    
            self.CLlabelsbA.SetVisibility(1)
            #self.CLselS.RemoveAllIDs() # comentado para acumular
            self.CLselS.AddID(0, point_id) # -1 (all pieces) ou 0
    
            self.widget.Render()

        elif self.pointcell == 1: # cell
            #closest=[0.0,0.0,0.0]
            #cellid = -1
            #subid = 0
            #dist2 = 0.0
            #print self.locator
            #print dir(self.locator)
            # no funciona: metodo no encontrado: el codigo en C++ lo tiene, en Python no?
            #self.locator.FindClosestPoint(pos,closest,cellid,subid,dist2)
            #print 'cell:', pos, closest, subid, dist2
            
            # no existe el método FindCell !!!
            #tol2 = 1
            #subId = 0
            #pcoords = [0.0, 0.0, 0.0]
            #weights = [0.0, 0.0, 0.0]
            #cell_id = self.src.GetOutput().FindCell(pos, None, -1, tol2, subId, pcoords, weights)
            #print 'cell_id 1', cell_id

            # no soluciona
            #self.locator.SetTolerance(1.0) # absolute in world coordinates to perform geometric operations
            
            cell_id = self.locator.FindCell(pos)
            print 'cell_id', cell_id
            
            if cell_id < 0:
                return

            self.CLlabelsbA.SetVisibility(1)
            #self.CLselS.RemoveAllIDs() # comentado para acumular
            self.CLselS.AddID(0, cell_id) # -1 (all pieces) ou 0

            self.widget.Render()
