from datetime import datetime
import os
import re
import time
from IPython.display import display
import numpy as np
import gzip
import pyvisa
from lib.file_manager import FileManager

class DmmLogRecorder():
    def __init__(self, base_path, ip):
        self.base_path = base_path
        self.ip = ip
        self.dmm = None
        self.running = False
        self._csv_file = None
        
    def __del__(self):
       self.close_csv_file()
 
    def play_sound(self):
        if os.path.exists("/System/Library/Sounds/Glass.aiff"):
            os.system("afplay /System/Library/Sounds/Glass.aiff")

    def close_csv_file(self):
        if self._csv_file:
            self._csv_file.close()
            self._csv_file = None

    def open_csv_file(self, prefix="", postfix=""):
        if not self._csv_file:
            file_manager = FileManager(self.base_path, prefix=prefix, extension="csv.gz")
            filename = file_manager.find_next_log_filename(postfix)
            display("Create CSV file: " + filename)
            self._csv_file = gzip.open(filename, 'wt')

    def write_csv(self, row):
        if not self._csv_file:
            self.open_csv_file()
            
        for line in row:          
            self._csv_file.write(f"{line}\r\n")
  
    def find_next_log_filename(self, postfix="", prefix="LOG"):
        max_index = 0
        today = datetime.now().strftime("%d.%m.%Y")
        folder_name = os.path.join(self.base_path, today, "JUPYTER")
        if not os.path.exists(folder_name):
            os.makedirs(folder_name, exist_ok=True)
        pattern = rf"{prefix}(\d{{5}})(.*?)\.csv"
        for fname in os.listdir(folder_name):
            match = re.match(pattern, fname)
            print(f"Checking file: {fname}, pattern: {pattern}, match: {match}")
            if match:
                idx = int(match.group(1))
                if idx >= max_index:
                    max_index = idx + 1
        return os.path.join(folder_name, '{:s}{:05d}{:s}.csv'.format(str(prefix), max_index, str(postfix)))
    
    # https://www.testunlimited.com/pdf/an/5990-3515en.pdf
    # 0.006 PLC | 6.0 ppm x Range | MAX  (for 34410A)
    # 0.02 PLC | 3.0 ppm x Range
    # 0.06 PLC | 1.5 ppm x Range |
    # 0.2 PLC | 0.7 ppm x Range |
    # 1 PLC (default) | 0.3 ppm x Range | DEF
    # 2 PLC | 0.2 ppm x Range |
    # 10 PLC | 0.1 ppm x Range |
    # 100 PLC | 0.03 ppm x Range | MIN

    def start(self, config, plc, range, duration, chunk_size, progress=None):
        rm = pyvisa.ResourceManager()
        t_start = time.time()
        t_start_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_start))
        try:
            
            self.open_csv_file(prefix="DMM", postfix=f"_{config.replace(":", '_')}_{duration}s") 
            self.dmm = rm.open_resource(f"TCPIP::{self.ip}::INSTR")
            self.dmm.timeout = 60000
            display(f"Connected: {self.ip}, {self.dmm.query("*IDN?")}")
            self.dmm.write("*RST")
            self.dmm.write("*CLS")
            # self.dmm.write("DISP OFF")
            self.dmm.write(f"CONF:{config} {range}")
                  
            self.dmm.write(f"SENS:{config}:RES MAX")
            if range == "AUTO":
                self.dmm.write(f"SENS:{config}:RANGE:AUTO ON")
            else:
                self.dmm.write(f"SENS:{config}:RANGE:AUTO OFF")
                self.dmm.write(f"SENS:{config}:RANGE {range}")

            self.dmm.write(f"SENS:{config}:ZERO:AUTO OFF")
            self.dmm.write(f"SENS:{config}:APER:ENAB OFF")
            self.dmm.write(f"SENS:{config}:NPLC {plc}") # MIN 0.006
            self.dmm.write(f"DATA:POIN:EVEN:THR {chunk_size}")
            self.dmm.write(f"SAMP:COUN {chunk_size}")
            self.dmm.write(f"SAMP:SOUR IMM")
            self.dmm.write(f"TRIG:SOUR BUS")
            self.dmm.write(f"TRIG:DEL 0")
            self.dmm.write(f"TRIG:COUN 1")
            self.dmm.write(f"FORM:DATA REAL,32")
            self.running = True
            header_ready = False
            start_time = time.time()
            total_lines = 0
            total_chunks = 0
            total_sample_rate = 0
            time.sleep(0.5)
            display(f"Waiting for reading. It may take a while...")
            while self.running:
                chunk_measurement_start_time = time.time()
                self.dmm.write("INIT")
                self.dmm.write("*TRG")
                self.dmm.query("*OPC?")
                chunk_measurement_time = time.time() - chunk_measurement_start_time
                sample_rate = round(chunk_size/chunk_measurement_time)
                if not header_ready:
                    header_ready = True
                    meta = f"start_time={chunk_measurement_start_time}|config={config}|plc={plc}|range={range}|duration={duration}|chunk_size={chunk_size}|sample_rate={sample_rate}"
                    self.write_csv([meta])
                    display(f"Speed: {sample_rate} samples/sec")

                row = self.dmm.query_binary_values("R?", datatype='f', is_big_endian=True)
                row = [f"{value:.8f}" for value in row if value is not None]
                self.write_csv(row)
                total_lines += len(row)
                total_chunks += 1
                total_sample_rate += sample_rate
                
                if progress:
                    progress.max = duration
                    progress.value = int(time.time() - start_time)
                
                if time.time() - start_time >= duration:
                    display("Time is up, stopping...")
                    display(f"[{config}] Total lines written: {total_lines}, plc: {plc}, range: {range} duration: {time.time() - start_time:.2f} sec, chunk_size: {chunk_size}, chunks: {total_chunks}, sample rate: {total_sample_rate/total_chunks} records/sec")
                    self.running = False
        finally:
            if self.dmm:
                self.dmm.write("DISP ON")
                self.dmm.write("*RST")
                self.dmm = None
            self.close_csv_file()
            self.running = False    
        
        self.play_sound()
    def stop(self, btn=None):
        self.running = False 
        