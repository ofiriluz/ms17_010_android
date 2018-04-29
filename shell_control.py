# from kivy.uix.gridlayout import GridLayout
# from kivy.logger import Logger
import uuid
import threading
import datetime
import time
from abc import abstractmethod


class ShellControlJob:
    def __init__(self):
        pass

    @abstractmethod
    def execute_job(self, log_stream):
        pass

    @abstractmethod
    def is_job_running(self):
        pass

    @abstractmethod
    def reset_job(self):
        pass


class ShellControlStream:
    def __init__(self, stream_name, job, stream_notifier):
        self.msgs = []
        self.job = job
        self.stream_name = stream_name
        self.stream_job_runner = threading.Thread(target=self.__stream_thread)
        self.stream_job_killer = threading.Event()
        self.stream_notifier = stream_notifier
        self.stream_lock = threading.Lock()

    def get_stream_name(self):
        return self.stream_name

    def debug(self, data):
        self.__add_msg(data, 'DEBUG')

    def info(self, data):
        self.__add_msg(data, 'INFO')

    def warn(self, data):
        self.__add_msg(data, 'WARNING')

    def error(self, data):
        self.__add_msg(data, 'ERROR')

    def is_streaming(self):
        return self.__has_more_msgs()

    def end_stream(self):
        if not self.stream_job_runner.isAlive():
            return

        self.stream_job_killer.set()

    def start_stream(self):
        if self.stream_job_runner.isAlive():
            return

        self.stream_job_runner.start()

    def __stream_thread(self):
        while not self.stream_job_killer.is_set():
            time.sleep(0.25)
            if self.__has_more_msgs() and self.stream_notifier:
                msg = self.__read_next_msg()
                self.stream_notifier(self, msg, self.job)

    def __add_msg(self, msg, type):
        self.stream_lock.acquire()
        self.msgs.append({'msg': msg, 'type': type})
        self.stream_lock.release()

    def __read_next_msg(self):
        self.stream_lock.acquire()
        next_msg = self.msgs.pop(0)
        self.stream_lock.release()
        return next_msg

    def __has_more_msgs(self):
        return len(self.msgs) > 0

    def __clear_all_msgs(self):
        self.stream_lock.acquire()
        self.msgs = []
        self.stream_lock.release()


class ShellControl:
    def __init__(self, **kwargs):
        # Logger.info("Init the shell control")
        self.flow_commands = {}
        self.flow_command_jobs = {}
        self.flow_command_jobs_lock = threading.Lock()
        self.flow_cleaner_job = threading.Thread(target=self.__flow_job_cleaner_thread)
        self.flow_cleaner_exit_event = threading.Event()

    def __enter__(self):
        self.flow_cleaner_job.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flow_cleaner_exit_event.set()
        self.flow_cleaner_job.join()

    def __flow_job_stream_notifier(self, stream, msg, job):
        msg_data = msg['msg']
        msg_type = msg['type']

        # Only outputs for now
        print('[%s][%s][%s][%s]: %s' % (str(datetime.datetime.now()), job['job_name'], stream.get_stream_name(), msg_type, msg_data))

    def __flow_job_runner(self, job):
        # Create streams
        job_log_stream = ShellControlStream('DataStream', job, self.__flow_job_stream_notifier)
        job_log_stream.start_stream()

        # For now only executes the job
        job['command_flow_handler'].execute_job(job_log_stream)

        # Wait for stream to end
        while job_log_stream.is_streaming():
            time.sleep(0.25)

        job_log_stream.end_stream()

    def __flow_job_cleaner_thread(self):
        jobs_to_remove = []
        while not self.flow_cleaner_exit_event.is_set():
            time.sleep(0.25)
            for id in self.flow_command_jobs.keys():
                if not self.flow_command_jobs[id].isAlive():
                    jobs_to_remove.append(id)
            if len(jobs_to_remove) > 0:
                self.flow_command_jobs_lock.acquire()
                for id in jobs_to_remove:
                    del self.flow_command_jobs[id]
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

        if not raw_flow_command['command_flow_handler']:
            # Logger.error('Could not add shell flow command %s, no handler' % job_name)
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
                job_id = uuid.uuid4()
                flow_job = threading.Thread(target=self.__flow_job_runner, args=(flow_command,))
                flow_job.start()
                self.flow_command_jobs_lock.acquire()
                self.flow_command_jobs[job_id] = flow_job
                self.flow_command_jobs_lock.release()
                return job_id
        return None

    def wait_for_shell_job_to_end(self, job_id):
        if job_id in self.flow_command_jobs.keys():
            self.flow_command_jobs[job_id].join()

    def get_shell_flow_command(self, id):
        if id in self.flow_commands.keys():
            return self.flow_commands[id]
        return None
