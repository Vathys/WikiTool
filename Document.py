from anytree import NodeMixin, find
import os
import shutil

ROOT = os.getcwd()

SRC_NAME = 'src'
OUT_NAME = 'out'

def menu_print_sort(items):
	return sorted(items, key = lambda item: (not item.dir, item.out_name))

def toc_print_sort(items):
	return sorted(items, key = lambda item: item.out_name)

class Document(NodeMixin):
	'''
	fields:
		name: base name without the filetype (.md or .html) but will contain the ITOC indicator; it is basically the src_name without the .md
		src_name: name of file in src
		parent: parent node
		children: list of children
		dir: boolean for if the file has a linked folder
		itoc: if the file should have an inner table of contents
		out_name: name of file in out (basically without the ITOC indicator)
	'''
	
	def __init__(self, name, parent=None, children=None, dir=None, itoc=None, type=None, docx_src_path = None, **kwargs):
		# the name is the base name without the filetype (.md or .html) but will contain the ITOC indicator
		# it is basically the src_name without the .md
		self.separator = os.sep
		self.name = name;
		self.parent = parent;
		self.src_name = name + '.md' if not self.is_root else SRC_NAME
		self.out_name = name + '.html' if not self.is_root else OUT_NAME
		if children:
			self.children = children
		
		self.dir = dir if not dir == None else False
		self.type = type if not type == None else "standard"
		self.itoc = itoc if not itoc == None else False
		self.docx_src_path = docx_src_path if not docx_src_path == None else ""
	
	def get_src_path(self, get_dir = False):
		'''
		Returns the source path of the document relative to the wiki src folder
		get_dir: determines if the extension is placed at the end of the path or not
		'''
		if self.is_root:
			return self.src_name
		else:
			path = self.parent.get_src_path(get_dir = True)
			if get_dir and dir:
				return path + self.separator + self.name
			else:
				return path + self.separator + self.src_name
	
	def get_out_path(self, get_dir = False):
		'''
		# Returns the source path of the document relative to the wiki src folder
		get_dir: determines if the extension is placed at the end of the path or not
		'''
		if self.is_root:
			return self.out_name
		else:
			path = self.parent.get_out_path(get_dir = True)
			if get_dir and dir:
				return path + self.separator + self.name
			else:
				return path + self.separator + self.out_name
	
	def get_out_name(self):
		'''
		Returns the name of the file for printing in table of contents, menus, and etc.
		Basically replaces the "_" with space. Can include more processing if needed
		'''
		return os.path.splitext(self.out_name)[0].replace("_", " ")
	
	def remake_out(self, debug):
		'''
		In case of compilation of directories, it removes and the directory associated with the file and remakes it (this helps with possible restructuring issues)
		'''
		dir_node = os.path.join(ROOT, self.get_out_path(get_dir = True))
		if self.dir:
			if os.path.isdir(dir_node):
				if not debug:
					print("Removed %s..." % (dir_node))
					shutil.rmtree(dir_node)
				else:
					print("Removed directory %s" % (dir_node))
		
			if not debug:
				print("Remade %s..." % (dir_node))
				os.mkdir(dir_node)
			else:
				print("Remade directory %s..." % (dir_node))
	
	def dump_info(self):
		'''
		Dumps node information into 2 clearly defined sections: directly editable fields and directly non-editable fields.
		Note: In theory all fields can be edited, except to edit name, src_name and out_name, we use the rename method rather than change_field.
		'''
		editable_fields = ['dir', 'type', 'itoc', "docx_src_path"]
		print_info = []
		print_info.append("============================================================")
		for field in self.__dict__:
			if not field in editable_fields:
				print_info.append("%s: %s" % (field, self.__dict__[field]))
		print_info.append('----------editable-fields----------')
		for field in self.__dict__:
			if field in editable_fields:
				print_info.append("%s: %s" % (field, self.__dict__[field]))
		print_info.append("============================================================")
		
		return '\n'.join(print_info)
	
	def change_field(self, field, new_val):
		'''
		Changes the field for directly editable fields: dir, itoc, type
		More fields can be added and changed.
		
		Returns false if field was changed, and true if field was unchanged (this is slightly counterintuitive but the idea is that it returns true if there was an error)
		'''
		if field == 'dir':
			if new_val.lower() in ['true', 'false']:
				self.dir = (new_val.lower() == 'true')
			else:
				return False
		elif field == 'itoc':
			self.itoc = (new_val.lower() == 'true')
		elif field == 'type':
			if new_val in ['standard', 'two-col', 'maker\'s-notes', 'profile']:
				self.type = new_val
			else: 
				return False
		elif field == "docx_src_path":
			self.docx_src_path = os.path.normpath(new_val)
		else:
			return False
		
		return True
	
	def rename(self, new_name):
		'''
		Renames the node to a new name
		'''
		self.name = new_name
		self.src_name = self.name + '.md' if not self.is_root else SRC_NAME
		self.out_name = self.name + '.html' if not self.is_root else OUT_NAME
	
	def __repr__(self):
		return self.name

