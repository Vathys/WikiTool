import os
import subprocess
import time
import argparse
import shutil
import traceback
from anytree import AbstractStyle, RenderTree, find, PreOrderIter

import Document
import nav_meta as nm

''' TO-DO
* create a config file with the following fields
	* absolute path for root
	* absolute path of css file
	* absolute path for html file
	* absolute path for resource folder (creates assets folder in root if not specified)

* implement .css and .html and .js for different profiles
	* standard (already done)
	* maker's note
	* two-column
	
* Spell-check
	* lua script now identifies which words are zean and english by checking if they are surrounded by {{...}}. 
	* Next step is to add zean dictionary to aspell.
		* Figure out how to use aspell
'''

ROOT = os.getcwd()
META_NAME = 'meta.json'
META = os.path.join(ROOT, META_NAME)

SRC_NAME = 'src'
OUT_NAME = 'out'
ASSET_NAME = 'assets'

OUT_TYPE = 'html5'
OUT_FORMAT = 'markdown+footnotes+grid_tables+definition_lists+yaml_metadata_block+fenced_divs-implicit_figures'

''' new template, css, js file implementation
TYPES = {"standard": 	{
							"template": os.path.join(ROOT, OUT_NAME, "tmpl", "standard.tmpl"),
							"css": os.path.join(ROOT, OUT_NAME, "css", "standard.css"),
							"js": os.path.join(ROOT, OUT_NAME, "standard.js")
						},
		"profile":		{
							"template": os.path.join(ROOT, OUT_NAME, "tmpl", "standard.tmpl"),
							"css": os.path.join(ROOT, OUT_NAME, "css", "standard.css"),
							"js": os.path.join(ROOT, OUT_NAME, "standard.js")
						},
		"two-column":	{
							"template": os.path.join(ROOT, OUT_NAME, "tmpl", "standard.tmpl"),
							"css": os.path.join(ROOT, OUT_NAME, "css", "standard.css"),
							"js": os.path.join(ROOT, OUT_NAME, "standard.js")
						}
}
'''


# standard
TEMPLATE_FILE = os.path.join(ROOT, OUT_NAME, "tmpl", "standard.tmpl")
CSS_FILE = os.path.join(ROOT, OUT_NAME, "css", "standard.css")
JS_FILE = os.path.join(ROOT, OUT_NAME, "js", "standard.js")

# LUA
STANDARD_LUA_FILE = os.path.join(ROOT, OUT_NAME, "lua", "standard.lua")
TOC_LUA_FILE = os.path.join(ROOT, OUT_NAME, "lua", "toc.lua")
SPELL_CHECK_LUA_FILE = os.path.join(ROOT, OUT_NAME, "lua", "spellcheck.lua")
DOC_LUA_FILE = os.path.join(ROOT, OUT_NAME, "lua", "doc.lua")

# META
NAV_JSON_FILE = os.path.join(ROOT, OUT_NAME, "tmpl", "meta_vars.js")

try: 
	os.remove(os.path.join(ROOT, OUT_NAME, "logs", "spellcheck_log.txt"))
except FileNotFoundError:
	print("logfile not found")

BASE = "pandoc -f %s -t %s -s --template=%s -V css=%s -V js=%s -V meta_vars=%s --lua-filter=%s --lua-filter=%s -M link_base=%s" % (OUT_FORMAT, OUT_TYPE, TEMPLATE_FILE, CSS_FILE, JS_FILE, NAV_JSON_FILE, STANDARD_LUA_FILE, SPELL_CHECK_LUA_FILE, os.path.join(ROOT, OUT_NAME))
# BASE = "pandoc -f %s -t %s -s --template=%s -V css=%s -V js=%s -V meta_vars=%s --lua-filter=%s -M link_base=%s" % (OUT_FORMAT, OUT_TYPE, TEMPLATE_FILE, CSS_FILE, JS_FILE, NAV_JSON_FILE, STANDARD_LUA_FILE, os.path.join(ROOT, OUT_NAME))

