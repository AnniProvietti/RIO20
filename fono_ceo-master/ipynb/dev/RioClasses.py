import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
import urllib.request
from json import loads  # pega o dado que esta em string
from urllib.request import urlopen  # abre url

URL = "http://activufrj.nce.ufrj.br/api/"
URLGET = f"{URL}getlist"
URLREG = f"{URL}getsession?id="


class RioPlayers:
    PARAMS = " session games ".split()
    PARAMSGAMES = " name maxlevel goal time".split()

    def __init__(self):
        self.players = self.legends = None

    def one_player(self, play_url='73fbc2485310c96337746a74be854235'):
        urlreg1 = URLREG + play_url  # vai somar colocando no link
        aluno1 = urlopen(urlreg1)
        pyset = loads(aluno1.read())
        return pyset

    def get_players(self, date="2012", start_count=(0, 20)):
        a, b = start_count
        dataset = urlopen(URLGET)  # por favor abra o pacote
        pyset = loads(dataset.read())  # vai transformar os strings do json
        registros = pyset['applist']  # registro principal que esta com o Mauricio
        registros = [numreg for data, numreg in registros if data and date in data]
        return registros[a:b]

    def file_demographics(self, date="2012", start_count=(0, 20), name="infodemo.csv"):
        a, b = start_count
        registros = self.get_players(date)
        params = self.PARAMSGAMES
        lines = []
        for reg in registros[a:b]:
            lines.append([self.one_player(reg)[col] for col in params])
        print("demo:", lines[0:10])
        import csv
        with open(name, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\t',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            [spamwriter.writerow(line) for line in lines]

    def games_file_demographics(self, date="2012", start_count=(0, 20), name="infodemo.csv"):

        a, b = start_count
        registros = self.get_players(date)
        params = self.PARAMSGAMES
        games = self.one_player()
        lines_aux = []
        lines = []
        reg: str
        for reg in registros[a:b]:
            games_one_player = RioPlayers().one_player(reg)["games"]
            for jogada in [0,1]: #REVER for game in games
                dados = games_one_player[jogada]
                for info_game in params:
                    lines.append(dados[info_game])
                    print(reg, jogada, info_game)
        print(lines)


# %%

class RioPandas:
    def __init__(self):
        self._data = pd.read_csv('infodemo.csv', delimiter='\t', names=RioPlayers.PARAMSGAMES)

    @property
    def data(self):
        return self._data
