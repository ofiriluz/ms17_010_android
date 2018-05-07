from abc import abstractmethod, ABCMeta


class ShellControlJob(object):
    __metaclass__ = ABCMeta

    def __init__(self, command_id):
        self.shell_listener = None
        self.command_id = command_id

    def notify_event(self, event_name, event_data):
        if self.shell_listener:
            self.shell_listener(self.command_id, event_name, event_data)

    def set_shell_listener(self, listener):
        self.shell_listener = listener

    def get_command_id(self):
        return self.command_id

    @abstractmethod
    def execute_job(self, command_args, log_stream):
        pass

    @abstractmethod
    def execute_job_event(self, event):
        pass

    @abstractmethod
    def is_job_running(self):
        pass

    @abstractmethod
    def cancel_job(self):
        pass

