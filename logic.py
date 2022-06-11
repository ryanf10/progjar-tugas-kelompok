import os
import json
import base64
from glob import glob
import shelve

VERSION = '0.1'

# asumsi, hanya ada player 1, 2 , 3
class PlayerServerInterface:
    def __init__(self):
        self.players = shelve.open('g.db', writeback=True)

    def set_information(self, params=[]):
        pnum = params[0]
        r = params[1]
        g = params[2]
        b = params[3]
        x = params[4]
        y = params[5]
        size = params[6]
        try:
            self.players[pnum] = f"{r},{g},{b},{x},{y},{size}"
            self.players.sync()
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR')

    def get_information(self, params=[]):
        pnum = params[0]
        try:
            return dict(status='OK', info=self.players[pnum])
        except Exception as ee:
            return dict(status='ERROR')

    def get_keys(self, params=[]):
        try:
            return dict(status='OK', keys=list(self.players.keys()))
        except Exception as e:
            return dict(status='ERROR')

    def remove(self, params=[]):
        try:
            self.players.pop(params[0])
            return dict(status='OK')
        except Exception as e:
            return dict(status='ERROR')

    def get_version(self, params=[]):
        global VERSION
        return dict(status='OK', version=VERSION)

    def check_collision(self, params=[]):
        pnum = params[0]
        try:
            player = self.players[pnum]
            info = player.split(',')
            player_x = int(info[3])
            player_y = int(info[4])
            player_size = int(info[5])
            print(info)
            keys = list(self.players.keys())
            for key in keys:
                if key != pnum:
                    other_player = self.players[key]
                    other_player_info = other_player.split(',')
                    other_player_x = int(other_player_info[3])
                    other_player_y = int(other_player_info[4])
                    other_player_size = int(other_player_info[5])
                    if (
                            player_x < other_player_x + other_player_size and
                            player_x + player_size > other_player_x and
                            player_y < other_player_y + other_player_size and
                            player_size + player_y > other_player_y
                    ):
                        if player_size < other_player_size:
                            return dict(status='GAMEOVER')
                        elif player_size > other_player_size:
                            player_size = player_size + other_player_size
                            self.players.pop(key)
                            self.players[pnum] = f'{info[0]},{info[1]},{info[2]},{info[3]},{info[4]},{player_size}'
                            self.players.sync()

            return dict(status='OK', info=self.players[pnum])
        except Exception as ee:
            return dict(status='ERROR')


if __name__ == '__main__':
    p = PlayerServerInterface()
    # p.set_location(['1', 100, 100])
    # print(p.get_location('1'))
    # p.set_location(['2', 120, 100])
    # print(p.get_location('2'))