import pickle

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

from watten_py.objects import Packet, Client
from watten_py.watten_tw import sr_reactor, TwistedServerFactory


class WattenServerApp(App):
    layout = None

    def build(self):
        self.layout = StackLayout()
        sr_reactor.listenTCP(5643, TwistedServerFactory(self))
        return self.layout

    def handle_data(self, data, transport):
        data = pickle.loads(data)
        match data.task_type:
            case "NODE_R":
                user = Client.get_user_by_node(data.data["node"])
                if user:
                    transport.user = user
                    transport.btn.text = user.username
                transport.write(pickle.dumps(Packet("USER", user=user)))
            case "LOGOUT":
                host = transport.getHost()
                transport.btn.text = f"{host.host}:{host.port}"
            case "LOGIN":
                user = Client.get_user(data.data["username"], data.data["password"])
                if isinstance(user, Client):
                    transport.user = user
                    transport.btn.text = user.username
                transport.write(pickle.dumps(Packet("USER_LOG", user=user)))
            case "REGISTER":
                user = Client.new_user(data.data["username"], data.data["email"], data.data["password"])
                if isinstance(user, Client):
                    transport.user = user
                    transport.btn.text = user.username
                transport.write(pickle.dumps(Packet("USER_REG", user=user)))
        print(data)

    def on_connection(self, transport):
        print(transport)
        host = transport.getHost()
        btn = Button(text=f"{host.host}:{host.port}", width=100, size_hint=(None, 0.15))
        transport.btn = btn
        self.layout.add_widget(btn)
        transport.write(pickle.dumps(Packet("NODE")))

    def on_disconnection(self, transport):
        self.layout.remove_widget(transport.btn)
        print(transport)


if __name__ == '__main__':
    WattenServerApp().run()
