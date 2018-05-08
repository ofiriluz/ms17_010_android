from kivy.logger import Logger
import threading
import time
import ipaddress
from abc import abstractmethod, ABCMeta


class AbstractSubnetScanner(object):
    __metaclass__ = ABCMeta

    def __init__(self, subnet, mask=24, nthreads=1, start_sub=None, update_sub=None, finish_sub=None):
        self.subnet = subnet
        self.mask = mask
        self.nthreads = nthreads
        self.running_jobs = []
        self.is_running_scan = False
        self.scanned_targets = []
        self.start_sub = start_sub
        self.update_sub = update_sub
        self.finish_sub = finish_sub
        self.ip_lock = threading.Lock()
        self.update_lock = threading.Lock()
        self.scan_job_thread = None
        self.network_generator = None
        self.network_generator_valid = False

    @abstractmethod
    def _Base_scan_ip(self, ip):
        pass

    def __create_network_generator(self):
        interface = ipaddress.ip_interface(unicode(self.subnet + '/' + str(self.mask)))
        self.network_generator = ipaddress.ip_network(interface.network).hosts()
        self.network_generator_valid = True

    def __get_next_ip(self):
        if not self.network_generator_valid:
            return None

        self.ip_lock.acquire()
        scanned_ip = None
        try:
            scanned_ip = self.network_generator.next()
        except StopIteration, e:
            self.network_generator_valid = False
        self.ip_lock.release()

        if scanned_ip:
            return scanned_ip.exploded
        return None

    def __has_more_jobs(self):
        return self.network_generator_valid

    def __cant_insert_job(self):
        return len(self.running_jobs) == self.nthreads

    def __validate_jobs(self):
        jobs_to_remove = []
        for job in self.running_jobs:
            if not job.isAlive():
                jobs_to_remove.append(job)
        self.running_jobs = [t for t in self.running_jobs if t not in jobs_to_remove]

    def __wait_for_jobs_to_end(self):
        for job in self.running_jobs:
            job.join()
        self.running_jobs = []

    def __scan_job_thread(self):
        Logger.info('Starting scan job thread')
        # Finish adding all the jobs
        try:
            if self.start_sub:
                self.start_sub()
            while self.__has_more_jobs() and self.is_running_scan:
                self.__validate_jobs()
                if self.__cant_insert_job():
                    time.sleep(1)
                    continue
                ip = self.__get_next_ip()
                if ip:
                    Logger.info('Starting job for = ' + ip)
                    job = threading.Thread(target=self.__scan_thread, args=(ip,))
                    job.start()
                    self.running_jobs.append(job)

            # Wait for the remaining jobs to end
            self.__wait_for_jobs_to_end()
        except Exception, e:
            Logger.fatal(str(e))
        if self.finish_sub:
            self.finish_sub()
        self.is_running_scan = False

    def __scan_thread(self, ip):
        Logger.info('Running scan on ' + ip)
        result = self._Base_scan_ip(ip)
        if result and result['result']:
            self.scanned_targets.append({'ip': ip, 'result_data': result})
            if self.update_sub:
                self.update_lock.acquire()
                self.update_sub()
                self.update_lock.release()
        Logger.info('Scan finished on ' + ip + ' with result of ' + str(result['result']))

    def start_scan(self):
        if self.is_running_scan:
            return
        Logger.info('Starting scan...')
        self.is_running_scan = True
        self.scanned_targets = []
        self.__create_network_generator()
        self.scan_job_thread = threading.Thread(target=self.__scan_job_thread)
        self.scan_job_thread.start()

    def stop_scan(self):
        if self.is_running_scan:
            self.is_running_scan = False
            self.scan_job_thread.join()

    def wait(self):
        while self.__has_more_jobs():
            self.__wait_for_jobs_to_end()

    def is_scan_running(self):
        return self.is_running_scan

    def get_scanned_targets(self):
        return self.scanned_targets
