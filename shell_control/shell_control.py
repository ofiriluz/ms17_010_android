import uuid
import threading
import datetime
import time
from shell_control_stream import ShellControlStream
from shell_control_job import ShellControlJob


class ShellControl:
    def __init__(self):
        self.flow_commands = {}
        self.flow_command_jobs = {}
        self.flow_command_jobs_results = {}
        self.flow_command_jobs_lock = threading.Lock()
        self.flow_cleaner_job = threading.Thread(target=self.__flow_job_cleaner_thread)
        self.flow_cleaner_exit_event = threading.Event()
        self.flow_control_events_listeners = {}

    def __enter__(self):
        self.flow_cleaner_job.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flow_cleaner_exit_event.set()
        self.flow_cleaner_job.join()

    def __on_event_notified(self, event_name, event_args):
        if event_name in self.flow_control_events_listeners.keys():
            for listener in self.flow_control_events_listeners[event_name]:
                listener(event_name, event_args)

    def __flow_job_stream_notifier(self, stream, msg, job):
        msg_data = msg['msg']
        msg_type = msg['type']

        # Only outputs for now
        formatted_msg = '[%s][%s][%s][%s]: %s' % (str(datetime.datetime.now()), job['job_name'], stream.get_stream_name(), msg_type, msg_data)
        # print('[%s][%s][%s][%s]: %s' % (str(datetime.datetime.now()), job['job_name'], stream.get_stream_name(), msg_type, msg_data))

        # Send job message stream event
        self.__on_event_notified('job_stream_message',{'job_id': job['job_id'],
                                                       'raw_message': msg,
                                                       'formatted_message': formatted_msg,
                                                       'message_type': msg_type})

    def __flow_job_runner(self, job_id, job, args):
        # Create streams
        job_log_stream = ShellControlStream('DataStream', job, self.__flow_job_stream_notifier)
        job_log_stream.start_stream()

        # Send a start event
        self.__on_event_notified('job_started', {'job_id': job_id})

        # For now only executes the job
        job_result = job['command_flow_handler'].execute_job(args, job_log_stream)

        # Wait for stream to end
        while job_log_stream.is_streaming():
            time.sleep(0.25)

        job_log_stream.end_stream()

        self.flow_command_jobs_results[job_id] = {'result': job_result, 'history': job_log_stream.get_stream_history()}

        # Send a finish event
        self.__on_event_notified('job_finishied', {'job_id': job_id})

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

    def add_event_listener(self, event, listener):
        if not event in self.flow_control_events_listeners:
            self.flow_control_events_listeners[event] = [listener]
        else:
            self.flow_control_events_listeners.append(listener)

    def add_shell_flow_command(self, job_name='FlowCommand', command_name='Flow', command_handler=None, is_async=False):
        raw_flow_command = {
            'job_name': job_name,
            'command_name': command_name,
            'command_flow_handler': command_handler,
            'is_async': is_async,
            'job_id': uuid.uuid4()
        }

        if not raw_flow_command['command_flow_handler']:
            # Logger.error('Could not add shell flow command %s, no handler' % job_name)
            return None

        raw_flow_command['command_flow_handler'].set_shell_listener(self.__on_event_notified)

        self.flow_commands[raw_flow_command['job_id']] = raw_flow_command

        return generated_command_uuid

    def get_shell_flow_commands(self):
        return self.flow_commands

    def remove_shell_flow_command(self, id):
        if id in self.flow_commands.keys():
            del self.flow_commands[id]

    def execute_shell_flow_commannd(self, id, flow_command_args):
        if id in self.flow_commands.keys():
            flow_command = self.flow_commands[id]
            if flow_command['is_async']:
                job_id = uuid.uuid4()
                flow_job = threading.Thread(target=self.__flow_job_runner, args=(id, flow_command, flow_command_args,))
                flow_job.start()
                self.flow_command_jobs_lock.acquire()
                self.flow_command_jobs[job_id] =  flow_job
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
