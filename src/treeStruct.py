import numpy as np
from math import sqrt
import glob
import os,sys
import re
import scipy.ndimage
import openDivTypeFile 
from getleaves import *

class Node : 
	def __init__(self,cellLabel):
		self.left = None
		self.right = None
		self.label = cellLabel
		self.divisionInterfaceIndex = None
		self.generation = None
		self.plot = None
		self.color = (np.random.rand(),np.random.rand(),np.random.rand())
		self.interfacesInvolvedIndexes = None
		self.interfacesPoints = np.array([],dtype = float).reshape((0,3))
		self.Triangles = np.array([],dtype = int).reshape((0,3))
		self.Vertices = np.array([],dtype = float).reshape((0,3)) #np.array([]).reshape(0,3)
		self.position = ''
		self.TypeOfDivision = None
		self.distanceToMotherCenter = None
		self.motherCellCenter = None
		self.volume = 0

	def __init__(self,cellLabel,G):
		self.left = None
		self.right = None
		self.label = cellLabel
		self.divisionInterfaceIndex = None
		self.generation = G
		self.plot = None
		self.color = (np.random.rand(),np.random.rand(),np.random.rand())
		self.interfacesInvolvedIndexes = None
		self.interfacesPoints = np.array([],dtype = float).reshape((0,3))
		self.Triangles = np.array([],dtype = int).reshape((0,3))
		self.Vertices = np.array([],dtype = float).reshape((0,3)) #np.array([]).reshape(0,3)
		self.position = ''
		self.TypeOfDivision = None
		self.distanceToMotherCenter = None
		self.motherCellCenter = None
		self.volume = 0

		#self.isLeaf = False
	def setDivision(self, daughter1, daughter2, interface) : 
		self.left = daughter1
		self.right = daughter2
		self.divisionInterface = interface
	def setDaughter(self, daughter1, daughter2) : 
		self.left = daughter1
		self.right = daughter2
	def setInterface(self, interface) : 
		self.divisionInterface = interface


