#!/usr/bin/env python
# -*- coding: utf-8 -*-



# list of aliases (temporary translate these strings)

alias = {
#    u'references_interactive': u'references',
#    u'labels_interactive': u'numbering',
#    u'scalar_field': u'filled',
#    u'scalar_field_range': u'threshold',
#    u'scalar_field_contour': u'contour',
#    u'scalar_field_deform': u'deformed',
#    u'scalar_field_line_probe_interactive': u'plot_over_line',
#    u'cut_interactive': u'slice',
#    u'clip_interactive': u'cut',
#    u'clip_raw_interactive': u'rough_cut',
#    u'deformed': u'scalar_deformed'
    }



# does plot need '<name>.plot.xml' ?

plotfile = {
    u'mesh': False,
    u'references': False,
    u'numbering': False,
    u'materials': False,
    u'filled': False,
    u'threshold': True,
    u'contour': True,
    u'scalar_deformed': True,
    u'vector_deformed': True,
    u'plot_over_line': True,
    u'slice': True,
    u'cut': True,
    u'rough_cut': True,
    u'vector_field': True,
    u'2d_graph': True,
    u'vector_components': True,
    u'pathline': True,
    u'streamline': True,
    u'image': False
    }



def get_alias(name):
    res = alias.get(name)
    if res is None:
        return name
    else:
        return res



def get_needs_plot(name):
    res = plotfile.get(name)
    if res is True:
        return True
    if res is False:
        return False
    if res is None:
        return None
