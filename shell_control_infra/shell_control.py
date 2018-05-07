import uuid
import threading
import datetime
import time
from kivy.logger import Logger
from shell_control_stream import ShellControlStream
from shell_control_job import ShellControlJob


class ShellControl:
    def __init__(self, allow_stdout_log=True):
        self.flow_commands = {}
        self.flow_command_jobs = {}
        self.flow_command_job_executors = {}
        self.flow_command_jobs_results = {}
        self.flow_command_jobs_lock = threading.Lock()
        self.flow_cleaner_job = threading.Thread(target=self.__flow_job_cleaner_thread)
        self.flow_cleaner_exit_event = threading.Event()
        self.flow_control_events_listeners = {}
        self.allow_stdout_log = allow_stdout_log

    def __enter__(self):
        self.flow_cleaner_job.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flow_cleaner_exit_event.set()
        self.flow_cleaner_job.join()

    def __on_event_notified(self, command_id, event_name, event_args):
        if command_id in self.flow_control_events_listeners.keys():
            if event_name in self.flow_control_events_listeners[command_id].keys():
                for listener in self.flow_control_events_listeners[command_id][event_name]:
                    listener(command_id, event_name, event_args)

    def __print_log_message(self, msg, type):
        # TODO
        print(msg)

    def __flow_job_stream_notifier(self, stream, msg, command_id, job_id):
        msg_data = msg['msg']
        msg_type = msg['type']

        # Only outputs for now
        formatted_msg = '[%s][%s][%s]: %s' % (str(datetime.datetime.now()), self.flow_commands[command_id]['command_title'], msg_type, msg_data)

        if self.allow_stdout_log:
            self.__print_log_message(formatted_msg, msg_type)

        # Send job message stream event
        self.__on_event_notified(command_id, 'job_stream_message', {'job_id': job_id,
                                                                   'raw_message': msg_data,
                                                                   'formatted_message': formatted_msg,
                                                                   'message_type': msg_type})

    def __flow_job_runner(self, command, job_id, args):
        # Create streams
        job_log_stream = ShellControlStream('DataStream', command, job_id, self.__flow_job_stream_notifier)
        job_log_stream.start_stream()

        # Send a start event
        self.__on_event_notified(command['command_id'], 'job_started', {'job_id': job_id})

        # For now only executes the job
        job_executor = command['command_flow_handler'](command['command_id'])
        job_executor.set_shell_listener(self.__on_event_notified)
        self.flow_command_job_executors[job_id] = job_executor

        job_result = job_executor.execute_job(args, job_log_stream)
        del self.flow_command_job_executors[job_id]
        # Wait for stream to end
        while job_log_stream.is_streaming():
            time.sleep(0.25)

        job_log_stream.end_stream()

        self.flow_command_jobs_results[job_id] = {'result': job_result, 'history': job_log_stream.get_stream_history()}

        # Send a finish event
        self.__on_event_notified(command['command_id'], 'job_finishied', {'job_id': job_id})

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

    def add_event_listener(self, command_id, event, listener):
        if not command_id in self.flow_control_events_listeners:
            self.flow_control_events_listeners[command_id] = {}
        if not event in self.flow_control_events_listeners[command_id]:
            self.flow_control_events_listeners[command_id][event] = [listener]
        else:
            self.flow_control_events_listeners[command_id][event].append(listener)

    def add_shell_flow_command(self, command_title='FlowCommand', command='Flow', command_handler_class=None, is_async=False):
        # Check class inheritance

        raw_flow_command = {
            'command_title': command_title,
            'command': command,
            'command_flow_handler': command_handler_class,
            'is_async': is_async,
            'command_id': uuid.uuid4()
        }

        if not raw_flow_command['command_flow_handler']:
            # Logger.error('Could not add shell flow command %s, no handler' % job_name)
            return None

        self.flow_commands[raw_flow_command['command_id']] = raw_flow_command

        return raw_flow_command['command_id']

    def get_shell_flow_commands(self):
        return self.flow_commands

    def remove_shell_flow_command(self, id):
        if id in self.flow_commands.keys():
            del self.flow_commands[id]

    def execute_shell_flow_commannd(self, id, flow_command_args=None):
        if id in self.flow_commands.keys():
            flow_command = self.flow_commands[id]
            job_id = uuid.uuid4()
            if flow_command['is_async']:
                flow_job = threading.Thread(target=self.__flow_job_runner, args=(flow_command, job_id, flow_command_args,))
                flow_job.start()
                self.flow_command_jobs_lock.acquire()
                self.flow_command_jobs[job_id] = flow_job
                self.flow_command_jobs_lock.release()
                return job_id
            else:
                self.__flow_job_runner(flow_command, job_id, flow_command_args)
        return None

    def send_flow_event(self, job_id, event):
        Logger.info(str(self.flow_command_job_executors))
        Logger.info(job_id)
        Logger.info(event)
        if job_id in self.flow_command_job_executors.keys():
            Logger.info('IN')
            job = self.flow_command_job_executors[job_id]
            job.execute_job_event(event)

    def wait_for_shell_job_to_end(self, job_id):
        if job_id in self.flow_command_jobs.keys():
            self.flow_command_jobs[job_id].join()

    def get_shell_flow_command(self, id):
        if id in self.flow_commands.keys():
            return self.flow_commands[id]
        return None
