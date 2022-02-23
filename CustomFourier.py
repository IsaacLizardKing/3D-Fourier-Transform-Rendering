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
		self.bounds = ((0, data.shape[0] / 2), (0, data.shape[1] / 2), (0, data.shape[2] / 2))
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
		w = np.sum((self.trans * np.exp(self.u*X[:, None] + self.v*Y[:, None] + self.w*Z[:, None])).real, axis = -1) / self.trans.size
		return np.float64(w)
