import math
import time
import tkinter as tk
#import tkinter.font as tkf
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg') # for LaTeX
import numpy as np
np.seterr(all="ignore")
"""
gotta ignore errors, otherwise you get warnings to stdout (i think, it might be stderr)

/media/robert/Data/school/ScienceFair2023/3D-Fourier-Transform-Rendering-main/Newton.py:196: RuntimeWarning: invalid value encountered in double_scalars
  OriginalSigns = np.absolute(w) / w

/media/robert/Data/school/ScienceFair2023/3D-Fourier-Transform-Rendering-main/Newton.py:208: RuntimeWarning: divide by zero encountered in true_divide
  dw[Terminated == 0] = np.absolute(w[Terminated == 0] / m[Terminated == 0])

/media/robert/Data/school/ScienceFair2023/3D-Fourier-Transform-Rendering-main/Camera.py:16: RuntimeWarning: invalid value encountered in true_divide
  img /= np.max(img)
"""
import Newton
#from PIL import Image, ImageTk
# https://github.com/augustt198/latex2sympy

import Camera
import Explicit

CamSettings = {
	"theta": 45 * math.pi / 180,
	"phi": 5 * math.pi / 180,
	"fov": 140 / 180 * math.pi,
	"resolution": (200, 200),
	"x": math.pi / 2,
	"y": math.pi / 2,
	"z": math.pi / 2,
}
Cam = Camera.camera(CamSettings["theta"], CamSettings["phi"], CamSettings["fov"], CamSettings["resolution"], CamSettings["x"], CamSettings["y"], CamSettings["z"])
Threshold = -0.1

Func = Explicit.UserFunc(Python="np.sin(X) * np.sin(Y) * np.sin(Z)")
#Func = Explicit.UserFunc(Python="Newton.FourierSeries(coords[None,:], np.array([[[1, 1, 0], [1, 1, 0], [1, 1, 0]]], np.float32))")
#Func = Explicit.UserFunc(Python="np.array([[[1, 1, 0], [1, 1, 0], [1, 1, 0]]], np.float32)")

#import CustomFourier
#size = 22
#x, y, z = np.mgrid[:size, :size, :size] - (size / 2)
#x = np.abs(x)
#y = np.abs(y)
#z = np.abs(z)
#octahedron = x + y + z - size * 0.6
## ~ octahedron -= np.min(octahedron)
## ~ octahedron /= np.max(octahedron)
## ~ octahedron *= 2
## ~ octahedron -= 1
#print(np.min(octahedron))
#print(np.max(octahedron))
#Func = CustomFourier.Fourier(octahedron)

def setStatusBar(status=None):
	if status is None:
		status = f"Threshold: {Threshold}, Theta: {Cam.theta}, Phi: {Cam.phi}" # maybe put resolution at some point
	StatusBar.configure(state='normal') # this ...
	StatusBar.delete("1.0", tk.END)
	StatusBar.insert("1.0", status)
	StatusBar.configure(state='disabled') # ... and this make the text read-only

def funcUpdate(event):
	status = None
	try:
		Func.Update(FuncInput.get(), Flavor.get())
	except Exception as E:
		status = "LaTeX translator says: " + repr(E)

	if Flavor.get() == "LaTeX":
		tmptext = FuncInput.get() # do i really need the "1.0", tk.END?
		tmptext = "$"+tmptext+"$"
		ax.clear()
		ax.text(0.1, 0.3, tmptext, fontsize=50)  
		try:
			LaTeXCanvas.draw()
		except Exception as E:
			status = "LaTeX renderer says: " + repr(E)

	else:
		ax.clear()
		LaTeXCanvas.draw()

	setStatusBar(status)

