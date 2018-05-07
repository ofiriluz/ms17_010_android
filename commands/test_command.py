from shell_control_infra.shell_control_job import ShellControlJob
import sys


class TestCommandJob(ShellControlJob):
    def __init__(self, command_id):
        super(TestCommandJob, self).__init__(command_id)

    def execute_job(self, command_args, log_stream):
        log_stream.debug('AAA')
        log_stream.error('BBB')

    def is_job_running(self):
        return True

    def cancel_job(self):
        pass


if __name__ == '__main__':
    from shell_control_infra.shell_control import ShellControl

    with ShellControl() as shell_control:
        command_id = shell_control.add_shell_flow_command('TestJob', 'Test', TestCommandJob, True)
        shell_control.add_event_listener(command_id, 'job_stream_message', lambda command_id, event, args: sys.stdout.write(str(args) + '\n'))
        job_id = shell_control.execute_shell_flow_commannd(command_id)
        shell_control.wait_for_shell_job_to_end(job_id)


