#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import wx.grid
import config
import FileParse



# window to show a table of values
class WindowTabular(wx.Frame):

    def __init__(self, parent, onclose=None):
    
        self.parent = parent
        self.panel_widgets = self.parent.panelA
        
        # for invoking close
        self.onclose = onclose
        
        wx.Frame.__init__(self, parent, wx.ID_ANY, u'Tabular data', style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT, size=(400,400))

        self.Centre(wx.BOTH)        
        self.struct = None
        
        self.panel = wx.Panel(self)
        
        self.ncols = None
        self.nrows = None
        self.colssize = 0
        self.rowssize = 0
        self.grid = None
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(self.box)
        
        self.Bind(wx.EVT_CLOSE, self.close_event)
        # agora faise bind ao grid
        self.panel.Bind(wx.EVT_SIZE, self.size_event)

        self.SetMinSize((100,100))
        
        self.set_title()
        
        self.Show()



    def add_grid(self,rowlabels = False):
        if self.grid is not None:
            self.grid.Destroy()
        self.grid = wx.grid.Grid( self.panel, wx.ID_ANY )
        self.grid.EnableEditing(False)
        #Controla el evento de pulsar enter, crea una nueva fila
        self.grid.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_grid_cell_change)
        if not rowlabels: 
            self.grid.Bind(wx.EVT_SIZE, self.size_event)
            self.grid.SetRowLabelSize(0) # cambio: que non mostre os numeros de fila
        self.box.Add( self.grid, 1, wx.EXPAND )
        self.box.Layout()
        
    #Se crea una nueva fila en la tabla al pulsar enter si la ultima esta vacia.
    #Al pulsar tabulador el cursor se mueve en la misma fila hasta llegar a la ultima posicion
    # en la que cambia de fila
    def on_key_down(self, event):

#        if event.GetKeyCode() == wx.WXK_RETURN:
#            print 'WindowTabular: EVT_ENTER_KEY_DOWN'
#            cursorcol = self.grid.GetGridCursorCol()
#            cursorrow = self.grid.GetGridCursorRow()
#            rownumber = self.grid.GetNumberRows()
#            colnumber = self.grid.GetNumberCols()
#            if rownumber-1 == cursorrow:
#                newrow = False
#                for i in range(colnumber):
#                    if not (self.grid.GetCellValue(cursorrow, i) == ''):
#                        newrow = True
#                if newrow:
#                    self.grid.InsertRows(rownumber, 1, True)
#                    self.grid.SetGridCursor(rownumber, 0)
#                else:
#                    event.Skip()
#            else:
#                event.Skip()
        if event.GetKeyCode() == wx.WXK_TAB:
            print 'WindowTabular: EVT_TAB_KEY_DOWN'
            cursorcol = self.grid.GetGridCursorCol()
            cursorrow = self.grid.GetGridCursorRow()
            rownumber = self.grid.GetNumberRows()
            colnumber = self.grid.GetNumberCols()
            if (colnumber-1 == cursorcol) and (rownumber-1 > cursorrow):
                self.grid.SetGridCursor(cursorrow+1, 0)
            else:
                event.Skip()
        else:
            event.Skip()

        
    def size_event(self, event):
