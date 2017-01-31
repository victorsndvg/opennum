#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
import wx_version
import wx
import vtk



class PlotMesh(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_outline_1()
        
        self.add_swe_1(selection=0)



    def get_options(self):
        return {u'title':'Triangulation'}



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        if changes.get('changed'):
            self.update_outline(self.src)
        if changes.get('new'):
            self.wireM.SetInputConnection(self.src.GetOutputPort())
        return True



    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return
        
        # creates self.src
        if not self.call_src():
            return

        # a malla
        self.wireM = vtk.vtkDataSetMapper()
        self.wireM.SetInputConnection(self.src.GetOutputPort())
        self.wireM.ScalarVisibilityOff()

        self.wireA = vtk.vtkActor()
        self.wireA.SetMapper(self.wireM)
        self.wireA.GetProperty().SetRepresentationToWireframe()
        self.wireA.GetProperty().SetColor(Plot.mesh_color)
        self.wireA.GetProperty().SetEdgeColor(Plot.edges_color)
        
        self.add_swe_2(self.wireA)

        self.add_outline_2(self.src)
        
        self.rens[0].AddActor(self.wireA) # surface/wireframe/surface+edges

        self.done = True



#    def update(self, struct):
#        pass
