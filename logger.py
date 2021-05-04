import logging
import socket


def get_logger(logger_name, create_file=False):
    log = logging.getLogger(logger_name)
    log.setLevel(level=logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if create_file:
        # create file handler for logger.
        fh = logging.FileHandler('output.log')
        fh.setLevel(level=logging.DEBUG)
        fh.setFormatter(formatter)
    # create console handler for logger.
    ch = logging.StreamHandler()
    ch.setLevel(level=logging.INFO)
    ch.setFormatter(formatter)

    # add handlers to logger.
    if create_file:
        log.addHandler(fh)

    log.addHandler(ch)
    return log


def init_message():
    print('               __')
    print('              / _)')
    print('     _/\/\/\_/ /')
    print('   _|         /')
    print(' _|  (  | (  |')
    print('/__.-\'|_|--|_|')
    print('You have been visited by code dino,')
    print('you shall receive eternal luck!\n\n')