''' Documents function testing
testSRCPath 	-> test get_src_path()
testOUTPath 	-> test get_out_path()
testSRCDir 		-> test get_src_dir()
testOUTDir		-> test get_out_dir()

testMenuPrint	-> test cmd line menu printing
testTOCPrint	-> test markdown toc printing
'''

def testSRCPath(doc_parent):
	from anytree import RenderTree
	
	for pre, _, node in RenderTree(doc_parent):
		print("%s%s" % (pre, node.get_src_path()))

def testOUTPath(doc_parent):
	from anytree import RenderTree
	
	for pre, _, node in RenderTree(doc_parent):
		print("%s%s" % (pre, node.get_out_path()))

def testSRCDir(doc_parent):
	from anytree import RenderTree
	
	for child in doc_parent.children:
		for pre, fill, node in RenderTree(child):
			print("%s%s\n%s%s" % (pre, node.src_name, fill, node.parent.get_src_path(True)))

def testOUTDir(doc_parent):
	from anytree import RenderTree
	
	for child in doc_parent.children:
		for pre, fill, node in RenderTree(child):
			print("%s%s\n%s%s" % (pre, node.out_name, fill, node.parent.get_out_path(True)))

def testMenuPrint(doc_parent):
	from anytree import RenderTree, AbstractStyle
	menu_style = AbstractStyle("  ", "-\t", "-\t")
	
	i = 0
	for pre, fill, node in RenderTree(doc_parent, style = menu_style, childiter = menu_print_sort, maxlevel = 2):
		if i == 0:
			print("===== %s =====" % (node.name.upper()))
		else:
			print("%s\t-\t%s: %s" % ('dir' if node.dir else "file", i, node.src_name))
		i += 1
		
	selection = 4
	
	sel_item = menu_print_sort(doc_parent.children)[selection - 1].get_src_path()
	print(sel_item)

def testTOCPrint(doc_parent, level = None):
	from anytree import RenderTree, AbstractStyle
	toc_style = AbstractStyle("  ", "* ", "* ")
	# toc_style = ContStyle
	
	for pre, fill, node in RenderTree(doc_parent, style = toc_style, childiter = toc_print_sort, maxlevel = level):
		if node.name != doc_parent.name:
			relpath = os.path.relpath(node.get_out_path(), node.parent.get_out_dir())
			print(("%s[%s](." + os.sep + "%s)") % (pre, node.get_out_name(), relpath))
	
def printDocDictStruct(node):
	print(node.__dict__)

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	
	parser.add_argument('test', nargs = '+', choices = ('srcpath', 'outpath', 'srcdir', 'outdir', 'menuprint', 'tocprint', 'docdictstruct'))
	
	res = parser.parse_args()
	print("Document module testing...")
	
	ROOT = os.getcwd()
	OUT = os.path.join(ROOT, OUT_NAME)
	
	doc_parent = Document(SRC_NAME, is_dir = True)
	
	for subdir, dirs, files in os.walk(os.path.join(ROOT, doc_parent.src_name)):
		# find the Document object with name subdir
		parent = find(doc_parent, lambda node: node.name == subdir.split(os.sep)[-1])
		# search all the files in one particular subdirectory
		for file in files:
			# remove the file ending from name
			filename = os.path.splitext(file)[0]
			# check if there is a directory with the same filename
			# if so, make is_dir parameter true, else false
			_ = Document(filename, parent = parent, is_dir = (True if filename in dirs else False))
	
	if 'srcpath' in res.test:
		testSRCPath(doc_parent)
	
	if 'outpath' in res.test:
		testOUTPath(doc_parent)
		
	if 'srcdir' in res.test:
		testSRCDir(doc_parent)
		
	if 'outdir' in res.test:
		testOUTDir(doc_parent)
		
	if 'menuprint' in res.test:
		testMenuPrint(doc_parent)
		
	if 'tocprint' in res.test:
		testTOCPrint(doc_parent, level = 3)
		
	if 'docdictstruct' in res.test:
		printDocDictStruct(find(doc_parent, lambda node: node.name == 'index'))