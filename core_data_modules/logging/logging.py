from core_data_modules.util import TimeUtils


class LogLevel(object):
    def __init__(self, string_value, numeric_value):
        self.string_value = string_value
        self.numeric_value = numeric_value


class LogLevels(object):
    ERROR = LogLevel("ERROR", 40)
    WARNING = LogLevel("WARNING", 30)
    INFO = LogLevel("INFO", 20)
    DEBUG = LogLevel("DEBUG", 10)


class Logger(object):
    project_name = ""
    
    def __init__(self, name):
        self.name = name

    def log(self, log_level, message):
        print(f"{TimeUtils.utc_now_as_iso_string()} {log_level.string_value} - "
              f"{self.project_name}{'/' if self.project_name is not '' else ''}{self.name}: {message}")

    def error(self, message):
        self.log(LogLevels.ERROR, message)

    def warning(self, message):
        self.log(LogLevels.WARNING, message)

    def info(self, message):
        self.log(LogLevels.INFO, message)

    def debug(self, message):
        self.log(LogLevels.DEBUG, message)
        
    @classmethod
    def set_project_name(cls, project_name):
        cls.project_name = project_name
