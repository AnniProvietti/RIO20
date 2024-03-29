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
    PARAMS = "ano1 idade1 sexo1 starttime endtime tipoescola".split()
    PARAMSGAMES = " name maxlevel time ".split()  # goal retirado
    PARAMSGOAL = "houses criteria markers trial headings time level".split()
    PARAMSTRIAL = "xpos house ypos player state score result time marker".split()
    PARAMSHOUSES = "categoria acertosConsecutivos indiceCartaAtual outrosConsecutivos wteste".split()
    PARAMSDADOS = "ano1 idade1 sexo1 starttime endtime tipoescola name maxlevel timeOne categoria acertosConsecutivos indiceCartaAtual " \
                  "outrosConsecutivos wteste  c0 c1 c2 c3 c4 c5 c6 c7 h0 h1 h2 h3 h4 h5 h6 h7 time level markers " \
                  "categoriaTrial xpos cor acertos house forma outros numero ypos player state score result time_trial marker carta_resposta".split()

    def __init__(self):
        self.players = self.legends = None

    def one_player(self, play_url='c5a0d8aa3cae2d7698df5b848a07e64b'):  # data de 2012
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

    def file_demographics(self, date="2012", start_count=(0, 2000)):
        a, b = start_count
        count = 0
        registros = self.get_players(date)
        params = self.PARAMS
        reg = [x for x in registros[a:b]]

        id = [self.one_player(y)["_id"] for y in reg for game in self.one_player(y)['games'] if game["name"] ==
              "wisconsin"]
        dados = [[self.one_player(y)["session"][col] for col in params] for y in reg for game in self.one_player(y)[
            'games'] if game["name"] == "wisconsin"]

        one_player = [[game[k] for k in "name maxlevel time".split()] for y in reg for game in self.one_player(y)[
            'games'] if game["name"] == "wisconsin"]

        # one_player_goal = [[goal[k] for k in "houses criteria markers trial headings time level".split()
        # ] for y in reg for game in self.one_player(y)[
        # "games"] for goal in game["goal"] if game["name"] == "wisconsin"]

        one_player_houses = [goals["houses"] for y in reg for game in self.one_player(y)["games"] for goals in game[
            'goal'] if game["name"] == "wisconsin"]

        one_player_trial = [trial for y in reg for game in self.one_player(y)["games"] for goals in game[
             "goal"] for trials in goals["trial"] for trial in trials if game["name"] == "wisconsin"]

        tr1 =[]
        tr2 =[]
        tr3 =[]

        for y in reg:
            one = self.one_player(y)
            for game in one["games"]:
                if game["name"] == "wisconsin":
                    one_name = game["name"]
                    for goals in game["goal"]:
                        for trials in goals["trial"]:
                            one_id = one["_id"]
                            one_name = game["name"]
                            for trial in trials:
                                    tr1.append(one_id)
                                    tr2.append(one_name)
                                    tr3.append(trial)



        one_player_criteria = [goals["criteria"] for y in reg for game in self.one_player(y)["games"] for goals in game[
            "goal"] if game["name"] == "wisconsin"]

        one_player_markers = [goals["markers"] for y in reg for game in self.one_player(y)["games"] for goals in game[
            "goal"] if game["name"] == "wisconsin"]

        one_player_headings = [goals["headings"] for y in reg for game in self.one_player(y)["games"] for goals in game[
            "goal"] if game["name"] == "wisconsin"]

        one_player_time = [goals["time"] for y in reg for game in self.one_player(y)["games"] for goals in game[
            "goal"] if game["name"] == "wisconsin"]

        one_player_level = [goals["level"] for y in reg for game in self.one_player(y)["games"] for goals in game[
            "goal"] if game["name"] == "wisconsin"]


        # df_id = pd.DataFrame(id, columns=["id"])
        df_dados = pd.DataFrame(dados,index=id, columns=["ano1", "idade1", "sexo1", "starttime", "endtime", "tipoescola"])
        df_one = pd.DataFrame(one_player,index=id, columns=["name", "maxlevel", "time"])
        df_one_houses = pd.DataFrame(one_player_houses,index=id)
        # , columns=['categoria', 'acertosConsecutivos', 'indiceCartaAtual',
                                                                #  'outrosConsecutivos', 'wteste'])
        df_one_trial = pd.DataFrame(one_player_trial,index=tr1,
                                    columns=['categoria', 'xpos', 'cor', 'acertos', 'house', 'forma', 'outros',
                                              'numero', 'ypos', 'player', 'state', 'score', 'result', 'time', 'marker', 'carta_resposta'])
        df_one_criteria = pd.DataFrame(one_player_criteria,index=id,columns=["0", "1", "2", "3", "4", "5", "6", "7"])
        df_one_markers = pd.DataFrame(one_player_markers,index=id)
        df_one_headings = pd.DataFrame(one_player_headings,index=id,columns=["h0", "h1", "h2", "h3", "h4", "h5", "h6", "h7"])
        df_one_time = pd.DataFrame(one_player_time,index=id, columns=["time"])
        df_one_level = pd.DataFrame(one_player_level,index=id, columns=["level"])

        df_oneplayer = pd.concat(
            [df_dados, df_one, df_one_houses, df_one_criteria,df_one_headings,
              df_one_time, df_one_level,df_one_markers], axis=1)

        df_wis = df_oneplayer

        df_wisconsin = pd.merge(df_wis,df_one_trial, how='outer', on=None, left_on=None, right_on=None, left_index=True, right_index=True)


        # print(len(one_id))
        # print(df_wis)
        # print(df_one_trial)
        print(df_wisconsin)

        # import csv
        # with open(name, 'w') as csvfile:
        #     spamwriter = csv.writer(csvfile, delimiter=';')
        #     [spamwriter.writerow(df_wisconsin.iloc[line]) for line in range(len(df_wisconsin))]

        return df_wisconsin


class WisconsinPandas:
    def __init__(self):
        self._data = pd.read_csv('wisconsin.csv', delimiter=';', names=WisconsinPlayers.PARAMSDADOS,
                                 encoding='ISO-8859-1', low_memory=False)

    @property
    def data(self):
        return self._data
