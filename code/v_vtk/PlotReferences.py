#!/usr/bin/env python
# -*- coding: utf-8 -*-



# este ficheiro non é reutilizable ao máximo: fai referencia a nomes de campos como nsd,nrc,nra



import config
import Plot
import wx_version
import wx
import vtk



epsilon = 1e-6
several_colors = False



class PlotReferences(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_outline_1()
        
        self.chmb = wx.ToggleButton(self.plotbar, wx.ID_ANY, 'Mesh', style=wx.BU_EXACTFIT)
        self.plotbar.add(self.chmb)
        self.chmb.Bind(wx.EVT_TOGGLEBUTTON, self.chmc)
        

        choicesl = [u'No labels', u'Selected', u'All']
        self.cbl = wx.Choice(self.plotbar, wx.ID_ANY, choices = choicesl)
        self.cbl.SetSelection(0) # in windows appears without selection
        self.plotbar.add(self.cbl)
        self.cbl.Bind(wx.EVT_CHOICE, self.cl)

        self.has_field = False
        self.numbers = [] # last selected numbers [to avoid Render with the same selection]



    def get_options(self):
        # para que cree un wxVTKRenderWindowInteractor e non un wxVTKRenderWindow
        return {u'interactor':True, u'title':'refs.'}


    def get_options_extra(self, data):
        title = None # 'refs.'
        if data is not None:
            field = data.get('fieldname')
            #dim = data.get('dim')
            #if dim == 3 and field == 'nsd':
            #    title = 'Domain refs.'
            #if dim == 3 and field == 'nrc':
            #    title = 'Face refs.'
            #if dim == 3 and field == 'nra':
            #    title = 'Edge refs.'
            #if dim == 2 and field == 'nsd':
            #    title = 'Domain refs.'
            #if dim == 2 and field == 'nra':
            #    title = 'Edge refs.'
            if field == 'element_ref':
                title = 'Domain refs.'
            if field == 'face_ref':
                title = 'Face refs.'
            if field == 'edge_ref':
                title = 'Edge refs.'
            if field == 'vertex_ref':
                title = 'Vertex refs.'
        return {'title':title}



    def chmc(self, event):
        if self.chmb.GetValue():
            self.wireA.SetVisibility(1)
        else:
            self.wireA.SetVisibility(0)

        self.widget.Render()



    def cl(self, event):
        if not self.done or not self.has_field:
            return

        sel = self.cbl.GetSelection()

        if sel == 0:
            if self.data1.get('fielddomain') == 'point':
                self.lrM.SetInputConnection(self.selrF.GetOutputPort())
            else:
                self.ccrF.SetInputConnection(self.selrF.GetOutputPort())
            self.lrA.SetVisibility(0)
        elif sel == 1:
            if self.data1.get('fielddomain') == 'point':
                self.lrM.SetInputConnection(self.selrF.GetOutputPort())
            else:
                self.ccrF.SetInputConnection(self.selrF.GetOutputPort())
            self.lrA.SetVisibility(1)
        elif sel == 2:
            if self.data1.get('fielddomain') == 'point':
                self.lrM.SetInputConnection(self.refsT.GetOutputPort())
            else:
                self.ccrF.SetInputConnection(self.refsT.GetOutputPort())
            self.lrA.SetVisibility(1)

        self.widget.Render()



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        if changes.get('new'):
            self.wireM.SetInputConnection(self.src.GetOutputPort())
        if changes.get('changed'):
            self.update_outline(self.src)
        if self.has_field:
            if changes.get('new'):
                self.refsT.SetInputConnection(self.src.GetOutputPort())
                # self.selrF.SetInputConnection(self.src.GetOutputPort()) # x1sbc
            if changes.get('changed'):
                self.selrM.SetScalarRange(self.change_range(self.src))
        return True



    def change_range(self, src):
        range = src.GetOutput().GetScalarRange()
        print 'range', range, u'->',
        # no less than 1
        range = (1.0,range[1])
        print range
        return range



    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        # creates self.src
        if not self.call_src():
            return

# wireframe

        # test proba
        #self.ref0 = vtk.vtkThreshold() # necesario en selrF_
        #self.ref0.SetInputConnection(self.src.GetOutputPort())
        #self.ref0.ThresholdByLower(0.999) # valor inclusive

        self.wireM = vtk.vtkDataSetMapper()
        # test proba
        #self.wireM.SetInputConnection(self.ref0.GetOutputPort())
        self.wireM.SetInputConnection(self.src.GetOutputPort())
        self.wireM.ScalarVisibilityOff()

        self.wireA = vtk.vtkActor()
        self.wireA.SetMapper(self.wireM)
        self.wireA.GetProperty().SetRepresentationToWireframe()
        self.wireA.GetProperty().SetColor(Plot.mesh3_color)
        self.wireA.SetVisibility(0)

        self.add_outline_2(self.src)

        if self.has_field:

# reference labels
            if self.data1.get('fielddomain') == 'point':
                self.refsT = vtk.vtkThresholdPoints()
                self.refsT.SetInputConnection(self.src.GetOutputPort())
                self.refsT.ThresholdByUpper(1.0-epsilon)
            else:
                self.refsT = vtk.vtkThreshold() # necesario en selrF_
                self.refsT.SetInputConnection(self.src.GetOutputPort())
                self.refsT.ThresholdByUpper(1.0-epsilon)
#            self.refsT.SetInputArrayToProcess(1, 0, 0, 0, self.fieldname)
#            self.refsT.SetAttributeModeToUseCellData()

            if self.data1.get('fielddomain') == 'point':
                label_con = self.refsT.GetOutputPort()
            else:
                self.ccrF = vtk.vtkCellCenters()
                self.ccrF.SetInputConnection(self.refsT.GetOutputPort())
                label_con = self.ccrF.GetOutputPort()

            self.lrM = vtk.vtkLabeledDataMapper()
            self.lrM.SetInputConnection(label_con)
            self.lrM.SetLabelModeToLabelScalars()
            self.lrM.GetLabelTextProperty().SetColor(Plot.label_color)

            self.lrA = vtk.vtkActor2D()
            self.lrA.SetMapper(self.lrM)
            self.lrA.SetVisibility(0)
            
            # CELL 	POINT 	FIELD 	VERTEX 	EDGE 	
            if self.data1.get('fielddomain') == 'point':
                ftype = 1 # vtkSelection::POINT
            else:
                ftype = 0 # vtkSelection::CELL

# selected edges
            self.selr = vtk.vtkSelectionSource()
            self.selr.SetContentType(7) # vtkSelection::THRESHOLDS
            self.selr.SetFieldType(ftype)
            if self.data1.get('fielddomain') == 'point': # necesario para los puntos, sino colapsa
                self.selr.SetContainingCells(0)

# unselected edges
            self.selr_ = vtk.vtkSelectionSource()
            self.selr_.SetContentType(7) # vtkSelection::THRESHOLDS
            self.selr_.SetFieldType(ftype)
            if self.data1.get('fielddomain') == 'point': # necesario para los puntos, sino colapsa
                self.selr_.SetContainingCells(0)
            self.selr_.SetInverse(1)

            self.selrF = vtk.vtkExtractSelectedThresholds()
            #self.selrF.SetInputConnection(self.src.GetOutputPort()) # por que era asi? # x1sbc
            self.selrF.SetInputConnection(self.refsT.GetOutputPort())
            self.selrF.SetSelectionConnection(self.selr.GetOutputPort())

            self.selrF_ = vtk.vtkExtractSelectedThresholds()
            self.selrF_.SetInputConnection(self.refsT.GetOutputPort()) #
            self.selrF_.SetSelectionConnection(self.selr_.GetOutputPort())

            self.selrM = vtk.vtkDataSetMapper()
            self.selrM.SetInputConnection(self.selrF.GetOutputPort())
            if not several_colors:
                self.selrM.ScalarVisibilityOff()

            self.selrM_ = vtk.vtkDataSetMapper()
            self.selrM_.SetInputConnection(self.selrF_.GetOutputPort())
            self.selrM_.ScalarVisibilityOff()

            self.selrM.SetScalarRange(self.change_range(self.src))

            self.selrA = vtk.vtkActor()
            self.selrA.SetMapper(self.selrM)
            if not several_colors:
                self.selrA.GetProperty().SetColor(Plot.mesh2_color)
            if self.data1.get('fielddomain') == 'point':
                self.selrA.GetProperty().SetRepresentationToPoints()
            else:
                self.selrA.GetProperty().SetRepresentationToSurface()

            self.selrA_ = vtk.vtkActor()
            self.selrA_.SetMapper(self.selrM_)
            if several_colors:
                self.selrA_.GetProperty().SetColor(Plot.unselected_color)
            else:
                self.selrA_.GetProperty().SetColor(Plot.mesh_color)
            if self.data1.get('fielddomain') == 'point':
                self.selrA_.GetProperty().SetRepresentationToPoints()
            else:
                self.selrA_.GetProperty().SetRepresentationToWireframe()
                
            if self.data1.get('fielddomain') == 'point':
                self.selrA.GetProperty().SetPointSize(3.0)
                self.selrA_.GetProperty().SetPointSize(2.0)

            # lóxica dudosa: depende do nome do campo
            if self.data1.get('fieldname') == 'edge_ref':
                self.selrA.GetProperty().SetLineWidth(5.0)
                self.selrA_.GetProperty().SetLineWidth(5.0)

            self.update_thresholds(struct, True)

# Add the actors to the render
            self.rens[0].AddActor(self.selrA_) # unselected
            self.rens[0].AddActor(self.selrA) # selected
            self.rens[0].AddActor(self.lrA) # labels

        self.rens[0].AddActor(self.wireA) # mesh
        
        self.set_iren()
        self.iren.AddObserver("LeftButtonPressEvent", self.ButtonEvent)

        if self.data1.get('fielddomain') == 'cell':
            self.picker = vtk.vtkCellPicker()
        else:
            self.picker = vtk.vtkPointPicker()
        self.picker.AddObserver("EndPickEvent", self.EndPick)
        self.iren.SetPicker(self.picker)

        
        self.done = True



    def EndPick(self, obj, event):
        print 'EndPick: event', event
        
        if self.data1.get('fielddomain') == 'cell':
            cellid = self.picker.GetCellId()
            print 'cellid', cellid
            print self.picker.GetSelectionPoint(), self.picker.GetPickPosition()
            if cellid < 0:
                return
            dataset = self.picker.GetDataSet()
            #cell = dataset.GetCell(cellid)
            #print cell
            cd = dataset.GetCellData()
            #print cd
            scalars = cd.GetScalars()
            # vtkDataArray
            #print scalars
            if scalars is None:
                return
            #value = scalars.GetTuple1(cellid)
            value = scalars.GetValue(cellid)
        else:
            pointid = self.picker.GetPointId()
            print 'pointid', pointid
            print self.picker.GetSelectionPoint(), self.picker.GetPickPosition()
            if pointid < 0:
                return
            dataset = self.picker.GetDataSet()
            cd = dataset.GetPointData()
            scalars = cd.GetScalars()
            if scalars is None:
                return
            #value = scalars.GetTuple1(pointid)
            value = scalars.GetValue(pointid)
            
        print 'value', value
        if value > 0:
            self.update_widget(value)



    def ButtonEvent(self, obj, event):
        print 'left', event
        xypos = self.iren.GetEventPosition()
        print xypos
        # anomalías:
        #altgr: provoca Control
        #alt: non provoca nada
        #control, shift: ok
        a = self.iren.GetAltKey()
        c = self.iren.GetControlKey()
        s = self.iren.GetShiftKey()
        kc = self.iren.GetKeyCode()
        ks = self.iren.GetKeySym()
        print 'alt', a, 'control', c, 'shift', s, 'code', repr(kc), 'sym', ks
        if not a and not c and not s: # si no se presionaron teclas
            # o seguinte daba segmentation fault con self.wireMadd.RemoveAllInputs()
            # [Plot...additional] (imprimía: ERROR: No input!)
            self.picker.Pick(xypos[0], xypos[1], 0, self.rens[0])



    def update_widget(self, tuple):
        self.panel_widgets.update_widget_param(self.struct, unicode(tuple))



    def update(self, struct):
        if self.has_field:
            if self.update_thresholds(struct):
                self.widget.Render()



# returns true => did update . false => not    update
    def update_thresholds(self, struct, force=False):
        updated = False
        numbers = []
        elements = struct.get_elements_selected()
        
        good = True
        token = None

        for element in elements:
            try:
                numbers.append(int(element))
            except ValueError, x:
                good = False
                token = element
                break

        if good:
            # solo actualiza si hay diferencias
            if numbers != self.numbers or force:
                self.selr.RemoveAllThresholds()
                self.selr_.RemoveAllThresholds()
                for a in numbers:
                    self.selr.AddThreshold(a-epsilon,a+epsilon)
                    self.selr_.AddThreshold(a-epsilon,a+epsilon)
                self.numbers = numbers
                updated = True
        else:
            self.data_error('Error converting \'' + token + '\' to integer')

        return updated
