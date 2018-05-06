from shell_control.shell_control_job import ShellControlJob
import sys


class TestCommandJob(ShellControlJob):
    def __init__(self):
        pass

    def execute_job(self, command_args, log_stream):
        log_stream.debug('AAA')
        log_stream.error('BBB')

    def is_job_running(self):
        return True

    def cancel_job(self):
        pass


if __name__ == '__main__':
    from shell_control.shell_control import ShellControl

    with ShellControl() as shell_control:
        shell_control.add_event_listener('job_stream_message', lambda event, args: sys.stdout.write(str(args) + '\n'))
        id = shell_control.add_shell_flow_command('TestJob', 'Test', TestCommandJob(), True)
        job_id = shell_control.execute_shell_flow_commannd(id)
        shell_control.wait_for_shell_job_to_end(job_id)


