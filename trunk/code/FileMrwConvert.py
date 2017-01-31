#!/usr/bin/env python
# -*- coding: utf-8 -*-



import FileMrwReconvxx as R
import FileMrwScalars as S
import sys



if __name__ == '__main__':
    def print_( string ):
        print ':', string

    args = len(sys.argv)

    if args < 3:
        print '\t converts Reconvxx mesh to vtk or vtu mesh\n'
        print 'use: python FileMrwConvert.py [-sub|-nosub] [-dim <dim>] input.mfm output.[vtk|vtu] [-cell field.mff | -point field.mff]'
        print
        print '\t-nosub -> do not create submesh (default)'
        print '\t-sub -> create submesh'
        print '\t-dim <dim> -> only read files of dimension <dim>'
        print '\t-cell file.mff -> adds cell field data'
        print '\t-point file.mff -> adds point field data'
        print
        print 'example: python FileMrwConvert.py -sub -dim 2 input.mfm output.vtk  #converts 2D input.mfm to output.vtk creating submesh\n'
        print 'example: python FileMrwConvert.py input.mfm output.vtu  #converts input.mfm to output.vtu without creating submesh\n'
        print 'example: python FileMrwConvert.py input.mfm output.vtk -point field  #converts input.mfm to output.vtk without creating submesh and incorporating point field\n'
        sys.exit(1)


    dim = None
    submesh = False
    fieldtype = 'point'
    ffield = None
    extra = []

    i = 1
    while i < args:
        if sys.argv[i] == '-dim':
            if i + 1 == args:
                print 'Error: missing dimension'
                sys.exit(10)
            else:
                dim = int(sys.argv[i + 1])
            i += 1
        elif sys.argv[i] == '-sub':
            submesh = True
        elif sys.argv[i] == '-nosub':
            submesh = False
        elif sys.argv[i] == '-cell':
            if i + 1 == args:
                print 'Error: missing cell field filename'
                sys.exit(10)
            else:
                ffield = sys.argv[i + 1]
                fieldtype = 'cell'
            i += 1
        elif sys.argv[i] == '-point':
            if i + 1 == args:
                print 'Error: missing point field filename'
                sys.exit(10)
            else:
                ffield = sys.argv[i + 1]
                fieldtype = 'point'
            i += 1
        else:
            extra.append(sys.argv[i])
        i += 1

    if len(extra) != 2:
        print 'Error: Exactly one input filename and one output filename needed'
        sys.exit(12)

    finput = extra[0]
    foutput = extra[1]

    if foutput.endswith('.vtk'):
        tp = 0
    elif foutput.endswith('.vtu'):
        tp = 1
    else:
        print 'Outputs only .vtk or .vtu'
        sys.exit(5)

    rr = R.FileMrwReconvxx(print_)
    res = rr.read(finput,{'dim':dim})
    if res is not True:
        print res
        print 'Aborting'
        sys.exit(3)

    if submesh:
        res = rr.calculate_submesh()
        if res is not True:
            print res
            print 'Aborting'
            sys.exit(4)

    if tp == 0:
        t = rr.to_vtk()
    elif tp == 1:
        t = rr.to_vtu()
    else:
        print 'Outputs only .vtk or .vtu'
        sys.exit(5)

    # array .. id [0..n-1] -> [1..n]
    # para ter os números dispoñibles para as etiquetas
    t.add_point_data_sequential()
    array = range(1, rr.nel + 1) # elementos originales numerados
    array.extend([0] * rr.nsm) # la submalla no se numera
    t.add_cell_data_sequential(array)
    
    if ffield is not None:
        ss = S.FileMrwScalars(print_)
        ss.read(ffield,{})
        if fieldtype == 'cell':
            t.add_cell_data('SCALARS','val','double',None,ss.gets())
        elif fieldtype == 'point':
            t.add_point_data('SCALARS','val','double',None,ss.gets())
        else:
            print 'Error: unknown field type'
            sys.exit(11)

    # optional
    # warning
    res = t.check()
    if res is not True:
        print 't.check():', res
        print 'Aborting'
        sys.exit(6)

    print t.save(foutput)

