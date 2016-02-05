#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET


class NodeObj:
	def __init__(self, node=None):
		if node is not None:
			self.parse(node)
	
	def parse(self, node):
		pass
	
	def as_node(self, parent=None):
		return '<node/>'


class Medication(NodeObj):
	def __init__(self, node=None):
		self.attributes = None
		self.data = None
		self.content = None
		super().__init__(node)
	
	def __getattr__(self, key):
		if self.attributes is not None:
			for attr in self.attributes:
				if key == attr.key:
					return attr.value
	
	def parse(self, node):
		assert('medicalInformation' == node.tag)
		
		# update from child node text
		attrs = []
		for child in node:
			if not child.tag in ['style', 'content', 'sections']:
				attrs.append(MedicationAttribute(self, child))
		for key, val in node.attrib.items():
			attr = MedicationAttribute(self)
			attr.key = key
			attr.value = val
			attrs.append(attr)
		self.attributes = attrs
		
		# create data from sections
		data = node.find('sections')
		if data is not None and len(data) > 0:
			sects = []
			for child in data.findall('section'):
				sects.append(MedicationData(child))
			self.data = sects
		
		# <content> is dirty HTML; unescape and clean it up
		content_node = node.find('content')
		if content_node is not None and content_node.text:
			from . import medicationcontent
			self.content = medicationcontent.MedicationContent(self, content_node)
			
			# update sections from data in HTML
			if self.data is not None:
				for sect in self.data:
					mapped = self.content.mapped(sect.id)
					if mapped is not None:
						sect.take_values(mapped)
	
	def as_node(self, parent=None):
		if parent is not None:
			medi = ET.SubElement(parent, 'medication')
		else:
			medi = ET.Element('medication')
		
		if self.attributes is not None:
			for attr in self.attributes:
				attr.as_node(medi)
		
		if self.data is not None:
			for data in self.data:
				data.as_node(medi)
		
		return medi
		

class MedicationAttribute(NodeObj):
	def __init__(self, medi, node=None):
		assert(isinstance(medi, Medication))
		self.medi = medi
		self.key = None
		self.value = None
		super().__init__(node)
	
	def parse(self, node):
		self.key = node.tag
		self.value = node.text
	
	def as_node(self, parent=None):
		if parent is not None:
			node = ET.SubElement(parent, self.key)
		else:
			node = ET.Element(self.key)
		node.text = self.value
		return node


class MedicationData(NodeObj):
	def __init__(self, node=None):
		self.id = None
		self.title = None
		self.value = []
		self.subdata = None
		super().__init__(node)
	
	def parse(self, node):
		assert('section' == node.tag[-7:])
		self.id = node.get('id')
		self.title = node.find('title').text
	
	def add_value(self, value):
		if isinstance(value, ET.Element):
			self.value.append(value)
		elif len(value.strip()) > 0:
			self.value.append(value.strip())
	
	def take_values(self, values):
		for value in values:
			self.add_value(value)
	
	def add_subdata(self, subdata):
		assert(isinstance(subdata, MedicationData))
		if self.subdata is None:
			self.subdata = []
		self.subdata.append(subdata)
	
	def as_node(self, parent=None):
		attrib = {}
		if self.id:
			attrib['id'] = self.id
		if self.title:
			attrib['title'] = self.title
		
		if parent is not None:
			node = ET.SubElement(parent, 'data', attrib=attrib)
		else:
			node = ET.Element('data', attrib=attrib)
		
		for value in self.value:
			sub = ET.SubElement(node, 'value')
			if isinstance(value, ET.Element):
				sub.append(value)
			else:
				sub.text = value
		
		if self.subdata is not None:
			for sub in self.subdata:
				sub.as_node(node)
		
		return node
