#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
import wx_version
import wx
import vtk
import ClickLabel3 as ClickLabel
import math

import sourceVTK2


# mostrar etiquetas con el valor del campo en los puntos donde se hace 'doble click'
interactive = True



class PlotVectorComponents(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_scalarbar_1()
        self.add_outline_1()
        
        self.add_swe_1(selection=1) # wireframe/surface/surface+edges
        self.add_opacity_1(selection=0) # Opacity: 100%/75%/50%/25%/0%
# pasado ao menu:
#        choices = ['X comp.', 'Y comp.', 'Z comp.', 'Modulus']
#        self.cbl = wx.Choice(self.plotbar, wx.ID_ANY, choices = choices)
#        self.cbl.SetSelection(0) # in windows appears without selection
#        self.plotbar.add(self.cbl)
#        self.Bind(wx.EVT_CHOICE, self.cl, self.cbl)

        self.clicker = None

#        self.add_time_1()

        self.esta = [False, False, False, False]

        self.lastmode = -1

        self.component_names = ['1st','2nd','3rd','Modulus']



    def get_options(self):
        ops = {u'title':'Vector components'}
        if interactive:
            ops[u'interactor']=True
        return ops



#    def cl(self, event):
#        if not self.done:
#            return
#
#        sel = self.cbl.GetSelection()
#        
#        self.lastmode = sel
#
#        if sel < 0 or sel > 3:
#            return
#        
#        self.src_update1b({'changed': True})
#
#        self.widget.Render()



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        if changes.get('changed'):
            self.esta = [False, False, False, False] # obliga a recalcular ahora que cambian los datos
            self.ugrid = self.construct_data(self.src)
            self.src_vc.SetInput(self.ugrid)
        return self.src_update1b(changes)



    def src_update1b(self, changes):
        if changes.get('changed'):
            res = self.apply_data(self.lastmode) # lida seleccion
        if changes.get('changed'):
            self.update_outline(self.src_vc)
        if changes.get('new'):
            self.wireM.SetInputConnection(self.src_vc.GetOutputPort())
        if changes.get('changed'):
            self.scalarrange.local_set(self.src_vc.GetOutput().GetScalarRange())
        self.src_update_clicker(self.clicker, self.src_vc, changes)

        self.data1['vector_component'] = False
        if self.lastmode >= 0 and self.lastmode < len(self.component_names):
            self.data1['vector_component'] = self.component_names[self.lastmode]
        self.update_legend_data()
        
        return True



    def range_update3(self, range_):
        self.wireM.SetScalarRange(range_)




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
        
        self.lastmode = self.get_selected(struct)
        self.apply_data(self.lastmode)

        self.add_outline_2(self.src_vc)
 
# test nrc. es visible con este cambio:
#        self.refsT = vtk.vtkThreshold()
#        self.refsT.SetInputConnection(self.src.GetOutputPort())
#        self.refsT.ThresholdByUpper(1.0)

        self.wireM = vtk.vtkDataSetMapper()
#        self.wireM.SetInputConnection(self.src.GetOutputPort())
        self.wireM.SetInputConnection(self.src_vc.GetOutputPort())

        # test
        if self.data1.get('fielddomain') == 'cell':
            self.wireM.SetScalarModeToUseCellData()
        elif self.data1.get('fielddomain') == 'point':
            self.wireM.SetScalarModeToUsePointData()

#        self.wireM.SetInputConnection(self.refsT.GetOutputPort()) # test nrc.

        self.scalarrange.local_set(self.src_vc.GetOutput().GetScalarRange())
    
# reverse rainbow [red->blue] -> [blue->red]
        look = self.wireM.GetLookupTable()

#para mostrar surface e wireframe ao mesmo tempo
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
            self.clicker = clicker = ClickLabel.ClickLabel()
            clicker.set_point_cell(self.data1.get('fielddomain'))
            clicker.set_objects(self.src_vc, self.rens[0], self.iren, self.widget)
            clicker.set_props([self.wireA])
            clicker.setup()

        self.add_scalarbar_2(look)

        self.done = True



    @staticmethod
    def get_from_array(vectors, pc, aname, mode):
    
        if vectors is None:
            return None
        
        tuples = vectors.GetNumberOfTuples()
        components = vectors.GetNumberOfComponents()
    
        print 'tuples', tuples, 'components', components

        if components <= 0:
            return None

        a = vtk.vtkDoubleArray()
        a.SetNumberOfComponents(1)
        a.SetNumberOfTuples(tuples)
        a.SetName(aname)
        
        if mode >= 0 and mode < 3:
            if components > mode:
                n = 0
                while n < tuples:
                    value = vectors.GetValue(n*components+mode)
                    a.SetValue(n,value)
                    n += 1
            else: # a cero ou erro ?
                n = 0
                while n < tuples:
                    value = 0.0
                    a.SetValue(n,value)
                    n += 1
        elif mode == 3:
            if components < 1:
                n = 0
                while n < tuples:
                    value = 0.0
                    a.SetValue(n,value)
                    n += 1
            elif components == 1:
                n = 0
                while n < tuples:
                    value = math.abs(vectors.GetValue(n))
                    a.SetValue(n,value)
                    n += 1
            else:
                n = 0
                while n < tuples:
                    s = 0.0
                    for i in range(components):
                        temp = vectors.GetValue(n*components+i)
                        s += temp * temp
                    a.SetValue(n,math.sqrt(s))
                    n += 1
        else: # a cero ou erro ?
            n = 0
            while n < tuples:
                value = 0.0
                a.SetValue(n,value)
                n += 1

        return a



    def construct_data(self, src):
        o = src.GetOutput()
        ugrid = vtk.vtkUnstructuredGrid()
        ugrid.SetPoints(o.GetPoints())
        ugrid.SetCells(o.GetCellTypesArray(), o.GetCellLocationsArray(), o.GetCells())
        #ugrid.ShallowCopy(o)
        ##ugrid.DeepCopy(o)
        
        if self.data1.get('fielddomain') == 'cell':
            self.vectors = o.GetCellData().GetVectors()
        elif self.data1.get('fielddomain') == 'point':
            self.vectors = o.GetPointData().GetVectors()
        else:
            self.vectors = None
        return ugrid



    def apply_data(self, mode):
    
        if mode < 0 or mode > 3:
            return False
    
        aname = 'vector_component_' + unicode(mode)
        
        if self.data1.get('fielddomain') == 'cell':
            pc = 1
        elif self.data1.get('fielddomain') == 'point':
            pc = 0
        else:
            return False
        
        if mode >=0 and mode <= 3:
            if self.esta[mode]: # xa estaba calculado
                self.src_vc.Assign(aname, 0, pc) # 0 scalar 1 vector ; 0 point 1 cell
                self.src_vc.Update() # necesario
                return True
        else:
            return False

        a = PlotVectorComponents.get_from_array(self.vectors, pc, aname, mode)
        
        if a is None:
            return False
        
        if pc == 1:
            data = self.ugrid.GetCellData()
        elif pc == 0:
            data = self.ugrid.GetPointData()

        data.AddArray(a) # replaces if exists

        self.src_vc.Assign(aname, 0, pc) # 0 scalar 1 vector ; 0 point 1 cell
        
        self.esta[mode] = True
        
        self.src_vc.Update()

        return True



    def update(self, struct):
        self.lastmode = self.get_selected(struct)
        self.src_update1b({'changed': True})
        self.widget.Render()



    def get_selected(self, struct):
        #return self.cbl.GetSelection()
        sel = -1 # ningun
        ops = struct.get_children()
        if len(ops) != 4:
            self.data_error('Incorrect number of elements (4 needed)')
            sel = -3 # error
        else:
            for r in range(len(ops)):
                att = ops[r].get_attribs()
                if att.get(config.AT_SELECTED) == config.VALUE_TRUE:
                    if sel == -1:
                        sel = r
                    else:
                        sel = -2 # multiple
        #print 'get_selected', sel
        return sel

