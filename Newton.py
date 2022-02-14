import math
import numpy as np
import time

COORDINATE_FUDGER = 1e-5

def PartialDerivativesSeries(T, c):
	DT = T * 0
	for a in range(0, c.shape[0]):
		X, Y, Z = FourierSeries(T, c)
		DT[:,0] += c[a, 0, 0] * c[a, 0, 1] * np.cos(c[a, 0, 1] * T[:,0] + c[a, 0, 2]) * Y * Z
		DT[:,1] += X * c[a, 1, 0] * c[a, 1, 1] * np.cos(c[a, 1, 1] * T[:,1] + c[a, 1, 2]) * Z
		DT[:,2] += X * Y * c[a, 2, 0] * c[a, 2, 1] * np.cos(c[a, 2, 1] * T[:,2] + c[a, 2, 2])
	return DT

def PartialDerivativesTransform(T, data):
	X = T[:, 0]
	Y = T[:, 1]
	Z = T[:, 2]
	w = data.ParallelEval(T)
	DT = T * 0
	DT[:, 0] = (w - data.ParallelEval(np.column_stack((X + COORDINATE_FUDGER, Y, Z)))) / COORDINATE_FUDGER
	DT[:, 1] = (w - data.ParallelEval(np.column_stack((X, Y + COORDINATE_FUDGER, Z)))) / COORDINATE_FUDGER
	DT[:, 2] = (w - data.ParallelEval(np.column_stack((X, Y, Z + COORDINATE_FUDGER)))) / COORDINATE_FUDGER
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
	
def ClassicalNewtonSeries(Vectors, T, origin, c = np.float32([[[1, 1, 0], [1, 1, 0], [1, 1, 0]]]), iterations = 1, thresh = 0):
	N = c.shape[0]
	while iterations > 0:
		X, Y, Z = FourierSeries(T, c)
		w = (X * Y * Z) / N - thresh
		m = np.sum(PartialDerivatives(T, c), axis = -1) / N
		m = (m / np.absolute(m)) * np.power(math.e, np.absolute(m))
		T[:,0] -= (w / m) * Vectors[:,0]
		T[:,1] -= (w / m) * Vectors[:,1]
		T[:,2] -= (w / m) * Vectors[:,2]
		iterations -= 1
	return T, PartialDerivatives(T, c)

def ModifiedNewtonSeries(Vectors, T, origin, c = np.float32([[[1, 1, 0], [1, 1, 0], [1, 1, 0]]]), iterations = 500, thresh = 0, MaxDistance = -1):
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

def ClassicalNewtonTransform(Vectors, T, origin, data, iterations = 1, thresh = 0):
	while iterations > 0:
		w = data.eval(T)
		m = w - data.eval(T + COORDINATE_FUDGER) / COORDINATE_FUDGER
		m = (m / np.absolute(m)) * np.power(math.e, np.absolute(m))
		w -= thresh
		T[:,0] -= (w / m) * Vectors[:,0]
		T[:,1] -= (w / m) * Vectors[:,1]
		T[:,2] -= (w / m) * Vectors[:,2]
		iterations -= 1
	return T, PartialDerivativesTransform(T, data)

def ModifiedNewtonTransform(Vectors, T, origin, data, iterations = 500, thresh = 0, MaxDistance = -1):
	MaxStep = math.pi / 16
	MinStep = MaxStep / 8
	w = data.ParallelEval(T) - thresh
	OriginalSigns = np.absolute(w) / w
	
	while iterations > 0:
		w = data.ParallelEval(T)
		m = (w - data.ParallelEval(T + COORDINATE_FUDGER)) / COORDINATE_FUDGER
		w -= thresh
		dw = w / m
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
	return T, PartialDerivativesTransform(T, data)
