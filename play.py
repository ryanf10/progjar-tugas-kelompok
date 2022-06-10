from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle, Line
from functools import partial
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen

import socket
import logging
import json

class ClientInterface:
    def __init__(self, idplayer='1'):
        self.idplayer = idplayer
        self.server_address = ('0.0.0.0', 6666)

    def send_command(self, command_str=""):
        global server_address
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.server_address)
        logging.warning(f"connecting to {self.server_address}")
        try:
            logging.warning(f"sending message ")
            command_str += "\r\n\r\n"
            sock.sendall(command_str.encode())
            # Look for the response, waiting until socket is done (no more data)
            data_received = "" # empty string
            while True:
                # socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
                data = sock.recv(16)
                if data:
                    #data is not empty, concat with previous content
                    data_received += data.decode()
                    if "\r\n\r\n" in data_received:
                        break
                else:
                    # no more data, stop the process by break
                    break
            # at this point, data_received (string) will contain all data coming from the socket
            # to be able to use the data_received as a dict, need to load it using json.loads()
            hasil = json.loads(data_received)
            logging.warning("data received from server:")
            return hasil
        except:
            logging.warning("error during data receiving")
            return False

    def set_location(self,x=100,y=100):
        player = self.idplayer
        command_str = f"set_location {player} {x} {y}"
        hasil = self.send_command(command_str)
        if (hasil['status']=='OK'):
            return True
        else:
            return False

    def get_location(self):
        player = self.idplayer
        command_str=f"get_location {player}"
        hasil = self.send_command(command_str)
        if (hasil['status']=='OK'):
            lokasi = hasil['location'].split(',')
            return (int(lokasi[0]),int(lokasi[1]))
        else:
            return False


class Player:
    def __init__(self,idplayer='1',r=1,g=0,b=0):
        self.current_x = 100
        self.current_y = 100
        self.warna_r = r
        self.warna_g = g
        self.warna_b = b
        self.idplayer = idplayer
        self.widget = Widget()
        self.buttons = None
        self.client_interface = ClientInterface(self.idplayer)
        self.inisialiasi()
        #self.draw(self.widget,self.warna_r,self.warna_g,self.warna_b)
    def get_client_interface(self):
        return self.client_interface
    def get_idplayer(self):
        return self.idplayer
    def set_xy(self,x=100,y=100):
        self.current_x = x
        self.current_y = y
        #self.draw(self.widget, self.warna_r, self.warna_g, self.warna_b)

    def get_widget(self):
        return self.widget
    def get_buttons(self):
        return self.buttons

    def draw(self):
        self.current_x, self.current_y = self.client_interface.get_location()
        wid = self.widget
        r = self.warna_r
        g = self.warna_g
        b = self.warna_b

        with wid.canvas:
            Color(r,g,b)
            Line(rectangle=(self.current_x,self.current_y, 200, 200))

    def move(self,wid, arah,*kwargs):
        #self.draw(wid,0,0,0)
        if (arah=='right'):
            self.current_x = self.current_x + 5
        if (arah=='left'):
            self.current_x = self.current_x - 5
        if (arah=='up'):
            self.current_y = self.current_y + 5
        if (arah=='down'):
            self.current_y = self.current_y - 5
        self.client_interface.set_location(self.current_x,self.current_y)
        #self.draw(wid,self.warna_r,self.warna_g,self.warna_b)

    def inisialiasi(self):
        wid = self.widget
        btn_left = Button(text='left', on_press=partial(self.move, wid, 'left'))
        btn_up = Button(text='up', on_press=partial(self.move, wid, 'up'))
        btn_down = Button(text='down', on_press=partial(self.move, wid, 'down'))
        btn_right = Button(text='right', on_press=partial(self.move, wid, 'right'))

        self.buttons = BoxLayout(size_hint=(1, None), height=50)
        self.buttons.add_widget(btn_left)
        self.buttons.add_widget(btn_up)
        self.buttons.add_widget(btn_down)
        self.buttons.add_widget(btn_right)


class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.menu_screen = MenuScreen(self, 'menu_screen')
        self.add_widget(self.menu_screen)


class MenuScreen(Screen):
    def __init__(self, sm, name):
        super(MenuScreen, self).__init__(name=name)
        self.sm = sm
        box = BoxLayout(size_hint=(1, None), height=200)
        box.add_widget(Button(text='Spawn', on_press=self.change_screen))
        self.add_widget(box)

    def change_screen(self, *kwargs):
        self.sm.play_screen = None
        self.sm.play_screen = PlayScreen(self.sm, 'play_screen')
        self.sm.add_widget(self.sm.play_screen)
        self.sm.current = 'play_screen'
        self.sm.play_screen.play()


class PlayScreen(Screen):
    players = []

    def __init__(self, sm, name):
        super(PlayScreen, self).__init__(name=name)
        self.sm = sm

    def refresh(self, root, callback):
        for i in self.players:
            i.get_widget().canvas.clear()
            i.draw()

    def play(self):
        p1 = Player('1', 1, 0, 0)
        p1.set_xy(100, 100)
        widget1 = p1.get_widget()
        buttons1 = p1.get_buttons()
        self.players.append(p1)

        p2 = Player('2', 0, 1, 0)
        p2.set_xy(100, 200)
        widget2 = p2.get_widget()
        buttons2 = p2.get_buttons()
        self.players.append(p2)

        p3 = Player('3', 0, 0, 1)
        p3.set_xy(150, 150)
        widget3 = p3.get_widget()
        buttons3 = p3.get_buttons()
        self.players.append(p3)

        root = BoxLayout(orientation='horizontal')
        root.add_widget(widget1)
        root.add_widget(buttons1)
        root.add_widget(widget3)
        root.add_widget(buttons3)

        self.add_widget(root)

        Clock.schedule_interval(partial(self.refresh, root), 1 / 60)


class MyApp(App):
    def __init__(self):
        super(MyApp, self).__init__()
        self.sm = MyScreenManager()

    def build(self):
        return self.sm


if __name__ == '__main__':
    MyApp().run()