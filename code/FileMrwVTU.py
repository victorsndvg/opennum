#!/usr/bin/env python
# -*- coding: utf-8 -*-



import FileMrwVTK



class FileMrwVTU(FileMrwVTK.FileMrwVTK):



    def __init__(self, callback=None):
        FileMrwVTK.FileMrwVTK.__init__(self, callback)


    def write_cell_point_data_vtu(self, openfile, d):
    
        tam = "1"
        if d['type'].lower() == 'SCALARS':
            tam = "1"
        elif d['type'].lower() == 'VECTORS':
            tam = "3"
        
        if d['tam'] is not None: # sobreescribe tam
            tam = unicode(d['tam'])

        if d['format'].lower() == 'int':
            format = 'Int32'
        elif d['format'].lower() == 'double':
            format = 'Float64'
        elif d['format'].lower() == 'float':
            format = 'Float32'
        else:
            format = 'Float64'
                
        openfile.write('    <DataArray type="'+format+'" Name="'+d['name']+'" ' +\
                'NumberOfComponents="'+tam+'" format="ascii">\n')

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

        openfile.write('    </DataArray>\n')



    def save2(self, openfile):
        npun = len(self.points)//3
        ncel = len(self.cells)
        openfile.write('<?xml version="1.0"?>\n')
        openfile.write('<VTKFile type="UnstructuredGrid" version="0.1" byte_order="LittleEndian">\n')
        openfile.write(' <UnstructuredGrid>\n')
        openfile.write('  <Piece NumberOfPoints="'+unicode(npun)+'" NumberOfCells="'+unicode(ncel)+'">\n')

        openfile.write('   <Points>\n')
        openfile.write('    <DataArray type="Float64" NumberOfComponents="3" Name="Point" format="ascii">\n')
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
        openfile.write('    </DataArray>\n')
        openfile.write('   </Points>\n')
        
        openfile.write('   <Cells>\n')
        openfile.write('    <DataArray type="Int32" Name="connectivity" format="ascii">\n')
        for cell in self.cells:
            index = 0
            while index < len(cell):
                openfile.write(repr(cell[index]))
                if index + 1 == len(cell):
                    openfile.write('\n')
                else:
                    openfile.write(' ')
                index += 1
        openfile.write('    </DataArray>\n')
        openfile.write('    <DataArray type="Int32" Name="offsets" format="ascii">\n')
        index = 0
        off = 0
        for cell in self.cells:
            off += len(cell)
            openfile.write(unicode(off))
            if index % 10 == 9:
                openfile.write('\n')
            else:
                openfile.write(' ')
            index += 1
        if index % 10 != 0:
            openfile.write('\n')
        openfile.write('    </DataArray>\n')
        openfile.write('    <DataArray type="UInt8" Name="types" format="ascii">\n')
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
        openfile.write('    </DataArray>\n')
        openfile.write('   </Cells>\n')
        
        openfile.write('   <PointData>\n')
        for d in self.pdata:
            self.write_cell_point_data_vtu(openfile, d)
        openfile.write('   </PointData>\n')
        
        openfile.write('   <CellData>\n')
        for d in self.cdata:
            self.write_cell_point_data_vtu(openfile, d)
        openfile.write('   </CellData>\n')
        
        openfile.write('  </Piece>\n')
        openfile.write(' </UnstructuredGrid>\n')
        openfile.write('</VTKFile>\n')

        return True
