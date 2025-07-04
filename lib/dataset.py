
import re
import time

import numpy as np

class Dataset(list):
    def __init__(self, data, dtype=float):
        super().__init__(list(data))
        self.dtype = dtype
        self.data_range = range(0, len(data))
        self.meta = {}
        self.parse_metadata()
    
    def set_range(self, range):
        self.data_range = range

    def slice(self):
        return np.array(self)[self.data_range[0]:self.data_range[1]]
    
    def parse_metadata(self):
        matches = re.findall(r'(([a-zA-Z_0-9]+)=([0-9\.:A-Za-z]+)[\|]?)', str(self[0]))
        if matches:
            for match in matches:
                self.meta[match[1]] = self.parse_value(match[1], match[2])
            slice = np.array(self)[1:]
        else:
            slice = self 
        
        self.clear()
        self.extend(np.array(slice).astype(self.dtype))
                       
    def parse_value(self, key, value):
        if key == 'start_time':
            return time.localtime(float(value))
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value 

    
        