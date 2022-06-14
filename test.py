import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

Window.size = (1000, 700)

Builder.load_file("start.kv")

login_data = {
    "daniel": "1234",
    "lucas": "4321",
    "chri": "4444"
}


class Login(Screen):
    username = StringProperty()
    password = StringProperty()
    button = ObjectProperty()

    def login_popup(self):
        if self.username in login_data:
            if self.password == login_data[self.username]:
                root = App.get_running_app().root
                root.current = "main"
                root.transition.direction = "left"
            else:
                popup = Popup(title="Invalid Input",
                              content="You didn't insert a valid Password",
                              size_hint=(None, None), size=(400, 400))
                popup.open()
        else:
            popup = Popup(title="Invalid Input",
                          content="You didn't insert a valid Username",
                          size_hint=(None, None), size=(400, 400))
            popup.open()


class MainScreen(Screen):
    pass


class ProfileScreen(Screen):
    pass


ms = ScreenManager()
ms.add_widget(Login(name="login"))
ms.add_widget(MainScreen(name="main"))
ms.add_widget(ProfileScreen(name="profile"))


class StartApp(App):
    def build(self):
        return ms


if __name__ == '__main__':
    StartApp().run()
