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

def BoundPoints(Vectors, coords, origin, MaxDistance, b):
		# ~ Vectors is the marching vectors
		# ~ coords is the current progress of the marching vectors
		# ~ origin is the coords of the camera
		# ~ MaxDistance is the maximum render distance
		# ~ b is the bounding box to be rendered, should be in the form [[lowerX,upperX],[lowerY,upperY],[lowerZ,upperZ]]
		# ~ returns coords, but all points outside of the box are set to MaxDistance * 1.1 away from the camera
		print("bounding")
		print("coords", coords.size)
		X = coords[:, 0]
		Y = coords[:, 1]
		Z = coords[:, 2]

		dw = X * 0

		A1 = b[0][0]#they should already be sorted
		A2 = b[1][0]
		A3 = b[2][0]
		B1 = b[0][1]
		B2 = b[1][1]
		B3 = b[2][1]
		
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
		mask = (X >= A1) * (X <= B1) * (Y >= A2) * (Y <= B2) * (Z >= A3) * (Z <= B3)
		mask = 1-mask
		print("mask", mask.sum())
#		Ca1mask = (Ca1x >= A1) * (Ca1x <= B1) * (Ca1y >= A2) * (Ca1y <= B2) * (Ca1z >= A3) * (Ca1z <= B3) * (Ca1 >= 0)
#		Ca2mask = (Ca2x >= A1) * (Ca2x <= B1) * (Ca2y >= A2) * (Ca2y <= B2) * (Ca2z >= A3) * (Ca2z <= B3) * (Ca2 >= 0)
#		Ca3mask = (Ca3x >= A1) * (Ca3x <= B1) * (Ca3y >= A2) * (Ca3y <= B2) * (Ca3z >= A3) * (Ca3z <= B3) * (Ca3 >= 0)
#		Cb1mask = (Cb1x >= A1) * (Cb1x <= B1) * (Cb1y >= A2) * (Cb1y <= B2) * (Cb1z >= A3) * (Cb1z <= B3) * (Cb1 >= 0)
#		Cb2mask = (Cb2x >= A1) * (Cb2x <= B1) * (Cb2y >= A2) * (Cb2y <= B2) * (Cb2z >= A3) * (Cb2z <= B3) * (Cb2 >= 0)
#		Cb3mask = (Cb3x >= A1) * (Cb3x <= B1) * (Cb3y >= A2) * (Cb3y <= B2) * (Cb3z >= A3) * (Cb3z <= B3) * (Cb3 >= 0)

		Ca1mask = (Ca1y >= A2) * (Ca1y <= B2) * (Ca1z >= A3) * (Ca1z <= B3) * (Ca1 >= 0)#the corresponding coordinates should already be inside, no?
		Ca2mask = (Ca2x >= A1) * (Ca2y <= B2) * (Ca2z >= A3) * (Ca2z <= B3) * (Ca2 >= 0)
		Ca3mask = (Ca3x >= A1) * (Ca3x <= B1) * (Ca3y >= A2) * (Ca3y <= B2) * (Ca3 >= 0)
		Cb1mask = (Cb1y >= A2) * (Cb1y <= B2) * (Cb1z >= A3) * (Cb1z <= B3) * (Cb1 >= 0)
		Cb2mask = (Cb2x >= A1) * (Cb2x <= B1) * (Cb2z >= A3) * (Cb2z <= B3) * (Cb2 >= 0)
		Cb3mask = (Cb3x >= A1) * (Cb3x <= B1) * (Cb3y >= A2) * (Cb3y <= B2) * (Cb3 >= 0)

		Valid = np.logical_or(np.logical_or(np.logical_or(Ca2mask, Ca3mask), Ca1mask), np.logical_or(np.logical_or(Cb2mask, Cb3mask), Cb1mask))
		print("Valid", Valid.sum())
		
		dw = np.minimum(np.minimum(np.minimum(Ca1, Ca2), Ca3), np.minimum(np.minimum(Cb1, Cb2), Cb3))
		dw[Valid == 0] = MaxDistance * 1.1#why do this multiple times? i simpilified it
		#dw[mask] = (X[mask] - origin[0]) / Vectors[mask, 0]
		coords[mask, 0] = origin[0] + (dw[mask] * Vectors[mask, 0])
		coords[mask, 1] = origin[1] + (dw[mask] * Vectors[mask, 1])
		coords[mask, 2] = origin[2] + (dw[mask] * Vectors[mask, 2])
		return coords

def ModifiedNewtonSeries(Vectors, T, origin, c = np.float32([[[1, 1, 0], [1, 1, 0], [1, 1, 0]]]), iterations = 500, thresh = 0, MaxDistance = -1, bounds = None):
	MaxStep = math.pi / 16
	MinStep = MaxStep / 8
	N = c.shape[0]
	X, Y, Z = FourierSeries(T, c)
	w = (X * Y * Z) / N - thresh
	OriginalSigns = np.absolute(w) / w
	
	while iterations > 0:
		X, Y, Z = FourierSeries(T, c)
		w = (X * Y * Z) / N - thresh
		m = np.sum(PartialDerivativesSeries(T, c), axis = -1)
		dw = w / m
		# ~ print(np.min(np.absolute(dw)) < MinStep, np.max(dw) > MaxStep)
		dw[dw < MinStep] = MinStep
		dw[dw > MaxStep] = MaxStep
		NewSigns = np.absolute(w) / w
		dw[OriginalSigns != NewSigns] = 0
		if bounds:
			T = BoundPoints(Vectors, T, origin, MaxDistance, bounds)
		if(MaxDistance > 0):
			dw[np.sqrt(np.sum(np.power(T - origin, 2), axis=-1)) > MaxDistance] = 0
		if(np.max(dw) == 0):
			break;
		T[:,0] += dw * Vectors[:,0]
		T[:,1] += dw * Vectors[:,1]
		T[:,2] += dw * Vectors[:,2]
		iterations -= 1
	return T, PartialDerivativesSeries(T, c)

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
		T = BoundPoints(Vectors, T, origin, MaxDistance, data.bounds)
		if(MaxDistance > 0):
			dw[np.sqrt(np.sum(np.power(T - origin, 2), axis=-1)) > MaxDistance] = 0
		if(np.max(dw) == 0):
			break
		T[:,0] += dw * Vectors[:,0]
		T[:,1] += dw * Vectors[:,1]
		T[:,2] += dw * Vectors[:,2]
		iterations -= 1
	return T, PartialDerivativesTransform(T, data)
