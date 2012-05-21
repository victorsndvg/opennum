#!/usr/bin/env python
# -*- coding: utf-8 -*-



import FileMrw



class FileMrwVTK(FileMrw.FileMrw):



    def __init__(self, callback=None):
        FileMrw.FileMrw.__init__(self, callback)
        self.comm = ''
        self.points = []
        self.cells = []
        self.types = []
        self.pdata = []
        self.cdata = []
        self.format1 = 'double'
        self.format2 = 'int'



    def set_comm(self, comm):
        self.comm = comm



    def add_point(self, x,y,z):
        self.points.append(x)
        self.points.append(y)
        self.points.append(z)



    def set_points(self, p):
        self.points = p



    def add_cell_type(self, p, t):
        self.cells.append(p)
        self.types.append(t)



    def set_cells(self, p):
        self.cells = p



    def set_types(self, t):
        self.types = t


        
    def get_point_num(self):
        return len(self.points) // 3



    def get_cell_num(self):
        return len(self.cells)



    def add_cell_data(self, dtype, dname, dformat, dtam, data):
        cdata = {'type':dtype, 'name':dname, 'format':dformat, 'tam': dtam, 'data':data}
        self.cdata.append(cdata)



    def add_point_data(self, dtype, dname, dformat, dtam, data):
        pdata = {'type':dtype, 'name':dname, 'format':dformat, 'tam': dtam, 'data':data}
        self.pdata.append(pdata)



    # metodo especifico
    def add_point_data_sequential(self):
        temp = range(1, len(self.points)//3 + 1)
        self.add_point_data('SCALARS','vertex_num','int',None,temp)



    # metodo especifico # solo fuera sabe la numeracion de los elementos necesarios !
    def add_cell_data_sequential(self, temp):
        self.add_cell_data('SCALARS','element_num','int',None,temp)



    def check(self):
        for pd in self.pdata:
            if pd.get('type') == 'VECTORS':
                if len(pd['data']) != len(self.points):
                    return 'vectors: #pdata!=#points ' + unicode(len(pd['data'])) + '!=' + unicode(len(self.points))
            else: # scalars ?
                if 3 * len(pd['data']) != len(self.points):
                    return 'scalars: #pdata!=#points 3*' + unicode(len(pd['data'])) + '!=' + unicode(len(self.points))
        for cd in self.cdata:
            if cd.get('type') == 'VECTORS':
                if len(cd['data']) != 3 * len(self.cells):
                    return 'vectors: #cdata!=#cells '  + unicode(len(cd['data'])) + '!=3*' + unicode(len(self.cells))
            else: # scalars ?
                if len(cd['data']) != len(self.cells):
                    return '#cdata!=#cells ' + unicode(len(cd['data'])) + '!=' + unicode(len(self.cells))
        if len(self.types) != len(self.cells):
            return '#types!=#cells ' + unicode(len(self.types)) + '!=' + unicode(len(self.cells))
        for c in self.cells:
            for p in c:
                if p >= len(self.points):
                    return 'point#>#points'
        return True



    def write_cell_point_data_vtk(self, openfile, d):
        openfile.write(d['type'])
        openfile.write(' ')
        openfile.write(d['name'])
        openfile.write(' ')
        openfile.write(d['format'])
        if d['tam'] is not None:
            openfile.write(' ')
            openfile.write(unicode(d['tam']))
        openfile.write('\n')
        if d['type'] == 'SCALARS':
            openfile.write('LOOKUP_TABLE default\n')
        index = 0
        for v in d['data']:
            openfile.write(repr(v))
            if index % 10 == 9:
                openfile.write('\n')
            else:
                openfile.write(' ')
            index += 1
        if index % 10 != 0:
            openfile.write('\n')



    def save2(self, openfile):
        openfile.write('# vtk DataFile Version 2.0\n')
        openfile.write(self.comm+'\n')
        openfile.write('ASCII\n')
        openfile.write('DATASET UNSTRUCTURED_GRID\n')
        openfile.write('\n') # separacion

        n1 = len(self.points)//3
        openfile.write('POINTS ' + unicode(n1) + ' ' + self.format1 + '\n')
        i = 0
        f = len(self.points)
        while i < f:
            openfile.write(repr(self.points[i]))
            openfile.write(' ')
            openfile.write(repr(self.points[i+1]))
            openfile.write(' ')
            openfile.write(repr(self.points[i+2]))
            openfile.write('\n')
            i += 3
        openfile.write('\n') # separacion

        n1 = len(self.cells)
        n2 = 0
        for cell in self.cells:
            n2 += len(cell) + 1
        openfile.write('CELLS ' + unicode(n1) + ' ' + unicode(n2) + '\n')
        for cell in self.cells:
            openfile.write(unicode(len(cell)))
            openfile.write(' ')
            for v in cell:
                openfile.write(repr(v))
                openfile.write(' ')
            openfile.write('\n')
        openfile.write('\n') # separacion

        n1 = len(self.types)
        openfile.write('CELL_TYPES ' + unicode(n1) + '\n')
        index = 0
        for ctype in self.types:
            openfile.write(unicode(ctype))
            if index % 10 == 9:
                openfile.write('\n')
            else:
                openfile.write(' ')
            index += 1
        if index % 10 != 0:
            openfile.write('\n')
        openfile.write('\n') # separacion
    

        if len(self.pdata)>0:
            openfile.write('POINT_DATA ' + unicode(len(self.points)//3) + '\n')
            for d in self.pdata:
                self.write_cell_point_data_vtk(openfile, d)
            openfile.write('\n') # separacion

        if len(self.cdata)>0:
            openfile.write('CELL_DATA ' + unicode(len(self.cells)) + '\n')
            for d in self.cdata:
                self.write_cell_point_data_vtk(openfile, d)
            openfile.write('\n') # separacion

        return True

