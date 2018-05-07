import socket
import sys
import threading
from collections import deque
from kivy.logger import Logger
import time


class MS1710Listener:
    def __init__(self, host='', port=3000, data_callback=None):
        self.host = host
        self.port = port
        self.is_listener_running = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_thread = threading.Thread(target=self.__listener_thread)
        self.commands_thread = threading.Thread(target=self.__commands_thread)
        self.conn = None
        self.addr = None
        self.data_callback = data_callback
        self.commands_queue = deque()

    def __has_commands_to_execute(self):
        return len(self.commands_queue) > 0

    def __get_next_command(self):
        return self.commands_queue.popleft()

    def __listener_thread(self):
        try:
            Logger.info('Starting socket')
            Logger.info(self.host + ':' + str(self.port))
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            Logger.info('Listen socket')
            self.conn, self.addr = self.socket.accept()
            self.commands_thread.start()
            Logger.info('Accept socket')
            while self.is_listener_running:
                try:
                    data = self.conn.recv(1024)
                    if not data:
                        break
                    Logger.info(data)
                    if self.data_callback:
                        self.data_callback(data)
                except:
                    break
            self.is_listener_running = False
            self.commands_thread.join()
            self.conn.close()
        except:
            pass

    def __commands_thread(self):
        while self.is_listener_running:
            if self.__has_commands_to_execute():
                command = self.__get_next_command()
                Logger.info('SENDING COMMAND ' + command)
                self.conn.sendall(command + '\n')
            time.sleep(0.05)

    def add_command_to_queue(self, command):
        self.commands_queue.append(command)

    def clear_commands_queue(self):
        self.commands_queue.clear()

    def start_listen(self):
        if self.is_listener_running:
            return

        self.is_listener_running = True
        self.listener_thread.start()

    def stop_listen(self):
        if not self.is_listener_running:
            return

        self.is_listener_running = False
        self.socket.close()
        self.listener_thread.join()

    def is_listening(self):
        return self.is_listener_running

