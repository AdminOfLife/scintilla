# LexGen.py - implemented 2002 by Neil Hodgson neilh@scintilla.org
# Released to the public domain.

# Regenerate the Scintilla and SciTE source files that list 
# all the lexers. Should be run whenever a new lexer is added or removed.
# Requires Python 2.1 or later
# The files are copied to a temporary file apart from sections between 
# a ++Autogenerated comment and a --Autogenerated comment which is 
# generated by the CopyWithInsertion function. After the temporary 
# file is created, it is copied back to the original file name.
# Does not regenerate the Visual C++ project files.

import string
import sys
import os
import glob

# Automatically generated sections contain start and end comments, 
# a definition line and the results.
# The results are replaced by regenerating based on the definition line.
# The definition line is a comment prefix followed by "**".
# Backslash is used as an escape within the definition line.
# The part between \( and \) is repeated for each item in the list.
# \* is replaced by each list item. \t, and \n are tab and newline.
def CopyWithInsertion(input, output, commentPrefix, list):
	copying = 1
	for line in input.readlines():
		if copying:
			output.write(line)
		if line.startswith(commentPrefix + "++Autogenerated"):
			copying = 0
			definition = ""
		elif not copying and line.startswith(commentPrefix + "**"):
			output.write(line)
			definition = line[len(commentPrefix + "**"):-1]
			# Hide double slashes as a control character
			definition = definition.replace("\\\\", "\001")
			# Do some normal C style transforms
			definition = definition.replace("\\n", "\n")
			definition = definition.replace("\\t", "\t")
			# Get the doubled backslashes back as single backslashes
			definition = definition.replace("\001", "\\")
			startRepeat = definition.find("\\(")
			endRepeat = definition.find("\\)")
			intro = definition[:startRepeat]
			if intro.endswith("\n"):
				pos = 0
			else:
				pos = len(intro)
			output.write(intro)
			middle = definition[startRepeat+2:endRepeat]
			for i in list:
				item = middle.replace("\\*", i)
				if pos and (pos + len(item) >= 80):
					output.write("\\\n")
					pos = 0
				output.write(item)
				pos += len(item)
				if item.endswith("\n"):
					pos = 0
			outro = definition[endRepeat+2:]
			output.write(outro)
			output.write("\n")
		elif line.startswith(commentPrefix + "--Autogenerated"):
			copying = 1
			output.write(line)

def Regenerate(filename, commentPrefix, list, outmode="wt"):
	try:
		infile = open(filename, "rt")
	except IOError:
		print "Can not open", filename
		return
	tempname = filename + ".tmp"
	out = open(tempname, outmode)
	CopyWithInsertion(infile, out, commentPrefix, list)
	out.close()
	infile.close()
	os.unlink(filename)
	os.rename(tempname, filename)

def FindModules(lexFile):
	modules = []
	f = open(lexFile)
	for l in f.readlines():
		if l.startswith("LexerModule"):
			l = l.replace("(", " ")
			modules.append(l.split()[1])
	return modules
root="../../"
lexFilePaths = glob.glob(root + "scintilla/src/Lex*.cxx")
lexFiles = [os.path.basename(f)[:-4] for f in lexFilePaths]
print lexFiles
lexerModules = []
for lexFile in lexFilePaths:
	lexerModules.extend(FindModules(lexFile))
print lexerModules
Regenerate(root + "scintilla/src/KeyWords.cxx", "//", lexerModules)
Regenerate(root + "scintilla/win32/makefile", "#", lexFiles)
Regenerate(root + "scintilla/win32/scintilla.mak", "#", lexFiles)
Regenerate(root + "scintilla/win32/scintilla_vc6.mak", "#", lexFiles)
Regenerate(root + "scintilla/gtk/makefile", "#", lexFiles, "wb")
Regenerate(root + "scintilla/gtk/scintilla.mak", "#", lexFiles)
Regenerate(root + "scite/win32/makefile", "#", lexFiles)
Regenerate(root + "scite/win32/scite.mak", "#", lexFiles)
