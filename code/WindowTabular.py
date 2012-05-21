#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import wx.grid
import config



# window to show a table of values
class WindowTabular(wx.Frame):

    def __init__(self, parent, onclose=None):
    
        self.parent = parent
	self.panel_widgets = self.parent.panelA
        
        # for invoking close
        self.onclose = onclose
        
        wx.Frame.__init__(self, parent, wx.ID_ANY, u'Tabular data', style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT, size=(400,400))
        
        self.struct = None
        
        self.panel = wx.Panel(self)
        
        self.ncols = None
        self.grid = None
        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(self.box)
        
        self.Bind(wx.EVT_CLOSE, self.close_event)
        # agora faise bind ao grid
        #self.panel.Bind(wx.EVT_SIZE, self.size_event)

        self.SetMinSize((100,100))
        
        self.set_title()
        
        self.Show()



    def add_grid(self):
        if self.grid is not None:
            self.grid.Destroy()
        self.grid = wx.grid.Grid( self.panel, wx.ID_ANY )
	self.grid.EnableEditing(False)
        self.grid.Bind(wx.EVT_SIZE, self.size_event)
	#Controla el evento de pulsar enter, crea una nueva fila
	self.grid.Bind(wx.EVT_KEY_DOWN, self.on_key_down)			#a�adido
	self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.on_grid_cell_change)	#a�adido

        self.grid.SetRowLabelSize(0) # cambio: que non mostre os numeros de fila
        self.box.Add( self.grid, 1, wx.EXPAND )
        self.box.Layout()
        
    #Se crea una nueva fila en la tabla al pulsar enter si la ultima esta vacia.
    #Al pulsar tabulador el cursor se mueve en la misma fila hasta llegar a la ultima posicion
    # en la que cambia de fila
    def on_key_down(self, event): 					#a�adido

#        if event.GetKeyCode() == wx.WXK_RETURN: 			#a�adido
#	    print 'WindowTabular: EVT_ENTER_KEY_DOWN'			#a�adido
#	    cursorcol = self.grid.GetGridCursorCol()			#a�adido
#	    cursorrow = self.grid.GetGridCursorRow()			#a�adido
#	    rownumber = self.grid.GetNumberRows()			#a�adido
#	    colnumber = self.grid.GetNumberCols()			#a�adido
#	    if rownumber-1 == cursorrow:				#a�adido
#		newrow = False						#a�adido
#		for i in range(colnumber):				#a�adido
#		    if not (self.grid.GetCellValue(cursorrow, i) == ''):#a�adido
#			newrow = True					#a�adido
#		if newrow:						#a�adido
#	    	    self.grid.InsertRows(rownumber, 1, True)		#a�adido
#	    	    self.grid.SetGridCursor(rownumber, 0)		#a�adido
#		else:							#a�adido
#		    event.Skip()					#a�adido
#	    else:							#a�adido
#		event.Skip()						#a�adido
        if event.GetKeyCode() == wx.WXK_TAB: 				#a�adido
	    print 'WindowTabular: EVT_TAB_KEY_DOWN'			#a�adido
	    cursorcol = self.grid.GetGridCursorCol()			#a�adido
	    cursorrow = self.grid.GetGridCursorRow()			#a�adido
	    rownumber = self.grid.GetNumberRows()			#a�adido
	    colnumber = self.grid.GetNumberCols()			#a�adido
	    if (colnumber-1 == cursorcol) and (rownumber-1 > cursorrow):#a�adido
		self.grid.SetGridCursor(cursorrow+1, 0)			#a�adido
	    else:							#a�adido
		event.Skip()						#a�adido
	else:								#a�adido
	    event.Skip()						#a�adido

        
    def size_event(self, event):
        #print 'sze', event.GetSize()
        if self.grid is not None and self.ncols is not None and self.ncols > 0:
            # clientsize: para obter o tama�o quitadas as scrollbars...
            size = self.grid.GetClientSize() # non sei se actualizado
            #print '->', size
            free = size[0] - self.grid.GetRowLabelSize()
            free -= 15 # truco para que non apareza a barra de desprazamento
            if free < 1:
                free = 1
            self.grid.SetDefaultColSize( free // self.ncols, True)
        event.Skip()



    def close_event(self, event):
        if self.onclose is not None:
            self.onclose()
	#self.save_data_from_grid()
        event.Skip()

    def on_grid_cell_change(self,event):			#a�adido
	#self.save_data_from_grid()				#a�adido
	event.Skip()						#a�adido

    def save_data_from_grid(self):				#a�adido
	
	rownumber = self.grid.GetNumberRows()			#a�adido
	colnumber = self.grid.GetNumberCols()			#a�adido
	childs = self.struct.get_children()			#a�adido
	
	for col in range(0,colnumber):				#a�adido
	    coldata = []					#a�adido
	    for row in range(0,rownumber):			#a�adido
		coldata.append(self.grid.GetCellValue(row,col))	#a�adido
	    childs[col].set_elements(coldata)			#a�adido

	self.panel_widgets.update_widget_struct(childs)		#a�adido
    
    
    def set_title(self):
        str = u'Tabular data'
        if self.struct is not None:
            str += u' - ' + self.struct.get_name()
        self.SetTitle(str)



    def display(self, struct):
        self.struct = struct
        self.set_title()
        self.build(True)



    def update(self, struct):
        if self.struct is not struct:
            return
        self.set_title()
        self.build(False)
        
        
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

        self.grid.CreateGrid(max, ncols)

        # establece t�tulos para as columnas
        col = 0
        while col < ncols:
            self.grid.SetColLabelValue(col,labels[col])
            col += 1

        # establece read-write para as celdas
        #self.grid.EnableEditing(True)

        # establece contidos das celas
        maxlen = 0 # tama�o m�ximo en caracteres, do que hai que hai que mostrar
        col = 0
	#contador de datos por columna
	lendata = 0						#a�adido
        while col < ncols:
            data = cols[col]
	    if len(data)>lendata:				#a�adido
		lendata=len(data)				#a�adido
            row = 0
            while row < len(data):
                if len(data[row]) > maxlen:
                    maxlen=len(data[row])
                self.grid.SetCellValue(row,col,data[row])
                row += 1
            col += 1

	#Si no hay datos se crea una fila para introducirlos
	if lendata==0:						#a�adido
	    self.grid.InsertRows(0, 1, True)			#a�adido
            
        # establece ali�ado
        col = 0
        while col < ncols:
            row = 0
            while row < max:
                self.grid.SetCellAlignment(row, col, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                row += 1
            col += 1

        print 'maxlen', maxlen,
        # incl�e no tama�o m�ximo os t�tulos das columnas
        for l in labels:
            if len(l) > maxlen:
                maxlen = len(l)
        print '->', maxlen,
        if maxlen < 1:
            maxlen = 1
        print '->', maxlen

        if new:
            sizex = self.grid.GetRowLabelSize() + 8 * maxlen * ncols
            self.SetSize( (sizex, -1) ) # xa levar� este a size_event

