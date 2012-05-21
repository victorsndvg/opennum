#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import dialogs
import sys
import vtk



def save_renderwindow(parent, renderwindow, title=None):
#    formats = u"JPEG (*.jpg)|*.jpg" + \
#        u"|PNG (*.png)|*.png" + \
#        u"|BMP (*.bmp)|*.bmp" + \
#        u"|TIFF (*.tiff)|*.tiff" + \
#        u"|PDF (*.pdf)|*.pdf" + \
#        u"|EPS (*.eps)|*.eps" + \
#        u"|PS (*.ps)|*.ps" + \
#        u"|SVG (*.svg)|*.svg"
    extensions = ['.jpg','.png','.bmp','.tiff']				#añadido
    formats = u"JPEG (*.jpg)|*.jpg" + \
        u"|PNG (*.png)|*.png" + \
        u"|BMP (*.bmp)|*.bmp" + \
        u"|TIFF (*.tiff)|*.tiff"

    [file,ext_index] = dialogs.get_file_save(parent,u".",u"",formats,title)#añadido
    if file is None:
        return

    print "file:", file

    point = file.rfind('.')
    if point == -1:
        base = file
        extension = extensions[ext_index]
    else:
        base = file[:point]
        extension = file[point:]

#    splitname = file.split('.')
#    if len(splitname) == 1:						#añadido
#        base = file							#añadido
#        extension = extensions[ext_index]				#añadido
#    else:								#añadido
#        base = splitname[0]						#añadido
#        extension = splitname[1]					#añadido

    error = None
    
    if extension == '.jpg' or extension == '.png' or \
            extension == '.bmp' or extension == '.tiff':
        error = save_image(renderwindow, base, extension)
    elif extension == '.pdf' or extension == '.eps' or \
            extension == '.svg' or extension == '.ps':
        error = save_exporter(renderwindow, base, extension)
    else:
        error = u'Unknown file extension: ' + extension

    if error is not None:
        dialogs.show_error(parent, error)

def save_movie_renderwindow(parent, renderwindow, title=None):			#añadido
						
    codec = [u'AVI',u'FFMPEGHQ',u'FFMPEGLQ',u'OGGTHEORA',u'MPEG2']				#añadido
    extensions = [u'.avi',u'.avi',u'.avi',u'.ogv',u'.mpg']			#añadido
    formats = u"AVI (*.avi)|*.avi" + \
        u"|FFMPEG (HQ) (*.avi)|*.avi" + \
        u"|FFMPEG (LQ) (*.avi)|*.avi" + \
        u"|OGGTHEORA (*.ogv)|*.ogv" + \
	u"|MPEG2 (*.mpg)\*.mpg"
    file = None									#añadido
    ext_index = None								#añadido
    [file,ext_index] = dialogs.get_file_save(parent,u".",u"",formats,title)	#añadido
    if file is None:								#añadido
        return None								#añadido

    point = file.rfind('.')							#añadido
    if point == -1:								#añadido
        base = file								#añadido
        extension = extensions[ext_index]					#añadido
    else:									#añadido
        base = file[:point]							#añadido
        extension = file[point:]						#añadido
    return [base+extension,codec[ext_index]]						#añadido


def save_image(renderwindow, base, extension):
    file = (base+extension).encode(sys.getfilesystemencoding())
    print 'save_image', file
    
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(renderwindow)
    w2i.Modified()
    if extension == '.jpg':
        image = vtk.vtkJPEGWriter()
        image.SetQuality(100)
    elif extension == '.png':
        image = vtk.vtkPNGWriter()
    elif extension == '.bmp':
        image = vtk.vtkBMPWriter()
    elif extension == '.tiff':
        image = vtk.vtkTIFFWriter()
        image.SetCompressionToNoCompression()
    else:
        return "Image exporter: unknown file extension: " + extension
    
    image.SetInput(w2i.GetOutput())
    image.SetFileName(file)
    image.Write()
    
    return None



def save_exporter(renderwindow, base, extension):
    base = base.encode(sys.getfilesystemencoding())
    print 'save_exporter', base, '+', extension
    
    try:
        exporter = vtk.vtkGL2PSExporter()
    except AttributeError, e:
        return 'Can\'t export image: ' + unicode(e)
        
    exporter.DrawBackgroundOff()
    exporter.SetInput(renderwindow)
    exporter.SetFilePrefix(base)
    
    if extension == '.pdf':
        exporter.SetFileFormatToPDF()
    elif extension == '.eps':
        exporter.SetFileFormatToEPS()
    elif extension == '.ps':
        exporter.SetFileFormatToPS()
    elif extension == '.tex':
        exporter.SetFileFormatToTeX()
    elif extension == '.svg':
        exporter.SetFileFormatToSVG()
        exporter.CompressOff()
    else:
        return u'Exporter: unknown file extension: ' + extension

    exporter.Write()
    
    return None
