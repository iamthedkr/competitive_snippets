import os

AVAILABLE_PROPERTIES = ["title", "doc", "defines", "include"] # '//@' will be ignorer
SNIPPETS_ROOT = "snippets"

def getSnippetsFiles():
	"""
		Return all the snippet files as a list of 
		{
			'filepath': <path to file>,
			'name': <name of the snippet>,
			'dirpath': <path to the directory containing the file>,
		}
	"""
	files = []
	for (dirpath, dirnames, filenames) in os.walk(SNIPPETS_ROOT):
		newDir = "/".join([SNIPPETS_ROOT]+dirpath.split("/")[1:])
		os.makedirs(newDir, exist_ok=True)

		for fName in filenames:
			if os.path.splitext(fName)[1] == '.cpp':
				fileInfos = {
					'filepath': os.path.join(dirpath, fName),
					'name': os.path.splitext(fName)[0],
					'dirpath': os.path.join(*(dirpath.split(os.path.sep)[1:])),
					'category': list(dirpath.split(os.path.sep)[1:])
				}
				files.append(fileInfos)
	return files

def insertInTemplate(templatePath, blocks):
	with open(templatePath, "r") as f:
		template = "".join(f.readlines())
		for name, content in blocks.items():
			seq = "{{{" + name + "}}}"
			template = template.replace(seq, content)
		return template

def removeFileComment(fileLines):
	return [l for l in fileLines if l[:1] != "@" and l[:3] != "/*@"]

def getIncludedSnippet(snippetName):
	"""
		Return the code of a given snippet.
		The name must be in a format like : algo/maths/math_numeric , without the ".cpp" extension.
	"""
	return readSnippet(os.path.join(SNIPPETS_ROOT, snippetName + ".cpp"))["code"]

def readSnippet(fileInfos):
	properties = {
		prop : [] for prop in AVAILABLE_PROPERTIES
	}

	with open(fileInfos['filepath'], "r") as snippet:
		lines = [l.rstrip() for l in snippet.readlines()]
		metaLines = [l[3:].strip() for l in lines if l[:3] == "//@"]
		cppLines = [l for l in lines if l[:3] != "//@"]

		metaLines = [l for l in metaLines if l]
		metaProps = [l.split()[0].strip() for l in metaLines]
		metaDatas = [
			(prop, val[len(prop):].strip()) for prop, val in zip(metaProps, metaLines)
		]

		for (prop, val) in metaDatas:
			if not prop in properties:
				raise Exception("Unknown property: {}".format(prop))
			properties[prop].append(val)

		includedLines = []
		for included in properties["include"]:
			includedLines += getIncludedSnippet(included)
	
		return {
			'name': fileInfos["name"],
			'properties': properties,
			'code': cppLines,
			'dirpath': fileInfos["dirpath"],
			'category': fileInfos["category"],
		}

def getAllSnippets():
	return [readSnippet(fileInfos) for fileInfos in getSnippetsFiles()]