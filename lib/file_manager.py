from datetime import datetime
import glob
import os
import re

class FileManager():
    def __init__(self, base_path, prefix="LOG", extension="csv.gz"):
        self.base_path = base_path
        self.prefix = prefix
        self.extension = extension
    
    def get_folders(self):
        globs = glob.iglob(self.base_path + "/*", recursive=True)
        globs = filter(lambda path: os.path.isdir(path), list(globs))
        globs = map(lambda path: os.path.basename(path), list(globs))
        globs = list(globs)
        return globs

    def get_files(self, folder):
        all_logs = []
        for root, dirs, files in os.walk(self.base_path + "/" + folder):
            logs = list(filter(lambda file: re.match(rf"^{self.prefix}(\d{{5}})(.*?)\.{self.extension}$", file), files))
            if len(logs) > 0:
                logs.sort()
            logs = map(lambda file: (root + "/" + file).replace(self.base_path + "/", ""), logs)
            all_logs = all_logs + list(logs);
        return all_logs
    
    def format_log_name(self, log_path):
        lists = log_path.split("/")[1:]
        return ' > '.join(lists)
    
    def find_next_log_filename(self, postfix=""):
        max_index = 0
        today = datetime.now().strftime("%d.%m.%Y")
        folder_name = os.path.join(self.base_path, today, "JUPYTER")
        if not os.path.exists(folder_name):
            os.makedirs(folder_name, exist_ok=True)
        pattern = rf"{self.prefix}(\d{{5}})(.*?)\.{self.extension}"
        for fname in os.listdir(folder_name):
            match = re.match(pattern, fname)
            # print(f"Checking file: {fname}, pattern: {pattern}, match: {match}")
            if match:
                idx = int(match.group(1))
                if idx >= max_index:
                    max_index = idx + 1
        return os.path.join(folder_name, '{:s}{:05d}{:s}.{:s}'.format(str(self.prefix), max_index, str(postfix), self.extension))
