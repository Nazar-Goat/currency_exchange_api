from http.server import BaseHTTPRequestHandler, HTTPServer
import time

class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        print("Hello from get /%s" % self.path)

        self.send_response(200, "OK")
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", 0)

        self.end_headers()

if __name__ == "__main__":
    hostName = "localhost"
    serverPort = 8080

    webServer= HTTPServer((hostName, serverPort), MyServer)
    print("Server started http:/%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Never stopped")