#        Controla el comportamiento y el tamaño minimo de las celdas
        if self.grid is not None:
            # clientsize: para obter o tamaño quitadas as scrollbars...
            size = self.GetClientSize() # non sei se actualizado
            if self.grid.GetRowLabelSize() > 0: 
                wfree = size[0] - self.colssize - 20
            else:
                wfree = size[0] - 20
            hfree = size[1] - self.rowssize - 20
            if wfree < 1: wfree = 1
            if hfree < 1: hfree = 1

            if  self.ncols is not None and self.ncols > 0 and (wfree / self.ncols) > self.colssize:
                self.grid.SetDefaultColSize( wfree / self.ncols, True)
            else:
                self.grid.AutoSizeColumns()

            if  self.nrows is not None and self.nrows > 0 and (hfree / self.nrows) > self.rowssize:
                self.grid.SetDefaultRowSize( hfree / self.nrows, True)
            else:
                self.grid.AutoSizeRows()

            self.Update()
            self.grid.Update()

        event.Skip()


    def close_event(self, event):
        if self.onclose is not None:
            self.onclose()
        #self.save_data_from_grid()
        event.Skip()

    def on_grid_cell_change(self,event):
        #self.save_data_from_grid()
        event.Skip()

    def save_data_from_grid(self):
        
        rownumber = self.grid.GetNumberRows()
        colnumber = self.grid.GetNumberCols()
        childs = self.struct.get_children()
        
        for col in range(0,colnumber):
            coldata = []
            for row in range(0,rownumber):
                coldata.append(self.grid.GetCellValue(row,col))
            childs[col].set_elements(coldata)

        self.panel_widgets.update_widget_struct(childs)
    
    
    def set_title(self):
        str = u'Tabular data'
        if self.struct is not None:
            str += u' - ' + self.struct.get_name()
        self.SetTitle(str)



    def display(self, struct, fromfile=False):
        self.struct = struct
        self.set_title()
        if fromfile: self.build_from_file(True)
        else:  self.build(True)



    def update(self, struct, fromfile=False):
        if self.struct is not struct:
            return
        if fromfile: self.build_from_file(True)
        else:  self.build(True)
        
        
    def build(self, new):
        cols = []
        labels = []
        max = 0
        for a in self.struct.get_children():
            labels.append(a.get_name())
            ele = a.get_elements()
            if len(ele)>max:
                max = len(ele)
            cols.append(ele)

        self.add_grid()

        #self.grid.ClearGrid()

        self.ncols = ncols = len(cols)
        self.nrows = max

        self.grid.CreateGrid(max, ncols)

        # establece títulos para as columnas
        col = 0
        while col < ncols:
            self.grid.SetColLabelValue(col,labels[col])
            col += 1

        # establece read-write para as celdas
        #self.grid.EnableEditing(True)

        # establece contidos das celas
        maxlen = 0 # tamaño máximo en caracteres, do que hai que hai que mostrar
        col = 0
        #contador de datos por columna
        lendata = 0
        while col < ncols:
            data = cols[col]
            if len(data)>lendata:
                lendata=len(data)
            row = 0
            while row < len(data):
                if len(data[row]) > maxlen:
                    maxlen=len(data[row])
                self.grid.SetCellValue(row,col,data[row])
                row += 1
            col += 1

        #Si no hay datos se crea una fila para introducirlos
        if lendata==0:
            self.grid.InsertRows(0, 1, True)
            
        self.grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        if new:
            self.grid.AutoSizeRows()
            self.grid.AutoSizeColumns()
            self.colssize = self.grid.GetColSize(0)
            self.rowssize = self.grid.GetRowSize(0)
            self.SetSize(self.grid.GetBestSize())
            self.Centre(wx.BOTH)       
#        self.grid.SetColMinimalAcceptableWidth(self.grid.GetColSize(0))
#        self.grid.SetRowMinimalAcceptableHeigth(self.grid.GetRowSize(0))


    def build_from_file(self,new):

        #Parseo de atributo data. solo admite la propiedad file:
        parsed = self.struct.parse_source_string_1(self.struct.get_attribs().get(u'data'))
        #data="file:..."
        if parsed[0] == 1: 
            sourcemenu = self.struct.parse_path_varx(parsed[1],False,False)
            if len(sourcemenu) > 0:
                self.filename = sourcemenu[0]
            else:
                self.parent.errormsg( u'Can not parse "file:" string value or path does not exist')
                self.Close()
                return False
        #data="menu:..."
        elif parsed[0] == 2: 
            sourcemenu = self.struct.parse_path_varx(parsed[1],True,True)
            if len(sourcemenu) > 0:
                self.filename = sourcemenu[0]
            else:
                self.parent.errormsg( u'Can not parse "menu:" string value or path does not exist')
                self.Close()
                return False
        else: 
            self.parent.errormsg( u'Can not parse "data" string value: only allows "menu:" and "file:" prefix')
            self.Close()
            return False

        matrix = self.read_matrix(self.filename)
        if not matrix: return False

        self.add_grid(rowlabels=True)

        self.ncols = matrix.get(u'col_num')
        self.nrows = matrix.get(u'row_num')

        self.grid.CreateGrid(self.nrows, self.ncols)
        self.grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        col_labels = matrix.get(u'col_labels')
        row_labels = matrix.get(u'row_labels')

        for col_index in range(self.ncols):
            self.grid.SetColLabelValue(col_index,col_labels[col_index])
        for row_index in range(self.nrows):
            self.grid.SetRowLabelValue(row_index,row_labels[row_index])


        row_list = matrix.get(u'row_list')
        for row_index in range(self.nrows):
            for col_index in range(self.ncols):
                self.grid.SetCellValue(row_index,col_index,row_list[row_index][col_index])
        if new:
            self.grid.AutoSizeRows()
            self.grid.AutoSizeColumns()
            self.colssize = self.grid.GetColSize(0)
            self.rowssize = self.grid.GetRowSize(0)
            self.SetSize(self.grid.GetBestSize())
            self.Centre(wx.BOTH)        

