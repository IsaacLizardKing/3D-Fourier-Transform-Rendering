import math
import time
import numpy as np
import pygame
pygame.init()

import Camera
import CustomFourier

class UserFunc:

	def LaTeX2Python(func):
		raise NotImplementedError("LaTeX flavor not supported yet")
		return func # TODO: ya know, the thing the title says

	def __init__(self, LaTeX=None, Python=None, bounds=((np.NINF, np.inf), (np.NINF, np.inf), (np.NINF, np.inf)), font=(pygame.font.get_default_font(), 80)):
		self.bounds = bounds
		self.font = pygame.font.Font(font[0], font[1])
		if LaTeX:
			self.Update(LaTeX, flavor="LaTeX")
		if Python:
			self.Update(Python, flavor="Python")

	# maybe some input cleaning is in order, otherwise this is the perfect target for an injection attack
	def Update(self, func, flavor):
		if flavor == "LaTeX":
			self.LaTeXfunc = func
			self._func = UserFunc.LaTeX2Python(func)
		elif flavor == "Python":
			self.LaTeXfunc = ""
			self._func = func
		else:
			raise NotImplementedError(f"\"{flavor}\" flavor not supported yet")
		self._flavor = flavor
		self.LaTeXImage = pygame.Surface((1,1)) # render LaTeX here
		self.LaTeXSourceImage = self.font.render(self.LaTeXfunc, True, (0,0,0))
		self.PythonImage = self.font.render(self._func, True, (0,0,0))

	def eval(self, coords):
		X = coords[0]
		Y = coords[1]
		Z = coords[2]
		return eval(self._func)

	def ParallelEval(self, coords):
		X = coords[:, 0]
		Y = coords[:, 1]
		Z = coords[:, 2]
		return eval(self._func).astype(np.float64)

theta = 90
phi = 0
fov = 140
fov = fov / 180 * math.pi
w = 200
h = 200
XT = math.pi / 2
YT = math.pi / 2
ZT = math.pi / 2
cam = Camera.camera(theta * math.pi / 180, phi * math.pi / 180, fov, [w,h], XT, YT, ZT)

myfunc = UserFunc(Python="3*X*X + 4*Y + np.sin(Z)")

Camera.show(cam.RenderExplicit(myfunc, 0))

