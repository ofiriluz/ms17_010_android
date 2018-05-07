__version__ = 1.1

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'commands'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ms1710'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'shell_control_infra'))
sys.path.append(os.path.join(os.getcwd(), 'commands'))
sys.path.append(os.path.join(os.getcwd(), 'ms1710'))
sys.path.append(os.path.join(os.getcwd(), 'shell_control_infra'))
sys.path.append(os.path.join(os.getcwd(), 'utils'))
sys.path.append(os.getcwd())

from kivy.logger import Logger
Logger.info("HI12")
Logger.info(str(sys.path))
from scanner_app.scanner_app import ScannerApp


if __name__ == "__main__":
    Logger.info("HI")
    ScannerApp().run()
