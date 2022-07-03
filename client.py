# Import The Client from the watten_py module
from watten_py import WattenClient

client = WattenClient()
# Run the Client and stop it when KeyboardInterrupt occurs
try:
    client.run()
except KeyboardInterrupt:
    client.stop()
