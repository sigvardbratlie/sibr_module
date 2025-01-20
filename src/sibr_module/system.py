import logging
from pathlib import Path
import tomllib


class Logger:
    def __init__(self,log_name):
        self._root = self._find_root_folder()
        self._logger = logging.getLogger(log_name)
        self._logName = log_name
        self._logger.setLevel(logging.INFO)
        self._path = self._create_log_folder() / f'{self._logName}.log'
        self._create_handlers()
    def _create_handlers(self):
        file_handler = logging.FileHandler(self._path, mode='w')
        console_handler = logging.StreamHandler()

        file_handler.setLevel(logging.DEBUG)  # Log all levels to the file
        console_handler.setLevel(logging.WARNING)  # Log only warnings and above to the console

        # Create formatters and add them to the handlers
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')

        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        # Add handlers to the logger
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    def _create_log_folder(self):
        if self._root:
            root = self._find_root_folder()
            path = root / 'logfiles'
        else:
            path = Path.cwd() / 'logfiles'
        if not path.exists():
            path.mkdir()
        return path

    def _find_root_folder(self):
        path = Path.cwd()
        while True:
            for file in path.iterdir():
                if '.venv' in file.name:
                    return path
            if path == path.parent:
                raise FileNotFoundError('.venv not found')
            path = path.parent

    def debug(self, msg: str):
        self._logger.debug(msg)

    def info(self, msg: str):
        self._logger.info(msg)

    def warning(self, msg: str):
        self._logger.warning(msg)

    def error(self, msg: str):
        self._logger.error(msg)

    def critical(self, msg: str):
        self._logger.critical(msg)
class ConfigReader:
    def __init__(self):
        self._root = self._find_root_folder()
        self._configs = {}
        self._find_all_config()

    def _read_config(self, config_path):
        with open(config_path,'rb') as fc:
            cfg = tomllib.load(fc)
        return cfg

    def _find_root_folder(self):
        path = Path.cwd()
        while True:
            for file in path.iterdir():
                if '.venv' in file.name:
                    return path
            if path == path.parent:
                raise FileNotFoundError('.venv not found')
            path = path.parent

    def _find_all_config(self):
        for file in self._root.rglob('*.toml'):
            self._configs[file.name] = file
        if not self._configs:
            raise FileNotFoundError('No config files found')

    def list_configs(self):
        return list(self._configs.keys())

    def get_config(self,config_name='stadard.toml'):
        return self._read_config(self._configs[config_name])
class Input:
    def __init__(self, cfg: dict):
        self._cfg = cfg
        self._setup_attributes(cfg)

    def _setup_attributes(self, cfg: dict, prefix: str = ''):
        for key, value in cfg.items():
            attr_name = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                # For nested dictionaries, create a new Input instance
                setattr(self, attr_name, Input(value))
            else:
                # For regular values, set them directly as attributes
                setattr(self, attr_name, value)

    def __repr__(self):
        attrs = [f"{k}={v!r}" for k, v in vars(self).items() if not k.startswith('_')]
        return f"Input({', '.join(attrs)})"


if __name__ == '__main__':
    print(Path(__name__).resolve().parents[0])