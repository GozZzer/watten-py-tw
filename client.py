from watten_py import WattenClient

client = WattenClient()
try:
    client.run()
except KeyboardInterrupt:
    client.stop()
