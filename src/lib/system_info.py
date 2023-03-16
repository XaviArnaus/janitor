from pyxavi.config import Config
import psutil
import socket
import logging


class SystemInfo:

    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
    
    def get_hostname(self) -> str:
        self._logger.debug("Getting hostname")
        return socket.gethostname()

    def get_cpu_data(self) -> dict:
        self._logger.debug("Getting CPU data")
        return {
            'cpu_percent': psutil.cpu_percent(1),
            'cpu_count': psutil.cpu_count(),
            # 'cpu_freq': psutil.cpu_freq(),
        }
    
    def get_mem_data(self) -> dict:
        self._logger.debug("Getting Memory data")
        memory = psutil.virtual_memory()
        return {
            'memory_total': memory.total,
            'memory_avail': memory.available,
            'memory_used': memory.used,
            'memory_free': memory.free,
            'memory_percent': round(( memory.used / memory.total ) * 100, 2)
        }
    
    def get_disk_data(self) -> dict:
        self._logger.debug("Getting Disk ['/'] data")
        disk = psutil.disk_usage('/')
        return {
            'disk_usage_total': disk.total,
            'disk_usage_used': disk.used,
            'disk_usage_free': disk.free,
            'disk_usage_percent': disk.percent,
        }
    
    def get_temp_data(self) -> dict:
        self._logger.debug("Getting Temperature data")
        return {
            # 'sensor_temperatures': psutil.sensors_temperatures()['cpu-thermal'][0].current,
        }
    
    def crossed_thressholds(self, data_to_check: dict, exceptions: list = []) -> bool:
        self._logger.debug("Checking if values crossed thresholds")
        thresholds = dict(self._config.get("system_info.thresholds"))

        for name, value in data_to_check.items():
            # Check if we're monitoring this metric and if the condition applies
            if name in thresholds.keys() and not name in exceptions:
                if "value" in thresholds[name] and value > thresholds[name]["value"]:
                    return True
                
        return False