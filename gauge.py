import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Wedge
from matplotlib.backends.backend_tkagg import FigureCanvasKivyAgg as FigureCanvas

from matplotlib.figure import Figure
import sys,os

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None):
        self.fig = Figure(facecolor='#DBE0E4')
        self.axes = self.fig.add_subplot(111,axisbg='#DBE0E4')
        self.axes.axis('off')
        #here I create the contour of the gauge
        #the two horizontal lines
        x1=[-1,-0.6]
        x2=[0.6,1.0]
        y=[0.004,0.004]
        self.axes.plot(x1,y,color='#646464')
        self.axes.plot(x2,y,color='#646464')
        #and the 2 circles(inner and outer)
        circle1=plt.Circle((0,0),radius=1,fill=False)
        circle1.set_edgecolor('#646464')
        circle1.set_facecolor(None)

        circle2=plt.Circle((0,0),radius=0.6,fill=False)
        circle2.set_edgecolor('#646464')
        circle2.set_facecolor(None)
        self.axes.add_patch(circle1)
        self.axes.add_patch(circle2)

        #Scaling of the figure
        self.axes.axis('scaled')
        self.axes.set_xlim(-1.1,1.1)
        self.axes.set_ylim(0,1.1)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.updateGeometry(self)


class Gauge(MyMplCanvas):
    def __init__(self,meter,parent=None):
        MyMplCanvas.__init__(self)


        self.patches=[]
        #here I create the wedge to start
        self.wedge=Wedge((0,0),0.99,1,179,width=0.38,facecolor='#FF0000')
        self.patches.append(self.wedge)
        self.timeClear=0
        self.update_figure()
        #self.Online_meter=meter
        #here starts the update
        # timer=QtCore.QTimer(self)
        # timer.timeout.connect(self.update_figure)
        # timer.start(5000)

    def update_figure(self):
        #here is the update command
        #every 5 sec, I call value from a measurement instrument
        #here I let the program generate random values
        self.timeClear=self.timeClear+1
        #new_data=self.Online_meter.__call__()
        self.wedge.set_theta1(180-np.random.random(1)*10/10*179)
        self.axes.add_patch(self.wedge)    
        self.axes.plot()