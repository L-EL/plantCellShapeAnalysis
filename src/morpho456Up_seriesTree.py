# calculate h, r1,r2 of tetrahedron at G4
# made by Elise Laruelle (Dec 2016)
import math
import numpy as np
import scipy.spatial 
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize
import os,sys,glob,re

from angles import *
import getSurfacesAvizo9np
import getSurfacesAvizoOld
import treeStruct



allTreeFiles = glob.glob("./data/*.treeV")
allSurfFiles = glob.glob("./data/*.surf")

name = []
embryo = []
for ftree in allTreeFiles:
	name.append(re.findall('/([^/]*)\.treeV', ftree)[0])
	for fSurf in allSurfFiles:
		if re.findall('/([^/]*)\.surf', fSurf)[0] == name[len(name)-1]:
			embryo.append([ftree, fSurf])

t = []
ratioAsym = {}
ratioleft = {}
ratioright ={}
ratiohrmax={}
idCell = {}

for eachE in range(len(embryo)) :
	print(embryo[eachE][1])

	# open surf file of the embryo
	[Interfaces, Vertices, NbMaterials, NbRealMaterials, Tissue, IdExt, Id, ColorExt, Color, BeforeVertices, labmax, VoxelSize] = getSurfacesAvizo9np.getSurfacesAvizo9np(embryo[eachE][1])

	# build tree Object where it's assign each interface of the surf file to a cell 
	t.append(treeStruct.tree(embryo[eachE][0]))
	t[eachE].leavesInitialize(Interfaces,Vertices) 
	t[eachE].addDivType('data')
	t[eachE].addPosition('data')

	print(embryo[eachE])

	# looking for cells in AI at G4 
	cAI = []
	for n in range(len(t[eachE].nodes)) :
		if t[eachE].nodes[n] != None and (t[eachE].nodes[n].generation == 4 and t[eachE].nodes[n].position == "AI" ):
				cAI.append(n)


	# looking for the daughters of cAI that have just divide, classif AI vs AE
	typeDivivionAI = []
	typeDivivionAE = []
	for ic in range(len(cAI)):
		if t[eachE].nodes[cAI[ic]].left != None and (t[eachE].nodes[cAI[ic]].left.left != None or t[eachE].nodes[cAI[ic]].right.left != None):
			typeDivivionAI.append(None)
		else :
			typeDivivionAI.append(t[eachE].nodes[cAI[ic]].TypeOfDivision)
		if (t[eachE].nodes[t[eachE].tree[cAI[ic]]-1].left.position == "AE" and t[eachE].nodes[t[eachE].tree[cAI[ic]]-1].left.left != None and t[eachE].nodes[t[eachE].tree[cAI[ic]]-1].left.left.left != None) or (t[eachE].nodes[t[eachE].tree[cAI[ic]]-1].right.position == "AE" and t[eachE].nodes[t[eachE].tree[cAI[ic]]-1].right.left != None and t[eachE].nodes[t[eachE].tree[cAI[ic]]-1].right.left.left != None):
			typeDivivionAE.append(None)
		else :
			if t[eachE].nodes[t[eachE].tree[cAI[ic]]-1].left.label == cAI[ic]+1 :
				typeDivivionAE.append(t[eachE].nodes[t[eachE].tree[cAI[ic]]-1].right.TypeOfDivision)
			else :
				typeDivivionAE.append(t[eachE].nodes[t[eachE].tree[cAI[ic]]-1].left.TypeOfDivision)
	print("typeDivivionAI = ")
	print(typeDivivionAI)
	print(" typeDivivionAE = ")
	print(typeDivivionAE)
	# identify AE interfaces :
	hs = []
	lLefts = []
	lrights = []
	angles = []
	for ic in range(len(cAI)):
		if typeDivivionAE[ic]==None and typeDivivionAE[ic]==None :
			hs.append(np.nan)
			lrights.append(np.nan)
			lLefts.append(np.nan)
			angles.append(np.nan)
			continue
		n= cAI[ic]
		interfaceEI = []
		interfaceAB = []
		interfaceCote1 = [] 
		interfaceCote2 = [] 
		for interface in t[eachE].nodes[n].interfacesInvolvedIndexes:
			if interface in t[eachE].nodes[t[eachE].tree[n]-1].divisionInterfaceIndex :
				interfaceEI.append(interface)
			elif  interface in t[eachE].nodes[t[eachE].tree[t[eachE].tree[n]-1]-1].divisionInterfaceIndex :
				interfaceAB.append(interface)
			elif interface in t[eachE].nodes[t[eachE].tree[t[eachE].tree[t[eachE].tree[n]-1]-1]-1].divisionInterfaceIndex :
				interfaceCote1.append(interface)
			else :
				interfaceCote2.append(interface)

		#identify the points of the edges
		pointsCote1 =  np.array([],dtype = float).reshape((0,3)) #
		for interface in interfaceCote1 : 
			trianglePointIndex = np.unique(np.ndarray.flatten( t[eachE].Interfaces[interface].Triangles))

			pointsCote1 = np.concatenate((pointsCote1 , t[eachE].Vertices[trianglePointIndex]),axis = 0) 

		pointsCote2  = np.array([],dtype = float).reshape((0,3)) #
		for interface in interfaceCote2 : 
			trianglePointIndex = np.unique(np.ndarray.flatten( t[eachE].Interfaces[interface].Triangles))
			pointsCote2 = np.concatenate((pointsCote2 , t[eachE].Vertices[trianglePointIndex]),axis = 0) 

		pointsEI =  np.array([],dtype = float).reshape((0,3)) #
		for interface in interfaceEI : 
			trianglePointIndex = np.unique(np.ndarray.flatten( t[eachE].Interfaces[interface].Triangles))

			pointsEI = np.concatenate((pointsEI , t[eachE].Vertices[trianglePointIndex]),axis = 0) 

		pointsAB = np.array([],dtype = float).reshape((0,3)) #
		for interface in interfaceAB : 
			trianglePointIndex = np.unique(np.ndarray.flatten( t[eachE].Interfaces[interface].Triangles))
			pointsAB = np.concatenate((pointsAB , t[eachE].Vertices[trianglePointIndex]),axis = 0) 

		# identify common points of the interfaces
		points2EI = []
		points2AB = []
		for point in range(len(pointsCote2)):
			for point1 in range(len(pointsEI)):
				if pointsCote2[point][0]== pointsEI[point1][0] and pointsCote2[point][1]== pointsEI[point1][1] and pointsCote2[point][2]  == pointsEI[point1][2] :
					points2EI.append(pointsCote2[point])
			for point1 in range(len(pointsAB)):
				if pointsCote2[point][0]== pointsAB[point1][0] and pointsCote2[point][1]== pointsAB[point1][1] and pointsCote2[point][2]  == pointsAB[point1][2] :
					  points2AB.append(pointsCote2[point])


		points1AB = []
		points12 = []
		points1EI = []
		for point in range(len(pointsCote1)):
			for point1 in range(len(pointsCote2)):
				if pointsCote1[point][0]== pointsCote2[point1][0] and pointsCote1[point][1]== pointsCote2[point1][1] and pointsCote1[point][2]  == pointsCote2[point1][2] :
					  points12.append(pointsCote1[point])
			for point1 in range(len(pointsEI)):
					if pointsCote1[point][0]== pointsEI[point1][0] and pointsCote1[point][1]== pointsEI[point1][1] and pointsCote1[point][2]  == pointsEI[point1][2] :
						points1EI.append(pointsCote1[point])
			for point1 in range(len(pointsAB)):
				if pointsCote1[point][0]== pointsAB[point1][0] and pointsCote1[point][1]== pointsAB[point1][1] and pointsCote1[point][2]  == pointsAB[point1][2] :
					  points1AB.append(pointsCote1[point])
		


		pointsEIAB = []
		for point in range(len(pointsEI)):
			indexs1 = np.argwhere(pointsEI[point][0] == pointsAB[:,0]).flatten()
			if len(indexs1 !=0) :
				indexs2 = np.argwhere(pointsEI[point][1] == pointsAB[indexs1,1].flatten()).flatten()
				if len(indexs2 )!=0 :
					indexs3 = np.argwhere(pointsEI[point][2] == pointsAB[indexs1[indexs2],2])
					if len(indexs3 )!=0 :
						pointsEIAB.append(pointsAB[indexs1[indexs2[indexs3]]][0][0])

		# mesure distances inside each interface side for having the extreme points
		Y = scipy.spatial.distance.pdist(points12)
		D =scipy.spatial.distance.squareform(Y)
		h = D.max()
		indexes = np.where(D==h)
		indexesAB1 = np.where(D== h)[0][0]
		indexesAB2 = np.where(D== h)[1][0]
		if indexesAB1 == indexesAB2:
			print("error sames indexes AB2 and AB1")

		Y = scipy.spatial.distance.pdist(points1AB)
		D =scipy.spatial.distance.squareform(Y) 
		r1 = D.max()
		indexes11 = np.where(D== r1)[0][0]
		indexes12 = np.where(D== r1)[1][0]
		if indexes11 == indexes12:
			print("error sames indexes 12 and 11")

		Y = scipy.spatial.distance.pdist(points2AB)
		D =scipy.spatial.distance.squareform(Y) 
		r2 = D.max()
		indexes21 = np.where(D== r2)[0][0]
		indexes22 = np.where(D== r2)[1][0]
		if indexes21 == indexes22:
			print("error sames indexes 22 and 21")

		# found vertex of the interface
		p1AB = [points1AB[indexes11],points1AB[indexes12]]
		p2AB = [points2AB[indexes21],points2AB[indexes22]]
		Y = scipy.spatial.distance.cdist(p1AB,p2AB)
		mm = Y.min()
		if mm !=0 :
			print("warning distance more than zero : "+ str(mm))
		i1 = np.squeeze(np.where(Y == mm)[0])
		i2 = np.squeeze(np.where(Y == mm)[1])
		
		p2 = p1AB[i1]
		if  i1 == 0 :
			p3 = p1AB[1]
		else : 
				p3 = p1AB[0]
		if  i2 == 0 :
			p4 = p2AB[1]
		else : 
			p4 = p2AB[0]
		pAB = [points12[indexesAB1],points12[indexesAB2]]
		if math.sqrt(math.pow(p2[0]-points12[indexesAB1][0],2)+math.pow(p2[1]-points12[indexesAB1][1],2)+math.pow(p2[2]-points12[indexesAB1][2],2)) == 0 :
			p1 = points12[indexesAB2]
		else :
			p1 = points12[indexesAB1]

		# orient sides
		vector23 = [p3[0]-p2[0],p3[1]-p2[1],p3[2]-p2[2]]
		vector24 = [p4[0]-p2[0],p4[1]-p2[1],p4[2]-p2[2]]
		vector21 = [p1[0]-p2[0],p1[1]-p2[1],p1[2]-p2[2]]
		n = np.cross(vector23, vector24)
		if dot_product(vector21,n)<0:
			tmp = p3
			p3 = p4
			p4 = tmp
			vector23 = [p3[0]-p2[0],p3[1]-p2[1],p3[2]-p2[2]]
			vector24 = [p4[0]-p2[0],p4[1]-p2[1],p4[2]-p2[2]]
			
		#order points : P3 and P4
		lLeft = length(vector23)
		lright = length(vector24)
		angle =inner_angle(vector23, vector24)

		hs.append(h)
		lrights.append(lright)
		lLefts.append(lLeft)
		angles.append(angle)

	##ratio values
	for ic in range(len(cAI)):
		ratioAsym[typeDivivionAE[ic]] = ratioAsym.get(typeDivivionAE[ic],[]) + [lLefts[ic]/lrights[ic]]
		ratioleft[typeDivivionAE[ic]] = ratioleft.get(typeDivivionAE[ic],[]) + [hs[ic]/lrights[ic]]
		ratioright[typeDivivionAE[ic]] = ratioright.get(typeDivivionAE[ic],[]) + [hs[ic]/lLefts[ic]]
		ratiohrmax[typeDivivionAE[ic]] = ratiohrmax.get(typeDivivionAE[ic],[]) + [hs[ic]/max(lLefts[ic],lrights[ic])]

		ratioAsym[typeDivivionAI[ic]] = ratioAsym.get(typeDivivionAI[ic],[]) + [lLefts[ic]/lrights[ic]]
		ratioleft[typeDivivionAI[ic]] = ratioleft.get(typeDivivionAI[ic],[]) + [hs[ic]/lrights[ic]]
		ratioright[typeDivivionAI[ic]] = ratioright.get(typeDivivionAI[ic],[]) + [hs[ic]/lLefts[ic]]
		ratiohrmax[typeDivivionAI[ic]] = ratiohrmax.get(typeDivivionAI[ic],[]) + [hs[ic]/max(lLefts[ic],lrights[ic])]
		idCell[typeDivivionAI[ic]] = idCell.get(typeDivivionAI[ic],[]) + [str(embryo[eachE])]
		idCell[typeDivivionAE[ic]] = idCell.get(typeDivivionAE[ic],[]) + [str(embryo[eachE])]

# Save
np.save('ratioAsymA_last.npy', ratioAsym) 
np.save('ratioleftA_last.npy', ratioleft) 
np.save('ratiorightA_last.npy', ratioright) 
np.save('ratiohrmaxA_last.npy', ratiohrmax) 
np.save('idCellA_last.npy', idCell)

