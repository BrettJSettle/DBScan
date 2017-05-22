from __future__ import division
import numpy as np
from qtpy.QtCore import Signal
from vispy import app
from vispy import gloo
from vispy.visuals.shaders import ModularProgram
from vispy.visuals import Visual, LinePlotVisual, LineVisual, PolygonVisual
from vispy.visuals.transforms import (STTransform, LogTransform,
                                      TransformSystem, ChainTransform)
from pyqtgraph import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from Visuals import *

class Canvas(QtCore.QObject, app.Canvas):
    roiCreated = Signal(object)
    roiDeleted = Signal(object)
    def __init__(self, visuals=[]):
        QtCore.QObject.__init__(self)
        app.Canvas.__init__(self, keys='interactive')
        ps = self.pixel_scale

        self.roi_visuals = []
        self.current_roi = None
        self.finished = False
        self.drawing_roi = False

        self.markers = visuals
        self.panzoom = STTransform(scale=(1, 1), translate=(0, 0))
        self.transform = ChainTransform([self.panzoom,
                                         STTransform(scale=[1, 1], translate=[1,1]),
                                         LogTransform(base=(0, 0, 0))])

        self.tr_sys = TransformSystem(self)
        self.tr_sys.visual_to_document = self.transform

        gloo.set_state(blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        self.timer = app.Timer('auto', connect=self.on_timer, start=True)
        #=self.native.setFixedSize(800, 600)

    def on_timer(self, event):
        self.update()

    def on_mouse_release(self, event):
        if event.button == 2 and self.drawing_roi:
            self.drawing_roi = False
            self.current_roi.draw_finished()
            self.roi_visuals.append(self.current_roi)
            self.current_roi.menu.addAction(QtGui.QAction('Export ROIs', self.current_roi.menu, triggered=lambda : save_file_gui(self.export_rois, prompt='Export ROIs to text file', filetypes='Text Files (*.txt)')))
            self.current_roi.menu.addAction(QtGui.QAction('Import ROIs', self.current_roi.menu, triggered=lambda : open_file_gui(self.import_rois, prompt='Import ROIs from text file', filetypes='Text Files (*.txt)')))
            self.current_roi.select()
            self.roiCreated.emit(self.current_roi)
        elif any([roi.hover for roi in self.roi_visuals]) and event.button == 2 and not self.drawing_roi and event.last_event.type == 'mouse_press':
            self.current_roi.contextMenuEvent(self.native.mapToGlobal(QtCore.QPoint(*event.pos)))
        for roi in self.roi_visuals:
            if roi.selected:
                roi.finish_translate()
    
    def export_rois(self, fname):
        roi_strs = [repr(roi) for roi in self.roi_visuals]
        with open(fname, 'w') as outf:
            outf.write('\n'.join(roi_strs))

    def import_rois(self, fname):
        rois = ROIVisual.importROIs(fname)
        for roi in rois:
            while roi.id in [r.id for r in self.roi_visuals]:
                roi.setId(roi.id + 1)
            self.roi_visuals.append(roi)

    def translatedPoint(self, pos):
        return np.array([(pos[0] - self.panzoom.translate[0]) / self.panzoom.scale[0], (pos[1] - self.panzoom.translate[1]) / self.panzoom.scale[1]])

    def on_mouse_press(self, event):
        if self.drawing_roi:
            return
        if 'Control' in event.modifiers:
            for roi in self.roi_visuals:
                if roi.contains(self.translatedPoint(event.pos)):
                    if roi.selected:
                        roi.deselect()
                    else:
                        roi.select()
        else:
            self.current_roi = None
            for roi in self.roi_visuals:
                if roi.mouseIsOver(self.translatedPoint(event.pos)):
                    self.current_roi = roi
                    roi.select()
                else:
                    roi.deselect()

    def on_key_press(self, event):
        if event.key == 'a' and 'Control' in event.modifiers:
            for roi in self.roi_visuals:
                roi.select()
        elif event.key == 'Delete':
            for roi in self.roi_visuals[:]:
                if roi.selected:
                    if self.current_roi == roi:
                        self.current_roi = None
                    self.roi_visuals.remove(roi)
                    self.roiDeleted.emit(roi)


    def on_mouse_move(self, event):
        pos = self.translatedPoint(event.pos)
        for roi in self.roi_visuals:
            if not self.drawing_roi:
                if roi.mouseIsOver(pos):
                    self.current_roi = roi
        if event.is_dragging:
            dxy = self.translatedPoint(event.pos) - self.translatedPoint(event.last_event.pos)
            button = event.press_event.button
            if button == 1:
                self.panzoom.move(event.pos - event.last_event.pos)
            elif button == 2:
                if not self.drawing_roi and any([roi.mouseIsOver(pos) for roi in self.roi_visuals]):
                    for roi in self.roi_visuals:
                        if roi.selected:
                            roi.translate(dxy)
                elif self.drawing_roi == True:
                    self.current_roi.extend(pos)
                else:
                    for roi in self.roi_visuals:
                        roi.deselect()
                    new_id = 1
                    while new_id in [roi.id for roi in self.roi_visuals]:
                        new_id += 1
                    self.current_roi = ROIVisual(new_id, pos)
                    self.drawing_roi = True
            self.update()

    def on_mouse_wheel(self, event):
        center = event.pos
        dz = event.delta[1]
        self.panzoom.zoom(np.exp(np.array([.1, .1]) * dz), center)
        #for ch in self.markers:
        #    ch._size=np.ones((len(ch.points))).astype(np.float32) * 2 * self.pixel_scale

    def on_resize(self, event):
        self.width, self.height = event.size
        gloo.set_viewport(0, 0, self.width, self.height)

    def on_draw(self, event):
        gloo.clear()
        for ch in self.markers:
            ch.draw(self.tr_sys)
        for roi in self.roi_visuals:
            roi.draw(self.tr_sys)
        if self.current_roi != None:
            self.current_roi.draw(self.tr_sys)
        