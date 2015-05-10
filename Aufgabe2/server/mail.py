import os

class Mail():
	def __init__(self, filename):
		self.filename = filename
		self.content = []
		self.uid = ''
		self.deleted = False

	def load(self):
		file = open(self.filename, 'r')
		self.content = file.read().split('\r\n')
		self.uid = file.name[:file.name.index('.')]
		file.close()

	def size(self):
		return len(self.content)

	def as_string(self):
		return '\r\n'.join(self.content)

	def remove(self):
		os.remove(self.filename)