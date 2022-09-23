#extract side number with the tree
# made by Elise Laruelle (Juin 2019)
import re,os,glob
import numpy as np
import getSurfacesAvizo9np
import getSurfacesAvizoOld
import treeStruct
import getleaves


allTreeFiles = glob.glob('./data/*.treeV')
allSurfFiles = glob.glob('./data/*.surf')


name = []
embryo = []
for ftree in allTreeFiles:
	name.append(re.findall('/([^/]*)\.treeV', ftree)[0])
	for fSurf in allSurfFiles:
		if re.findall('/([^/]*)\.surf', fSurf)[0] == name[len(name)-1]:
			embryo.append([ftree, fSurf])

t = []
outputFile = 'sideNumber'
if  not(os.path.exists(outputFile)): 
	os.makedirs(outputFile)
			
for eachE in range(len(embryo)) :

	f = open(outputFile+embryo[eachE][1][embryo[eachE][1].rfind('/'):embryo[eachE][1].rfind('.')]+'.txt','w')
	print(embryo[eachE][1])

	# open surf file of the embryo
	try :
		[Interfaces, Vertices, NbMaterials, NbRealMaterials, Tissue, IdExt, Id, ColorExt, Color, BeforeVertices, labmax, VoxelSize] = getSurfacesAvizo9np.getSurfacesAvizo9np(embryo[eachE][1])
	except : 
		[Interfaces, Vertices, NbMaterials, NbRealMaterials, Tissue, IdExt, Id, ColorExt, Color, BeforeVertices, labmax, VoxelSize] = getSurfacesAvizoOld.getSurfacesAvizoOld(embryo[eachE][1])

	# load in my embryo interface where it's assign each interface of the surf file to a cell 
	t.append(treeStruct.tree(embryo[eachE][0]))
	t[-1].allInitialize(Interfaces,Vertices)
	t[-1].addPosition('data')

	# look at each cell present in the embryo
	for n in range(len(t[-1].nodes)) :
		if t[-1].nodes[n] != None and t[-1].nodes[n].position != "" :
			fromWitchOldInterfaceOfEmbryo = []
			fromWitchOldInterfaceOutside = []

			# look at each interface that compose the cell 
			for interface in t[-1].nodes[n].interfacesInvolvedIndexes:	

				# search for the first appearance of the interface when rewind 
				parent = t[-1].tree[n]-1 # parent label
				while parent != -1:
					if not(interface in t[-1].nodes[parent].interfacesInvolvedIndexes) :
						fromWitchOldInterfaceOfEmbryo.append(parent)
						break
					else :
						parent = t[-1].tree[parent]-1
				print(parent)
			

				
				if parent==-1 :# if not found : means interface present since the beginning

					# is an outside surface (labeled as 0)
					if t[-1].Interfaces[interface].InnerRegion[-3:]=='ior' or t[-1].Interfaces[interface].OuterRegion[-3:]=='ior' :
						fromWitchOldInterfaceOutside.append(0)
					else : # or a surface with the suspensor : take the other cell label
						childs = np.array(getleaves.getleaves(t[-1].tree, n+1))
						if int(t[-1].Interfaces[interface].InnerRegion[-3:]) in childs:
							fromWitchOldInterfaceOutside.append(int(t[-1].Interfaces[interface].OuterRegion[-3:])-1)
						elif int(t[-1].Interfaces[interface].OuterRegion[-3:]) in childs: 
							fromWitchOldInterfaceOutside.append(int(t[-1].Interfaces[interface].InnerRegion[-3:])-1)

			
			cellNotInEmbryo = np.unique(fromWitchOldInterfaceOutside)==0 # surface contacting the exterior
			nbOutside = (cellNotInEmbryo).sum() + ((np.unique(fromWitchOldInterfaceOutside)!=0).sum()>=1) # = number of surfaces contacting the exterior + (1 if there are surfaces contacting cells of the suspensor)

			nbFace = len(np.unique(fromWitchOldInterfaceOfEmbryo)	) + nbOutside # = number of founding sister cells + number of surfaces in contact with the ouside of the embryo
			if nbFace ==1 :
				print("error : with with only one face (a sphere !)")
			f.write(str(n)+'\t'+str(nbFace)+'\n')
		else:
			f.write(str(n)+'\t'+'NA'+'\n')
	f.close()
	

				
				





