import urllib.request, json
import pandas as pd

furl = 'https://games.alite.selfip.org/score/'
furlplayers = f"{furl}players"
furlplayer = f"{furl}player?oid="
furlgames = f"{furl}games?oid="

class Players:

    PARAMSDADOS = "id name ano sexo idade time games".split()
    def __init__(self):
        self.players = self.legends = None

    def players_alite(self, name="alite.csv"):
        with urllib.request.urlopen(furlplayers) as url:
            data = json.loads(url.read().decode())
            df = pd.DataFrame(data)

        df_alite = df

        import csv
        with open(name, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';')
            [spamwriter.writerow(df_alite.iloc[line]) for line in range(len(df_alite))]

        return df_alite

    def one_player(self, play_url= "649d7851b9995c27c863da60"):

        url1 = furlplayer + play_url
        with urllib.request.urlopen(url1) as url:
            data = json.loads(url.read().decode())
            df = pd.DataFrame(data)

        df_one_player = df

        return df_one_player

    def one_player_games(self, play_url= "649d7851b9995c27c863da60"):

        url1 = furlgames + play_url
        with urllib.request.urlopen(url1) as url:
            data = json.loads(url.read().decode())
            df = pd.DataFrame(data)

        df_one_player_games = df

        return df_one_player_games


class AlitePandas:
    def __init__(self):
        self._data = pd.read_csv('alite.csv', delimiter=';', names=Players.PARAMSDADOS,
                                 encoding='ISO-8859-1', low_memory=False)

    @property
    def data(self):
        return self._data