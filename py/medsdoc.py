#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import logging
import xml.dom.minidom as minidom    # for pretty-printing
import xml.etree.ElementTree as ET   # for parsing and element creation

from . import medication


class MedsDoc:
	def __init__(self, filepath):
		self.filepath = filepath
		self.meds = None
	
	def write_to(self, filepath):
		""" Parses the AIPS XML present at `self.filepath`, cleans and writes
		all medications to the given path.
		
		This method does not use ElementTree.write since it a) cannot produce
		pretty-printed XML and b) requires the whole parsing to stay in RAM.
		Instead we manually write the root nodes and then append each
		medication as it is parsed.
		
		:param filepath: The path of the output file; will be overwritten
		"""
		print("-->  Parsing tree...")
		tree = ET.parse(self.filepath)
		root = tree.getroot()
		assert('medicalInformations' == root.tag)
		
		print("-->  Tree parsed, processing meds...")
		with io.open(filepath, 'w', encoding='utf-8') as h:
			h.write("<medications>")
			i = 0
			for med_node in root.iter('medicalInformation'):
				#if i > 10:
				#	break
				print("--->  {}".format(i), end="\r")
				try:
					medi = medication.Medication(med_node)
					new_node = medi.as_node()
					as_dom = minidom.parseString(ET.tostring(new_node))
					as_xml = as_dom.documentElement.toprettyxml().strip().replace("\n", "\n\t")
					h.write("\n\t"+as_xml)
				except Exception as e:
					print("xxx>  {}".format(i))
					raise e
				i += 1
			
			# finish
			print()
			h.write("\n</medications>\n")
		
		print("-->  Done")

