from shell_control_infra.shell_control_job import ShellControlJob
from ms1710.subnet_checker import MS1710SubnetChecker


class MS1710SubnetScannerCommand(ShellControlJob):
    def __init__(self, command_id):
        super(MS1710SubnetScannerCommand, self).__init__(command_id)
        self.subnet_checker = None
        self.is_scanner_running = False
        self.log_stream = None

    def on_scan_started(self):
        self.notify_event('scan_started', {})

    def on_scan_finished(self):
        self.notify_event('scan_finished', {'ip_list': self.subnet_checker.get_scanned_targets()})

    def on_scan_update(self):
        self.log_stream.debug("Update")
        self.log_stream.debug(str(self.subnet_checker.get_scanned_targets()))
        self.notify_event('scan_update', {'ip_list': self.subnet_checker.get_scanned_targets()})

    def execute_job(self, command_args, log_stream):
        if not command_args or not all(elem in ['subnet', 'mask', 'nthreads'] for elem in command_args.keys()):
            log_stream.error('Invalid args for job')
            return

        self.log_stream = log_stream
        subnet = command_args['subnet']
        mask = command_args['mask']
        nthreads = command_args['nthreads']

        self.subnet_checker = MS1710SubnetChecker(subnet=subnet, nthreads=nthreads, mask=mask,
                                                  start_sub=self.on_scan_started,
                                                  update_sub=self.on_scan_update,
                                                  finish_sub=self.on_scan_finished)
        log_stream.debug("Starting Scan")
        self.subnet_checker.start_scan()
        self.is_scanner_running = True
        log_stream.debug("Waiting for scan to end")
        self.subnet_checker.wait()
        log_stream.debug("Scan Ended")

    def execute_job_event(self, event):
        pass

    def is_job_running(self):
        return self.is_scanner_running

    def cancel_job(self):
        if self.subnet_checker:
            self.subnet_checker.stop_scan()


if __name__ == '__main__':
    from shell_control_infra.shell_control import ShellControl
    from utils.ip_utils import get_computer_ip

    with ShellControl() as shell_control:
        id = shell_control.add_shell_flow_command('MS1710Scan', 'MS1710Scan', MS1710SubnetScannerCommand, False)
        shell_control.execute_shell_flow_commannd(id, {'subnet': get_computer_ip(), 'mask': 16, 'nthreads': 10})
        # shell_control_infra.wait_for_shell_job_to_end(job_id)
