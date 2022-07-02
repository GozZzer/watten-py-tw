from watten_py import WattenServer

server = WattenServer()
try:
    server.run()
except KeyboardInterrupt:
    server.stop()
