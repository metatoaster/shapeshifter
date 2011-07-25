import os
import json

from log import logger

APPNAME = 'shapeshifter'

CONFIG_DEFAULT = '%s.cfg' % APPNAME
CONFIG_USER = os.path.expanduser('~/.%s.cfg' % APPNAME)


class BaseConfig(object):

    _valid_keys = []

    def _read(self, filename):
        result = None

        try:
            f = open(filename)
        except IOError:
            logger.info('Unable to open config "%s" for reading', filename)
            return

        try:
            result = json.load(f)
        except ValueError:
            logger.info('Could not parse config "%s"', filename)
        finally:
            f.close()

        if not result:
            return

        if isinstance(result, dict):
            self._settings.update(result)
            return True
        else:
            logger.info('Invalid config in config "%s"', filename)

    def read(self):
        self._settings.clear()
        self._read(CONFIG_DEFAULT)
        self._read(CONFIG_USER)

    def write(self):
        try:
            f = open(CONFIG_USER, 'w')
        except IOError:
            logger.info('Unable to open config "%s" for writing', filename)
            return

        try:
            json.dump(self._settings, f)
        except:
            logger.info('Unable to write to user config "%s"', filename)
            return False
        finally:
            f.close()

    def __setitem__(self, key, value):
        if key in self._valid_keys:
            self._settings[key] = value

    def __getitem__(self, key):
        return _settings[key]

    def get(self, key, default=None):
        if key in self._valid_keys and key in self._settings:
            return self._settings[key]
        else:
            return default


class AppConfig(BaseConfig):

    _valid_keys = [
        'cwd',
    ]
    _settings = {}
