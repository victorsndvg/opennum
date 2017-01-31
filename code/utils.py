#!/usr/bin/env python
# -*- coding: utf-8 -*-



def indent(element, level=0, last=False):

    children = element.getchildren()

    l = level
    if (last):
        l = l - 1
    if (l<0):
        l = 0

    element.tail = u'\n' + (u'\t' * l)

    if len(children) == 0:
        string2 = u'\n' + (u'\t' * level)
    else:
        string2 = u'\n' + (u'\t' * (level+1))

    if not isinstance(element.text,basestring):
        element.text = string2

    i = 0
    for child in children:
        is_last = i + 1 == len(children)
        indent(child, level+1, is_last)
        i = i + 1
