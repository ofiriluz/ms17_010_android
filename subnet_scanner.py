from kivy.logger import Logger
import threading
import time
from checker import is_vulnerable


class SubnetScanner:
    def __init__(self, subnet, nthreads=1, start_sub=None, update_sub=None, finish_sub=None):
        self.subnet = subnet
        self.nthreads = nthreads
        self.running_jobs = []
        self.current_subnet_ip = [0, 0, 0, 0]
        self.is_running_scan = False
        self.scanned_targets = []
        self.start_sub = start_sub
        self.update_sub = update_sub
        self.finish_sub = finish_sub

    def __create_ip_list(self):
        ip_list = self.subnet.split('.')
        for i, item in enumerate(ip_list):
            if i > 3:
                break
            try:
                self.current_subnet_ip[i] = int(item)
            except Exception, e:
                Logger.warn(str(e))
        self.current_subnet_ip[3] = 0

    def __get_next_ip(self):
        scanned_ip = '.'.join(str(x) for x in self.current_subnet_ip)
        self.current_subnet_ip[3] += 1
        return scanned_ip

    def __has_more_jobs(self):
        return self.current_subnet_ip[3] == 255

    def __cant_insert_job(self):
        return len(self.running_jobs) == self.nthreads

    def __validate_jobs(self):
        for job in self.running_jobs:
            if not job.isAlive():
                job.handled = True
        self.running_jobs = [t for t in self.running_jobs if not t.handled]

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
            while self.__has_more_jobs():
                self.__validate_jobs()
                if self.__cant_insert_job():
                    time.sleep(1)
                    continue
                ip = self.__get_next_ip()
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
        result = is_vulnerable(ip)
        if result and result['Result']:
            self.scanned_targets.append({'IP': ip, 'OS': result['OS']})
            if self.update_sub:
                self.update_sub()
        Logger.info('Scan finished on ' + ip + ' with result of ' + str(result['Result']))

    def start_scan(self):
        if self.is_running_scan:
            return
        Logger.info('Starting scan...')
        self.is_running_scan = True
        self.scanned_targets = []
        self.__create_ip_list()
        threading.Thread(target=self.__scan_job_thread).start()

    def wait(self):
        while self.__has_more_jobs():
            self.__wait_for_jobs_to_end()

    def is_scan_running(self):
        return self.is_running_scan

    def get_scanned_targets(self):
        return self.scanned_targets