menu_style = AbstractStyle(" \t", "-\t", "-\t")
toc_style = AbstractStyle("  ", "* ", "* ")

def pos_int(x):
	x = int(x)
	if x < 0:
		raise argparse.ArgumentError("Integer must be bigger than or equal to 0")
	return x

def compile_file(node, debug, open_after = False):
	'''
	compile a single file
	
	parameters:
		node: Document-class node to compile
		debug: print call instead of executing call
		open_after: start the output after compiling or not?
	'''
	input = os.path.join(ROOT, node.get_src_path())
	output = os.path.join(ROOT, node.get_out_path())
	
	start = time.time()
	
	call = BASE
	
	if node.itoc:
		call += " --toc --toc-depth=4 --lua-filter=%s" % (TOC_LUA_FILE)
	
	if node.dir:
		otoc_contents = "\n::: {.toc}\n\n"
		otoc_contents += "# Outer Table of Content\n"
		otoc_contents += printTOC(node, level = 2)
		otoc_contents += ":::\n"
		
		with open(input, 'r', encoding = 'utf-8') as fd:
			contents = fd.readlines()
		
		i = 0;
		while(contents[i] != '\n'):
			i += 1
			if i >= len(contents):
				break
		contents.insert(i, otoc_contents)
		
		temp_file = os.path.join(ROOT, node.parent.get_src_path(True), "temp_" + node.src_name)
		
		with open(temp_file, 'w', encoding = 'utf-8') as fd:
			fd.writelines(contents)
		
		full_input = temp_file
	else:
		full_input = input
	
	if not node.docx_src_path == "":
		full_input += " " + os.path.join(ROOT, node.get_src_path(get_dir = True) + "__doc.md")
	
	call += " -o %s %s" % (output, full_input)
	
	if not debug:
		os.system(call)
		if open_after:
			os.system("start " + output)
		
	if node.dir:
		os.remove(temp_file)
	end = time.time()
	
	print(f"Created {output} in {end - start}s...")
	
	if debug:
		print(call)
		if open_after:
			print("start " + output)
			
		print()

def compile(node, debug, open_after = False):
	'''
	recursive compile function
	
	If children of node exists, recursively call compile on children. 
	Then if node is not the src node, compile the node itself.
	
	Keep in mind if open_after is true, it only goes on the main node itself and not its children or grandchildren or thereafter
	'''
	
	if not node.is_root:
		node.remake_out(debug)
	
	if node.children:
		for child in node.children:
			compile(child, debug)
	
	if not node.is_root:
		compile_file(node, debug, open_after)
	
	if node.is_root and open_after:
		index = find(node, lambda node: node.name == "index")
		if not debug:
			os.system("start " + os.path.join(ROOT, index.get_out_path()))
		else:
			print("start " + os.path.join(ROOT, index.get_out_path()))

def new_file_contents(name):
	result = ""
	result += "---\n"
	result += "title: %s\n" % (name)
	result += "---\n"
	
	return result

def compile_docx_src(root, debug = False):
	call_prefix = "pandoc -f docx -t markdown --wrap=none --lua-filter=%s" % (DOC_LUA_FILE)
	for node in PreOrderIter(root):
		if not node.docx_src_path == "":
			docx_input = os.path.join(ROOT, OUT_NAME, "assets", node.docx_src_path, node.name + ".docx")
			docx_output = os.path.join(ROOT, node.get_src_path(get_dir = True) + "__doc.md")
			call = "%s -o %s %s" % (call_prefix, docx_output, docx_input)
			if debug:
				print(call)
			else:
				os.system(call)

def printTOC(par, level):
	result = ""
	for pre, _, node in RenderTree(par, style = toc_style, childiter = Document.toc_print_sort, maxlevel = level):
		if node.name != par.name:
			if par.is_root:
				relpath = os.path.relpath(node.get_out_path(), par.get_out_path(True))
			else:
				relpath = os.path.relpath(node.get_out_path(), par.parent.get_out_path(True))
			result += ("%s[%s](." + os.sep + "%s)\n") % (pre, node.get_out_name(), relpath)
	return result

