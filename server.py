# Import The Server from the watten_py module
from watten_py import WattenServer


server = WattenServer()
# Run the Server and stop it when KeyboardInterrupt occurs
try:
    server.run()
except KeyboardInterrupt:
    server.stop()
