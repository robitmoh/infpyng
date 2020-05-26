#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import multiprocessing
import signal
import subprocess
import sys
import time
import datetime
from concurrent import futures

import polling2

import include.logger as log
from include.core import Infpyng
from include.core import Influx


def infpyng(targets):
    args = [
        'fping',
        '-q',
        '-c', str(core.count),
        '-i', str(core.interval),
        '-p', str(core.period),
        '-t', str(core.timeout),
        '-B', str(core.backoff),
        '-r', str(core.retry),
        '-O', str(core.tos),
    ]

    cmd = args + targets

    run = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    (output, errors) = run.communicate()
    lines = output.decode('utf-8').strip()

    return lines


def set_output(r, t):
    # parse output from fping to influxdb
    core.inf_parse(r, t)


def exit_infpyng(signum, frame):
    core.bye = False
    log.warning(':: Interrupted requested...exiting')


def main():
    # set all hosts to ping
    ips = core.set_targets()
    log.info(':: Total of targets : %d' % len(ips))
    # get numbers of CPUs
    cpu = multiprocessing.cpu_count() * 10
    log.info(':: Multiprocessing : %d' % cpu)
    # set buckets (number of ips / number of CPUs)
    buckets = round(len(ips) / cpu)
    if buckets == 0:
        buckets = len(ips)
    log.info(':: Buckets : %d' % buckets)
    # split list into other sublists
    chunks = [ips[x:x + buckets] for x in range(0, len(ips), buckets)]
    # start timer perf
    t_1 = time.perf_counter()

    # pool of threads and schedule the execution of tasks
    with futures.ProcessPoolExecutor(max_workers=cpu) as executor:
        futs = [(host, executor.submit(functools.partial(infpyng, host)))
                for host in chunks]

    # end timer perf
    t_2 = time.perf_counter()

    # get the result
    for ip, f in futs:
        # set round timestamp for data point in nanosecond-precision Unix time
        # if interval="300s" then always collect on 5:00, 10:00, 15:00, etc.
        diff_polling = round(t_2 - t_1)
        now = (core.round_time(
            datetime.datetime.now().replace(second=0, microsecond=0),
            date_delta=datetime.timedelta(seconds=core.poll),
            to='average', drift=diff_polling))
        # timestamp to insert into InfluxDB without drift time polling
        timestamp = datetime.datetime.timestamp(now)
        if f.result():
            set_output(f.result(), str(int(timestamp * 1000000000)))

    # list all alive/unreachable hosts
    not_alive = list(set(ips).difference(core.alive))
    log.info(':: Targets alive : %d' % len(core.result))
    log.info(':: Targets unreachable : %d' % len(not_alive))
    for n in not_alive:
        log.warning(':: ' + str(n) + ' is unreachable')

    if not core.bye:
        # exit gracefully if stopped or interrupt
        executor.shutdown(wait=True)
        log.logging.shutdown()
        sys.exit()
    else:
        # write final result to influxdb
        result = []
        for i in core.result:
            result.append(i.strip())
        influx.write_data(result)
        log.info(':: Data written to DB successfully')

        # cleanup before looping poller
        core.clean()

        log.info(':: Finished in : {:.2f} seconds'.format(round(t_2 - t_1, 2)))
        log.info(':: ---------------------------------------')


if __name__ == "__main__":
    # process pool executor shutdown on signal
    # --> https://stackoverflow.com/a/44163801
    signal.signal(signal.SIGTERM, exit_infpyng)
    signal.signal(signal.SIGINT, exit_infpyng)

    # init logging and if config OK then return Class core
    core = log.set_logger()
    # init Infpyng conf
    core.init_infpyng()
    log.info(':: Settings loaded successfully')
    # init InfluxDB
    influx = Influx()
    # check if InfluxDB is reachable
    if not influx.init_db():
        log.warning(":: Can't connect to InfluxDB...exiting")
        sys.exit()
    log.info(':: Init InfluxDB successfully')
    # start Infpyng poller
    log.info(':: Starting Infpyng Multiprocessing v%s' % core.version)
    log.info(':: Polling time every %ds' % core.poll)
    polling2.poll(lambda: main(), step=core.poll, poll_forever=True)