def printMenu(curr_node):
	i = 0
	for pre, fill, node in RenderTree(curr_node, style = menu_style, childiter = Document.menu_print_sort, maxlevel = 2):
		if i == 0:
			print("%s\t-\t%s: %s" % ('dir' if node.dir else "file", i, ".\\"))
		else:
			print("%s\t-\t%s: %s" % ('dir' if node.dir else "file", i, node.name if node.dir else node.src_name))
		i += 1
	
	print("------------------------------------------------------------")
	act = input("Action: ")
	print("------------------------------------------------------------")
	
	return act

def createMainParser():
	parser = argparse.ArgumentParser()
	
	option_group = parser.add_mutually_exclusive_group()
	option_group.add_argument('-eo', '--examine-options', action = 'store_true', help = "examine files metadata and settings")
	option_group.add_argument('-co', '--compile-options', action = 'store_true', help="compile one file or directory")
	option_group.add_argument('-ao', '--add-options', action = 'store_true', help = "add a file or directory to source")
	option_group.add_argument('-ro', '--remove-options', action = 'store_true', help = "remove a file or directory from source")
	option_group.add_argument('-mo', '--modify-options', action = 'store_true', help = "modify file or directory settings")
	
	parser.add_argument('-u', '--update', action = 'store_true', help = "update any documents from assets folder into .md files.")
	parser.add_argument('-d', '--debug', action = 'store_true', help = argparse.SUPPRESS)
	
	return parser

def createCompileSubParser():
	subParser = argparse.ArgumentParser(prog = "", add_help = False, exit_on_error = False)
	group = subParser.add_mutually_exclusive_group(required=True)
	group.add_argument('-o', '--open', nargs = 1, type=pos_int, help = 'open directory')
	group.add_argument('-s', '--select', nargs = 1, type=pos_int, help = 'select directory or file to compile')
	group.add_argument('-b', '--back', action = 'store_true', help = 'go back one directory')
	group.add_argument('-e', '--exit', action = 'store_true', help = "exit from program")
	subParser.add_argument("-a", '--open-after', action = 'store_true', help = "open file after compilation")
	
	return subParser

def createAddSubParser():
	subParser = argparse.ArgumentParser(prog = "", add_help = False, exit_on_error = False)
	group = subParser.add_mutually_exclusive_group(required=True)
	group.add_argument('-o', '--open', nargs = 1, type=pos_int, help = 'open directory')
	group.add_argument('-s', '--select', nargs = 1, type=pos_int, help = 'select directory or file to compile')
	group.add_argument('-b', '--back', action = 'store_true', help = 'go back one directory')
	group.add_argument('-e', '--exit', action = 'store_true', help = "exit from program")
	subParser.add_argument("-a", '--open-after', action = 'store_true', help = "open file after compilation")
	
	return subParser

def createRemoveSubParser():
	subParser = argparse.ArgumentParser(prog = "", add_help = False, exit_on_error = False)
	group = subParser.add_mutually_exclusive_group(required=True)
	group.add_argument('-o', '--open', nargs = 1, type=pos_int, help = 'open directory')
	group.add_argument('-s', '--select', nargs = 1, type=pos_int, help = 'select directory or file to compile')
	group.add_argument('-b', '--back', action = 'store_true', help = 'go back one directory')
	group.add_argument('-e', '--exit', action = 'store_true', help = "exit from program")
	subParser.add_argument('-rd', '--remove-directory', action = 'store_true', default = False, help = 'remove accompanying directory with the file if there exists one')
	
	return subParser

def createModifySubParser():
	subParser = argparse.ArgumentParser(prog = "", add_help = False, exit_on_error = False)
	group = subParser.add_mutually_exclusive_group(required=True)
	group.add_argument('-o', '--open', nargs = 1, type=pos_int, help = 'open directory')
	group.add_argument('-s', '--select', nargs = 1, type=pos_int, help = 'select directory or file to modify settings')
	group.add_argument('-m', '--move', nargs = 1, type=pos_int, help = 'move selected file')
	group.add_argument('-r', '--rename', nargs = 1, type = pos_int, help = 'rename selected file')
	group.add_argument('-b', '--back', action = 'store_true', help = 'go back one directory')
	group.add_argument('-e', '--exit', action = 'store_true', help = "exit from program")
	
	return subParser

