#  coding: utf-8 
import socketserver
from pathlib import Path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


# mime-types enum
EXT_CONTENT_TYPE = {
    '.html': 'text/html',
    '.css':  'text/css',
    '.js': 'text/javascript',
}


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)
        self.site = Path('./www').resolve()  # site dir, only serve this dir
        self.data = self.data.split()
        if len(self.data) < 3:  # not valid http format
            return self.send_response(400, 'Bad Request')

        method = self.data[0].decode()  # decode bytes to str
        if method != 'GET':  # only handle GET request
            return self.send_response(405, '405 Method Not Allowed')

        request_uri = self.data[1].decode()  # decode bytes to str
        uri = Path(self.site / ('.' + request_uri)).resolve()
        if not is_relative_to(uri, self.site) or not uri.exists():  # if uri not found
            return self.send_response(404, 'Not Found')

        if uri.is_dir() and request_uri[-1] != '/':  # redirect to endswith /
            self.send_response(301, 'Move Permanently')  # 301
            self.send_header('Location', request_uri+'/')
            return
        if uri.is_dir():  # if is dir, send dir/index.html
            uri = uri/'index.html'

        # send file with content-type
        file_ct = EXT_CONTENT_TYPE.get(uri.suffix, 'application/octet-stream')
        self.send_response(200, 'OK')
        self.send_header('Content-Type', file_ct)
        self.end_header()
        # open file and send to http body
        with open(str(uri), 'rb') as f:
            self.send_body(f.read())

    def send_body(self, _bytes):
        # send http body
        self.request.sendall(_bytes)

    def send_response(self, code, message=None):
        # send http response code message
        self.request.sendall(bytearray("HTTP/1.1 {code} {message}\r\n".format(code=code, message=message), 'utf-8'))

    def send_header(self, key, value):
        # send http resonse headers
        self.request.sendall(bytearray('{key}: {value}\r\n'.format(key=key, value=value), 'utf-8'))

    def end_header(self):
        # send http header end flag
        self.request.sendall(bytearray('\r\n', 'utf-8'))


# determine whether it is a subdirectory
def is_relative_to(sub_path, parent_path):
    try:
        sub_path.relative_to(parent_path)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
