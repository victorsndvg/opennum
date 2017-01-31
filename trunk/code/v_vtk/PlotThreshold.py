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



class PlotThreshold(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_scalarbar_1()
        self.add_outline_1()
        
        self.add_swe_1(selection=1) # wireframe/surface/surface+edges
        self.add_opacity_1(selection=0) # Opacity: 100%/75%/50%/25%/0%
        
        self.clicker = None
        if interactive:
            self.clicker = ClickLabel.ClickLabel()

        #self.scalarrange.mode_set(0) # tiña rango nulo => non actualiza rango
        #self.scalarrange.mode_mutable_set(False) # always local scalar range



    def get_options(self):
        ops = {u'title':'Threshold'}
        if interactive:
            ops[u'interactor']=True
        return ops



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        if changes.get('changed'):
            self.update_outline(self.src)
        if changes.get('new'):
            self.wireT.SetInputConnection(self.src.GetOutputPort())
            #self.wireM.SetInputConnection(self.src.GetOutputPort()) # en copy_params
        if changes.get('changed'):
            self.rango = self.src.GetOutput().GetScalarRange() # self.rango necesario # independentemente
            self.scalarrange.local_set(self.rango)
        #self.src_update_clicker(self.clicker, self.src, changes) # en copy_params
        if changes.get('changed'):
            self.copy_params(self.struct)
        return True



    def range_update3(self, range):
        self.wireM.SetScalarRange(range)
        self.wireM.GetLookupTable().SetTableRange(range)
        #self.rango = range # optional (posto => posibles rangos externos. quitado => so rangos locais para
        if not self.is_done():
            return
        #self.copy_params(self.struct) # xa chamado antes/despois



    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        # creates self.src
        if not self.call_src():
            return

        self.add_outline_2(self.src)

        self.wireT = vtk.vtkThreshold()
        self.wireT.SetInputConnection(self.src.GetOutputPort())
        #self.wireT.ThresholdBetween(0.1,0.2)

        self.wireM = vtk.vtkDataSetMapper()
        self.wireM.SetInputConnection(self.src.GetOutputPort())
        #self.wireM.SetInputConnection(self.wireT.GetOutputPort())

        self.rango = self.src.GetOutput().GetScalarRange() # self.rango necesario # independentemente
        self.scalarrange.local_set(self.rango)

# reverse rainbow [red->blue] -> [blue->red]
        look = self.wireM.GetLookupTable()

        self.wireA = vtk.vtkActor()
        self.wireA.SetMapper(self.wireM)
        self.wireA.GetProperty().SetRepresentationToSurface()
        self.wireA.GetProperty().SetColor(Plot.edges_color)
        self.wireA.GetProperty().SetEdgeColor(Plot.edges_color)
        
        self.add_swe_2(self.wireA) # wireframe/surface/surface+edges
        self.add_opacity_2([self.wireA]) # Opacity: 100%/75%/50%/25%/0%
        self.rens[0].AddActor(self.wireA) # malla con cores

        if interactive:
            self.set_iren()
            self.clicker.set_point_cell(self.data1.get('fielddomain'))
            self.clicker.set_objects(self.src, self.rens[0], self.iren, self.widget)
            self.clicker.set_props([self.wireA])
            self.clicker.setup()

        self.add_scalarbar_2(look)

        self.copy_params(struct)

        self.done = True



# fai falta
    def update(self, struct):
        self.copy_params(struct)
        self.widget.Render()



    def copy_params(self, struct):

        ch = struct.get_children()

        if len(ch) != 2:
            self.data_error('Incorrect number of childs in PlotThreshold (2 needed)')
            return
        
        upper = lower = None
        err = False

    # upper
        nums = ch[0].get_elements()
        if len(nums) == 1:
            num = nums[0]
            try:
                upper = float(num)
            except ValueError:
                pass
            if upper is None:
                self.data_error('Error converting \'' + num + '\' to float')
                err = True
        elif len(nums) == 0:
            pass
        else:
            self.data_error('Incorrect number of elements in upper limit (0 or 1 needed)')
            err = True
            

    # lower
        nums = ch[1].get_elements()
        if len(nums) == 1:
            num = nums[0]
            try:
                lower = float(num)
            except ValueError:
                pass
            if lower is None:
                self.data_error('Error converting \'' + num + '\' to float')
                err = True
        elif len(nums) == 0:
            pass
        else:
            self.data_error('Incorrect number of elements in lower limit (0 or 1 needed)')
            err = True

        if err is True:
            return

        # necesario change_src, o como minimo change_src/update_src

        if upper is None and lower is None:
            self.wireM.SetInputConnection(self.src.GetOutputPort())
            self.scalarrange.local_set(self.rango)
            #self.wireM.SetScalarRange(self.rango)
            if interactive:
                self.clicker.change_src(self.src)
        if upper is None and lower is not None:
            self.wireT.ThresholdByUpper(lower) # returns cells greater than lower
            self.wireM.SetInputConnection(self.wireT.GetOutputPort())
            self.scalarrange.local_set((lower,self.rango[1]))
            #self.wireM.SetScalarRange((lower,self.rango[1]))
            if interactive:
                self.clicker.change_src(self.wireT)
        if upper is not None and lower is None:
            self.wireT.ThresholdByLower(upper) # returns cells less than upper
            self.wireM.SetInputConnection(self.wireT.GetOutputPort())
            self.scalarrange.local_set((self.rango[0],upper))
            #self.wireM.SetScalarRange((self.rango[0],upper))
            if interactive:
                self.clicker.change_src(self.wireT)
        if upper is not None and lower is not None:
            self.wireT.ThresholdBetween(lower,upper)
            self.wireM.SetInputConnection(self.wireT.GetOutputPort())
            self.scalarrange.local_set((lower,upper))
            #self.wireM.SetScalarRange((lower,upper))
            if interactive:
                self.clicker.change_src(self.wireT)
