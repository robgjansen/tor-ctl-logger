## tor-ctl-logger

This utility connects to a running Tor (https://www.torproject.org) process on the Tor control port, registers for several asynchronous events, and logs the events to disk as they occur over time.

## setup

Install the `python-stem` package on your distro, or from the homepage here: https://stem.torproject.org/

## usage

```
python tor-ctl-logger.py --help
```

## run 

If your Tor client runs on port `9051`, you can run the utility like this:

```
python tor-ctl-logger.py -p 9051 /path/to/log/file.log
```

where `file.log` is where the output gets dumped.

