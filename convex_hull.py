import numpy as np
from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 1.0

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)


# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		points.sort(key= lambda point: point.x())
		t2 = time.time()
		
  
		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		# polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		polygon = self.divide_conquer(points)

		t4 = time.time()
		
		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
	
	def divide_conquer(self, points):
		# get length of points
		l = len(points)
		# base case when our list only has 3 points or 
		# less just return the lines conecting the points
		if l <= 3:
			polygon = [QLineF(points[i],points[(i+1)%l]) for i in range(l)]
			if (l == 2 or self.slope(polygon[0].p1(), polygon[0].p2()) > self.slope(polygon[1].p1(), polygon[1].p2())):
				return polygon
			else:
				return [QLineF(points[0],points[2]), QLineF(points[2],points[1]), QLineF(points[1],points[0]) ]
		
		# calling our recursion with lists of halved sizes
		left_hull = self.divide_conquer(points[0 : l // 2])
		right_hull = self.divide_conquer(points[l // 2  : l])

		# combine left and right hulls and return
		merged = self.combine_hulls(left_hull, right_hull)
		return merged
		

	def combine_hulls(self, left_hull, right_hull):

		# find the line connecting the sidemost points 
		[right_index, right_point, left_index, left_point] = self.sidemost_line(left_hull, right_hull)

		# get the indexes of the lines containing the endpoits of sidemost line in each convex
		# left_hull_index = [i for i, x in enumerate(left_hull) if x.p2() == sidemost_line.p1()][0]
		# right_hull_index = [i for i, x in enumerate(right_hull) if x.p1() == sidemost_line.p2()][0]

		# find upper tangent 
		[uptangent, endup_left, startup_right] = self.upper_tangent(left_hull, right_hull, left_point, right_point, right_index, left_index)
		# find lower tangent
		[lowtangent, startlow_left, endlow_right] = self.lower_tangent(left_hull, right_hull, left_point, right_point, right_index, left_index)
		merged = []
		if(len(left_hull) == 2):
			if(endup_left == 0):
				merged.append(left_hull[0])
		else:
			if(endup_left == len(left_hull) - 1):
				pass
			else: 
				for start in range(endup_left + 1):
					merged.append(left_hull[start])

		merged.append(uptangent)

		for start in range(startup_right, (endlow_right - 1) % len(right_hull) +1 ):
			merged.append(right_hull[start])
		
		merged.append(QLineF(lowtangent.p2(),lowtangent.p1()))
		for start in range(startlow_left + 1, len(left_hull)):
			merged.append(left_hull[start])

		return merged
		

	def upper_tangent(self, left_hull, right_hull, left_point, right_point, left_index, right_index):

		# initialize upper tangent data using he points of the sidemost line
		left_upper_pt = right_point
		right_upper_pt = left_point
		# adujst the endpoints of our for an inderterminate amount of times 
		must_adjust = True

		while(must_adjust):
			# adjust left upper point of upper_tangent to maximize the angle
			hull_len = len(left_hull)
			prev_left_upper_pt = left_upper_pt
			next_left_pt = left_hull[(left_index - 1) % hull_len].p2()

			while (self.slope(next_left_pt, right_upper_pt) < self.slope(left_upper_pt, right_upper_pt)):
				left_upper_pt = next_left_pt
				left_index = (left_index - 1) % hull_len
				next_left_pt = left_hull[(left_index - 1) % hull_len].p2()
				
			# see if the left upper point has changed
			left_changed = False
			if(left_upper_pt != prev_left_upper_pt):
				left_changed = True
			
			if (must_adjust or left_changed):
				# adjust right upper point of upper tangent to maximize the angle
				hull_len = len(right_hull)
				previous_right_upper_pt = right_upper_pt
				next_right_pt = right_hull[(right_index + 1) % hull_len].p1()

				while (self.slope(left_upper_pt, next_right_pt) > self.slope(left_upper_pt, right_upper_pt)):
					right_upper_pt = next_right_pt
					right_index = (right_index + 1) % hull_len
					next_right_pt = right_hull[(right_index + 1) % hull_len].p1()

				if (right_upper_pt == previous_right_upper_pt):
					must_adjust = False
		
		return QLineF(left_upper_pt, right_upper_pt), left_index, right_index

	def lower_tangent(self, left_hull, right_hull, left_point, right_point, left_index, right_index):

		# initialize upper tangent data using passed lower_tangent line
		left_lower_pt = right_point
		right_lower_pt = left_point

		# adujst the endpoints of our for an inderterminate amount of times 
		must_adjust = True

		while(must_adjust):
			# adjust left upper point of upper_tangent to maximize the angle
			hull_len = len(left_hull)
			prev_left_lower_pt = left_lower_pt
			next_left_pt = left_hull[(left_index + 1) % hull_len].p2()

			while (self.slope(next_left_pt, right_lower_pt) > self.slope(left_lower_pt, right_lower_pt)):
				left_lower_pt = next_left_pt
				left_index = (left_index + 1) % hull_len
				next_left_pt = left_hull[(left_index + 1) % hull_len].p2()
			
			# see if the left lower point has changed
			left_changed = False
			if(left_lower_pt != prev_left_lower_pt):
				left_changed = True
			

			if (must_adjust or left_changed):
				# adjust right upper point of upper tangent to maximize the angle
				hull_len = len(right_hull)
				prev_right_lower_pt = right_lower_pt
				next_right_pt = right_hull[(right_index - 1) % hull_len].p1()

				
				while (self.slope(left_lower_pt, next_right_pt) < self.slope(left_lower_pt, right_lower_pt)):
					right_lower_pt = next_right_pt
					right_index = (right_index - 1) % hull_len
					next_right_pt = right_hull[(right_index - 1) % hull_len].p1()

				if (right_lower_pt == prev_right_lower_pt):
					must_adjust = False

		return QLineF(left_lower_pt, right_lower_pt), left_index, right_index

	def sidemost_line(self, left_hull, right_hull):

		# finding rightmost point of left hull
		right_index = max(range(len(left_hull)), key = lambda index: left_hull[index].p2().x())
		right_point = left_hull[right_index].p2()

		# finding left hull's upper tangent point
		left_index = min(range(len(right_hull)), key= lambda index: right_hull[index].p1().x())
		left_point = right_hull[left_index].p1()

		# sidemost_line = QLineF(right_point, left_point)
	
		return right_index, right_point, left_index, left_point

	def slope(self, left_pt, right_pt):
		return (right_pt.y() - left_pt.y())/(right_pt.x() - left_pt.x())
		

		
	
  
  