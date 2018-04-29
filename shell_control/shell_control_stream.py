import time


class ShellControlStream:
    def __init__(self, stream_name, job, stream_notifier):
        self.msgs = []
        self.msgs_history = []
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

    def get_stream_history(self):
        return self.msgs_history

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
        self.msgs_history.append(next_msg)
        self.stream_lock.release()
        return next_msg

    def __has_more_msgs(self):
        return len(self.msgs) > 0

    def __clear_all_msgs(self):
        self.stream_lock.acquire()
        self.msgs = []
        self.stream_lock.release()