def createExamineSubParser():
	subParser = argparse.ArgumentParser(prog = "", add_help = False, exit_on_error = False)
	group = subParser.add_mutually_exclusive_group(required=True)
	group.add_argument('-o', '--open', nargs = 1, type=pos_int, help = 'open directory')
	group.add_argument('-s', '--select', nargs = 1, type=pos_int, help = 'select directory or file to examine')
	group.add_argument('-l', '--launch', nargs = 1, type=pos_int, help = 'launch page')
	group.add_argument('-b', '--back', action = 'store_true', help = 'go back one directory')
	group.add_argument('-e', '--exit', action = 'store_true', help = "exit from program")
	
	return subParser

def main():
	parser = createMainParser()
	res = parser.parse_args()
	# print(res)
	
	''' Creating the tree
	doc_root -> parent
	'''
	if not os.path.isfile(META):
		doc_root = Document.Document(SRC_NAME, dir = True)
		
		if os.path.isdir(os.path.join(ROOT, doc_root.get_src_path(get_dir = True))):
			doc_root = nm.growTree(doc_root)
		else:
			os.mkdir(os.path.join(ROOT, doc_root, get_src_path(get_dir = True)))
		
		nm.genExportTree(doc_root, META)
	else:
		doc_root = nm.importTree(META)

	if res.update:
		compile_docx_src(doc_root)
	
	if res.compile_options:
		subParser = createCompileSubParser()
		select = False
		curr_node = doc_root
		
		subParser.print_help()
		
		print("------------------------------------------------------------")
		
		while not select:
			# print files and directories for selection
			act = printMenu(curr_node)
			
			try:
				subres = subParser.parse_args(act.split(" "))
				#print(subres)
				if not subres.select == None:
					# Action at select
					selection = subres.select[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else: 
						select_node = curr_node
					compile(select_node, res.debug, subres.open_after)
					select = True
				elif not subres.open == None:
					# Action at open
					selection = subres.open[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else: 
						select_node = curr_node
					if select_node.dir:
						curr_node = select_node
					else:
						raise Exception("Please select a directory...")
				elif subres.back == True:
					# Action at back
					if curr_node.parent:
						curr_node = curr_node.parent
					else: 
						raise Exception("No parent to move back to...")
				elif subres.exit == True:
					select = True
			except SystemExit:
				print("Please try again")
			except argparse.ArgumentError as err:
				print(err)
			except Exception as err:
				# print(traceback.format_exc())
				print(err)
	elif res.add_options:
		subParser = createAddSubParser()
		select = False
		curr_node = doc_root
		
		subParser.print_help()
		
		print("------------------------------------------------------------")
		
		while not select:
			# print files and directories for selection
			act = printMenu(curr_node)
			
			try:
				subres = subParser.parse_args(act.split(" "))
				#print(subres)
				if not subres.select == None:
					# Action at select
					selection = subres.select[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else: 
						select_node = curr_node
					
					if select_node.dir:
						node_name = input("name: ")
						invalid_names = [child.name for child in select_node.children]
						invalid_names.append(select_node.root.name)
						while ' ' in node_name or node_name in invalid_names:
							print("Please input valid name (not src or other file names without a space)...")
							node_name = input("name: ")
						
						new_node = Document.Document(node_name, parent = select_node)
						node_dir = input("dir: ")
						while not new_node.change_field('dir', node_dir):
							print("Please input valid dir (true or false)...")
							node_dir = input("dir: ")
						
						node_itoc = input("itoc: ")
						while not new_node.change_field('itoc', node_itoc):
							print("Please input valid itoc (true or false)...")
							node_itoc = input("itoc: ")
						
						node_type = input("type: ")
						new_node.change_field('type', node_type)
						
						with open(os.path.join(ROOT, new_node.get_src_path()), 'x') as f:
							f.write(new_file_contents(new_node.get_out_name()))
						
						try:
							if new_node.dir:
								os.mkdir(os.path.join(ROOT, new_node.get_src_path(get_dir = True)))
						except FileExistsError:
							print("Directory already exists...")
						
						print(new_node.dump_info())
						
						if subres.open_after:
							os.system("start %s" % (os.path.join(ROOT, new_node.get_src_path())))
						
						select = True
					else:
						raise Exception("Please select a directory...")
				elif not subres.open == None:
					# Action at open
					selection = subres.open[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else: 
						select_node = curr_node
					if select_node.dir:
						curr_node = select_node
					else:
						raise Exception("Please select a directory...")
				elif subres.back == True:
					# Action at back
					if curr_node.parent:
						curr_node = curr_node.parent
					else: 
						raise Exception("No parent to move back to...")
				elif subres.exit == True:
					select = True
			except SystemExit:
				print("Please try again")
			except argparse.ArgumentError as err:
				print(err)
			except Exception as err:
				# print(traceback.format_exc())
				print(err)
		
		nm.exportTree(doc_root, META)
		nm.getNavJson()
	elif res.remove_options:
		subParser = createRemoveSubParser()
		select = False
		curr_node = doc_root
		
		subParser.print_help()
		
		print("------------------------------------------------------------")
		
		while not select:
			act = printMenu(curr_node)
			
			try:
				subres = subParser.parse_args(act.split(" "))
				#print(subres)
				if not subres.select == None:
					# Action at select
					selection = subres.select[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else: 
						select_node = curr_node
					
					confirm = input("Are you sure you want to remove %s? (y/n)\n" % (select_node.name))
					
					if confirm.lower() == 'y':
						if subres.remove_directory:
							if select_node.dir:
								shutil.rmtree(os.path.join(ROOT, select_node.get_src_path(get_dir = True)))
						os.remove(os.path.join(ROOT, select_node.get_src_path()))
						select_node.parent = None
						
						select = True
					elif confirm.lower() == 'n':
						select = True
					else:
						raise Exception("We'll take that as a no...")
				elif not subres.open == None:
					# Action at open
					selection = subres.open[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else: 
						select_node = curr_node
					if select_node.dir:
						curr_node = select_node
					else:
						raise Exception("Please select a directory...")
				elif subres.back == True:
					# Action at back
					if curr_node.parent:
						curr_node = curr_node.parent
					else: 
						raise Exception("No parent to move back to...")
				elif subres.exit == True:
					select = True
			except SystemExit:
				print("Please try again")
			except argparse.ArgumentError as err:
				print(err)
			except Exception as err:
				# print(traceback.format_exc())
				print(err)
		
		nm.exportTree(doc_root, META)
		nm.getNavJson()
	elif res.modify_options:
		subParser = createModifySubParser()
		
		exit = False
		curr_node = doc_root
		moving = False
		
		subParser.print_help()
		
		print("------------------------------------------------------------")
		
		while not exit:
			act = printMenu(curr_node)
			
			try:
				subres = subParser.parse_args(act.split(" "))
				#print(subres)
				if not subres.select == None:
					# Action at select
					if moving:
						selection = subres.select[0]
						if selection > 0:
							select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
						else: 
							select_node = curr_node
						
						if select_node.dir:
							curr_path = os.path.join(ROOT, move_node.get_src_path())
							move_node.parent = select_node
							new_path = os.path.join(ROOT, move_node.get_src_path())
							os.rename(curr_path, new_path)
							if move_node.dir:
								os.rename(os.path.splitext(curr_path)[0], os.path.splitext(new_path)[0])
							moving = False
							curr_node = doc_root
						else:
							raise Exception("Please select a directory...")
					else:
						selection = subres.select[0]
						if selection > 0:
							select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
						else: 
							select_node = curr_node
						print(select_node.dump_info())
						valid_field = True
						
						field_act = input("Change Field: ")
						new_val_act = input("To: ")
						
						valid_field = select_node.change_field(field_act, new_val_act)
						
						while not valid_field:
							print("Please select an editable field...")
							print(select_node.dump_info())
							field_act = input("Change Field: ")
							new_val_act = input("To: ")
							
							valid_field = select_node.change_field(field_act, new_val_act)
						
						try:
							if select_node.dir and not os.path.isdir(os.path.join(ROOT, select_node.get_src_path(get_dir = True))):
								os.mkdir(os.path.join(ROOT, select_node.get_src_path(get_dir = True)))
						except FileExistsError:
							print("Directory already exists...")
						
						print(select_node.dump_info())
				elif not subres.open == None:
					# Action at open
					selection = subres.open[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else: 
						select_node = curr_node
					
					if select_node.dir:
						curr_node = select_node
					else:
						raise Exception("Please select a directory")
				elif not subres.move == None and not moving:
					selection = subres.move[0]
					if selection > 0:
						move_node = Document.menu_print_sort(curr_node.children)[selection - 1]
						moving = True
					else: 
						if not curr_node.is_root:
							move_node = curr_node
							curr_node = curr_node.parent
							moving = True
						else:
							raise Exception("Cannot move root...")
					print("Move To...")
				elif not subres.rename == None and not moving:
					selection = subres.rename[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else:
						if not curr_node.is_root:
							select_node = curr_node
						else:
							raise Exception("Cannot rename root...")
					
					new_act = ""
					curr_path = os.path.join(ROOT, select_node.get_src_path())
					new_act = input("Rename to: ")
					invalid_names = [child.name for child in select_node.children]
					invalid_names.append(select_node.root.name)
					while ' ' in node_name or node_name in invalid_names:
						print("Please input valid name (not src or other file names without a space)...")
						new_act = input("Rename to: ")
					select_node.rename(new_act)
					os.rename(curr_path, os.path.join(ROOT, select_node.get_src_path()))
				elif subres.back == True:
					# Action at back
					if curr_node.parent:
						curr_node = curr_node.parent
					else: 
						raise Exception("No parent to move back to...")
				elif subres.exit == True and not moving:
					exit = True
				else:
					print("Please select a valid option...")
			except SystemExit:
				print("Please try again")
			except argparse.ArgumentError as err:
				print(err)
			except Exception as err:
				# print(traceback.format_exc())
				print(err)
		
		nm.exportTree(doc_root, META)
		nm.getNavJson()
	elif res.examine_options:
		subParser = createExamineSubParser()
		
		exit = False
		curr_node = doc_root
		
		subParser.print_help()
		
		print("------------------------------------------------------------")
		
		while not exit:
			act = printMenu(curr_node)
			
			try:
				subres = subParser.parse_args(act.split(" "))
				#print(subres)
				if not subres.select == None:
					# Action at select
					selection = subres.select[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else: 
						select_node = curr_node
					print(select_node.dump_info())
				elif not subres.open == None:
					# Action at open
					selection = subres.open[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else: 
						select_node = curr_node
					if select_node.dir:
						curr_node = select_node
					else:
						raise Exception("Please select a directory...")
				elif not subres.launch == None:
					selection = subres.launch[0]
					if selection > 0:
						select_node = Document.menu_print_sort(curr_node.children)[selection - 1]
					else:
						select_node = cur_node
					os.system("start " + os.path.join(ROOT, select_node.get_out_path()))
					exit = True
				elif subres.back == True:
					# Action at back
					if curr_node.parent:
						curr_node = curr_node.parent
					else: 
						raise Exception("No parent to move back to...")
				elif subres.exit == True:
					exit = True
			except SystemExit:
				print("Please try again")
			except argparse.ArgumentError as err:
				print(err)
			except Exception as err:
				# print(traceback.format_exc())
				print(err)
	
	print("Exiting Tool")
	
if __name__ == '__main__':
	main()