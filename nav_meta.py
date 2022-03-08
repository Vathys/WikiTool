import os
import Document
from anytree import find, NodeMixin
from anytree.importer import JsonImporter, DictImporter
from anytree.exporter import JsonExporter, DictExporter
from collections import OrderedDict
import re

ROOT = os.getcwd()
META_NAME = 'meta.json'
META = os.path.join(ROOT, META_NAME)

SRC_NAME = 'src'
OUT_NAME = 'out'

SRC = os.path.join(ROOT, SRC_NAME)
OUT = os.path.join(ROOT, OUT_NAME)
ASSETS = os.path.join(OUT, "assets")

exporter = JsonExporter(indent = 1, sort_keys = True, allow_nan = True)
doc_importer = DictImporter(Document.Document)
importer = JsonImporter(doc_importer)

class DocumentMeta(NodeMixin):
	def __init__(self, doc = None):
		self.label = doc.name
		self.href = os.path.join(ROOT, doc.get_out_path()).replace("\\", "/")
		temp_children = []
		for child in doc.children:
			temp_children.append(DocumentMeta(doc = child))
		self.children = temp_children

def growTree(doc_root):
	for subdir, dirs, files in os.walk(os.path.join(ROOT, doc_root.name)):
		# find the Document object with name subdir
		parent = find(doc_root, lambda node: node.name == subdir.split(os.sep)[-1])
		# search all the files in one particular subdirectory
		for file in files:
			# remove the file ending from name
			filename = os.path.splitext(file)[0]
			# check if there is a directory with the same filename
			# if so, make is_dir parameter true, else false
			if not filename.endswith("__doc"):
				_ = Document.Document(filename, parent = parent, dir = (True if filename in dirs else False))
	
	return doc_root

def exportTree(root, metafile):
	exporter.write(root, open(metafile, 'w'))

def genExportTree(root, metafile):
	exporter.write(root, open(metafile, 'x'))

def importTree(metafile):
	return importer.read(open(metafile, 'r'))

def getNavJson():
	doc_root = importTree(META)
	
	nav_root = DocumentMeta(doc = doc_root)
	
	nav_file = os.path.join(OUT, "tmpl", "meta_vars.js")
	
	nav_dict_ex = DictExporter(childiter = lambda children: sorted(children, key = lambda item: item.label))
	nav_json_exp = JsonExporter(nav_dict_ex, indent = 1)
	
	nav_json_exp.write(nav_root, open(nav_file, 'w'))
	
	contents = []

	with open(nav_file, 'r', encoding = 'utf-8') as f:
		contents = f.readlines()
	
	json = "".join(contents)
	
	#json = json.replace('"', '')
	pattern = re.compile(r'\s+')
	
	json = re.sub(pattern, '', json)
	
	json = 'var data = `' + json + '`;'
	
	with open(nav_file, 'w') as f:
		f.writelines([json])
	
if __name__ == "__main__":
	getNavJson()