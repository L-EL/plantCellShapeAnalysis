import numpy as np

def getleaves(tree,father ):

# Determine les feuilles d'une branche de sommet father
#
#Entrees :
#           tree: pointeurs vers les parents
#           p(i) : parent du noeud no i
#           father : no du sommet pere
#
# Sorties :
#           leaves : feuilles

	#e=np.array(father)
	e= [father]
	#print(e)
	leaves=[]
	while e != [] :
		p1=[]
		for i in range(len(e)):
			flag = 0
			for label in range(len(tree)):
				if tree[label] == e[i]:
					p1.append(label +1)
					flag = flag +1
					
			if flag == 0 :
				leaves.append(e[i])
  	  #leaves= leaves+ p1
		#print(p1)
		e=p1


	#leaves=leaves(find(~ismember(leaves,p)));

	return leaves
