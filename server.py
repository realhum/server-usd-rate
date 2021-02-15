from http.server import BaseHTTPRequestHandler, HTTPServer
from settings import USD_SITE, ADDRESS, PORT
import argparse
import json
import re
import requests


def get_usd_rate() -> float:
    """Parse www.cbr.ru with regex and return usd rate for rub"""

    resp = requests.get(USD_SITE)
    regex = "<div class=\"col-md-2 col-xs-9 _right mono-num\">([0-9,]*)"
    pattern = re.compile(regex)
    curr = re.findall(pattern, resp.text)
    return float(curr[1].replace(',', '.'))


class Handler(BaseHTTPRequestHandler):
    """This class will handle any incoming request to server.
    Class inherited form BaseHTTPRequestHandler

    Methods
    -------
    _set_response()
        Set status code and headers.
    do_GET()
        Extend inherited method. Handle GET requests.
    """

    def _set_response(self, code: int):
        """Set status code and headers.
        Parameters
        ----------
        code : int
            Status code for the response
        """

        self.send_response(code)
        self.send_header('Content-type',
                         'application/json')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests.

        Return response with 200 code which include:
            'usd' : float
                value from request
            'rub/usd' : float
                rate of usd in rub
            'rub' : float
                multiply of usd and rate

        If requesting other method than GET - return response with 501 code.

        If data type in request not json - return response with 415 code.

        If type of 'usd' argument in request other than float or int and
        lesser than 0 - return response with 400 code.

        """

        if self.headers.get('Content-Type', 0) != 'application/json':
            self._set_response(415)
            response = {
                'error': 'Unsupported Media Type'
            }
            self.wfile.write(json.dumps(response).encode(encoding='utf_8'))
            return
        content_length = int(self.headers['Content-Length'])
        get_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        usd = get_data.get('usd', '0')
        if (isinstance(usd, float) or isinstance(usd, int)) and (usd >= 0):
            usd = float(usd)
            print('Get request received')
            self._set_response(200)
            rate = get_usd_rate()
            response = {
                'currency': 'usd',
                'usd': usd,
                'rub/usd': rate,
                'rub': round(rate * usd, 4)
            }
            self.wfile.write(json.dumps(response).encode(encoding='utf_8'))
        else:
            self._set_response(400)
            response = {
                'error': 'Bad Request'
            }
            self.wfile.write(json.dumps(response).encode(encoding='utf_8'))
            return
        return


def run(addr: str, port: int, server_class=HTTPServer, handler_class=Handler):
    """Start server on the set address and port"""

    server = server_class((addr, port), handler_class)
    print(f"Starting server on {addr}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--address",
        default=ADDRESS,
        help="Specify the IP address",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=PORT,
        help="Specify the port",
    )
    args = parser.parse_args()
    run(addr=args.address, port=args.port)
