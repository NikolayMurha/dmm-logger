from functools import partial
import threading
from IPython.display import display
import ipywidgets as widgets
from lib.dmm_log_recorder import DmmLogRecorder

class DmmLogRecorderUi():
    def __init__(self, global_state, base_path):
        self.global_state = global_state
        self.base_path = base_path
        self.ip_address = None
        self.plc = None
        self.duration = None
        self.ip_address = None
        self.mes_options = None

    def display(self):
        self.ip_address =  widgets.Text(description="IP", value=self.global_state.get('ip_address', "192.168.1.202"));
        self.ip_address.observe(lambda change: self.global_state.set('ip_address', self.ip_address.value))

        self.mes_options =  widgets.Dropdown(
            options=[
                ('DC Voltage', 'VOLT:DC'),
                ('DC Current', 'CURR:DC'),
                ('AC Voltage', 'VOLT:AC'),
                ('AC Current', 'CURR:AC'),
            ],
            value=self.global_state.get('self.mes_options', 'VOLT:DC'),
            description='Параметр:',
        )
        self.mes_options.observe(lambda change: self.global_state.set('self.mes_options', self.mes_options.value))

        self.plc =  widgets.Dropdown(
            options=[
                ('0.006 PLC (MAX)', '0.006'),
                ('0.02 PLC', '0.02'),
                ('0.06 PLC', '0.06'),
                ('0.2 PLC', '0.2'),
                ('1 PLC (DEF)', '1'),
                ('2 PLC', '2'),
                ('10 PLC', '10'),
                ('100 PLC (MIN)', '100'),
            ],
            value = self.global_state.get('plc', '1'),
            description='PLC:',
        )
        self.plc.observe(lambda change: self.global_state.set('plc', self.plc.value))
        
        self.chunk_size =  widgets.Dropdown(
            options=[
                ('1000', '1000'),
                ('5000', '5000'),
                ('10000', '10000'),
                ('20000', '20000'),
                ('50000', '50000'),
            ],
            value = self.global_state.get('chunk_size', '5000'),
            description='Буфер:',
        )
        self.chunk_size.observe(lambda change: self.global_state.set('chunk_size', self.chunk_size.value))
        self.duration =  widgets.Dropdown(
            options=[
                ('5s', '5'),
                ('10s', '10'),
                ('30s', '30'),
                ('60s', '60'),
                ('90s', '90s'),
                ('180s', '180s'),
                ('1h', '3600'),
                ('2h', '7200'),
                ('3h', '10800'),
                ('6h', '21600'),
                ('12h', '43200'),
                ('24h', '86400'),
            ],
            value = self.global_state.get('duration', '30'), 
            description='Час запису:',
        )
        self.duration.observe(lambda change: self.global_state.set('duration', self.duration.value))
        out = widgets.interactive_output(self.show_measurement_range, {'mes_option': self.mes_options})
        ui = widgets.VBox([
            widgets.HBox([self.ip_address, self.duration, self.chunk_size]),
            widgets.HBox([self.mes_options, self.plc]),
        ])
        display(ui, out) 

    def show_measurement_range(self, mes_option= None):
        # store selected state
        if mes_option == 'VOLT:DC' or mes_option == 'VOLT:AC':
            self.mes_range =  widgets.Dropdown(
                options=[
                    ('AUTO', 'AUTO'),
                    ('100 mV', '0.1'),
                    ('1 V', '1'),
                    ('10 V', '10'),
                    ('100 V', '100'),
                    ('1000 V (MAX)', '1000'),
                ],
                value = self.global_state.get('mes:range:'+mes_option, '0.001'),
                description='Діапазон:',
            )
        elif mes_option == 'CURR:DC' or mes_option == 'CURR:AC':
            self.mes_range =  widgets.Dropdown(
                options=[
                    ('AUTO', 'AUTO'),
                    ('100 µA', '0.0001'),
                    ('1 mA', '0.001'),
                    ('10 mA', '0.01'),
                    ('100 mA', '0.1'),
                    ('1 A', '1'),
                    ('3 A (MAX)', '3'),
                ],
                value = self.global_state.get('mes:range:'+mes_option, '0.001'),
                description='Діапазон:',
            )
        
        self.mes_range.observe(lambda change: self.global_state.set('mes:range:'+mes_option, self.mes_range.value))
        
        button = widgets.Button(description="Start")
        button.on_click(partial(self.button_handler, self))
        ui = widgets.HBox([self.mes_range, button])
        display(ui)

    def button_handler(self, *args):
        self.start_record_log(mes_options=self.mes_options.value, 
                              plc=float(self.plc.value), 
                              range=self.mes_range.value, 
                              duration=int(self.duration.value), 
                              chunk_size=int(self.chunk_size.value), 
                              ip_address=self.ip_address.value)

    def start_record_log(self, mes_options, plc, range, duration, chunk_size, ip_address):
        stop_button = widgets.Button(description="Stop")
        progress = widgets.IntProgress(
            value=0,
            min=0,
            max=duration,
            description='Запис:',
            bar_style='success', # 'success', 'info', 'warning', 'danger' or ''
            style={'bar_color': 'maroon'},
            orientation='horizontal'
        )
        log_recorder = DmmLogRecorder(self.base_path, ip=ip_address)
        thread = threading.Thread(target=log_recorder.start, args=(mes_options, plc, range, duration, chunk_size, progress))
        stop_button.on_click(log_recorder.stop)
        display(widgets.HBox([progress, stop_button]))
        thread.start()
