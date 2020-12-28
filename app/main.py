""" flask app to redirect request to appropriate armbian mirror and image """

import os
import json
import sys

import uwsgi
from flask import (
        Flask,
        redirect,
        request
)
from geolite2 import geolite2
from ruamel.yaml import YAML
from mirror_list import Mirror

def load_mirrors():
    """ open mirrors file and return contents """
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True

    if not os.path.exists('mirrors.yaml'):
        sys.exit("Unable to find mirrors.yaml")
    with open('mirrors.yaml', 'r') as mirror_file:
        config_yaml = yaml.load(mirror_file)

    print("using mode: {}".format(config_yaml.get('mode')))
    return config_yaml

config = load_mirrors()
mirror = Mirror(config.get('mode'), config.get('mirrors'))
reader = geolite2.reader()


def get_ip():
    """ returns requestor's IP by parsing proxy headers,
        defaults to the true remote address """
    return request.environ.get('HTTP_X_FORWARDED_FOR',
                               request.environ.get('REMOTE_ADDR')
                              )

def get_region(client_ip: str, mirror_class=mirror, geolite_reader=reader):
    """ this is where we geoip and return region code """
    try:
        match = geolite_reader.get(client_ip)
        if not match:
            print(f"match failure for IP: {client_ip}")
            return None
        conti = match.get('continent', {}).get('code')
        if conti in mirror_class.continents:
            print(f"Match {client_ip} to continent {conti}")
            return conti
    except Exception as error_message:
        print(f"Error message: {error_message}")
        print(f"match failure for IP: {client_ip}")
        print(json.dumps(match))
    else:
        return None

def get_redirect(mirror_class: Mirror, path: str, client_ip: str):
    """ get redirect based on path and IP """
    region = get_region(client_ip)
    split_path = path.split('/')
    if split_path[0] == "region":
        if split_path[1] in mirror_class.all_regions():
            region = split_path[1]
        del split_path[0:2]
        path = "{}".format("/".join(split_path))
    if mirror_class.mode == "dl_map" and len(split_path) == 2:
        key = "{}/{}".format(split_path[0], split_path[1])
        new_path = mirror_class.dl_map.get(key, path)
        return "{}{}".format(mirror_class.next(region), new_path)
    if path == '':
        return mirror_class.next(region)
    return "{}{}".format(mirror_class.next(region), path)

app = Flask(__name__)


@ app.route('/status')
def status():
    """ return health check status """
    return "OK"


@ app.route('/reload')
def signal_reload():
    """ trigger graceful reload via uWSGI """
    uwsgi.reload()
    return "reloding"


@ app.route('/mirrors')
def show_mirrors(mirror_class=mirror):
    """ return all_mirrors in json format to requestor """
    return json.dumps(mirror_class.all_mirrors())


@ app.route('/regions')
def show_regions(mirror_class=mirror):
    """ return all_regions in json format to requestor """
    return json.dumps(mirror_class.all_regions())


@ app.route('/dl_map')
def show_dl_map(mirror_class=mirror):
    """ returns a JSON of the dl_map config """
    if mirror_class.mode == "dl_map":
        return json.dumps(mirror_class.dl_map)
    return "no map. in direct mode"


@ app.route('/geoip')
def show_geoip():
    """ returns the client's geolocated IP address """
    return json.dumps(reader.get(get_ip()))

@ app.route('/', defaults={'path': ''})
@ app.route('/<path:path>')
def catch_all(path, mirror_class=mirror):
    """ default app route for redirect """
    return redirect(get_redirect(mirror_class, path, get_ip()), 302)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=False, port=80)
