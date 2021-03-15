import logging

logger = logging.getLogger('spotify')
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
  'level:%(levelname)s\ttime:%(asctime)s\tname:%(name)s(%(lineno)d)\tmessage:%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