class tree : 
	def __init__(self,treeFile):
		f = open(treeFile, 'r')
		data = f.readlines()
		f.close()
		t = data[0].split('\t')
		if len(t) <= 1 :
				t = data[0].split(' ')
		self.tree=np.array(list(map(int,t[:-1])))
		self.root = None
		self.cellNumber = None
		self.nodes = [None]*len(self.tree)
		self.buildTree()
		self.suspensor = []
		self.visible = []
		self.patchPlot = []
		self.fileName = treeFile
		self.Vertices = []
		self.Interfaces = None
		self.p1 = [0,0,0]
		self.p2 = [None,None,None]
		self.clickCounter = 0
		self.scaleBarObjet = None
		
	def buildTree(self) :
		self.findRoot()
		if self.root != None:
			fillTree(self.tree,self.root, 0)
			self.fillArray(self.root)
		else : 
			print('error : no root')
			
		
	def findRoot(self) : 
		n = 0
		for i in range(len(self.tree)) : 
			if self.tree[i] == 0 and (i+1) in self.tree :
				self.root = Node(i+1,0)
			elif self.tree[i] != 0 and not((i+1) in self.tree) :
				n = n +1
		self.cellNumber = n
				
	def fillMaterial(self, Interfaces) :
		"""remplissage des Triangles pour chaque noeud
		"""
		materialOf(self.root, Interfaces)
		self.suspensorInit(Interfaces) 
		for i in range(len(self.tree)):
			self.nodes[i].interfacesInvolvedIndexes = np.unique(self.nodes[i].interfacesInvolvedIndexes)
			if  self.nodes[i].left != None :
				self.nodes[i].divisionInterfaceIndex = np.unique(self.nodes[i].divisionInterfaceIndex)
			for each in self.nodes[i].interfacesInvolvedIndexes :
				#print(self.nodes[i].Triangles.shape)
				#print(Interfaces[each].Triangles.shape)
				self.nodes[i].Triangles = np.concatenate((self.nodes[i].Triangles , Interfaces[each].Triangles),axis = 0)

	def splitVerticesForCells(self,Interfaces,Vertices,interfaceOnly = False ) : 
		for each in range(len(self.nodes)) :
			if self.nodes[each].interfacesInvolvedIndexes != [] :
				#self.nodes[each].interfacesInvolvedIndexes = np.unique(self.nodes[each].interfacesInvolvedIndexes)
				if  self.nodes[each].left != None :
					for patch in range(len(self.nodes[each].divisionInterfaceIndex)) :
						sortedTriangles = np.unique(np.array(Interfaces[self.nodes[each].divisionInterfaceIndex[patch]].Triangles))
						self.nodes[each].interfacesPoints = np.concatenate((self.nodes[each].interfacesPoints,Vertices[sortedTriangles]),axis = 0)
			if not(interfaceOnly) :
				if len(self.nodes[each].Triangles) != 0 :
					sortedTriangles = np.unique(np.array(self.nodes[each].Triangles))
					print(each)
					self.nodes[each].Vertices = Vertices[sortedTriangles]
					#for indx in range(len(sortedTriangles)):
					self.nodes[each].Triangles = np.digitize(self.nodes[each].Triangles.ravel(),sortedTriangles, right = True).reshape(self.nodes[each].Triangles.shape)
				else : 
					print('warning: cell without surface')
				
	
	def splitVerticesForLeaves(self,Interfaces,Vertices,interfaceOnly = False ) : 
		for each in range(len(self.nodes)) :
			if self.nodes[each].interfacesInvolvedIndexes != [] :
				#self.nodes[each].interfacesInvolvedIndexes = np.unique(self.nodes[each].interfacesInvolvedIndexes)
				if  self.nodes[each].left != None :
					for patch in range(len(self.nodes[each].divisionInterfaceIndex)) :
						sortedTriangles = np.unique(np.array(Interfaces[self.nodes[each].divisionInterfaceIndex[patch]].Triangles))
						self.nodes[each].interfacesPoints = np.concatenate((self.nodes[each].interfacesPoints,Vertices[sortedTriangles]),axis = 0)
			if not(interfaceOnly) :
				if len(self.nodes[each].Triangles) != 0 and self.nodes[each].left == None:
					sortedTriangles = np.unique(np.array(self.nodes[each].Triangles))
					print(each)
					self.nodes[each].Vertices = Vertices[sortedTriangles]
					#for indx in range(len(sortedTriangles)):
					self.nodes[each].Triangles = np.digitize(self.nodes[each].Triangles.ravel(),sortedTriangles, right = True).reshape(self.nodes[each].Triangles.shape)
				else : 
					print('warning: cell without surface')
				

	def fillArray(self, node):
		self.nodes[node.label-1] = node
		if node.left != None :
			self.fillArray(node.left)
			self.fillArray(node.right)
	
	def suspensorInit(self,Interfaces) :
		for i in range(len(self.tree)):
			if self.tree[i] == 0 and not((i+1) in self.tree) :
				self.nodes[i] = Node(i+1,-1)
				self.nodes[i].interfacesInvolvedIndexes = cellMaterial(i+1, Interfaces)
				self.suspensor = self.suspensor +[i+1]

		
	def allInitialize(self,Interfaces,Vertices, interfaceOnly = False) :
		self. Vertices = Vertices
		self.Interfaces = Interfaces
		self.fillMaterial(Interfaces)
		self.splitVerticesForCells(Interfaces,Vertices,interfaceOnly)

	def leavesInitialize(self,Interfaces,Vertices, interfaceOnly = False) :
		self. Vertices = Vertices
		self.Interfaces = Interfaces
		self.fillMaterial(Interfaces)
		self.splitVerticesForLeaves(Interfaces,Vertices,interfaceOnly) 


	
	def addDivType(self, path = ''):
		divTypefile = path + '/divisionType.txt'
		[name, typeDiv] = openDivTypeFile.openDivTypeFile(divTypefile)
		n =  re.findall('/([^/]*)\.treeV',self.fileName)[0]
		flag = 0
		for i in range(len(name)):
			if n in name[i] :
				flag = 1
				break
		print([n, name[i]])
		if flag == 0 :
			print("pas vu")
			return 1
		for nod in range(len(self.nodes)):
			if self.nodes[nod].left != None: 
				for n in range(len(typeDiv[i])):
					#print([typeDiv[i][n][0],typeDiv[i][n][1]])
					#print([self.nodes[nod].left.label,self.nodes[nod].right.label])
					if (typeDiv[i][n][0] == self.nodes[nod].left.label or typeDiv[i][n][0] == self.nodes[nod].right.label) and ( typeDiv[i][n][1] == self.nodes[nod].left.label or typeDiv[i][n][1] == self.nodes[nod].right.label) :
						self.nodes[nod].TypeOfDivision = typeDiv[i][n][2]
		return 0
	
	def addPosition(self,path = '') : 
		allBAEFiles = glob.glob(path + "/*BAE*.txt")
		n =  re.findall('/([^/]*)\.treeV',self.fileName)[0]
		apicale = []
		basale = []
		epiderm = []
		flag = 1
		for iBAE in range(len(allBAEFiles)) :
			if  n in allBAEFiles[iBAE] :
				f = open(allBAEFiles[iBAE], 'r') 
				data = f.readlines()
				f.close()
				flag = 0
				for i in range(len(data)):
					d= data[i][:-1]
					d=d.split('\t')
					#print(d)
					if i == 1:
						apicale= list(map(int,d[:-1]))
					if i ==0 :
						basale= list(map(int,d[:-1]))
					if i ==2 :
						epiderm= list(map(int,d[:-1]))
				break
		if flag == 1:
			print("pas de BAE file")
			return 1
		apicalCells = []
		basalCells = []
		for cell in range(len(self.tree)):
			if apicale[cell] != 0 :
				apicalCells = apicalCells + getleaves(self.tree,cell +1)	
			if basale[cell] != 0 :
				basalCells = basalCells + getleaves(self.tree,cell +1)	
		for cell in apicalCells:
				if epiderm[cell-1] == 1 :
					self.nodes[cell-1].position = 'AE'
				else :
					self.nodes[cell-1].position = 'AI'
		for cell in basalCells:
				if epiderm[cell-1] == 1:
					self.nodes[cell-1].position = 'BE'
				else:
					self.nodes[cell-1].position = 'BI'
		# heritage
		for cell in range(len(self.tree)):
			if self.nodes[cell].position != "" :
				c = self.tree[cell] -1
				while c != -1 :
					self.nodes[c].position = self.nodes[cell].position					
					c = self.tree[c]-1
		return 0


