import re

def remove_whitespaces(queryParams):
	"""
	* Purpose:
		- function is use to trim the more than one blankspaes
		  in words
		- it will remove left, right and middel blank spaces
		- it will iterate throughout list and stip it.
		
	* Input:
		- queryParams contains list of integers and string values 
	"""
	params_list = []
	for param in queryParams:
		if type(param)==int:
			params_list.append(param)
		else:
			st = param.strip()
			substr = re.sub(r'\s+',' ',st)
			params_list.append(substr)
		
	return params_list
