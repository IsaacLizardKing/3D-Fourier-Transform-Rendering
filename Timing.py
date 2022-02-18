# i'm not sure how the cameracoordinates work / how they should be rendered. they have to be adjusted i think

import numpy as np
import cv2
import Camera
import math
import time
import os
import CustomFourier
XT = math.pi / 2
YT = math.pi / 2
ZT = math.pi / 2

theta = 90
phi = 0
fov = 140
fov = fov / 180 * math.pi

OctaTheta, OctaPhi, _ = Camera.cartesian2Spherical(1,1,1)

def EggCrate(cam, name, bounds = None):
	cam.facePoint((0,0,0))
	for p in range(0, 200):
		threshold = -1 + (p*0.01)
		out = cam.RenderFourierSeries(EggCrate, threshold, bounds = bounds)
		cv2.imwrite(os.path.join(name, f"{p:03}.png"), out)

def Octahedron(cam, name):
	for p in range(0, 360):
		out = cam.RenderFourierTransform(OctahedronTransform, 0)
		cv2.imwrite(os.path.join(name, f"{p:03}.png"), out)
		cam.rotate(math.pi / 180, 0)


EggCrate = np.array([[[1, 1, 0], [1, 1, 0], [1, 1, 0]]], np.float32)
bounds1 = [[-5,5],[-5,5],[-5,5]]

# ~ octahedron input data
size = 10
x, y, z = np.mgrid[:size, :size * 2, :size * 3] - (size / 2)
x = np.abs(x)
y = np.abs(y)
z = np.abs(z)
octahedron = np.round(x + y + z - size * 0.4)
octahedron += np.random.normal(0,3,octahedron.size).reshape(octahedron.shape)
OctahedronTransform = CustomFourier.Fourier(octahedron)
# ~ suite[n] = (function, cameraGenerator, ((camResolution, otherArgs), ...))
suite = (
	(Octahedron, lambda res : Camera.camera(OctaTheta, OctaPhi, fov, (res,res), 0, 0, 0), ((50, "octo50"), (100, "octo100"), (500, "octo500"))),
	(EggCrate, lambda res : Camera.camera(theta * math.pi / 180, phi * math.pi / 180, fov, (res,res), XT, YT, ZT), ((50, "EggCrateBounded50", bounds1), (100, "EggCrateBounded100", bounds1), (500, "EggCrateBounded500", bounds1), (50, "EggCrateUnbounded50"), (100, "EggCrateUnbounded100"), (500, "EggCrateUnbounded500"))),
)

for timer in suite:
	for run in timer[2]:
		cam = timer[1](run[0])
		print(run[1])
		if not os.path.exists(run[1]):
			print("making directory")
			os.makedirs(run[1])
		args = (cam,) + run[1:]
		start = time.time()
		timer[0](*args)
		print(time.time()-start)
