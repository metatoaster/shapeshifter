import os
import json

from log import logger

APPNAME = 'shapeshifter'

CONFIG_DEFAULT = '%s.cfg' % APPNAME
CONFIG_USER = os.path.expanduser(os.path.join('~', '.%s.cfg') % APPNAME)


class BaseConfig(object):

    _valid_keys = {}

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
            # XXX filter out values that do not validate against expected
            # type
            return True
        else:
            logger.info('Invalid config in config "%s"', filename)

    def delete(self):
        self._settings.clear()
        if os.path.exists(CONFIG_USER):
            os.unlink(CONFIG_USER)
            logger.info('Removed user config "%s"', CONFIG_USER)
        self.read()

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

    def _validate(self, key, value):
        return (key in self._valid_keys.keys() and 
                isinstance(value, self._valid_keys[key]))

    def __setitem__(self, key, value):
        if self._validate(key, value):
            self._settings[key] = value

    def __getitem__(self, key):
        return _settings[key]

    def get(self, key, default=None):
        if key in self._valid_keys.keys():
            value = self._settings.get(key, default)
            if self._validate(key, value):
                return value
            logger.info('"%s" not of expected type', key)
            return None
        #logger.info('"%s" not a valid key', key)
        return None


class AppConfig(BaseConfig):

    _valid_keys = {
        'cwd': basestring,
        'columns': list,
    }
    _settings = {}
