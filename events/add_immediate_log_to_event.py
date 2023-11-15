import os
import re

def is_match(regex, text):
	compiled = re.compile(regex)
	return compiled.search(text) is not None

def main():
	dir = os.listdir(os.getcwd())
	for filename in dir:
		if not os.path.isdir(filename) and filename != "add_immediate_log_to_event.py":
			replaced = ""
			lines = []
			with open(filename, 'r+', encoding='utf-8') as f:
				lines = f.read().splitlines()
				
				start = 1
				counter = 0
				i = 0
				for l in lines:
					if "{" not in l and "}" not in l:
						i = i + 1
						continue
					counter = counter + l.count("{")
					counter = counter - l.count("}")
					
					if counter == 0 and start == 0:
						pos = l.rfind("}")
						lines[i] = l[:pos] + "immediate = { log = \"Event: [ROOT.GetName] [GetDateString] " + f"file:{filename} line:{i}\"" + " }}" + l[pos + 1:]
					elif start == 1:
						start = 0
					
					i = i + 1
			with open(filename, "w", encoding='utf-8') as f:
				for l in lines:
					f.write("%s\n" % l)
		else:
			print("Encountered self, skipping.")

if __name__ == "__main__":
	main()