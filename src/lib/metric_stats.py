from __future__ import annotations
from pyxavi.config import Config
from pyxavi.storage import Storage
from datetime import datetime, timezone
from string import Template
from strenum import LowercaseStrEnum
import logging

class MetricStatsWhen(LowercaseStrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class MetricStats:

    PARAMS_PER_WHEN = {
        "daily": {
            "filename_template": "system_info.metric_storage.daily_file",
            "datetime_format": "%Y-%m-%d"
        },
        "weekly": {
            "filename_template": "system_info.metric_storage.weekly_file",
            "datetime_format": "%Y-%W"
        },
        "monthly": {
            "filename_template": "system_info.metric_storage.monthly_file",
            "datetime_format": "%Y-%m"
        },
    }

    TIME_METRIC_LABEL = "time"
    TIME_METRIC_FORMAT = "%H:%M"
    METADATA_OBJECT = "metadata"
    METRICS_OBJECT = "metrics"


    def __init__(self, config: Config, hostname: str, when: MetricStatsWhen = MetricStatsWhen.DAILY) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
        self._hostname = hostname
        self._when = when
        self._stack = Storage(self.get_current_filename(hostname, when))
        self._initialize(hostname, when)
    
    def append(self, system_info: dict, exceptions: list = []) -> None:
        self._logger.debug(f"Appending SystemInfo dataset into the file for [{self._hostname}] and [{self._when}]") 
        # Save all the metrics
        for metric_name, metric_value in system_info.items():
            if metric_name in exceptions:
                continue
            data = list(self._stack.get(f"{self.METRICS_OBJECT}.{metric_name}", []))
            data.append(metric_value)
            self._stack.set(f"{self.METRICS_OBJECT}.{metric_name}", data)
        # And now save the current time to get a sense of when it happened
        data = list(self._stack.get(f"{self.METRICS_OBJECT}.{self.TIME_METRIC_LABEL}", []))
        data.append(datetime.strftime(datetime.now(timezone.utc), self.TIME_METRIC_FORMAT))
        self._stack.set(f"{self.METRICS_OBJECT}.{self.TIME_METRIC_LABEL}", data)
        # Finally write back the file
        self._stack.write_file()
    
    def get_metric(self, metric_name: str) -> list:
        return self._stack.get(f"{self.METRICS_OBJECT}.{metric_name}", [])
    
    def get_time(self) -> list:
        return self.get_metric(f"{self.METRICS_OBJECT}.{self.TIME_METRIC_LABEL}")
    
    def get_all(self) -> dict:
        return self._stack.get_all()

    def get_current_filename(self, who: str, when: MetricStatsWhen) -> str:
        self._logger.debug(f"Warming up stack file for [{who}] and [{when}]")
        return Template(self._config.get(self.PARAMS_PER_WHEN[when]["filename_template"])).substitute(
            who = who,
            when = datetime.strftime(datetime.now(timezone.utc), self.PARAMS_PER_WHEN[when]["datetime_format"])
        )
    
    def _initialize(self, hostname: str, when: MetricStatsWhen) -> None:
        current_metadata = self._stack.get(self.METADATA_OBJECT, None)
        if not current_metadata:
            self._logger.debug(f"Setting the metadata in the stack file for [{hostname}] and [{when}]")
            self._stack.set(self.METADATA_OBJECT, {
                "hostname": hostname,
                "when": datetime.strftime(datetime.now(timezone.utc), self.PARAMS_PER_WHEN[when]["datetime_format"])
            })
            self._stack.set(self.METRICS_OBJECT, {})
            self._stack.write_file()

# class MetricStatsGraph:

#     def __init__(self, config: Config) -> None:
#         self._config = config
#         self._logger = logging.getLogger(config.get("logger.name"))
    
#     def get_graph_monometric(self,
#                              x_axis_values: list,
#                              y_axis_values: list,
#                              filename: str
#                              ) -> figure:
#         # Create the actual graph for this metric
#         fig = figure()
#         fig.line(x_axis_values, y_axis_values, color="red", line_width=2)

#         # Prepare the output file
#         path = self._config.get("system_info.metric_storage.media_storage")
#         output_file(filename = f"{path}{filename}")

#         # Save it (in HTML!)
#         save(fig)
