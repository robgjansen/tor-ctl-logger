#!/usr/bin/python

import sys, os, argparse, time, datetime, stem
from functools import partial
from stem.control import EventType, Controller

DESCRIPTION="""
This utility connects to Tor on an open Tor control port, and logs various asynchronous events to file.
"""

#EVENTS=['ORCONN', 'CIRC', 'STREAM', 'BW', 'GUARD', 'INFO', 'NOTICE', 'WARN', 'ERR', 'HS_DESC', 'BUILDTIMEOUT_SET', 'DESCCHANGED', 'NEWCONSENSUS', 'NEWDESC', 'STATUS_CLIENT', 'STATUS_GENERAL', 'STATUS_SERVER', 'CONN_BW', 'CIRC_BW', 'STREAM_BW', 'TB_EMPTY', 'HS_DESC_CONTENT']

# collect everything except DEBUG log messages
EVENTS = [e for e in list(EventType) if e not in ['DEBUG']] #['DEBUG', 'INFO', 'NOTICE', 'WARN', 'ERR']

def main():
    # construct the options
    parser = argparse.ArgumentParser(
        description=DESCRIPTION, 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter) # RawTextHelpFormatter

    parser.add_argument('-p', 
        help="""the Tor control port number N""", 
        action="store", type=int, metavar="N",
        dest="ctlport", required=True)

    parser.add_argument('-l', 
        help="""a STRING path to log Tor controller output""", 
        action="store", type=str, metavar="STRING",
        dest="logpath", default="{0}/{1}".format(os.getcwd(), "tor-ctl-logger.log"))

    # get args
    args = parser.parse_args()
    args.logpath = os.path.abspath(os.path.expanduser(args.logpath))

    try:
        run(args)
    except KeyboardInterrupt:
        pass  # the user hit ctrl+c

def run(args):
    with open(args.logpath, 'a') as logfile:
        startup_msg = "started tor-ctl-logger on port {0}, logging events to {1}\n".format(args.ctlport, args.logpath)
        __log(logfile, startup_msg)
        __log(sys.stderr, startup_msg)

        with stem.control.Controller.from_port(port = args.ctlport) as torctl:
            torctl.authenticate()

            # register for async events!
            # some events are only supported in newer versions of tor, so ignore errors from older tors
            event_handler = partial(__handle_tor_event, logfile, )
            try:
                events_added = []
                for e in EVENTS:
                    if e in EventType:
                        torctl.add_event_listener(event_handler, EventType[e])
                        events_added.append(e)
                __log(logfile, "registered for the following events: {0}".format(' '.join(events_added)))
            except:
                pass

            # let stem run its threads and log all of the events, until user interrupts
            try:
                while True:
                    with open(args.logpath, 'rb') as sizef:
                        msg = "heartbeat: logged {0} bytes to {1}, press CTRL-C to quit\n".format(os.fstat(sizef.fileno()).st_size, args.logpath)
                        __log(sys.stderr, msg)
                    time.sleep(60)
            except KeyboardInterrupt:
                pass  # the user hit ctrl+c

def __handle_tor_event(logfile, event):
    __log(logfile, event.raw_content())

def __log(logfile, msg):
    now = datetime.datetime.now()
    utcnow = datetime.datetime.utcnow()
    epoch = datetime.datetime(1970, 1, 1)
    unix_ts = (utcnow - epoch).total_seconds()
    print >>logfile, "{0} {1:.02f} {2}".format(now.strftime("%Y-%m-%d %H:%M:%S"), unix_ts, msg),

if __name__ == '__main__': sys.exit(main())
