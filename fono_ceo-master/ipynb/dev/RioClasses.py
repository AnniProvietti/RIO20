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

    PARAMS = "ano1 idade1 sexo1 starttime endtime tipoescola escola".split()
    PARAMSGAMES = " name maxlevel time ".split() #goal retirado
    PARAMSGOAL = "houses criteria markers trial headings time level".split()
    PARAMSTRIAL = "xpos house ypos player state score result time marker".split()

    def __init__(self):
        self.players = self.legends = None

    def one_player(self, play_url='969f29df688afc71a6d07864a7008eeb'): #data de 2012
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

    def file_demographics(self, date="2012", start_count=(0, 2000), name="infodemo.csv"):
        a, b = start_count
        registros = self.get_players(date)
        params = self.PARAMS
        lines = [[self.one_player(reg)["session"][col] for col in params] for reg in registros[a:b]]
        print("demo:", lines[0])
        import csv
        with open(name, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\t',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            [spamwriter.writerow(line) for line in lines]

    def games_file_demographics(self, date="2012", start_count=(0, 2000), name="infogames.csv"):

        a, b = start_count
        registros = self.get_players(date)
        params = self.PARAMSGAMES
        # lines_name = []
        # lines_maxlevel =[]
        # lines_time = []
        # lines = []
        # reg: str
        # for reg in registros[a:b]:
        #     games_one_player = self.one_player(reg)["games"]
        #     for jogada in range(len(games_one_player)):
        #         dados = games_one_player[jogada]
        #         for info_dados in params:
        #             if info_dados == "name":
        #                 lines_name.append(dados[info_dados])
        #             elif info_dados == "maxlevel":
        #                 lines_maxlevel.append(dados[info_dados])
        #             elif info_dados == "time":
        #                 lines_time.append(dados[info_dados])
        #             #salva as informações de cada jogador
        # lines = {'Name': lines_name, 'Maxlevel': lines_maxlevel, 'Time': lines_time}
        # print(lines[0:20])
        reg = [x for x in registros[a:b]]
        one_player = [[game[k] for k in "name maxlevel time".split()] for y in reg for game in self.one_player(y)["games"]]
        df_DIV = pd.DataFrame(one_player, columns=['Name','Maxlevel','Time'])
        print(df_DIV.iloc[2])

        import csv
        with open(name, 'w') as csvfile:
            #informacoes coletadas: name maxlevel time
            spamwriter = csv.writer(csvfile, delimiter='\t')
            for line in range(len(df_DIV)):
                [spamwriter.writerow(df_DIV.iloc[line])]

    def goal_file_demographics(self, date="2012", start_count=(0,2000), name="goal.csv"):

        a,b = start_count
        registros = self.get_players(date)
        params = self.PARAMSGOAL
        reg = [x for x in registros[a:b]]
        one_player = [[goal[k] for k in "houses criteria markers trial headings time level".split()] for y in reg for game in self.one_player(y)["games"] for goal in game["goal"]]
        df_DIV = pd.DataFrame(one_player, columns=['Houses', 'Criteria', 'Markers', 'Trial', 'Headings', 'Time', 'Level'])
        print(df_DIV)

        import csv
        with open(name, 'w') as csvfile:
            #informacoes coletadas: houses criteria markers trial headings time level
            spamwriter = csv.writer(csvfile, delimiter='\t')
            print(df_DIV.iloc[2])
            for line in range(len(df_DIV)):
                [spamwriter.writerow(df_DIV.iloc[line])]

    def trial_file_demographics(self, date="2012", start_count=(0,2000), name="goal_trial.csv"):

        a,b = start_count
        registros = self.get_players(date)
        reg = [x for x in registros[a:b]]
        one_player = [[trial[k] for k in "xpos house ypos player state score result time marker".split()] for y in reg for game in self.one_player(y)["games"] for goals in game["goal"] for trials in goals["trial"] for trial in trials]
        df_DIV = pd.DataFrame(one_player, columns=['xpos', 'house', 'ypos', 'player', 'state', 'score', 'result', 'time', 'marker'])
        print(df_DIV)

        import csv
        with open(name, 'w') as csvfile:
            #informacoes coletadas
            spamwriter = csv.writer(csvfile, delimiter='\t')
            print(df_DIV.iloc[2])
            for line in range(len(df_DIV)):
                [spamwriter.writerow(df_DIV.iloc[line])]

    def houses_file_demographics(self, date="2012", start_count=(0,2000), name="houses.csv"):


        a,b = start_count
        registros = self.get_players(date)
        params = self.PARAMSGOAL
        reg = [x for x in registros[a:b]]

        game_tol = [goals["houses"] for y in reg for game in self.one_player(y)["games"] for goals in game["goal"] if game["name"] == "tol"]
        sorted_tol = sorted(game_tol, key=lambda k: (k['h'], k['b'],k['m'],k['l']))

        game_wis = [goals["houses"] for y in reg for game in self.one_player(y)["games"] for goals in game["goal"]if game["name"] == "wisconsin"]
        sorted_wis = sorted(game_wis, key=lambda k: (k['categoria'], k['acertosConsecutivos'],k['indiceCartaAtual'], k['outrosConsecutivos'], k['wteste']))
        other_games = [goals["houses"] for y in reg for game in self.one_player(y)["games"] for goals in game["goal"] if (game["name"] == "trainz" and game["name"] == "cancel" and game["name"] == "trilha")]


        df_tol = pd.DataFrame(sorted_tol, columns=['h','b','m','l'])
        df_wis = pd.DataFrame(sorted_wis)
        df_other = pd.DataFrame(other_games)

        print("--TOL--",df_tol)
        print("--WISCONSIN--",df_wis)
        print("--OUTROS--",df_other)

        # import csv
        # with open(name, 'w') as csvfile:
        #     #informacoes coletadas
        #     spamwriter = csv.writer(csvfile, delimiter='\t')
        #
        #     for line in range(len(df_tol)):
        #         [spamwriter.writerow(df_tol.iloc[line])]
# %%

class RioPandas:
    def __init__(self):
        self._data = pd.read_csv('infodemo.csv', delimiter='\t', names=RioPlayers.PARAMS)
        #self._data = pd.read_csv ('infogames.csv')
    @property
    def data(self):
        return self._data

# %%
class RioPandasGames:
    def __init__(self):
        self._data = pd.read_csv('infogames.csv', delimiter='\t', names=RioPlayers.PARAMSGAMES)
        #self._data = pd.read_csv ('infogames.csv')
    @property
    def data(self):
        return self._data

# %%
class RioPandasGoal:
    def __init__(self):
        self._data = pd.read_csv('goal.csv', delimiter='\t', names=RioPlayers.PARAMSGOAL)
        #self._data = pd.read_csv ('infogames.csv')
    @property
    def data(self):
        return self._data

class RioPandasTrial:
    def __init__(self):
        self._data = pd.read_csv('goal_trial.csv', delimiter='\t', names=RioPlayers.PARAMSTRIAL)
        #self._data = pd.read_csv ('infogames.csv')
    @property
    def data(self):
        return self._data




#%%
