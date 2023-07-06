import urllib.request, json
import pandas as pd
import seaborn as sns
from pandas import DataFrame
from collections import namedtuple
import numpy as np

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

    # def players_games(self):
    #
    #     url1 = "https://games.alite.selfip.org/score/games?oid={}"
    #     with urllib.request.urlopen(url1.format()) as urlp:
    #         data = json.loads(urlp.read().decode())
    #         df = pd.DataFrame(data)
    #     df_one_player_games = df
    #
    #     return df_one_player_games

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



class WiscPlot:
    Cfplot = namedtuple("Cfplot", "col title ylabel xlabel")
    Pnt = namedtuple("Pnt", "ok no td")
    Val = namedtuple("Val", "cc cf cn ct")
    def __init__(self, game_url='https://games.alite.selfip.org/score/games?oid={}'):
        self.game_url = game_url
        self.df: DataFrame = DataFrame()
        self.game_data = []
        self.count = 0

    def retrieve_games(self, player):
        with urllib.request.urlopen(self.game_url.format(player)) as urlp:
            self.game_data.extend(json.loads(urlp.read().decode()))

    def process_df(self):
        dfg_ = pd.DataFrame(self.game_data)
        dfg_ = dfg_.loc[dfg_['game'] == 'wcst']
        dfx_ = dfg_.explode('scorer')
        dfl_ = pd.DataFrame(dfx_.scorer.values.tolist())
        dfx_ = dfx_.drop(columns=["scorer"], inplace=False).reset_index()
        return dfx_.join(dfl_)
    # retrieve_games('6477cf19f626d3cb95e08c92')
    def get_all_games(self, player_oids):
        _ = [self.retrieve_games(oid) for oid in player_oids]
        # print(self.game_data)
        self.df = self.process_df()

    def rerieve_oid_from_person_df(self, person_df):
        import re
        oid_list = [re.findall(r"'(.+?)'",text)[0] for text in person_df._id.to_list()]
        # print("rerieve_oid_from_person_df", oid_list)
        self.get_all_games(oid_list)
        return self

    def refine_point_value_info(self):
        def counter(a, b):
            a, b = int(a), int(b)
            self.count += (1 if a else 0)
            count, self.count = self.count if not b else 0 , 0 if not b else self.count
            return count
        def joiner(k, t, w):
            k, t = int(k), int(t)
            return int(int(t!=w)*2**(w % 3)*k)
        def bother(c, f, n, t):
            c, f, n, t = int(c), int(f), int(n), int(t) %3
            all_k = [c, f, n]
            target = all_k.pop(t)
            return target * sum(all_k)
        point_list = [self.Pnt(text[:-2],*list(text[-2:])) for text in self.df.ponto.to_list()]
        new_list = point_list[1:]+[self.Pnt(0, 0, 0)]
        val_list0 = [self.Val(*list(text)) for text in self.df.valor.to_list()]
        val_list = [joiner(val.cc, val.ct, 0) + joiner(val.cf, val.ct, 1) + joiner(val.cn, val.ct, 2) +
                    joiner(val.cc, val.ct, 3) + joiner(val.cf, val.ct, 4) + joiner(val.cn, val.ct, 5)
                    for val in val_list0]
        val_listn = val_list[1:]+[0]
        conserve = [(int(a.ok)) for a, b in zip(point_list, new_list)]
        conservation = [counter(a.ok, b.ok) for a, b in zip(point_list, new_list)]
        perseveration = [counter(a.no, b.no) for a, b in zip(point_list, new_list)]
        oposition = [counter(a.td, b.td) for a, b in zip(point_list, new_list)]
        deviation = [counter(a, b) for a, b in zip(val_list, val_listn)]
        ambiguation = [bother(c, f, n, t) for c, f, n, t in val_list0]
        # print("refine_point_info", conserve)
        # print("refine_point_infoc", conservation)
        # print("refine_val_infof", ambiguation)
        # # print("refine_point_infon", alterationn)
        zipped = list(zip(conservation, perseveration, oposition, deviation, ambiguation))
        df__ = pd.DataFrame(zipped, columns='conservation perseveration oposition deviation ambiguation'.split())
        _df = self.df.drop(columns='game goal trial carta casa move time ponto valor'.split(), inplace=False).reset_index()
        _df = _df.join(df__).drop(columns='level_0 index _id'.split(), inplace=False)
        # self.df = _df
        return _df

    def plot(self, cfg: Cfplot):
        import seaborn as sbn
        from matplotlib import pyplot as plt_
        _ = plt_.figure(figsize=(15,8))
        chart_ = sbn.countplot(data=self.df, x="name", hue=cfg.col)
        _ = chart_.set(title=cfg.title, ylabel=cfg.ylabel, xlabel=cfg.xlabel)
        _ = chart_.set_xticklabels(chart_.get_xticklabels(), rotation=45, horizontalalignment='right')

    def factorplot(self, cfg: Cfplot):
        import seaborn as sbn
        from matplotlib import pyplot as plt_
        f = plt_.figure(figsize=(15,8))
        # ax = f.add_subplot(1,1,1)
        df_ = self.refine_point_value_info()
        df_ = pd.melt(df_, id_vars="name", var_name="measure", value_name="incidence")

        chart_ = sbn.catplot(x='name', y='incidence', hue='measure', data=df_, kind='bar')
        _ = chart_.set(title=cfg.title, ylabel=cfg.ylabel, xlabel=cfg.xlabel)
        # _ = chart_.set_xticklabels(chart_.get_xticklabels(), rotation=45, horizontalalignment='right')

    def violinplot(self, cfg: Cfplot):
        import seaborn as sbn
        from matplotlib import pyplot as plt_
        f = plt_.figure(figsize=(15,8))
        # ax = f.add_subplot(1,1,1)
        df_ = self.refine_point_value_info()
        df_ = pd.melt(df_, id_vars="name", var_name="measure", value_name="incidence")

        chart_ = sbn.violinplot(x='name', y='incidence', hue='measure', inner="quart", data=df_)
        _ = chart_.set(title=cfg.title, ylabel=cfg.ylabel, xlabel=cfg.xlabel)
        # _ = chart_.set_xticklabels(chart_.get_xticklabels(), rotation=45, horizontalalignment='right')

    def histplot(self, cfg: Cfplot):
        import seaborn as sbn
        from matplotlib import pyplot as plt_
        f = plt_.figure(figsize=(15,8))
        ax = f.add_subplot(1,1,1)
        df_ = self.refine_point_value_info()
        df_ = pd.melt(df_, id_vars="name", var_name="measure", value_name="incidence")
        chart_ = sns.histplot(data=df_, stat="count", multiple="stack",
                              x="incidence", kde=False,
                              palette="pastel", hue="measure",
                              element="bars", ax=ax, legend=True)
        ax.set(xlim=(9, None), ylim=(0, 30))

        _ = chart_.set(title=cfg.title, ylabel=cfg.ylabel, xlabel=cfg.xlabel)
        # _ = chart_.set_xticklabels(chart_.get_xticklabels(), rotation=45, horizontalalignment='right')

    def heatmap(self, cfg: Cfplot):
        import seaborn as sbn
        from matplotlib import pyplot as plt_
        f = plt_.figure(figsize=(15,8))
        # ax = f.add_subplot(1,1,1)
        df_ = self.refine_point_value_info()
        df_ = df_.drop(columns=['name'], inplace=False)
        # Compute the correlation matrix
        corr = df_.corr()
        # Generate a mask for the upper triangle
        mask = np.triu(np.ones_like(corr, dtype=bool))
        # Generate a custom diverging colormap
        cmap = sns.diverging_palette(230, 20, as_cmap=True)
        # Draw the heatmap with the mask and correct aspect ratio
        chart_ = sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
                             square=True, linewidths=.5, cbar_kws={"shrink": .5})
        _ = chart_.set(title=cfg.title, ylabel=cfg.ylabel, xlabel=cfg.xlabel)

