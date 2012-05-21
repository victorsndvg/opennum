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
        
        self.point_locator = None
        self.point_locator_pending = True
        
        self.mode = 0



    def set_mode(self, mode):
        if mode == 'scalars':
            self.mode = 0
        elif mode == 'vectors':
            self.mode = 1



    def set_props(self, props):
        self.props = vtk.vtkPropCollection()
        for prop in props:
            self.props.AddItem(prop)



    def set_objects(self, source, renderer, iren, widget):
        self.src = source
        self.renderer = renderer
        self.iren = iren
        self.widget = widget



    # src object changes: another object
    def change_src(self, source):
        self.src = source
        self.CLselF.SetInputConnection(self.src.GetOutputPort())
        self.point_locator_pending = True
        self.clear(False)



    # src object is updated: same object, different data
    def update_src(self):
        self.point_locator_pending = True
        self.clear(False)



    def clear(self, render=True):
        self.CLselS.RemoveAllIDs()
        if render:
            self.widget.Render()



    def setup(self):
    
        self.CLselS = vtk.vtkSelectionSource()
        self.CLselS.SetContentType(4) # vtkSelection:: #1 GLOBALIDS(nada) #3 VALUES(nada) #4 INDICES(varios)
        self.CLselS.SetFieldType(1) # vtkSelection:: #0 CELL #1 POINT
        self.CLselS.SetContainingCells(0) # para non extraer tamén as celdas que conteñen o punto dado

        self.CLselF = vtk.vtkExtractSelectedIds()
        self.CLselF.SetInputConnection(self.src.GetOutputPort())
        self.CLselF.SetSelectionConnection(self.CLselS.GetOutputPort())
        
# marcar puntos
        if True:
            # puntos. tamanho en pantalla constante
#            self.CLPointsV = vtk.vtkVertexGlyphFilter()
#            self.CLPointsV.SetInputConnection(self.CLselF.GetOutputPort())
#            self.CLPointsM = vtk.vtkPolyDataMapper()
#            self.CLPointsM.SetInputConnection(self.CLPointsV.GetOutputPort())
#            self.CLPointsM.ScalarVisibilityOff()
            self.CLPointsM = vtk.vtkDataSetMapper()
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
        self.CLlabelsbM = vtk.vtkLabeledDataMapper()
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
        self.point_locator = vtk.vtkPointLocator()
        self.point_locator_pending = True        

        self.iren.AddObserver("LeftButtonPressEvent", self.ButtonPress)
        self.iren.AddObserver("LeftButtonReleaseEvent", self.ButtonRelease)

        self.picker = vtk.vtkPropPicker()
#        picker.SetTolerance(0.005)
        self.picker.AddObserver("EndPickEvent", self.EndPick)
        self.iren.SetPicker(self.picker)



    def ButtonPress(self, obj, event):
        xypos = self.iren.GetEventPosition()
        print 'leftPress', event, 'repeat', self.iren.GetRepeatCount(), xypos
#        self.picker.Pick(xypos[0], xypos[1], 0, self.rens[0])



# funciona en Windows ( se llama a LeftButtonReleaseEvent sólo para double click )
    def ButtonRelease(self, obj, event):
        xypos = self.iren.GetEventPosition()
        print 'leftRel', event, 'repeat', self.iren.GetRepeatCount(), xypos
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
        print 'pos', pos, there_is
        
        if not there_is:
            return

        if self.point_locator_pending: # así no inicializa varias veces innecesariamente
            self.point_locator.SetDataSet(self.src.GetOutput())
            self.point_locator_pending = False

        pointid = self.point_locator.FindClosestPoint(pos)
        print 'point_id', pointid
        
        if pointid < 0:
            return

        self.CLlabelsbA.SetVisibility(1)
        #self.CLselS.RemoveAllIDs() # comentado para acumular
        self.CLselS.AddID(0, pointid) # -1 (all pieces) ou 0

        self.widget.Render()
