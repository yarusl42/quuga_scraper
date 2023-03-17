import logging

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create stdout handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create file handler
file_handler = logging.FileHandler('logfile.log')
file_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('[%(asctime)s:%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