############ outside functions
def cellMaterial(label, Interfaces) :
	out = []
	for i in range(len(Interfaces)) : 
		if Interfaces[i].InnerRegion != 'Exterior'  and int(Interfaces[i].InnerRegion[-3:]) == label:
			out = out+ [i] 
		if  Interfaces[i].OuterRegion != 'Exterior'  and int(Interfaces[i].OuterRegion[-3:]) == label:
			out = out+ [i] 
	return out

def materialOf(node, Interfaces) : 
	"""remplit node.interfacesInvolvedIndexes, node.divisionInterfaceIndex, node.interfacesInvolvedIndexes de chaque noeud
	"""
	if node.left == None : 		
		node.interfacesInvolvedIndexes = cellMaterial(node.label, Interfaces)
	else :
		inter = []
		materialOf(node.left,Interfaces)
		materialOf(node.right,Interfaces)
		leaves1 = getLeaves(node.left)
		leaves2 = getLeaves(node.right)
		
		out = node.left.interfacesInvolvedIndexes + node.right.interfacesInvolvedIndexes
		for i in node.left.interfacesInvolvedIndexes+node.right.interfacesInvolvedIndexes: 
			if (Interfaces[i].InnerRegion != 'Exterior' and Interfaces[i].OuterRegion != 'Exterior')  and (int(Interfaces[i].InnerRegion[-3:]) in leaves1+leaves2) and (int(Interfaces[i].OuterRegion[-3:]) in leaves1+leaves2) :
				inter = inter + [i]
				out.remove(i)
		node.divisionInterfaceIndex = inter
		node.interfacesInvolvedIndexes = out

def fillTree(treeL,mother,G) :	
	daughters = np.where(treeL == mother.label)
	#print(daughters)
	if daughters != np.array([]) :
		G = G +1
		mother.setDaughter(Node(daughters[0][0]+1,G), Node(daughters[0][1]+1,G))
		fillTree(treeL,mother.left,G)
		fillTree(treeL,mother.right,G)

	
def getLeaves(node) :
	if node.left == None : 
		return [node.label]
	else :
		return getLeaves(node.left) + getLeaves(node.right)

	

		
