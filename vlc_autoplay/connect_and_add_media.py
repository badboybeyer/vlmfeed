#!/usr/bin/env python
"""
connect via telent to a VLC console interface
check if a media source has a queue of media and is playing
add media sources from a dump if the queue is short
play using the media source if it is stopped
"""

import os
import logging
from pathlib import Path
from .vlc_cli import VLCCLI
from .constants import MY_NAME, DEBUG, TELNET_TIMEOUT_SEC, PROMPT, \
    ALL_MEDIA, VIDEO_MEDIA

# localization
CONSOLE_PORT = '4212'
CONSOLE_HOST = '127.0.0.1'
CONSOLE_PASSWD = 'admin'
SHOWS_DIR = os.path.join(Path.home(), 'Videos')

# tuning params
TOO_FEW_MEDIAS_IN_QUEUE = 10

logger = logging.getLogger(MY_NAME)


def main():
    import argparse
    from sys import stdout
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-H', '--host', help='hostname for VLC console',
                        default=CONSOLE_HOST)
    parser.add_argument('-p', '--port', type=int, default=CONSOLE_PORT,
                        help='port number for VLC console'),
    parser.add_argument('-P', '--password', default=CONSOLE_PASSWD,
                        help='login password for VLC console')
    parser.add_argument('-d', '--dump', default=SHOWS_DIR,
                        help='path to search for new medias in')
    parser.add_argument('-m', '--min', type=int,
                        default=TOO_FEW_MEDIAS_IN_QUEUE,
                        help='minimum number of media files in queue and not '
                        'playing')
    parser.add_argument('-v', '--verbose', action='count',
                        help='verbose operation')
    parser.add_argument('-l', '--logfile', type=argparse.FileType('a'),
                        default=stdout, help='log file')
    parser.add_argument('-A', '--all', action='store_true',
                        help='add all media - default is to only add videos')
    args = parser.parse_args()
    if isinstance(args.verbose, type(None)):
        verbosity = logging.WARNING
    elif args.verbose >= 2:
        verbosity = logging.DEBUG
    elif args.verbose == 1:
        verbosity = logging.INFO
    else:
        msg = 'Unsupported number of verbose flags "{}"'
        raise RuntimeError(msg.format(args.verbose))
    if args.all:
        mediatypes = ALL_MEDIA
    else:
        mediatypes = VIDEO_MEDIA
    initLogger(logger, args.logfile, verbosity)
    connect_and_play(host=args.host, port=args.port, password=args.password,
                     showsdir=args.dump, minqueue=args.min,
                     mediatypes=mediatypes)
    return


def connect_and_play(host=CONSOLE_HOST, port=CONSOLE_PORT,
                     password=CONSOLE_PASSWD, showsdir=SHOWS_DIR,
                     minqueue=TOO_FEW_MEDIAS_IN_QUEUE, mediatypes=VIDEO_MEDIA):
    handle = connect(host=host, port=port, password=password)
    # TODO: handle/escape characters in file name
    handle.add_medias_if_queue_short(minqueue, showsdir, mediatypes)
    handle.play()
    if not DEBUG:
        handle.close()
    return handle


def connect(host, port, password):
    logger.info(f'Connecting to VLC console on {host}:{port}')
    handle = VLCCLI(host=host, port=port)
    handle.read_until_line('Password: ', timeout=TELNET_TIMEOUT_SEC)
    handle.write_line(password)
    handle.read_until_line(PROMPT, timeout=TELNET_TIMEOUT_SEC)
    return handle


def initLogger(logger, fh, verbosity=logging.WARNING):
    """
    Configures the logger for my perfered semantics

    logger is the logging.GetLogger object to configure
    fh is  the file like object to output the log to
    verbosity is one of the enumerated logging levels
              from the library
    """
    loggerhandler = logging.StreamHandler(fh)
    format_ = '%(asctime)s, %(name)s, %(levelname)s, %(message)s'
    loggerformatter = logging.Formatter(format_)
    loggerhandler.setFormatter(loggerformatter)
    logger.addHandler(loggerhandler)
    logger.setLevel(verbosity)
    logger.info('%s started', MY_NAME)
    logger.debug("Logging to file: {}".format(str(fh)))
    return


if __name__ == '__main__':
    main()
