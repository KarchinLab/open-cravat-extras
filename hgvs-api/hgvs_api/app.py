import logging

from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix

from service import coordinates
from util import oc_response

app = Flask('hgvs_api')
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)


@app.route('/hello')
def hello_world():
    return oc_response(code=200, message='HGVS API is running.')


@app.route('/coordinates', methods=['post'])
def get_coordinates():
    h = request.json.get('hgvs')
    if not h:
        return oc_response(400, message='HGVS parameter missing')

    r = coordinates.get_coordinates(hgvs_string=h)
    if type(r) is str:
        return oc_response(400, message=r, **{'hgvs': h})

    return oc_response(200, message='HGVS successfully converted to coordinates', **r)


@app.route('/coordinates_all', methods=['post'])
def get_coordinates_all():
    h_str = request.json.get('hgvs')
    if not h_str:
        return oc_response(400, message='HGVS parameter missing')
    if type(h_str) is not list:
        return oc_response(400, message='HGVS parameter must be a list of strings')

    r = coordinates.get_all_coordinates(hgvs_list=h_str)
    if type(r) is str:
        return oc_response(400, message=r, **{'hgvs': h_str})

    return oc_response(200, message=f'{len(h_str)} HGVS strings converted to coordinates', **r)


if __name__ == '__main__':
    logging.getLogger().setLevel(level=logging.DEBUG)
    app.run()
