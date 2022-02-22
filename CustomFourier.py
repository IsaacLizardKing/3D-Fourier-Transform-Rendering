# ~ https://www.gaussianwaves.com/2015/11/interpreting-fft-results-obtaining-magnitude-and-phase-information/
# ~ this site implies you could get coefficients so as to be able to find the normals.  That would be an excelent place for future research

import numpy as np
import time
import cv2
# ~ this is a class to have pre-computed values
def show(img, time = 0):
	cv2.imshow("image", img)
	cv2.waitKey(time)
	if time == 0:
		cv2.destroyAllWindows()


class Fourier:
	def __init__(self, data):
		# ~ TODO maybe test a couple and find the fastest, also see what data can be thrown, if any
		self.bounds = np.int32(data.shape) // 2 + 1
		self.origin = [0, 0, 0]
		self.trans = np.fft.fftn(data)[:data.shape[0] // 2 + 1, :data.shape[1] // 2 + 1, :data.shape[2] // 2 + 1]
		self.u,self.v,self.w = np.mgrid[:self.trans.shape[0], :self.trans.shape[1], :self.trans.shape[2]] * 1j * 2 * np.pi
		self.u /= self.trans.shape[0]
		self.v /= self.trans.shape[1]
		self.w /= self.trans.shape[2]
		self.u = np.reshape(self.u, (self.u.size))
		self.v = np.reshape(self.v, (self.v.size))
		self.w = np.reshape(self.w, (self.w.size))
		self.trans = np.reshape(self.trans, (self.trans.size))

	def eval(self, coords):
		return np.sum(abs(self.trans * np.exp(self.u*coords[0] + self.v*coords[1] + self.w*coords[2]))) / self.trans.size
		# ~ this works only in 3D.
		# ~ coords: coordinates of value you want to find, in the order of numpy's axes.  It should be a 1x3 array
		# ~ returns: w, the value at the coordinates
		# ~ adapted from https://www.originlab.com/doc/Origin-Help/InverseFFT2-Algorithm
	
	def ParallelEval(self, coords):
		X = coords[:, 0]
		Y = coords[:, 1]
		Z = coords[:, 2]
		# ~ start = time.time()
		w = np.sum(abs(self.trans * np.exp(self.u*X[:, None] + self.v*Y[:, None] + self.w*Z[:, None])), axis = -1) / self.trans.size
		# ~ end = time.time()
		# ~ print(end - start)
		return w

	def CheckBounds(self, Vectors, coords, origin, MaxDistance):
		# ~ Vectors is the marching vectors
		# ~ coords is the current progress of the marching vectors
		# ~ origin is the coords of the camera
		# ~ MaxDistance is the maximum render distance
		# ~ returns coords, but all points outside of the box are set to MaxDistance * 1.1 away from the camera
		X = coords[:, 0]
		Y = coords[:, 1]
		Z = coords[:, 2]
		
		dw = X * 0
		
		#PLANES
		A1 = min(self.origin[0], self.bounds[0])
		A2 = min(self.origin[1], self.bounds[1])
		A3 = min(self.origin[2], self.bounds[2])
		B1 = max(self.origin[0], self.bounds[0])
		B2 = max(self.origin[1], self.bounds[1])
		B3 = max(self.origin[2], self.bounds[2])
		
		#GET INTERSECTION RHO
		Ca1 = (A1 - origin[0]) / Vectors[:, 0]
		Ca2 = (A2 - origin[1]) / Vectors[:, 1]
		Ca3 = (A3 - origin[2]) / Vectors[:, 2]
		Cb1 = (B1 - origin[0]) / Vectors[:, 0]
		Cb2 = (B2 - origin[1]) / Vectors[:, 1]
		Cb3 = (B3 - origin[2]) / Vectors[:, 2]
		
		#GET COORDINATES OF INTERSECTIONS
		Ca1x = origin[0] + Vectors[:, 0] * Ca1
		Ca1y = origin[1] + Vectors[:, 1] * Ca1
		Ca1z = origin[2] + Vectors[:, 2] * Ca1
		Ca2x = origin[0] + Vectors[:, 0] * Ca2
		Ca2y = origin[1] + Vectors[:, 1] * Ca2
		Ca2z = origin[2] + Vectors[:, 2] * Ca2
		Ca3x = origin[0] + Vectors[:, 0] * Ca3
		Ca3y = origin[1] + Vectors[:, 1] * Ca3
		Ca3z = origin[2] + Vectors[:, 2] * Ca3
		Cb1x = origin[0] + Vectors[:, 0] * Cb1
		Cb1y = origin[1] + Vectors[:, 1] * Cb1
		Cb1z = origin[2] + Vectors[:, 2] * Cb1
		Cb2x = origin[0] + Vectors[:, 0] * Cb2
		Cb2y = origin[1] + Vectors[:, 1] * Cb2
		Cb2z = origin[2] + Vectors[:, 2] * Cb2
		Cb3x = origin[0] + Vectors[:, 0] * Cb3
		Cb3y = origin[1] + Vectors[:, 1] * Cb3
		Cb3z = origin[2] + Vectors[:, 2] * Cb3
		
		#DETERMINE INTERSECTION VALIDITY
		mask = (X >= A1) * (X <= B2) * (Y >= A2) * (Y <= B2) * (Z >= A3) * (Z <= B3)
		Ca1mask = (Ca1x >= A1) * (Ca1x <= B2) * (Ca1y >= A2) * (Ca1y <= B2) * (Ca1z >= A3) * (Ca1z <= B3) * (Ca1 >= 0)
		Ca2mask = (Ca2x >= A1) * (Ca2x <= B2) * (Ca2y >= A2) * (Ca2y <= B2) * (Ca2z >= A3) * (Ca2z <= B3) * (Ca2 >= 0)
		Ca3mask = (Ca3x >= A1) * (Ca3x <= B2) * (Ca3y >= A2) * (Ca3y <= B2) * (Ca3z >= A3) * (Ca3z <= B3) * (Ca3 >= 0)
		Cb1mask = (Cb1x >= A1) * (Cb1x <= B2) * (Cb1y >= A2) * (Cb1y <= B2) * (Cb1z >= A3) * (Cb1z <= B3) * (Cb1 >= 0)
		Cb2mask = (Cb2x >= A1) * (Cb2x <= B2) * (Cb2y >= A2) * (Cb2y <= B2) * (Cb2z >= A3) * (Cb2z <= B3) * (Cb2 >= 0)
		Cb3mask = (Cb3x >= A1) * (Cb3x <= B2) * (Cb3y >= A2) * (Cb3y <= B2) * (Cb3z >= A3) * (Cb3z <= B3) * (Cb3 >= 0)
		Valid = np.logical_or(np.logical_or(np.logical_or(Ca2mask, Ca3mask), Ca1mask), np.logical_or(np.logical_or(Cb2mask, Cb3mask), Cb1mask))
		show(Valid * 255, 1)
		Ca1[Valid == 0] = MaxDistance * 1.1
		Ca2[Valid == 0] = MaxDistance * 1.1
		Ca3[Valid == 0] = MaxDistance * 1.1
		Cb1[Valid == 0] = MaxDistance * 1.1
		Cb2[Valid == 0] = MaxDistance * 1.1
		Cb3[Valid == 0] = MaxDistance * 1.1
		
		dw = np.minimum(np.minimum(np.minimum(Ca1, Ca2), Ca3), np.minimum(np.minimum(Cb1, Cb2), Cb3))
		dw[mask] = (X[mask] - origin[0]) / Vectors[mask, 0]
		coords[mask, 0] = origin[0] + (dw[mask] * Vectors[mask, 0])
		coords[mask, 1] = origin[1] + (dw[mask] * Vectors[mask, 1])
		coords[mask, 2] = origin[2] + (dw[mask] * Vectors[mask, 2])
		return coords
