def openDivTypeFile(filename) :
	f = open(filename,'r')
	data = f.readlines()
	f.close()
	
	name = []
	typeDiv = []
	for line in range(len(data)) :
		if '/' in data[line] :
			name.append(data[line])
			typeDiv.append([])
		else : 
			S = data[line].split('\n')[0].split('\t')
			typeDiv[len(name)-1].append(list(map(int,S)))

	return [name,typeDiv]
