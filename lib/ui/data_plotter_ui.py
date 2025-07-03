import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

class DataPlotterUi:
    def __init__(self, title="Графік значень з CSV", xlabel="Час, с", ylabel=""):
        self.title = title
        self.xlabel = xlabel
        self.ylabel= ylabel
        self.color_cycle = list(mcolors.TABLEAU_COLORS.values())
        
    def get_color(self, index):
        return self.color_cycle[index % len(self.color_cycle)]
    
    def display(self, data, offset = 0, vlines = [], xvalues = []):
        data = np.array(data)
        if len(xvalues) == 0:
            xvalues = np.arange(offset, offset + len(data)) 

        plt.figure(figsize=(12, 2.5))
        
        for idx, vline in enumerate(vlines):
            if vline > offset and vline < xvalues[-1]:
                plt.axvline(x = vline, color = self.get_color(idx+1), linestyle = '--', label = f'Відмітка: {vline}')

        plt.plot(xvalues, data, marker = '.', linestyle = '-', linewidth = 1)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        plt.grid(True)
        plt.tight_layout()
        plt.show()