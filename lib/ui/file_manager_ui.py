import os
from IPython.display import display
from ipywidgets import interact
import ipywidgets as widgets

class FileManagerUi():
    def __init__(self, global_state, file_manager):
        self.global_state = global_state
        self.file_manager = file_manager
        self._callback = None

    def on_select(self, callback):
        self._callback = callback

    def display(self):    
        folders = self.file_manager.get_folders()
        file_selector = widgets.Dropdown(
            options=folders,
            value=self.global_state.get_or_set('selected_folder', folders[-1]),
            description='Дата:',
            disabled=False,
        )
        interact(self.show_file_selector, folder=file_selector)
    
    def format_file_name(self, log_path):
        lists = log_path.split("/")[1:]
        return ' > '.join(lists)
    
    def show_file_selector(self, folder):
        files = self.file_manager.get_files(folder)
        
        if len(files) == 0:
            display("No files found in folder: " + folder)
            return
        
        self.global_state.set('selected_folder', folder)
        selected_log_file = self.global_state.get_or_set('selected_log_file', files[-1])
        
        if not os.path.exists(selected_log_file):
            selected_log_file = files[-1]
            self.global_state.set("selected_log_file", selected_log_file)

        if (len(files) > 0):
            files = [(self.format_file_name(log), log) for log in files]
            files_selector = widgets.Dropdown(
                options=files,
                # value=selected_log_file,
                description='File:',
                disabled=False,
                # layout=widgets.Layout(width='98%')
            )
            interact(self.load_selected_file, selected_folder=widgets.fixed(str(folder)), selected_file=files_selector)

    def load_selected_file(self, selected_folder, selected_file):
        self.selected_file = selected_file
        self.selected_folder = selected_folder
        if self._callback:
            self._callback(self.file_manager.base_path + "/" + selected_file)