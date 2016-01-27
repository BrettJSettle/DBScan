from __future__ import division
import numpy as np
from PyQt4.QtCore import pyqtSignal as Signal
from vispy import app
from vispy import gloo
from vispy.visuals.shaders import ModularProgram
from vispy.visuals import Visual, LinePlotVisual, LineVisual, PolygonVisual
from vispy.visuals.transforms import (STTransform, LogTransform,
                                      TransformSystem, ChainTransform)
from pyqtgraph import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from vispy.scene.visuals import Text


class ClusterVisual(PolygonVisual):
    def __init__(self, points):
        PolygonVisual.__init__(self, color=None, border_color='white')
        self.points = np.array(points, dtype=np.float32)
        self.centroid = np.mean(self.points, 0)
        self.box_area = boxArea(self.points)
        self.grid_area = gridArea(self.points)
        self.averageDistance = averageDistance(self.points)
        self.density = len(self.points) / self.box_area
        self.border_points = getBorderPoints(self.points)
        self.pos = np.array(self.border_points, dtype=np.float32)

class PointVisual(Visual):
    VERTEX_SHADER = """
        #version 120

        attribute vec2 a_position;
        attribute vec3 a_color;
        attribute float a_size;

        varying vec4 v_fg_color;
        varying vec4 v_bg_color;
        varying float v_radius;
        varying float v_linewidth;
        varying float v_antialias;

        void main (void) {
            v_radius = a_size;
            v_linewidth = 1.0;
            v_antialias = 1.0;
            v_fg_color  = vec4(0.0,0.0,0.0,0.5);
            v_bg_color  = vec4(a_color,    1.0);

            gl_Position = $transform(vec4(a_position,0,1));

            gl_PointSize = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
        }
    """

    FRAGMENT_SHADER = """
        #version 120
        varying vec4 v_fg_color;
        varying vec4 v_bg_color;
        varying float v_radius;
        varying float v_linewidth;
        varying float v_antialias;
        void main()
        {
            float size = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
            float t = v_linewidth/2.0-v_antialias;
            float r = length((gl_PointCoord.xy - vec2(0.5,0.5))*size);
            float d = abs(r - v_radius) - t;
            if( d < 0.0 )
                gl_FragColor = v_fg_color;
            else
            {
                float alpha = d/v_antialias;
                alpha = exp(-alpha*alpha);
                if (r > v_radius)
                    gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
                else
                    gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
            }
        }
    """

    def __init__(self, name, color, points=None, size=None):
        self._program = ModularProgram(self.VERTEX_SHADER,
                                       self.FRAGMENT_SHADER)        
        self.name = name
        print(points)
        self.set_data(points=points, color=color, size=size)

    def set_options(self):
        """Special function that is used to set the options. Automatically
        called at initialization."""
        gloo.set_state(clear_color=(1, 1, 1, 1), blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def set_data(self, points=None, color=None, size=None):
        """I'm not required to use this function. We could also have a system
        of trait attributes, such that a user doing
        `visual.position = myndarray` results in an automatic update of the
        buffer. Here I just set the buffers manually."""
        self.points = points
        self._pos = np.array(points, dtype=np.float32)
        if isinstance(color, QtGui.QColor):
            color=np.array([color.redF(), color.greenF(), color.blueF()])
        if color.ndim == 1:
            self._color = np.array([color for i in range(len(points))], dtype=np.float32)
        if size == None:
            self._size = np.ones((len(points),)).astype(np.float32) * 2


    def draw(self, transforms):
        # attributes / uniforms are not available until program is built
        tr = transforms.get_full_transform()
        self._program.vert['transform'] = tr.shader_map()
        self._program.prepare()  # Force ModularProgram to set shaders
        self._program['a_position'] = gloo.VertexBuffer(self._pos)
        self._program['a_color'] = gloo.VertexBuffer(self._color)
        self._program['a_size'] = gloo.VertexBuffer(self._size)
        self._program.draw('points')

class ROIVisual(QtCore.QObject, PolygonVisual):
    translateFinished = Signal(object)
    selectionChanged = Signal(object, bool)
    def __init__(self, num, pos):
        QtCore.QObject.__init__(self)
        self.id = num
        PolygonVisual.__init__(self, color=None, border_color='white')
        self.text = Text("%d" % self.id, color='white')
        self.text.font_size=20
        self.text.pos = pos
        self.points = np.array([pos],dtype=np.float32)
        self.finished = False
        self.hover = False
        self.selected = False
        self._selected_color = np.array([1, 1, 1], dtype=np.float32)
        self.colorDialog=QtGui.QColorDialog()
        self.colorDialog.colorSelected.connect(self.colorSelected)
        self._make_menu()

    def setId(self, num):
        self.id = num
        self.text.text = "%d" % self.id

    @staticmethod
    def importROIs(fname):
        rois = []
        text = open(fname, 'r').read()
        kind=None
        pts=None
        for line in text.split('\n'):
            if kind is None:
                kind=line
                pts=[]
            elif line=='':
                rois.append(ROIVisual(1, pts[0]))
                for p in pts[1:]:
                    rois[-1].extend(p)
                rois[-1].draw_finished()
                kind=None
                pts=None
            elif kind == 'freehand':
                pts.append(tuple(int(i) for i in line.split()))
        return rois

    def __repr__(self):
        s = 'freehand\n'
        s += '\n'.join(['%d\t%d' % (p[0], p[1]) for p in self.points])
        s += '\n'
        return s

    def colorSelected(self, color):
        self.border_color = (color.redF(), color.greenF(), color.blueF())
        self._selected_color = self.border_color

    def mouseIsOver(self, pos):
        self.hover = self.contains(pos)
        return self.hover

    def _make_menu(self):
        self.menu = QtGui.QMenu('ROI Menu')
        self.menu.addAction(QtGui.QAction("Change Color", self.menu, triggered = self.colorDialog.show))

    def contextMenuEvent(self, pos):
        self.menu.popup(pos)

    def extend(self, pos):
        if not self.finished:
            self.points = np.array(np.vstack((self.points, pos)), dtype=np.float32)
            self.pos = self.points
        
    def select(self):
        if not self.selected:
            self.selected = True
            self.border_color = np.array([1, 0, 0], dtype=np.float32)
            self.selectionChanged.emit(self, True)

    def deselect(self):
        if self.selected:
            self.selected = False
            self.border_color = self._selected_color
            self.selectionChanged.emit(self, False)

    def draw_finished(self):
        self.points = np.vstack((self.points, self.points[0]))
        self.pos = self.points
        self.finished = True
        self.select()

    def finish_translate(self):
        self.translateFinished.emit(self)

    def contains(self, pt):
        if not hasattr(self, 'path_item'):
            self.path_item = QtGui.QPainterPath()
            self.path_item.moveTo(*self.points[0])
            for i in self.points[1:]:
                self.path_item.lineTo(*i)
            self.path_item.lineTo(*self.points[0])
        return self.path_item.contains(QtCore.QPointF(*pt))

    def translate(self, dxy):
        self.points += dxy
        self.pos = self.points
        self.text.pos = self.pos[0]
        if hasattr(self, 'path_item'):
            self.path_item.translate(*dxy)
    
    def draw(self, tr_sys):
        if not self.finished:
            color = np.ones((len(self.points), 3)).astype(np.float32)
            lp = LinePlotVisual(data=self.points, color=color, marker_size=5)
            lp.draw(tr_sys)
        elif len(self.points) > 2:
            PolygonVisual.draw(self, tr_sys)
            self.text.draw(tr_sys)
