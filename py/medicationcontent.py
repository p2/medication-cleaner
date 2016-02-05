#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bs4
import html
import logging
import xml.etree.ElementTree as ET

try:
	from . import medication
except ImportError:
	import py.medication as medication

class MedicationContent(medication.NodeObj):
	def __init__(self, medi, node=None):
		assert(isinstance(medi, medication.Medication))
		self.medi = medi
		self.html = None
		self.map_dict = None
		super().__init__(node)
	
	def mapped(self, key):
		return self.map_dict.get(key) if self.map_dict is not None else None
	
	def parse(self, node):
		unescaped = html.unescape(node.text)
		soup = bs4.BeautifulSoup(unescaped, 'html.parser')
		
		# create a map between HTML section ids and their content (i.e. the
		# nodes following it)
		mapped = {}
		curr_id = None
		previous = None
		for p in soup.div:
			if isinstance(p, bs4.NavigableString):
				if len(p.strip()) > 0:
					logging.warning('Found non-empty string at top level of HTML: {}'.format(p))
				continue
			
			sec_id = p.get('id')
			if sec_id:
				curr_id = sec_id
				previous = None
			
			elif curr_id:
				current = mapped.get(curr_id, [])
				if 'table' == p.name:
					current.append(self.data_from_table(p))
				elif previous is not None and previous.name == p.name:
					t_prev = current[len(current)-1]
					t_this = p.text
					
					# if there's a space between the previous and this tag, concatenate
					if t_this and len(t_this) > 0 and t_prev and len(t_prev) > 0 and (' ' == t_prev[-1] or ' ' == t_this[0]):
						current[len(current)-1] += t_this
					else:
						current.append(t_this)
				else:
					current.append(p.text)
				mapped[curr_id] = current
				previous = p
		
		self.map_dict = mapped
	
	def data_from_table(self, table):
		data = ET.Element('table')
		for row in table.find_all('tr'):
			tr = ET.SubElement(data, 'tr')
			for cell in row.find_all('td'):
				td = ET.SubElement(tr, 'td')
				td.text = cell.text
				if td.text:
					td.text = td.text.strip()
				if cell.has_attr('rowspan'):
					td.set('rowspan', cell['rowspan'])
				if cell.has_attr('colspan'):
					td.set('colspan', cell['colspan'])
		# print(ET.tostring(data, encoding="unicode"))
		return data