#        self.grid.SetColMinimalAcceptableWidth(self.grid.GetColSize(0))
#        self.grid.SetRowMinimalAcceptableHeigth(self.grid.GetRowSize(0))


    def read_matrix(self,filename):
        matrix = {}

        #Apertura y comprobacion de existencia del fichero
        f = FileParse.FileParse()
        err = f.open(filename)
        if err is not True:
            self.parent.errormsg (u'Error opening file: ' + unicode(err))
            self.Close()
            return False

        #Lectura del numero de filas
        temp = f.getword()
        if temp is None:
            self.parent.errormsg (u'Premature EOF')
            return False
        if temp is False:
            self.parent.errormsg (u'I/O Error: ' + f.get_error())
            return False

        matrix[u'row_num'] = FileParse.FileParse.to_int(temp)
        if matrix.get(u'row_num') is False:
            self.parent.errormsg (u'Error converting \'' + unicode(temp) + '\' to integer 1')
            return False

        #Lectura del numero de columnas
        temp = f.getword()
        if temp is None:
            self.parent.errormsg (u'Premature EOF')
            return False
        if temp is False:
            self.window.errormsg (u'I/O Error: ' + f.get_error())
            return False

        matrix[u'col_num'] = FileParse.FileParse.to_int(temp)
        if matrix.get(u'col_num') is False:
            self.parent.errormsg (u'Error converting \'' + unicode(temp) + '\' to integer')
            return False
        matrix['row_list'] = []

        #Lectura de datos por filas
        for s in range(matrix.get(u'row_num')):

            row=[]
            for r in range(matrix.get(u'col_num')):
                temp = f.getword()
                if temp is None:
                    self.parent.errormsg (u'Premature EOF')
                    return False
                if temp is False:
                    self.parent.errormsg (u'I/O Error: ' + f.get_error())
                    return False
                row.append(temp)
            matrix.get(u'row_list').append(row)

        #Lectura de las etiquetas de las filas
        matrix[u'row_labels'] = [] # string o None
        for t in range(matrix.get(u'row_num')):
            temp = f.getline()
            if temp is False:
                self.window.errormsg (u'I/O Error: ' + f.get_error())
                return False
            elif temp is None:
                temp = str(t)
            else:
                temp = temp.rstrip() # quita \n e espazos
            matrix.get(u'row_labels').append(temp)

        #Lectura de las etiquetas de las columnas
        matrix[u'col_labels'] = [] # string o None
        for t in range(matrix.get(u'col_num')):
            temp = f.getline()
            if temp is False:
                self.window.errormsg (u'I/O Error: ' + f.get_error())
                return False
            elif temp is None:
                temp = str(t)
            else:
                temp = temp.rstrip() # quita \n e espazos
            matrix.get(u'col_labels').append(temp)

        err = f.close()
        if err is not True:
            self.window.errormsg (u'Error closing file: ' + unicode(err))
            return False
        f = None

        return matrix

