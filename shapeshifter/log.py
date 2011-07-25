import logging

level = logging.DEBUG

logger = logging.getLogger('core')
logger.setLevel(level)

ch = logging.StreamHandler()
ch.setLevel(level)
logger.addHandler(ch)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