# # out = WiscPlot().rerieve_oid_from_person_df(df_players).refine_point_value_info()
# conf0 = WiscPlot.Cfplot(
#     col='ponto', title='Contagem dos Pontos Wisc', ylabel='Contagem de Pontos', xlabel="Participantes")
# # out = WiscPlot().rerieve_oid_from_person_df(df_players).factorplot(conf)
# conf = WiscPlot.Cfplot(
#     col='ponto', title='Histograma das medidas do Wisc', ylabel='frequência das incidência', xlabel="incidência das medidas")
# out = WiscPlot().rerieve_oid_from_person_df(df_players).histplot(conf)
# # out = WiscPlot().rerieve_oid_from_person_df(df_players).violinplot(conf)
# # out = WiscPlot().rerieve_oid_from_person_df(df_players).heatmap(conf)
# # out = WiscPlot().rerieve_oid_from_person_df(df_players).plot(conf)
# # print(out)
# # WiscPlot().rerieve_oid_from_person_df(df_players).refine_point_value_info()




class AlitePandas:
    def __init__(self):
        self._data = pd.read_csv('alite.csv', delimiter=';', names=Players.PARAMSDADOS,
                                 encoding='ISO-8859-1', low_memory=False)

    @property
    def data(self):
        return self._data
#%%
