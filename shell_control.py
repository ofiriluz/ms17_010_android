from kivy.uix.gridlayout import GridLayout
from kivy.logger import Logger
import uuid
import threading
from abc import ABCMeta, abstractmethod


class ShellControlStream:
    def __init__(self):
        pass

    def debug(self, data):
        pass

    def info(self, data):
        pass

    def warn(self, data):
        pass

    def error(self, data):
        pass

    def __read_next_msg(self):
        pass

    def __has_more_msgs(self):
        pass

    def __clear_all_msgs(self):
        pass


class ShellControlJob:
    def __init__(self):
        pass

    @abstractmethod
    def execute_job(self, stdout_stream, stderr_stream):
        pass

    @abstractmethod
    def is_job_running(self):
        pass

    @abstractmethod
    def reset_job(self):
        pass

class ShellControl:
    def __init__(self, **kwargs):
        Logger.info("Init the shell control")
        self.flow_commands = {}
        self.flow_command_jobs = []
        self.flow_command_jobs_lock = threading.Lock()
        self.flow_cleaner_job = threading.Thread(target=self.__flow_job_cleaner_thread)
        self.flow_cleaner_exit_event = threading.Event()
        self.flow_cleaner_job.start()

    def __flow_job_stream_runner(self, job, stream):
        pass

    def __flow_job_runner(self, job):


    def __flow_job_cleaner_thread(self):
        jobs_to_remove = []
        while self.flow_cleaner_exit_event.wait(1):
            for index, job in enumerate(self.flow_command_jobs):
                if not job.isAlive:
                    jobs_to_remove.append(job)
            if len(jobs_to_remove) > 0:
                self.flow_command_jobs_lock.acquire()
                self.flow_command_jobs = [t for t in self.flow_command_jobs if t not in jobs_to_remove]
                self.flow_command_jobs_lock.release()
                jobs_to_remove = []

    def add_shell_flow_command(self, job_name='FlowCommand', command_name='Flow', command_handler=None, is_async=False):
        raw_flow_command = {
            'job_name': job_name,
            'command_name': command_name,
            'command_flow_handler': command_handler,
            'is_async': is_async
        }

        generated_command_uuid = uuid.uuid4()

        if not raw_flow_command['command_flow_handler':]:
            Logger.error('Could not add shell flow command %s, no handler' % job_name)
            return None

        self.flow_commands[generated_command_uuid] = raw_flow_command

        return generated_command_uuid

    def get_shell_flow_commands(self):
        return self.flow_commands

    def remove_shell_flow_command(self, id):
        if id in self.flow_commands.keys():
            del self.flow_commands[id]

    def execute_shell_flow_commannd(self, id):
        if id in self.flow_commands.keys():
            flow_command = self.flow_commands[id]
            if flow_command['is_async']:
                flow_job = threading.Thread(target=self.__flow_job_runner, args=(flow_command,))
                flow_job.start()
                self.flow_command_jobs_lock.acquire()
                self.flow_command_jobs.append(flow_job)
                self.flow_command_jobs_lock.release()

    def get_shell_flow_command(self, id):
        if id in self.flow_commands.keys():
            return self.flow_commands[id]
        return None