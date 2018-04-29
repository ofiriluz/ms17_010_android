from shell_control import ShellControlJob


class TestCommandJob(ShellControlJob):
    def __init__(self):
        pass

    def execute_job(self, log_stream):
        log_stream.debug('AAA')
        log_stream.error('BBB')

    def is_job_running(self):
        return True


if __name__ == '__main__':
    from shell_control import ShellControl

    with ShellControl() as shell_control:
        id = shell_control.add_shell_flow_command('TestJob', 'Test', TestCommandJob(), True)
        job_id = shell_control.execute_shell_flow_commannd(id)
        shell_control.wait_for_shell_job_to_end(job_id)


