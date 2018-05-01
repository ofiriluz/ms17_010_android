from abc import abstractmethod


class ShellControlJob:
    def __init__(self):
        self.shell_listener = None

    def notify_event(self, event_name, event_data):
        if self.shell_listener:
            self.shell_listener(event_name, event_data)

    def set_shell_listener(self, listener):
        self.shell_listener = list

    @abstractmethod
    def execute_job(self, command_args, log_stream):
        pass

    @abstractmethod
    def is_job_running(self):
        pass

    @abstractmethod
    def cancel_job(self):
        pass