print("""Controls:
Up/Down: increase/decrease phi
Right/Left: increase/decrease theta
Period/Comma: increase/decrease threshold
""")
def displayKeyPress(event):
	global Cam, Threshold
	if event.keysym == "Up":
		Cam.rotate(0, 0.1)
		if Cam.phi > math.pi/2:
			Cam.rotate(0, (math.pi/2) - Cam.phi)
	elif event.keysym == "Down":
		Cam.rotate(0, -0.1)
		if Cam.phi < -math.pi/2:
			Cam.rotate(0, (-math.pi/2) - Cam.phi)
	elif event.keysym == "Left":
		Cam.rotate(-0.1, 0)
		if Cam.theta < 0:
			Cam.rotate(math.pi*2, 0)
	elif event.keysym == "Right":
		Cam.rotate(0.1, 0)
		if Cam.theta > math.pi*2:
			Cam.rotate(-math.pi*2, 0)
	elif event.keysym == "period":
		Threshold += 0.1
	elif event.keysym == "comma":
		Threshold -= 0.1
#	elif event.keysym == "a":
#		Threshold -= 0.1
	else:
		print(event.keysym)
		return # so updateImg doesn't get called
	updateCam()
	updateSize(None)
	# TODO: for some reason, it will process the events of keys pressed while rendering before displaying it to the screen, leading to a frozen screen while you repeatedly tap a new movement command
	# make it display each frame while computing the next one, por favor

def updateSize(event):
	ViewPort.configure(state="normal")
	ViewPort.delete("1.0", tk.END)
	FuncImageID = ViewPort.image_create("1.0", image=FuncImage, pady=ViewPort.winfo_height()/2-FuncImage.height()/2, padx=ViewPort.winfo_width()/2-FuncImage.width()/2)
	ViewPort.configure(state="disabled")

def numpy2tk(array):
	height, width = array.shape[:2]
	ppm_header = f'P6 {width} {height} 255 '.encode()
	data = ppm_header + array.tobytes()
	return tk.PhotoImage(width=width, height=height, data=data, format='PPM')

def updateCam():
	global FuncImage, FuncImageID
	status = None
	print("rendering image...")
	try:
		raw = Cam.RenderExplicit(Func, Threshold)
	except Exception as E:
		status = "Renderer says: " + repr(E)
		raw = np.zeros((1,1,3), dtype=np.uint8)
	FuncImage = numpy2tk(raw)
	print("done rendering")
#	FuncImageID = ViewPort.create_image(ViewPort.winfo_width()/2, ViewPort.winfo_height()/2, image=FuncImage)
	setStatusBar(status)

#FuncImage = ImageTk.PhotoImage(image=Cam.RenderExplicit(Func, Threshold))

Window = tk.Tk()
Window.geometry('550x450')


DisplayFrame = tk.Frame(Window)

StatusBar = tk.Text(DisplayFrame, height=1)
StatusBar.pack(side=tk.TOP, fill=tk.X)

ViewPort = tk.Text(DisplayFrame, height=1)
ViewPort.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
ViewPort.bind("<KeyPress>", displayKeyPress)

DisplayFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


FuncInputFrame = tk.Frame(Window)

LaTeXWidget = tk.Label(FuncInputFrame)
fig = matplotlib.figure.Figure(figsize=(10, 2), dpi=100)
ax = fig.add_subplot(111)
LaTeXCanvas = FigureCanvasTkAgg(fig, master=LaTeXWidget)
LaTeXCanvas.get_tk_widget().pack(side="top", fill="both", expand=True)
LaTeXCanvas._tkcanvas.pack(side="top", fill="both", expand=True)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
LaTeXWidget.pack()

Flavor = tk.StringVar(Window)
Flavor.set("Python")
FlavorMenu = tk.OptionMenu(FuncInputFrame, Flavor, "Python", "LaTeX")
FlavorMenu.pack(side=tk.LEFT)
FlavorMenu.bind("<Button-1>", funcUpdate)

FuncInput = tk.Entry(FuncInputFrame)
FuncInput.pack(fill=tk.X)
FuncInput.bind("<KeyRelease>", funcUpdate)

FuncInputFrame.pack(side=tk.BOTTOM, fill=tk.X)


updateCam()

Window.bind("<Configure>", updateSize)
Window.mainloop()
