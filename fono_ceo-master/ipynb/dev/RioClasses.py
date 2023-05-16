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
    PARAMSGAMES = " name maxlevel time ".split() #goal retirado

    def __init__(self):
        self.players = self.legends = None

    def one_player(self, play_url='86cb91e61f4d95f831f128dbdde863ba'): #data de 2012
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

    def file_demographics(self, date="2012", start_count=(0, 20), name="infogames.csv"):
        a, b = start_count
        registros = self.get_players(date)
        params = self.PARAMS
        lines = []
        for reg in registros[a:b]:
            lines.append([self.one_player(reg)[col] for col in params])
        print("demo:", lines[0:10])
        import csv
        with open(name, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\t',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            [spamwriter.writerow(line) for line in lines]

    def games_file_demographics(self, date="2012", start_count=(0, 20), name="infogames.csv"):

        a, b = start_count
        registros = self.get_players(date)
        params = self.PARAMSGAMES
        lines_name = []
        lines_maxlevel =[]
        lines_time = []
        lines = []
        reg: str
        for reg in registros[a:b]:
            games_one_player = self.one_player(reg)["games"]
            for jogada in range(len(games_one_player)):
                dados = games_one_player[jogada]
                for info_dados in params:
                    if info_dados == "name":
                        lines_name.append(dados[info_dados])
                    elif info_dados == "maxlevel":
                        lines_maxlevel.append(dados[info_dados])
                    elif info_dados == "time":
                        lines_time.append(dados[info_dados])
                    #salva as informações de cada jogador
        lines = {'Name': lines_name, 'Maxlevel': lines_maxlevel, 'Time': lines_time}
        print(lines)
        df_DIV = pd.DataFrame(lines, columns=['Name','Maxlevel','Time'])
        print(df_DIV.iloc[2])

        import csv
        with open(name, 'w') as csvfile:
            #informacoes coletadas: name maxlevel time
            spamwriter = csv.writer(csvfile, delimiter='\t')
            for line in range(len(df_DIV)):
                [spamwriter.writerow(df_DIV.iloc[line])]





# %%

class RioPandas:
    def __init__(self):
        self._data = pd.read_csv('infogames.csv', delimiter='\t', names=RioPlayers.PARAMSGAMES)
        #self._data = pd.read_csv ('infogames.csv')
    @property
    def data(self):
        return self._data
