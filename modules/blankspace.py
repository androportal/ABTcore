import re
def remove_whitespaces(queryParams):
	params_list = []
	print queryParams
	for q in queryParams:
		print q
		a = q.strip()
		s = re.sub(r'\s+',' ',a)
		params_list.append(s)
		
	return params_list
