from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle, Line, Ellipse
from functools import partial
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.label import Label

import socket
import logging
import json
import random
import string

VERSION = '0.1'


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
            data_received = ""  # empty string
            while True:
                # socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
                data = sock.recv(16)
                if data:
                    # data is not empty, concat with previous content
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

    def set_information(self, r=1, g=0, b=0, x=100, y=100, size=50):
        player = self.idplayer
        command_str = f"set_information {player} {r} {g} {b} {x} {y} {size}"
        hasil = self.send_command(command_str)
        if (hasil['status'] == 'OK'):
            return True
        else:
            return False

    def get_information(self):
        player = self.idplayer
        command_str = f"get_information {player}"
        hasil = self.send_command(command_str)
        if (hasil['status'] == 'OK'):
            info = hasil['info'].split(',')
            return (float(info[0]), float(info[1]), float(info[2]), int(info[3]), int(info[4]), int(info[5]))
        else:
            return False

    def check_collision(self):
        player = self.idplayer
        command_str = f"check_collision {player}"
        hasil = self.send_command(command_str)
        return hasil

    def check_existence(self):
        player = self.idplayer
        command_str = f"check_existence {player}"
        hasil = self.send_command(command_str)
        return hasil


class Player:
    def __init__(self, idplayer='1', r=1, g=0, b=0, size=50):
        self.current_x = 100
        self.current_y = 100
        self.warna_r = r
        self.warna_g = g
        self.warna_b = b
        self.size = size
        self.idplayer = idplayer
        self.widget = Widget()
        self.buttons = None
        self.client_interface = ClientInterface(self.idplayer)
        self.inisialiasi()
        # self.draw(self.widget,self.warna_r,self.warna_g,self.warna_b)

    def get_client_interface(self):
        return self.client_interface

    def get_idplayer(self):
        return self.idplayer

    def set_xy(self, x=100, y=100):
        self.current_x = x
        self.current_y = y
        # self.draw(self.widget, self.warna_r, self.warna_g, self.warna_b)

    def get_widget(self):
        return self.widget

    def get_buttons(self):
        return self.buttons

    def draw(self):
        hasil = self.client_interface.get_information()

        if hasil:
            self.warna_r, self.warna_g, self.warna_b, self.current_x, self.current_y, self.size = hasil
            wid = self.widget
            r = self.warna_r
            g = self.warna_g
            b = self.warna_b

            with wid.canvas:
                Color(r, g, b)
                Ellipse(pos=(self.current_x, self.current_y), size=(self.size, self.size))

    def move(self, wid, arah, *kwargs):
        # self.draw(wid,0,0,0)
        if (arah == 'right'):
            self.current_x = self.current_x + 5
        if (arah == 'left'):
            self.current_x = self.current_x - 5
        if (arah == 'up'):
            self.current_y = self.current_y + 5
        if (arah == 'down'):
            self.current_y = self.current_y - 5

        self.client_interface.set_information(self.warna_r, self.warna_g, self.warna_b, self.current_x, self.current_y,
                                            self.size)

    def check_collision(self):
        return self.client_interface.check_collision()

    def check_existence(self):
        return self.client_interface.check_existence()

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
        self.cli = ClientInterface()
        box = BoxLayout(size_hint=(1, None), height=200)
        box.add_widget(Button(text='Spawn', on_press=self.change_screen))
        self.add_widget(box)

    def change_screen(self, *kwargs):
        global VERSION

        hasil = self.cli.send_command(f"get_version")
        if hasil['status'] == 'OK' and hasil['version'] == VERSION:
            self.sm.play_screen = None
            self.sm.play_screen = PlayScreen(self.sm, 'play_screen')
            self.sm.add_widget(self.sm.play_screen)
            self.sm.current = 'play_screen'
            self.sm.play_screen.play()
        else:
            label = Label(text='Please update your client')
            self.sm.menu_screen.add_widget(label)


player = None
isPlaying = False


class PlayScreen(Screen):
    def __init__(self, sm, name):
        super(PlayScreen, self).__init__(name=name)
        self.sm = sm
        self.players = []
        self.player_keys = []
        self.cli = ClientInterface()
        self.get_other_player()

        self.event_refresh = None
        self.event_spawn_food = None

        self.label_score = Label(pos=(0, 0), text=f"Score:50")

        global player
        player = self.new_player(random.random(), random.random(), random.random())

        global isPlaying
        isPlaying = True

    def spawn_food(self, callback):
        hasil = self.cli.send_command("spawn_food")

    def get_other_player(self):
        hasil = self.cli.send_command("get_keys")

        for key in hasil['keys']:
            p = Player(key, 1, 0, 0)
            self.player_keys.append(key)
            self.players.append(p)

    def refresh(self, root, callback):
        global player
        global isPlaying

        if player is not None:
            self.remove_widget(self.label_score)
            self.label_score = Label(pos=(0, 0), text=f"Score:{player.size}")
            self.add_widget(self.label_score)
            
            cek = player.check_existence()
            if cek['status'] == 'GAMEOVER':
                isPlaying = False

            cek_collision = player.check_collision()
            if cek_collision['status'] == 'GAMEOVER':
                isPlaying = False

            elif cek_collision['status'] == 'OK':
                info = cek_collision['info'].split(',')
                player.size = info[5]

        if isPlaying:
            hasil = self.cli.send_command("get_keys")
            new_other_player = [key for key in hasil['keys'] if key not in self.player_keys]
            removed_player = [key for key in self.player_keys if key not in hasil['keys']]
            index_remove = []
            for key in removed_player:
                for i in range(0, len(self.player_keys)):
                    if self.player_keys[i] == key:
                        index_remove.append(i)

            for i in index_remove:
                if i < len(self.player_keys):
                    self.players[i].get_widget().canvas.clear()
                    self.player_keys.pop(i)
                    self.players.pop(i)

            for key in new_other_player:
                p = Player(key, 1, 0, 0)
                self.player_keys.append(key)
                self.players.append(p)
                root.add_widget(p.get_widget())

            for i in self.players:
                i.get_widget().canvas.clear()
                i.draw()
        else:
            self.game_over()

    def game_over(self):
        global player

        for i in self.players:
            i.get_widget().canvas.clear()

        player = None
        self.players = []
        self.player_keys = []
        self.sm.remove_widget(self.sm.play_screen)
        self.sm.current = 'menu_screen'

        if self.event_refresh:
            self.event_refresh.cancel()

    def new_player(self, r, g, b):
        p = Player(''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) + str(len(self.players) + 1), r,
                   g, b, 50)
        x = 100
        y = 100
        p.set_xy(x, y)
        p.client_interface.set_information(r, g, b, x, y, p.size)
        self.players.append(p)
        self.player_keys.append(p.idplayer)
        return p

    def play(self):
        root = BoxLayout(orientation='horizontal')

        for i in self.players:
            root.add_widget(i.get_widget())

        global player
        self.add_widget(player.get_buttons())

        self.add_widget(root)

        self.event_refresh = Clock.schedule_interval(partial(self.refresh, root), 1 / 60)
        self.event_spawn_food = Clock.schedule_interval(self.spawn_food, 10)


class MyApp(App):
    def __init__(self):
        super(MyApp, self).__init__()
        self.sm = MyScreenManager()
        self.cli = ClientInterface()

    def on_request_close(self, *kwargs):
        if self.sm.current == "play_screen":
            self.cli.send_command(f'remove {player.idplayer}')

    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        return self.sm


if __name__ == '__main__':
    try:
        app = MyApp()
        app.run()
    except KeyboardInterrupt:
        app.on_request_close()