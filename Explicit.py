import numpy as np
import Newton

class UserFunc:

	def LaTeX2Python(func):
		raise NotImplementedError("LaTeX flavor not supported yet")
		return func # TODO: ya know, the thing the title says

#	def __init__(self, LaTeX=None, Python=None, bounds=((np.NINF, np.inf), (np.NINF, np.inf), (np.NINF, np.inf))):
	def __init__(self, LaTeX=None, Python=None, bounds=((-10, 10), (-10, 10), (-10, 10))):
		self.bounds = bounds
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

	def eval(self, coords):
		X = coords[0]
		Y = coords[1]
		Z = coords[2]
		return eval(self._func).astype(np.float64)

	def ParallelEval(self, coords):
		X = coords[:, 0]
		Y = coords[:, 1]
		Z = coords[:, 2]
		return eval(self._func).astype(np.float64)
