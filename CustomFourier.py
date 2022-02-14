# ~ https://www.gaussianwaves.com/2015/11/interpreting-fft-results-obtaining-magnitude-and-phase-information/
# ~ this site implies you could get coefficients so as to be able to find the normals.  That would be an excelent place for future research

import numpy as np
import time
# ~ this is a class to have pre-computed values
class Fourier:
	def __init__(self, data):
		# ~ TODO maybe test a couple and find the fastest
		self.trans = np.fft.fftn(data) 
		self.u,self.v,self.w = np.mgrid[:self.trans.shape[0], :self.trans.shape[1], :self.trans.shape[2]] * 1j * 2 * np.pi
		self.u /= self.trans.shape[0]
		self.v /= self.trans.shape[1]
		self.w /= self.trans.shape[2]
		self.u = np.reshape(self.u, (self.u.size))
		self.v = np.reshape(self.v, (self.v.size))
		self.w = np.reshape(self.w, (self.w.size))
		self.trans = np.reshape(self.trans, (self.trans.size))



	def eval(self, coords):
		return np.sum((self.trans * np.exp(self.u*coords[0] + self.v*coords[1] + self.w*coords[2])).real) / self.trans.size
		# ~ this works only in 3D.
		# ~ coords: coordinates of value you want to find, in the order of numpy's axes.  It should be a 1x3 array
		# ~ returns: w, the value at the coordinates
		# ~ adapted from https://www.originlab.com/doc/Origin-Help/InverseFFT2-Algorithm
		# ~ TODO possibly this should be made to take a 1D array of points (which would make it a 2D array), but that might take up too much memory.  Currently to do multiple points, just call this function in a loop
	
	def ParallelEval(self, coords):
		X = coords[:, 0]
		Y = coords[:, 1]
		Z = coords[:, 2]
		# ~ start = time.time()
		w = np.sum((self.trans * np.exp(self.u*X[:, None] + self.v*Y[:, None] + self.w*Z[:, None])).real, axis = -1) / self.trans.size
		# ~ end = time.time()
		# ~ print(end - start)
		return w
		
