

import os
import pickle


class GobalState:
    def __init__(self, state_file = 'state.pkl', default={}):
        self.state_file = state_file
        self.state = default
        self.loaded = False
    
    def __del__(self):
        if self.loaded:
            self.save()
            
    def load(self):
        if not os.path.exists(self.state_file):
            self.save()
        pkl_file = open(self.state_file, "rb")
        self.state = pickle.load(pkl_file)
        self.loaded = True
        pkl_file.close()
    
    def save(self):
        pkl_file = open(self.state_file, "wb")
        pickle.dump(self.state, pkl_file)
        pkl_file.close()
    
    def get_or_set(self, name, default=None):
        value = self.get(name)
        if value:
            return value
        return self.set(name, default)
        
    def get(self, name, default=None):
        if not self.loaded:
            self.load()
        return self.state.get(name, default)

    def unset(self, name):
        if not self.loaded:
            self.load()
        if name in self.state:
            del self.state[name]

    def set(self, name, value):
        if not self.loaded:
            self.load()
        self.state[name] = value
        return value 
