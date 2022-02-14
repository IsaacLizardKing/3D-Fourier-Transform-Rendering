import numpy as np
import math
import time
import cv2
import Camera
import os
XT = math.pi / 2
YT = math.pi / 2
ZT = math.pi / 2

theta = 90
phi = 0
fov = 140
fov = fov / 180 * math.pi
w = 600
h = 600
cam = Camera.camera(theta * math.pi / 180, phi * math.pi / 180, fov, [w,h], XT, YT, ZT)

EggCrate = np.array([[[1, 1, 0], [1, 1, 0], [1, 1, 0]]], np.float32)

try:
	os.mkdir("C:/NewtonRenders")
except:
	pass
try:
	os.mkdir("C:/NewtonRenders/CubeRotateRender")
except:
	pass
try:
	os.mkdir("C:/NewtonRenders/SpaceTraversalRender")
except:
	pass
try:
	os.mkdir("C:/NewtonRenders/CuboidOrbitRender")
except:
	pass
try:
	os.mkdir("C:/NewtonRenders/ThresholdRender")
except:
	pass



# ~ incrementally render 360 degrees at t = 0
# ~ threshold = 0
# ~ os.chdir("C:/NewtonRenders/CubeRotateRender")
# ~ for p in range(0, 360):
	# ~ out = cam.RenderFourier(EggCrate, threshold)
	# ~ cv2.imwrite(f"{100 + p}.png", out)
	# ~ Camera.show(out, 1)
	# ~ cam.rotate(math.pi / 180, 0)
	# ~ print(p, end = "\r")
# ~ cam.faceDir(0, 0)

# ~ move through empty space at t = -0.1

# ~ os.chdir("C:/NewtonRenders/SpaceTraversalRender")
# ~ threshold = -0.1
# ~ cam.rotate(math.pi/4, 0)
# ~ print(cam.theta, cam.phi)
# ~ M = ((math.pi * 2) ** 2 / 2) ** 0.5 / 360
# ~ for p in range(0, 360):
	# ~ out = cam.RenderFourier(EggCrate, threshold)
	# ~ Camera.show(out, 1)
	# ~ cv2.imwrite(f"{100 + p}.png", out)
	# ~ cam.origin[0] += M 
	# ~ cam.origin[2] += M
	# ~ print(p, end = "\r")

# ~ orbit origin at t = -0.02

# ~ This is broken

os.chdir("C:/NewtonRenders/CuboidOrbitRender")
Center = np.array([-math.pi / 2, -math.pi / 2, -math.pi / 2], np.float32)
threshold = -0.2
for p in range(0, 1):
	th = p / 180 * math.pi
	ph = 0 # math.pi / 4 * np.sin(p / 180 * math.pi)
	x = math.pi * math.cos(th) * math.sin(ph)
	y = math.pi * math.cos(th) * math.sin(ph) 
	z = math.pi * math.cos(ph)
	cam.origin[0] = x + Center[0]
	cam.origin[1] = y + Center[0]
	cam.origin[2] = z + Center[0]
	cam.facePoint(Center)
	out = cam.RenderFourier(EggCrate, threshold)
	Camera.show(out, 1)
	cv2.imwrite(f"{100 + p}.png", out)
	
	print(p, end = "\r")


# ~ show threshold change from t = 0 to t = 1
os.chdir("C:/NewtonRenders/ThresholdRender")
threshold = -1
cam.faceDir(0, 0)
for p in range(0, 200):
	out = cam.RenderFourier(EggCrate, threshold)
	Camera.show(out, 1)
	cv2.imwrite(f"{100 + p}.png", out)
	threshold += 0.005
	print(p, end = "\r")

