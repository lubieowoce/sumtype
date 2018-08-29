import pathlib
import sys
here = pathlib.Path(__file__).resolve()
parent_package_location = here.parents[2]

# allow this module to import the whole package
if __name__ == '__main__':

	print('Adding', str(parent_package_location), 'to sys.path to enable import\n')
	sys.path.append(str(parent_package_location))


def extract_doctest_snippets(lines):
	blocks = []
	in_block = False
	block = None
	for line in lines:
		line = line.lstrip().rstrip('\n')
		# ^ python whitespace is safe,
		# because in the repl indented blocks are prefixed with '...' 
		if not in_block:
			if line.startswith(r'```'):
				# block start
				in_block = True
				block = []
				continue
		else: # in_block
			if line.startswith(r'```'):
				# block end
				blocks.append(block)
				in_block = False
				block = None
				continue
			else:
				# in the middle of a block
				block.append(line)
				continue

	return blocks


with open(str(parent_package_location/'README.md'), 'r') as readme:
	blocks = extract_doctest_snippets(readme.readlines())

# for block in blocks:
# 	print(*block, sep='\n', end='\n----\n\n')


src = '\n'.join(
	block_ for block in blocks for block_ in ('\n'.join(block),)
	if 'pickle.loads' not in block_ # pickle doesn't seem to work when doctest runs a module
)
print(src)

import doctest


doctest.run_docstring_examples(src, name='readme', globs={})

# import os

# # Create a temp file with the code.
# # doctest.run_docstring_examples() works on strings,
# # but the pickle example doesn't seem to work in that case.
# temp_readme_path = str(parent_package_location/'temp_readme_module.py')
# try:
# 	with open(temp_readme_path, 'w') as temp_readme:
# 		temp_readme.write('"""\n')
# 		temp_readme.write(src)
# 		temp_readme.write('\n"""')

# 	import temp_readme_module
# 	doctest.testmod(temp_readme_module)
# finally:
# 	if os.path.exists(temp_readme_path):
# 		os.remove(temp_readme_path)
