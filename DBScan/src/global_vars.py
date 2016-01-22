# -*- coding: utf-8 -*-
"""
Created on Tue Jul 01 11:28:38 2014

@author: Kyle Ellefsen
"""

import sys
if sys.version_info.major==2:
    import cPickle as pickle # pickle serializes python objects so they can be saved persistantly.  It converts a python object into a savable data structure
else:
    import pickle

class Settings:
    INITIAL = {'last_dir': '', 'epsilon': 30,'min_neighbors': 4,'min_density': 5}
    def __init__(self):
        self.config_file='config.p'
        try:
            self.d=pickle.load(open(self.config_file, "rb" ))
        except (IOError, ValueError, EOFError):
            self.d=dict()
            self.d['last_dir']='' #this is the name of the most recently opened file
            self.d['epsilon']=30 
            self.d['min_neighbors']=4
            self.d['min_density'] = 5
        self.d['show_windows'] = True
    def __getitem__(self, item):
        try:
            self.d[item]
        except KeyError:
            self.d[item] = Settings.INITIAL[item]
        return self.d[item]
    def __setitem__(self,key,item):
        self.d[key]=item
        self.save()
    def save(self):
        '''save to a config file.'''
        pickle.dump(self.d, open( self.config_file, "wb" ))