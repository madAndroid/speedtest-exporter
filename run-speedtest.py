#!/usr/bin/python

import os
import speedtest
import time
from prometheus_client import start_http_server, Summary, Gauge

server_list = os.environ['SERVERS'].split(",")

servers = server_list

s = speedtest.Speedtest()

labels = ['host', 'country', 'city']

g_download = Gauge('download_speed', 'Download speed', labels)
g_upload = Gauge('upload_speed', 'Upload speed', labels)
g_ping = Gauge('ping', 'Ping', labels)
g_latency = Gauge('latency', 'Latency', labels)

def display_servers():
    for server in servers:
        serv = s.get_servers([server])
        for key, values in serv.items():
            s.get_best_server(values)
            s.download()
            s.upload()
            results = s.results.dict()
            name = results['server']['name']
            host = results['server']['host']
            country = results['server']['country']
            print("Running speed tests for: %(name)s, %(country)s, %(host)s" % locals())

def process_request(t):
    for server in servers:
        serv = s.get_servers([server])
        for key, values in serv.items():
            s.get_best_server(values)
            s.download()
            s.upload()
            results = s.results.dict()
            name = results['server']['name']
            host = results['server']['host']
            country = results['server']['country']
            g_download.labels(host, country, name).set(results["download"])
            g_upload.labels(host, country, name).set(results["upload"])
            g_ping.labels(host, country, name).set(results["ping"])
            g_latency.labels(host, country, name).set(results["server"]["latency"])
    time.sleep(t)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(9104)
    # Generate some requests.
    display_servers()
    while True:
        process_request(60)
