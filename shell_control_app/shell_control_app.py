from shell_control import ShellControl
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from widgets.scrollable_label import ScrollableLabel
from kivy.uix.textinput import TextInput
from kivy.logger import Logger
from ms1710_scan_shell_command import MS1710SubnetScannerCommand
from ms1710_reverse_shell_command import MS1710ReverseShellCommand
from ip_utils import get_computer_ip


class ShellControlLayout(GridLayout):
    def __init__(self, **kwargs):
        self.shell_control = ShellControl()
        self.scanner_id = self.shell_control.add_shell_flow_command('MS1710Scanner', 'ms1710_scan', MS1710SubnetScannerCommand, True)
        self.revere_shell_id = self.shell_control.add_shell_flow_command('MS1710ReverseShell', 'ms1710_reverse_shell', MS1710ReverseShellCommand, True)

        self.shell_control.add_event_listener(self.scanner_id, 'scan_started', self.on_scan_started_event)
        self.shell_control.add_event_listener(self.scanner_id, 'scan_update', self.on_scan_update_event)
        self.shell_control.add_event_listener(self.scanner_id, 'scan_finished', self.on_scan_finished_event)

        self.command_output_label = ScrollableLabel(size_hint_x=1.0, size_hint_y=0.8)
        self.command_input = TextInput(hint_text='Write cmd here', size_hint_x=0.7, size_hint_y=0.2)
        self.send_command_button = Button(size_hint_x=0.3, size_hint_y=0.2, text="S")
        self.command_input_grid = GridLayout(size_hint_x=1.0, size_hint_y=0.2, cols=2)
        self.command_input_grid.add_widget(self.command_input)
        self.command_input_grid.add_widget(self.send_command_button)

        kwargs['cols'] = 1
        kwargs['size_hint'] = (1.0, 1.0)
        super(ShellControlLayout, self).__init__(**kwargs)

        self.add_widget(self.command_output_label)
        self.add_widget(self.command_input_grid)

    def on_command_execute_button_pressed(self, instance):
        pass
        # command_args = str(self.ip_list.list_adapter.selection[0].text).split(' ')
        # if len(command_args) > 0:
        #     command_name = command_args[0]
        #     if command_name == 'ms1710_scan':
        #         Logger.fatal("Starting the scanner")
        #         my_ip = get_computer_ip()
        #         if not my_ip:
        #             Logger.fatal('Cannot init scanner, failed to find IP, aborting')
        #             return
        #         self.shell_control.execute_shell_flow_commannd(self.scanner_id, {'subnet': my_ip, 'nthreads': 20})
        #     elif command_name == 'ms1710_reverse_shell':
        #         ip = command_args[1]
        #         self.shell_control.execute_shell_flow_commannd(self.revere_shell_id,
        #                                                        {'target': ip, 'listening_port': 5555})

    def on_scan_started_event(self, command_id, event, event_args):
        Logger.info('Scanner Start CB')

    def on_scan_finished_event(self, command_id, event, event_args):
        Logger.info('Scanner Finish CB')

    def on_scan_update_event(self, command_id, event, event_args):
        Logger.info('Scanner Update CB')


class ShellControlApp(App):
    def build(self):
        layout = ShellControlLayout()
        return layout
