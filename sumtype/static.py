import re

import sumtype_slots

with open(sumtype_slots.__file__, 'r') as slots:
	src = slots.read()
	start_pat = re.compile('\tclass Class:')
	end_pat   = re.compile('\t# end class')

	start_m = re.search(start_pat, src)
	end_m   = re.search(end_pat,   src)

	start_ix = start_m.span()[0]
	end_ix   = end_m.span()[0]

	print(start_m)
	print(end_m)

	class_src = src[start_ix:end_ix+1]
	class_src2 = '\n'.join(line[1:] for line in class_src.splitlines())
	print(class_src2)