import re
import numpy as np
class interface : 
	def __init__(self):
		self.InnerRegion = None
		self.OuterRegion = None
		self.NbTriangles = None
		self.Triangles = []
		self.Vertices = None

def getSurfacesAvizoOld(inputfile) : 

# 
# Lecture d'un fichier .surf
# 
# 

		  
	f = open(inputfile,'r')

	# Entete
	S = f.readline()
	S = f.readline()
	S = f.readline()
	S = f.readline()
	S = f.readline()


	IdExt= f.readline()
	ColorExt = f.readline()


	count2 = 0

	NbRealMaterials = 0
	S =  f.readline()
	Tissue = []
	Id =[]
	Color = []
	Tissue.append(f.readline())
	k = 1
	while (count2 != 1) :
		Color.append(f.readline())
		Id.append(f.readline())

		S = f.readline()
		S3 = f.readline()
		if S3[4] == '}' :
			count2 = 1
		else :
			Tissue.append(S3[:-1])

		NbRealMaterials = NbRealMaterials + 1;


	NbMaterials= int(Tissue[len(Tissue)-1][-4:-2]) 

	for i in range(3) : 
		S = f.readline()
	BeforeVertices = []
	BeforeVertices.append(f.readline())
	gridBox = BeforeVertices[0].split(' ')
	indxGrid = gridBox.index('GridBox')
	VoxelSize =[1,1,1]
	if indxGrid : 
		VoxelSize[0] = float(gridBox[indxGrid+1])*-0.35
		VoxelSize[1] = float(gridBox[indxGrid+3])*-0.35
		VoxelSize[2] = float(gridBox[indxGrid+5])*-0.35
		  

	for i in range(3) : 
		S = f.readline()


	S = f.readline()
	NbVertices = int(S[9:])
	Vertices = np.empty((NbVertices,3))
	for line in range(NbVertices) : 
		S = f.readline()
		ind = S.split()
		Vertices[line][0]= float(ind[0])
		Vertices[line][1]= float(ind[1])
		Vertices[line][2]= float(ind[2])
	#W =  line = list(islice(f, 10))#fscanf(fid,['%f %f %f'],[3,NbVertices]);
	#Vertices=W';


	S = f.readline()
	NBranchingPoints = int(S[16:])
	S = f.readline()
	NVerticesOnCurves = int(S[18:])
	S = f.readline()
	BoundaryCurves = int(S[15:])
	S = f.readline()
	Patches = int(S[8:])

	Interfaces = []
	labmax = 0 
	for p in range(Patches) :
		Interfaces.append(interface())
		S = f.readline()
		S = f.readline()
		if S[12:-1]== 'Exterior' :
			InnerRegion='Exterior';
		else :
			n = re.findall('[\d][\d][\d]',S) #n = re.regexpi(S,'([\d]*)','tokens');

			n = int(n[0])
		  
			if n < 10 :
				C1 = '00' + str(n)
			elif n < 100 :
				C1 = '0' + str(n)
			else :
				C1 = str(n)
			InnerRegion = 'Tissues' + C1

		Interfaces[p].InnerRegion = InnerRegion;
		S = f.readline()
		  

		if S[12:-1] == 'Exterior' :
			OuterRegion = 'Exterior'
		else :
			n = re.findall('([\d][\d][\d])',S)

			n = int(n[0])
			if n<10 :
				C1 = '00' + str(n)
			elif n<100 :
				C1 = '0' + str(n)
			else :
				C1 = str(n)

			OuterRegion = 'Tissues'+C1

		if InnerRegion != 'Exterior' :
			labmax=max(int(InnerRegion[-3:]),labmax)
		if OuterRegion != 'Exterior' :
			labmax=max(int(OuterRegion[-3:]),labmax)

		Interfaces[p].OuterRegion = OuterRegion

		S = f.readline()
		BoundaryID = int(S[11:])
		  
		S = f.readline()
		BranchingPoints = int(S[16:])
		S = f.readline()
		S = f.readline()

		NbTriangles = int(S[10:-1])
		Interfaces[p].NbTriangles = NbTriangles
		Interfaces[p].Triangles = np.empty((NbTriangles,3),dtype = np.int)
		for t in range(NbTriangles):
			l = f.readline()
			ls = l.split()
			Interfaces[p].Triangles[t][0] = int(ls[0])-1 #W=fscanf(fid,['%f %f %f'],[3,NbTriangles]);
			Interfaces[p].Triangles[t][1] = int(ls[1])-1
			Interfaces[p].Triangles[t][2] = int(ls[2])-1
		S = f.readline()

	f.close()
	return [Interfaces, Vertices, NbMaterials, NbRealMaterials, Tissue, IdExt, Id, ColorExt, Color, BeforeVertices, labmax, VoxelSize]
