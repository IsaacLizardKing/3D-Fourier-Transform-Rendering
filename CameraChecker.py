import numpy as np
import cv2
import Camera
import sys
import math


shape = (60, 60, 60)


rotPoint = (30, 30, 30)
rotRadius = 70
its = 30 # iterations
res = 50 # resolution
fov = 100

YT = rotPoint[1]
phi = 0
fov = fov / 180 * math.pi
w = res
h = res
cam = Camera.camera(0, phi, fov, [w,h], 0, YT, 0)
for i in range(its):
	print(i)
	theta = i/its * 2 * math.pi
	XT = math.sin(theta) * rotRadius + rotPoint[0]
	ZT = math.cos(theta) * rotRadius + rotPoint[2]
	cam.origin[0] = XT
	cam.origin[2] = ZT
	cam.faceDir(theta - math.pi, phi)
	print(f"Camera.camera({theta}, {phi}, {fov}, {[w,h]}, {XT}, {YT}, {ZT})")

	Camera.show(cam.RenderCube(((0,shape[0]),(0,shape[1]),(0,shape[2]))),100)
