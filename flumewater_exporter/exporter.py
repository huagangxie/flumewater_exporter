import argparse
import http.server
import logging
import sys

import prometheus_client

import flumewater_exporter


def main():
    parser = argparse.ArgumentParser("Flumewater Parser")

    parser.add_argument("--verbose", "-v", action="count")
    parser.add_argument("--port", type=int, default=9183)
    parser.add_argument("--bind_address", default="0.0.0.0")
    parser.add_argument("--clientid", required=True)
    parser.add_argument("--clientsecret", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--tokenfile")

    args = parser.parse_args()

    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(stream=sys.stdout, level=level)

    if not args.clientid and not args.clientsecret:
        parser.error("--clientid or --clientsecret must be specified")

    api = flumewater_exporter.FlumewaterAPI(
                clientid =args.clientid, clientsecret=args.clientsecret,
                username =args.username, password=args.password,
                tokenfile=args.tokenfile)
    collector = flumewater_exporter.FlumewaterCollector(api)

    prometheus_client.REGISTRY.register(collector)

    handler = prometheus_client.MetricsHandler.factory(
            prometheus_client.REGISTRY)
    server = http.server.HTTPServer(
            (args.bind_address, args.port), handler)
    server.serve_forever()
