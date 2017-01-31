#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
#import Menus
import wx_version
import wx
import vtk



# pointdata: ok
# celldata: clickar en elemento de submalla se detecta y no aparece el numero [indice] ni la etiqueta
# elementos de la submalla pueden ocultar a los de la malla al hacer click



class PlotNumbering(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_outline_1()

        self.add_sw_1(selection=0)

        self.has_field = False
        self.locator = None



    def get_options(self):
        # para que cree un wxVTKRenderWindowInteractor e non un wxVTKRenderWindow
        return {u'interactor':True,u'title':'Numbering'}



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        # labelsb
        if changes.get('changed'):
            self.update_outline(self.src)
        if changes.get('new'):
            if self.data1.get('fielddomain') == 'cell':
                self.cellcenters.SetInputConnection(self.src.GetOutputPort())
            else:
                self.labels_b_data_change([self.src])
        if changes.get('new'):
            self.wireM.SetInputConnection(self.src.GetOutputPort())
        self.locator = None
        return True



    def plot(self, struct):
    
        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        # creates self.src
        if not self.call_src():
            return

        self.add_outline_2(self.src)

        if self.has_field:
            self.add_labels_b_1()
            if self.data1.get('fielddomain') == 'cell':
                self.cellcenters = vtk.vtkCellCenters()
                self.cellcenters.SetInputConnection(self.src.GetOutputPort())
                self.add_labels_b_2([self.cellcenters])
            else:
                self.add_labels_b_2([self.src])

            # aqui para que apareza de ultimo
            # so con campo?
            self.add_search_1(self.search_callback, self.search_callback_coords)

# wireframe
        self.wireM = vtk.vtkDataSetMapper()
        self.wireM.SetInputConnection(self.src.GetOutputPort())
        self.wireM.ScalarVisibilityOff()

        self.wireA = vtk.vtkActor()
        self.wireA.SetMapper(self.wireM)
        self.wireA.GetProperty().SetRepresentationToWireframe()
        self.wireA.GetProperty().SetColor(Plot.mesh_color)

        self.add_sw_2(self.wireA)

        self.rens[0].AddActor(self.wireA)
        
        self.set_iren()
        #MouseMoveEvent
        self.iren.AddObserver("LeftButtonPressEvent", self.ButtonEvent)
        #self.iren.AddObserver("LeftButtonReleaseEvent", self.ButtonEvent2)

        if self.data1.get('fielddomain') == 'cell':
            self.picker = vtk.vtkCellPicker()
        else:
            self.picker = vtk.vtkPointPicker()
        self.picker.AddObserver("EndPickEvent", self.EndPick)
        self.iren.SetPicker(self.picker)

        self.copy_params(struct)

        self.done = True



    def EndPick(self, obj, event):
        if self.data1.get('fielddomain') == 'cell':
            self.picked(self.picker.GetCellId())
        else:
            self.picked(self.picker.GetPointId())



    def ButtonEvent(self, obj, event):
        xypos = self.iren.GetEventPosition()
        print ':', event, xypos
        self.picker.Pick(xypos[0], xypos[1], 0, self.rens[0])



    def update_widget(self, pointnum):
        self.struct.set_elements_nosel([unicode(pointnum)])
        self.panel_widgets.update_widget_struct(self.struct)
        self.labels_b_update(pointnum)



    def update(self, struct):
        self.copy_params(struct)
        self.widget.Render()



    def update_thresholds(self, struct):
        pass



    def copy_params(self, struct):
        nums = struct.get_elements()
#        print 'nums', nums
        if len(nums) == 1:
            num = nums[0]
            if num == '':
                self.labels_b_update(None)
            else:
                numf = None
                try:
                    numf = int(num)
                except ValueError:
                    pass
                if numf is not None:
                    self.labels_b_update(numf)
                else:
                    self.data_error('Error converting \'' + num + '\' to integer')
        elif len(nums) == 0:
            self.labels_b_update(None)
        else:
            self.data_error('Incorrect number of elements (0 or 1 needed)')



    def search_callback_coords(self):
        if self.labels_b_value is None:
            return {}
        ide = self.labels_b_value - 1
        if ide < 0:
            return {}
        if self.data1.get('fielddomain') == 'cell':
            o = self.src.GetOutput()
            if ide >= o.GetNumberOfCells():
                return {}
            cell = o.GetCell(ide)
            bounds = cell.GetBounds()
            # aproximate, not exact
            return {'x':unicode((bounds[0]+bounds[1])/2.0),
                    'y':unicode((bounds[2]+bounds[3])/2.0),
                    'z':unicode((bounds[4]+bounds[5])/2.0)}
        else:
            o = self.src.GetOutput()
            if ide >= o.GetNumberOfPoints():
                return {}
            coords = o.GetPoint(ide)
            return {'x':unicode(coords[0]),
                    'y':unicode(coords[1]),
                    'z':unicode(coords[2])}



    def search_callback(self, xyz):
        ide = -1

        if self.data1.get('fielddomain') == 'cell':

            # no existe el método FindCell !!!
            #tol2 = 1
            #subId = 0
            #pcoords = [0.0, 0.0, 0.0]
            #weights = [0.0, 0.0, 0.0]
            #print 'cell', self.src.GetOutput().FindCell(pos, None, -1, tol2, subId, pcoords, weights)

            if self.locator is None:
                self.locator = vtk.vtkCellLocator()
                self.locator.SetDataSet(self.src.GetOutput())

            # no existe el método FindCell !!!
            ide = self.locator.FindCell(xyz)

        else:

            ide = self.src.GetOutput().FindPoint(xyz)

        self.picked(ide)

        if ide < 0:
            self.window.errormsg('Could not locate ' + self.data1.get('fielddomain') + ' at given coordinates')



    def picked(self, ide):
        if self.data1.get('fielddomain') == 'cell':
            print 'cellid', ide
        else:
            print 'pointid', ide

        if ide < 0:
            return

#        if self.data1.get('fielddomain') == 'cell': # revisar: submesh quitar ou non ?
#            unstructured = self.src.GetOutput()
#            celldata = unstructured.GetCellData()
#            scalars = celldata.GetScalars()
#            if scalars is not None:
#                v = scalars.GetTuple1(ide)
#                if v == 0.0:
#                    print 'submesh', v
#                    return
#                #else:
#                #    print 'no submesh'

        num = ide + 1

        self.update_widget(num)

