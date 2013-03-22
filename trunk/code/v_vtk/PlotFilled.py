#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
import wx_version
import wx
import vtk
import ClickLabel3 as ClickLabel



# mostrar etiquetas con el valor del campo en los puntos donde se hace 'doble click'
interactive = True



class PlotFilled(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_scalarbar_1()
        self.add_outline_1()
        
        self.add_swe_1(selection=1) # wireframe/surface/surface+edges

        self.add_opacity_1(selection=0) # Opacity: 100%/75%/50%/25%/0%
        
        self.clicker = None

#        self.add_time_1()



    def get_options(self):
        ops = {u'title':'Filled'}
        if interactive:
            ops[u'interactor']=True
        return ops



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        if changes.get('changed'):
            self.update_outline(self.src)
        if changes.get('new'):
            self.wireM.SetInputConnection(self.src.GetOutputPort())
        if changes.get('changed'):
            self.scalarrange.local_set(self.src.GetOutput().GetScalarRange())
        self.src_update_clicker(self.clicker, self.src, changes)
        return True



    def range_update3(self, range):
        self.wireM.SetScalarRange(range)



    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        # creates self.src
        if not self.call_src():
            return

        self.add_outline_2(self.src)

# test nrc. es visible con este cambio:
#        self.refsT = vtk.vtkThreshold()
#        self.refsT.SetInputConnection(self.src.GetOutputPort())
#        self.refsT.ThresholdByUpper(1.0)

        self.wireM = vtk.vtkDataSetMapper()
        self.wireM.SetInputConnection(self.src.GetOutputPort())

        # test
        if self.data1.get('fielddomain') == 'cell':
            self.wireM.SetScalarModeToUseCellData()
        elif self.data1.get('fielddomain') == 'point':
            self.wireM.SetScalarModeToUsePointData()

#        self.wireM.SetInputConnection(self.refsT.GetOutputPort()) # test nrc.

        self.scalarrange.local_set(self.src.GetOutput().GetScalarRange())
    
# reverse rainbow [red->blue] -> [blue->red]
        look = self.wireM.GetLookupTable()

#para mostrar surface e wireframe ao mesmo tempo
        self.wireA = vtk.vtkActor()
        self.wireA.SetMapper(self.wireM)
        self.wireA.GetProperty().SetRepresentationToSurface()
        self.wireA.GetProperty().SetColor(Plot.edges_color)
        self.wireA.GetProperty().SetEdgeColor(Plot.edges_color)

        self.add_swe_2(self.wireA) # wireframe/surface/surface+edges
        self.add_opacity_2([self.wireA]) # wireframe/surface/surface+edges
	axes = vtk.vtkAxesActor()
        self.rens[0].AddActor(self.wireA) # malla con cores

        if interactive:
            self.set_iren()
            self.clicker = clicker = ClickLabel.ClickLabel()
            clicker.set_point_cell(self.data1.get('fielddomain'))
            clicker.set_objects(self.src, self.rens[0], self.iren, self.widget)
            clicker.set_props([self.wireA])
            clicker.setup()

        self.add_scalarbar_2(look)

        self.done = True



# non fai falta
#    def update(self, struct):
#        self.widget.Render()
