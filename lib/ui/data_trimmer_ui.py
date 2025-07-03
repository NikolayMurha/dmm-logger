from ipywidgets import interact
import ipywidgets as widgets
import numpy as np


from lib.dataset import Dataset
from lib.ui.data_plotter_ui import DataPlotterUi

class DataTrimmerUi():    
    def __init__(self, max_depth=None):
        self.max_depth = max_depth
        self.dataset = None
        self.callbacks = []
        self.current_data_range = None

    def on_complete(self, callback):
        self.callbacks.append(callback)

    def get_color(self, index):
        return self.color_cycle[index % len(self.color_cycle)]
    
    def display(self, dataset):
        # TODO: Винести завантаження данних за межі дата тримеру
        self.dataset = dataset

        interact(
            self.trim_data,
            level = widgets.fixed(0),
            data_range = widgets.fixed([0, len(self.dataset)]),
            next_data_range = widgets.IntRangeSlider(value=[0, len(self.dataset)], min=0, max=len(self.dataset), step=1, description='Вибірка', continuous_update=False, layout=widgets.Layout(width='100%'))
        )

    def trim_data(self, next_data_range, data_range=None, level=0):
        next_level = level + 1
        current_offset = 0
        if data_range is not None:
            current_data = self.dataset[data_range[0]:data_range[1]]
            current_offset = data_range[0]
        else:
            data_range = [0, len(self.dataset)]
            current_data = self.dataset  

        has_changes = (next_data_range[0] != data_range[0] or next_data_range[1] != data_range[1])

        if has_changes:
            current_title = f"Рівень приточнення {level}: "    
        else:
            current_title = f"Зріз для аналізу: "
        current_title += f"[{next_data_range[0]}:{next_data_range[1]}], Розмір: {next_data_range[1]-next_data_range[0]}" 
        
        dt = 1.0/ self.dataset.meta.get('sample_rate', 1.0)
        current_offset = current_offset * dt
        timestamps = current_offset + np.arange(len(current_data)) * dt

        DataPlotterUi(title=current_title, xlabel="Час, с", ylabel=self.dataset.meta.get('config', 'ADC Value')).display(current_data, 
                                                                                                                         offset=current_offset, 
                                                                                                                         vlines=[next_data_range[0]*dt, next_data_range[1]*dt], 
                                                                                                                         xvalues=timestamps)

        if has_changes and (self.max_depth is None or next_level <= self.max_depth):
            interact(
                self.trim_data,
                level = widgets.fixed(next_level),
                data_range = widgets.fixed(next_data_range),
                next_data_range = widgets.IntRangeSlider(value=[next_data_range[0], next_data_range[1]], min=next_data_range[0], max=next_data_range[1], step=1, description='Вибірка', continuous_update=False, layout=widgets.Layout(width='100%'))
            )
        else:
            self.current_data_range = next_data_range
            self.dataset.set_range(self.current_data_range)
                
            if len(self.callbacks) > 0:
                for callback in self.callbacks:
                    callback(self.dataset)
        
