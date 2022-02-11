import math
import numpy as np
import cv2
import Newton
import time

def show(img, time = 0):
	cv2.imshow("image", img)
	cv2.waitKey(time)
	if time == 0:
		cv2.destroyAllWindows()

def normalize(img):
	img = img * 1.0
	img -= np.min(img)
	img /= np.max(img)
	img *= 255.999
	return np.uint8(img)

def cartesian2Spherical(x, y, z):
	return np.arctan2(y,x), np.arctan2(np.sqrt(np.power(x, 2) + np.power(y, 2)), z),  np.sqrt(np.power(x, 2) + np.power(y, 2) + np.power(z, 2))
	
def spherical2Cartesian(theta, phi, rho = 1):
	return rho * np.cos(theta) * np.sin(phi), rho * np.sin(theta) * np.sin(phi), rho * np.cos(phi)
	
def getVectorMagnitude(Vect):
	return np.sum(np.power(Vect, 2)) ** 0.5
	
def normalizeVector(Vect):
	t = np.arctan2(Vect[1], Vect[0])
	p = np.arctan2(np.sqrt(np.power(Vect[0], 2) + np.power(Vect[1], 2)), Vect[2])
	return np.array([np.cos(t) * np.sin(p), np.sin(t) * np.sin(p), np.cos(p)], np.float32)

def parallelNormalizeVector(Vect):
	t = np.arctan2(Vect[:,:,1], Vect[:,:,0])
	p = np.arctan2(np.sqrt(np.power(Vect[:,:,0], 2) + np.power(Vect[:,:,1], 2)), Vect[:,:,2])
	Vect[:,:,0] = np.cos(t) * np.sin(p)
	Vect[:,:,1] = np.sin(t) * np.sin(p)
	Vect[:,:,2] = np.cos(p)
	return Vect

class camera:
	def facePoint(self, coords):
		theta, phi, _ = cartesian2Spherical(coords[0] - self.origin[0], coords[1] - self.origin[1], coords[2] - self.origin[2])
		self.rotate(phi - self.phi, theta - self.theta)

	def faceDir(self, theta, phi):
		self.rotate(theta - self.theta, phi - self.phi)

	def rotate(self, theta, phi):
		self.theta += theta
		self.phi += phi
	
	def __init__(self, theta, phi, fov, resolution, x, y, z):
		self.origin = np.array([x, y, z], np.float32)
		Y, X = np.mgrid[:resolution[0], :resolution[1]]
		coords = np.zeros((resolution[0], resolution[1], 3), np.float64)
		width, height = resolution[0], resolution[1]
		X = (X - ((X.shape[1] - 1) / 2))
		Y = (Y - ((Y.shape[0] - 1) / 2))
		coords[:, :, 0] = X[:, :]
		coords[:, :, 1] = Y[:, :]
		coords[:, :, 2] = np.array(spherical2Cartesian(fov / 2, fov / 2, np.array(cartesian2Spherical(X[0, -1], Y[-1, 0], math.sqrt(((width / 2) ** 2 + (height / 2) ** 2))), np.float32)[2]), np.float32)[2]
		x, y, z = spherical2Cartesian(0, 0)
		
		coords = parallelNormalizeVector(coords)
		coords[:, :, 0] -= x
		coords[:, :, 1] -= y
		coords[:, :, 2] -= z
		self.coords = coords * 1
		self.theta = theta
		self.phi = phi
		self.MaxRenderDistance = 16 * math.pi
		
	def DoShading(self, Coords, normals):
		x, y, z = spherical2Cartesian(self.theta, self.phi)
		Vect = self.coords * 1
		Vect[:, :, 0] += x 
		Vect[:, :, 1] += y
		Vect[:, :, 2] += z
		
		normals = parallelNormalizeVector(normals)
		bright = np.sum(normals * Vect, axis = -1)
		MaxD = self.MaxRenderDistance
		distances = np.sqrt(np.sum(np.power(Coords - self.origin,2), axis=-1))
		distances[distances < 1] = 1
		distances = MaxD / distances
		normals[:,:,0] *= bright
		normals[:,:,1] *= bright
		normals[:,:,2] *= bright
		normals -= np.min(normals)
		frame = normals * 0
		frame[:,:,0] = normals[:,:,0] * (distances)
		frame[:,:,1] = normals[:,:,1] * (distances)
		frame[:,:,2] = normals[:,:,2] * (distances)
		return frame
		
	def viewEggCrate(self, Thresh):
		x, y, z = spherical2Cartesian(self.theta, self.phi)
		Vect = np.reshape(self.coords * 1, (self.coords.shape[0] * self.coords.shape[1], 3))
		Coords = Vect * 0
		Vect[:, 0] += x 
		Vect[:, 1] += y
		Vect[:, 2] += z
		Coords[:, 0] = self.origin[0]
		Coords[:, 1] = self.origin[1]
		Coords[:, 2] = self.origin[2]
		start = time.time()
		Estimates, _ = Newton.ModifiedNewton(Vect, Coords, self.origin * 1, thresh = Thresh, MaxDistance = self.MaxRenderDistance)
		# ~ T, DT = Newton.ClassicalNewton(Vect, Estimates, self.origin, thresh = Thresh)
		end = time.time()
		print(end - start)
		
		T = np.reshape(T, self.coords.shape)
		DT = np.reshape(DT, self.coords.shape)
		frame = self.DoShading(T, DT)
		return normalize(frame)
		
ThreshHold = -0.02
def Threshold(val):
	global ThreshHold
	ThreshHold = val/200 - 0.5

# ~ XT = math.pi/3
# ~ YT = math.pi/3
# ~ ZT = math.pi/3
XT = (math.pi / 2)
YT = (math.pi / 2)
ZT = (math.pi / 2)
# ~ XT = 0
# ~ YT = 0
# ~ ZT = 0

theta = 0
phi = 0
fov = 120
fov = fov / 180 * math.pi
w = 400
h = 400
cam = camera(theta * math.pi / 180, phi * math.pi / 180, fov, [w,h], XT, YT, ZT)

for p in range (0, 128):
	out = cam.viewEggCrate(ThreshHold)
	cv2.imwrite(f'CubicShift/{100+p}.png', out)
	show(out, 1)
	ThreshHold += 0.005




















# ~ Vect = normalizeVector(np.array([1, 1, 1], np.float32))
# ~ origin = 0
# ~ T = np.array([origin, origin, origin], np.float32)
# ~ Thresh = 0

# ~ a = T * 1
# ~ b = 0
# ~ start = time.time()
# ~ while abs(np.sin(T[0]) * np.sin(T[1]) * np.sin(T[2]) - Thresh) >= 1e-15:
	# ~ w = np.sin(T[0]) * np.sin(T[1]) * np.sin(T[2]) - Thresh
	# ~ m = np.cos(T[0]) * np.sin(T[1]) * np.sin(T[2]) + np.sin(T[0]) * np.cos(T[1]) * np.sin(T[2]) + np.sin(T[0]) * np.sin(T[1]) * np.cos(T[2])
	# ~ if(m == 0):
		# ~ m += np.sum(Vect) / 10
	# ~ sigmoid function limits the magnitude of the step
	# ~ if(abs(w / m) >= 1):
		# ~ m = (m / abs(m)) / (math.e ** abs(m))
		# ~ T -= w * Vect * m
	# ~ regular newton approximation for speed
	# ~ else:
		# ~ T -= w / (Vect * m)
	# ~ b+=1



