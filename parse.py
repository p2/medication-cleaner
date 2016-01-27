#!/usr/bin/env python3
#

import py.medsdoc as md


if '__main__' == __name__:
	doc = md.MedsDoc('Download.xml')
	doc.write_to('Cleaned.xml')

