import logging

from flask import Flask, request

from util import oc_response
from service import coordinates

app = Flask('hgvs_api')


@app.route('/hello')
def hello_world():
    return oc_response(code=200, message='HGVS API is running.')


@app.route('/coordinates', methods=['post'])
def get_coordinates():
    h = request.json.get('hgvs')
    if not h:
        return oc_response(400, message='HGVS parameter missing')

    r = coordinates.get_coordinates(hgvs=h)
    if type(r) is str:
        return oc_response(400, message=r, **{'hgvs': h})

    return oc_response(200, message='HGVS successfully converted to coordinates', **r)


if __name__ == '__main__':
    logging.Logger.setLevel(level=logging.DEBUG)
    app.run()
