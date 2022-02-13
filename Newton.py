import math
import numpy as np
import time
def PartialDerivatives(T, c):
	DT = T * 0
	for a in range(0, c.shape[0]):
		X, Y, Z = FourierSeries(T, c)
		DT[:,0] += c[a, 0, 0] * c[a, 0, 1] * np.cos(c[a, 0, 1] * T[:,0] + c[a, 0, 2]) * Y * Z
		DT[:,1] += X * c[a, 1, 0] * c[a, 1, 1] * np.cos(c[a, 1, 1] * T[:,1] + c[a, 1, 2]) * Z
		DT[:,2] += X * Y * c[a, 2, 0] * c[a, 2, 1] * np.cos(c[a, 2, 1] * T[:,2] + c[a, 2, 2])
	return DT

def FourierSeries(T, c):
	X = T[:,0] * 0
	Y = T[:,0] * 0
	Z = T[:,0] * 0
	N = c.shape[0]
	for a in range(0, c.shape[0]):
		X += c[a, 0, 0] * np.sin(c[a, 0, 1] * T[:,0] + c[a, 0, 2])
		Y += c[a, 1, 0] * np.sin(c[a, 1, 1] * T[:,1] + c[a, 1, 2])
		Z += c[a, 2, 0] * np.sin(c[a, 2, 1] * T[:,2] + c[a, 2, 2])
	return X, Y, Z
	
def ClassicalNewton(Vectors, T, origin, c = np.float32([[[1, 1, 0], [1, 1, 0], [1, 1, 0]]]), iterations = 5, thresh = 0):
	N = c.shape[0]
	while iterations > 0:
		X, Y, Z = FourierSeries(T, c)
		w = (X * Y * Z) / N - thresh
		m = np.sum(PartialDerivatives(T, c), axis = -1) / N
		cond1 = np.absolute(w / m) >= 1
		asymptotics = m[cond1] * 1
		m[cond1] = (asymptotics / np.absolute(asymptotics)) * np.power(math.e, np.absolute(asymptotics))
		T[:,0] -= (w / m) * Vectors[:,0]
		T[:,1] -= (w / m) * Vectors[:,1]
		T[:,2] -= (w / m) * Vectors[:,2]
		iterations -= 1
	return T, PartialDerivatives(T, c)

def ModifiedNewton(Vectors, T, origin, c = np.float32([[[1, 1, 0], [1, 1, 0], [1, 1, 0]]]), iterations = 500, thresh = 0, MaxDistance = -1):
	MaxStep = math.pi / 16
	MinStep = MaxStep / 8
	N = c.shape[0]
	X, Y, Z = FourierSeries(T, c)
	w = (X * Y * Z) / N - thresh
	OriginalSigns = np.absolute(w) / w
	
	while iterations > 0:
		X, Y, Z = FourierSeries(T, c)
		w = (X * Y * Z) / N - thresh
		m = np.sum(PartialDerivatives(T, c), axis = -1)
		dw = w / m
		# ~ print(np.min(np.absolute(dw)) < MinStep, np.max(dw) > MaxStep)
		dw[dw < MinStep] = MinStep
		dw[dw > MaxStep] = MaxStep
		NewSigns = np.absolute(w) / w
		dw[OriginalSigns != NewSigns] = 0
		if(MaxDistance > 0):
			dw[np.sqrt(np.sum(np.power(T - origin, 2), axis=-1)) > MaxDistance] = 0
		if(np.max(dw) == 0):
			break;
		T[:,0] += dw * Vectors[:,0]
		T[:,1] += dw * Vectors[:,1]
		T[:,2] += dw * Vectors[:,2]
		iterations -= 1
	return T, PartialDerivatives(T, c)
