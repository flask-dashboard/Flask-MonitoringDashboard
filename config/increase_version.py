#!/usr/bin/env python
"""
    Run this script to increase the version defined in flask_monitoringdashboard/constants.py
    The script can use the arguments 'major', 'minor', or 'patch' to increase the corresponding
    version. If no argument is specified, the 'patch' version is increased
"""
import argparse
import json
import sys
import requests
import os
import subprocess

HERE = os.path.dirname(os.path.realpath(__file__))
FILE = os.path.abspath(os.path.join(HERE, '..', 'flask_monitoringdashboard', 'constants.json'))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("type", nargs="?", default="patch")
    args = parser.parse_args(argv)

    options = ['major', 'minor', 'patch']
    if args.type not in options:
        print('Incorrect argument type: {}. Options are: {}'.format(args.type, ', '.join(options)))
        return 1

    branch = (
        subprocess.Popen("git rev-parse --abbrev-ref HEAD", shell=True, stdout=subprocess.PIPE)
        .stdout.read()
        .decode('utf-8')
        .replace('\n', '')
    )

    if branch != 'development':
        print('Only increasing version on development, not on branch "{}"'.format(branch))
        return 0

    index = options.index(args.type)

    # read current data
    with open(FILE, 'r', encoding='UTF-8') as json_file:
        constants = json.load(json_file)

    # retrieve latest version
    response = requests.get('https://pypi.org/pypi/Flask-MonitoringDashboard/json')
    pypi_json = response.json()
    version = pypi_json['info']['version'].split('.')

    version[index] = int(version[index]) + 1
    for i in range(index + 1, len(version)):  # set version after updated version to 0
        version[i] = 0
    constants['version'] = '.'.join(str(v) for v in version)
    print('Increased {} version to {}'.format(args.type, constants['version']))

    # write new version
    with open(FILE, 'w', encoding='UTF-8') as json_file:
        json.dump(constants, json_file, indent=4, separators=(',', ': '))

    return 0


if __name__ == '__main__':
    sys.exit(main())
