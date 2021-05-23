import logging
from datetime import timezone, timedelta

logger = logging.getLogger('spotify')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
  'level:%(levelname)s\ttime:%(asctime)s\tname:%(name)s(%(lineno)d)\t%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

JST = timezone(timedelta(hours=9), 'JST')
