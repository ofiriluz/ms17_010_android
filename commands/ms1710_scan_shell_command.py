from shell_control.shell_control_job import ShellControlJob
from ms1710.subnet_checker import MS1710SubnetChecker


class MS1710SubnetScannerCommand(ShellControlJob):
    def __init__(self):
        self.subnet_checker = None
        self.is_scanner_running = False

    def on_scan_started(self):
        self.notify_event('scan_started', {})

    def on_scan_finished(self):
        self.notify_event('scan_finished', {'ip_list': self.subnet_checker.get_scanned_targets()})

    def on_scan_update(self):
        self.notify_event('scan_update', {'ip_list': self.subnet_checker.get_scanned_targets()})

    def execute_job(self, command_args, log_stream):
        # Acquire args for the checker, NOT safe
        subnet = command_args['subnet']
        nthreads = command_args['nthreads']

        self.subnet_checker = MS1710SubnetChecker(subnet=subnet, nthreads=nthreads,
                                                  start_sub=self.on_scan_started,
                                                  update_sub=self.on_scan_update,
                                                  finish_sub=self.on_scan_finished)
        self.subnet_checker.start_scan()
        self.is_scanner_running = True
        self.subnet_checker.wait()

    def is_job_running(self):
        return self.is_scanner_running

    def cancel_job(self):
        if self.subnet_checker:
            self.subnet_checker.stop_scan()
