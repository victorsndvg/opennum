#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
import wx_version
import wx
import vtk



# si las referencias no son consecutivas, rellena



class PlotMaterials(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_outline_1()
        
        self.button_table = wx.ToggleButton(self.plotbar, wx.ID_ANY, 'Table', style=wx.BU_EXACTFIT)
        self.button_table.SetValue(True)
        self.plotbar.add(self.button_table)
        self.button_table.Bind(wx.EVT_TOGGLEBUTTON, self.handler_table)

        self.add_sw_1(selection=1)
        
        self.has_field = False
        self.numbers = [] # last selected numbers [to avoid Render with the same selection]



    def get_options(self):
        # para que cree un wxVTKRenderWindowInteractor e non un wxVTKRenderWindow
        #return {u'interactor':True}
        return {u'title':'Materials'}



    def handler_table(self, event):
        self.lbA.SetVisibility(self.button_table.GetValue())
        self.widget.Render()



    # para cuando cambia el tiempo y por tanto, self.src
    # en este grafico no sé si será de mucha utilidad
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
            
        self.update_field_name('element_ref')
        self.update_field_type('scalar')
        self.update_field_domain('cell')
        self.update_legend_data()

        # creates self.src
        if not self.call_src():
            return

        self.add_outline_2(self.src)
        
        scalarrange = self.src.GetOutput().GetScalarRange()
        print 'src scalarrange', scalarrange

        self.get_materials()
        
        scalarrange = [0.0, float(self.max) + 1] # +1 por si hay otros valores ponerlos a negro
        print 'src scalarrange ->', scalarrange
        
        self.set_colors()
        
        self.wireM = vtk.vtkDataSetMapper()
        self.wireM.SetInputConnection(self.src.GetOutputPort())
        self.wireM.SetScalarRange(scalarrange)

        self.look = self.wireM.GetLookupTable()
        self.look.SetTableRange(scalarrange)
        self.set_lookup()


        self.lbA = vtk.vtkLegendBoxActor()
        self.set_legendbox()
#        print 'pos1', self.lbA.GetPosition()
#        print 'pos2', self.lbA.GetPosition2()
        self.lbA.SetPosition(0.8, 0.1)
        self.lbA.SetPosition2(0.2, 0.8)
#        self.lbA.LockBorderOn() #nada
#        self.lbA.GetEntryTextProperty().SetVerticalJustificationToTop() #nada
        
        self.wireA = vtk.vtkActor()
        self.wireA.SetMapper(self.wireM)
        self.wireA.GetProperty().SetRepresentationToSurface()

        self.add_sw_2(self.wireA)

        self.sbA = vtk.vtkScalarBarActor()
        self.sbA.SetLookupTable(self.look)
        self.sbA.SetNumberOfLabels(self.look.GetNumberOfTableValues())
        self.sbA.SetPosition(0.0, 0.1)
        self.sbA.SetPosition2(0.2, 0.8)

# podese descomentar, está preparado
#        self.rens[0].AddActor(self.sbA)
        self.rens[0].AddActor(self.lbA)
        self.rens[0].AddActor(self.wireA)

        
        self.done = True



    def update(self, struct):
        self.get_materials()
        
        scalarrange = [0.0, float(self.max) + 1] # +1 por si hay otros valores ponerlos a negro

        print 'src scalarrange ->', scalarrange
        
        self.set_colors()
        
        self.wireM.SetScalarRange(scalarrange)
        self.look.SetTableRange(scalarrange)
        
        self.set_lookup()
        
        self.set_legendbox()

        self.sbA.SetNumberOfLabels(self.look.GetNumberOfTableValues())
        
        self.widget.Render()



    def set_colors(self):
        num = len(self.names)
        lt = vtk.vtkLookupTable()
        lt.SetNumberOfColors(num)
        lt.SetHueRange(Plot.hue_1, Plot.hue_2)
        if num < 1:
            lt.SetTableRange(1, 1)
        else:
            lt.SetTableRange(1, num) # se 'num' é cero dá erro ao executar con warnings
        lt.Build()
        self.cols = []
        self.namecol = {}
        c = 1
        while c <= num:
            col = [0,0,0]
            lt.GetColor(c, col)
            print 'gc', c, col
            self.cols.append(col)
            self.namecol[self.names[c-1]] = col #
            c += 1
        print 'namecol', self.namecol



    def set_legendbox(self):
        size = len(self.names)
        self.lbA.SetNumberOfEntries(size)
        n = 0
        while n < size:
            self.lbA.SetEntry(n,None,self.names[n],self.cols[n])
            n += 1



    def set_lookup(self):
        self.look.SetNumberOfTableValues(2+self.max)
        self.look.SetTableValue(0, Plot.unassigned_color) # se non hai cero engadese tango fóra
        i = 1
        while i <= self.max:
            name = self.numname.get(unicode(i))
            if name is None:
                self.look.SetTableValue(i, Plot.unassigned_color)
            else:
                col = self.namecol[name]
                self.look.SetTableValue(i, col[0],col[1],col[2], 1)
            i += 1
        self.look.SetTableValue(self.max+1, Plot.unassigned_color) # se non hai cero engadese tango fóra # 2+len



    def get_materials(self):

        self.numname = {}
        self.namenum = {}
        self.nums = []
        self.names = []
        self.max = 0

        materialspath = self.struct.get_attribs().get(config.PLOT_MATERIALS)
        
        if materialspath is None:
            self.window.errormsg('Materials Plot: "materials" source not found')
            return
        else:
            parsed = self.struct.parse_source_string_1(materialspath)
            if parsed[0] is None:
                print u'Materials Plot: Can not parse "materials" string value'
            if parsed[0] != 2:
                print u'Materials Plot: Can not parse "materials" string value: only allows "menu:" prefix'
            source_path = parsed[1]
            objects = []
            res = self.struct.parse_path_varx(source_path,True,False,objects,True)
            if isinstance(res, basestring):
                self.window.errormsg('Materials Plot: "materials" source not found: ' + res)
                return
            if len(res) < 1:
                self.window.errormsg('Materials Plot: "materials" source: no nodes found')
                return
            if len(res) > 1:
                self.window.errormsg('Materials Plot: "materials" source: multiple nodes found')
                return
            # non engado dependencia porque sería para os fillos dos fillos de materialsnode,
            # ou sexa, engadir todos os fillos de materialsnode como dependencias
            materialsnode = res[0]


        faces = materialsnode.get_children() # get_elements_with_source


        # dependencias aqui !
        #print 'start + pointers for', self.struct.get_path()
        #clear ?
        #self.struct.add_dependencies(faces, True)
        #for f in faces:
        #    print ':', f.get_path()
        #print 'end + pointers', 'total', len(faces)
        # end
        

        for f in faces:
        
            face = f.get_name()
            sel = f.get_elements_selected()
            print 'face:', face, 'sel:', sel

            self.nums.append(face)

            # calculate maximum value
            try:
                num = int(face)
            except ValueError:
                pass
            else:
                if self.max < num:
                    self.max = num

            name = None
            if len(sel) == 1:
                name = sel[0]
            
            # do not forget not-assigned-faces
            self.numname[face] = name

            if name is not None:
                if self.namenum.get(name) is None:
                    self.namenum[name] = [face]
                    self.names.append(name)
                else:
                    self.namenum[name].append(face)

        print 'numname', self.numname
        print 'namenum', self.namenum
        print 'names', self.names
        print 'nums', self.nums
