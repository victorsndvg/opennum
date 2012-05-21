#!/usr/bin/env python
# -*- coding: utf-8 -*-



import vtk
import Plot



# mostrar etiquetas con el valor del campo en los puntos donde se hace 'doble click'



class ClickLabel():



    def __init__(self):
        self.src = None
        self.renderer = None
        self.iren = None
        self.widget = None
        
        self.CLselF = None



    def set_objects(self, source, renderer, iren, widget):
        self.src = source
        self.renderer = renderer
        self.iren = iren
        self.widget = widget



    def change_src(self, source):
        self.src = source
        self.CLselF.SetInputConnection(self.src.GetOutputPort())
        self.clear(False)



    # src object is updated: same object, different data
    def update_src(self):
        pass
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
 
        self.CLlabelsbM = vtk.vtkLabeledDataMapper()
        self.CLlabelsbM.SetInputConnection(self.CLselF.GetOutputPort())
        # self.CLlabelsbM.SetLabelFormat("%g")
        self.CLlabelsbM.SetLabelModeToLabelScalars()
        self.CLlabelsbM.GetLabelTextProperty().SetColor(Plot.label_color)

        self.CLlabelsbA = vtk.vtkActor2D()
        self.CLlabelsbA.SetMapper(self.CLlabelsbM)
#        self.CLlabelsbA.SetVisibility(0)
        self.renderer.AddActor(self.CLlabelsbA)

        self.iren.AddObserver("LeftButtonPressEvent", self.ButtonPress)
        self.iren.AddObserver("LeftButtonReleaseEvent", self.ButtonRelease)

        self.picker = vtk.vtkPointPicker()
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
        self.picker.Pick(xypos[0], xypos[1], 0, self.renderer)



    def EndPick(self, obj, event):
        #print 'EndPick: event', event
        points = self.picker.GetPickedPositions()
        pos = self.picker.GetPickPosition()
        print 'num', points.GetNumberOfPoints(), 'pos', pos

        pointid = self.picker.GetPointId()
        print 'pointid', pointid
        #print self.picker.GetSelectionPoint()
        #print self.picker.GetPickPosition()
        if pointid < 0:
            return

        self.CLlabelsbA.SetVisibility(1)
#        self.CLselS.RemoveAllIDs() # comentado para acumular
        self.CLselS.AddID(0, pointid) # -1 (all pieces) ou 0

        self.widget.Render()
