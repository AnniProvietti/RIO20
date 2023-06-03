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

class WisconsinPlayers:

    PARAMS = "ano1 idade1 sexo1 starttime endtime tipoescola escola".split()
    PARAMSGAMES = " name maxlevel time ".split() #goal retirado
    PARAMSGOAL = "houses criteria markers trial headings time level".split()
    PARAMSTRIAL = "xpos house ypos player state score result time marker".split()
    PARAMSHOUSES = "h b m l categoria acertosConsecutivos indiceCartaAtual outrosConsecutivos wteste".split()
    PARAMSDADOS = "ano1 idade1 sexo1 starttime endtime tipoescola escola name maxlevel timeOne houses criteria markers trial headings time level".split()

    def __init__(self):
        self.players = self.legends = None

    def one_player(self, play_url='c5a0d8aa3cae2d7698df5b848a07e64b'): #data de 2012
        urlreg1 = URLREG + play_url  # vai somar colocando no link
        aluno1 = urlopen(urlreg1)
        pyset = loads(aluno1.read())
        return pyset

    def get_players(self, date="2012", start_count=(0, 2000)):
        a, b = start_count
        dataset = urlopen(URLGET)  # por favor abra o pacote
        pyset = loads(dataset.read())  # vai transformar os strings do json
        registros = pyset['applist']  # registro principal que esta com o Mauricio
        registros = [numreg for data, numreg in registros if data and date in data]
        return registros[a:b]
    
    def file_demographics(self, date="2012", start_count=(0, 2000), name="wisconsin.csv"):
        a, b = start_count
        registros = self.get_players(date)
        params = self.PARAMS
        reg = [x for x in registros[a:b]]
        
        dados = [[self.one_player(y)["session"][col] for col in params] for y in reg for game in self.one_player(y)["games"] if game["name"] == "wisconsin"]

        one_player = [[game[k] for k in "name maxlevel time".split()] for y in reg for game in self.one_player(y)["games"] if game["name"] == "wisconsin"]

        one_player_goal = [[goal[k] for k in "houses criteria markers trial headings time level".split()] for y in reg for game in self.one_player(y)["games"] for goal in game["goal"] if game["name"] == "wisconsin"]
        
        df_dados = pd.DataFrame(dados, columns=["ano1" ,"idade1", "sexo1", "starttime", "endtime", "tipoescola", "escola"])
        df_one = pd.DataFrame(one_player, columns=["name", "maxlevel", "time"])
        df_onegoal = pd.DataFrame(one_player_goal, columns=['Houses', 'Criteria', 'Markers', 'Trial', 'Headings', 'Time', 'Level'])

        print(len(df_dados))
        print(len(df_one) )
        print(len(df_onegoal) )
        
        df_wis = pd.concat([df_dados, df_one, df_onegoal], axis=1)
        print(df_wis)

        import csv
        with open(name, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\t',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            [spamwriter.writerow(df_wis.iloc[line]) for line in range(len(df_wis))]



class WisconsinPandas:
    def __init__(self):
        self._data = pd.read_csv('wisconsin.csv', delimiter='\t', names=WisconsinPlayers.PARAMSDADOS,encoding='ISO-8859-1')

    @property
    def data(self):
        return self._data