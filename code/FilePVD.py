#!/usr/bin/env python
# -*- coding: utf-8 -*-



#sys.path.append('..')



import sys
import trees



"""Reads .pvd files"""



def read(filename):
    """Read a .pvd file. Return list of times and filenames if ok, error string if ko"""
    
    times = []
    
    try:
        tree = trees.ET.parse(filename)
    except Exception , x:
        return u'Error loading .pvd file: \'' + filename + '\': ' + repr(x)

    root = tree.getroot()
    
    if root.tag != 'VTKFile':
        return u'Error loading .pvd file: root tag != \'VTKFile\''

    items = root.getchildren()

    collections = 0

    for item in items:
        if item.tag == u'Collection':
            collections += 1
            items2 = item.getchildren()
            for item2 in items2:
                if item2.tag != 'DataSet':
                    return u'Error loading .pvd file: dataset tag != \'DataSet\''
                time = item2.attrib.get('timestep')
                group = item2.attrib.get('group')
                part = item2.attrib.get('part')
                file = item2.attrib.get('file')
                
                # solo carga entradas con tiempo definido y convertible a float
                # solo carga entradas que son primeras partes
                # solo carga entradas con fichero definido
                if (time is not None and time != '') and \
                    (part is None or part == '0' or part == '') and \
                    (file is not None and file != ''):
                    
                    timedouble = None
                    try:
                        timedouble = float(time)
                    except ValueError, e:
                        pass

                    if timedouble is not None:
                        #data = {'time':time, 'file':file}
                        data = {'time':timedouble, 'file':file}
                        times.append(data)
                    else:
                        print '.pvd file \'' + filename + '\': line skipped (can\'t convert \''+time+'\' to float)'

                else:
                    print '.pvd file \'' + filename + '\': line skipped'
            
            
    if collections != 1:
        return u'Error loading .pvd file: incorrect number of \'Collection\' tags ('+unicode(collections)+')'

    return times



if __name__ == '__main__':
    args = len(sys.argv)
    if args == 2:
        res = read(sys.argv[1])
        if isinstance(res,list):
            for r in res:
                print r
        else:
            print 'result:', res
