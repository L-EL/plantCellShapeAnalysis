# from http://stackoverflow.com/questions/31735499/calculate-angle-clockwise-between-two-points
from math import acos
from math import atan2
from math import sqrt
from math import pi
import numpy as np

def length(v):
    return sqrt(v[0]**2+v[1]**2+v[2]**2)
def dot_product(v,w):
   return v[0]*w[0]+v[1]*w[1]+v[2]*w[2]
def determinant(v,w,n):
   return v[0]*w[1]*n[2] + w[0]*n[1]*v[2] + n[0]*v[1]*w[2] - v[2]*w[1]*n[0] - w[2]*n[1]*v[0] - n[2]*v[1]*w[0] #v[0]*w[0]-v[1]*w[0]
def inner_angle(v,w):
   cosx=dot_product(v,w)/(length(v)*length(w))
   rad=acos(cosx) # in radians
   return rad*180/pi # returns degrees
def angle_clockwise3D(A,B) :
	n = np.cross(A, B)
	n = [n[0]/length(n), n[1]/length(n), n[2]/length(n)]
	det = determinant(A,B,n)
	print(det)
	a = atan2(det, dot_product(A,B))
	return   a*180/pi
def angle_clockwise(A, B):
    inner=inner_angle(A,B)
    det = determinant(A,B)
    if det<0: #this is a quality of the det. If the det < 0 then B is clockwise of A
        return inner
    else: # if the det > 0 then A is immediately clockwise of B
        return 360-inner
