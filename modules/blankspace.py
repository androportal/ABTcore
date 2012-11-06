import re
def remove_whitespaces(queryParams):
	params_list = []
	print queryParams
	for param in queryParams:
		if type(param)==int:
			params_list.append(param)
		else:
			st = param.strip()
			substr = re.sub(r'\s+',' ',st)
			params_list.append(substr)
		
	return params_list
