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


class Activ:
    PARAMS = "ano1 idade1 sexo1 starttime endtime tipoescola escola".split()

    def __init__(self):  # underline em python quer dizer que é um nome reservado, um nome com significado predefinido
        self.jogadores = self.legends = None

    def one_player(self, play_url='73fbc2485310c96337746a74be854235'):
        urlreg1 = URLREG + play_url  # vai somar colocando no link
        aluno1 = urlopen(urlreg1)
        pyset = loads(aluno1.read())
        return pyset
        # print(len(pyset), )

    def players (self, date="2012", start_count=(0, 2000)):
        a, b = start_count
        dataset = urlopen(URLREG)
        pyset = loads(dataset.read())
        registros = pyset
        registros = [numreg for data, numreg in registros if data and date in data]
        return registros[a:b]
    def get_jogadores(self, date="2012", start_count=(0, 2000)):
        a, b = start_count
        dataset = urlopen(URLGET)  # por favor abra o pacote
        pyset = loads(dataset.read())  # vai transformar os strings do json
        registros = pyset['applist']  # registro principal que esta com o Mauricio
        registros = [numreg for data, numreg in registros if data and date in data]
        return registros[a:b]

    def file_demographics(self, date="2012", start_count=(0, 2000), name="bigdemo.csv"):
        a, b = start_count
        registros = self.get_jogadores(date)
        params = self.PARAMS
        lines = [[self.one_player(reg)["session"][col] for col in params] for reg in registros[a:b]]
        print("demo:", lines[0])
        import csv
        with open(name, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\t',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            [spamwriter.writerow(line) for line in lines]

    def file_game_demographics(self, date="2012", start_count=(0, 2000), name="bigdemo.csv"):
        a, b = start_count
        registros = self.get_jogadores(date)
        params = self.PARAMS
        lines = [[self.one_player(reg)["session"][col] for col in params] for reg in registros[a:b]]
        print("demo:", lines[0])
        import csv
        with open(name, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\t',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            [spamwriter.writerow(line) for line in lines]


# %%

# %%
class RioPandas:
    def __init__(self):
        self._data = pd.read_csv('bigdemo.csv', delimiter='\t', names=Activ.PARAMS)

    @property
    def data(self):
        return self._data


# %%
class Sample:
    """Todos os jogadores de uma amostra"""

    def __init__(self, sample, **kwargs):
        self.players = [Player(**player) for player in sample]

    def visit(self, visitor):
        visitor.visit_sample(self, players=self.players)


class Player:
    """Todos os dados de um jogador, que joga uma coleção de Games"""

    def __init__(self, session, games, **kwargs):
        self.session = session
        self.games = [Game(**game) for game in games]

    def visit(self, visitor):
        visitor.visit_player(self, session=self.session, games=self.games)


class Game:
    """Todos os games jogados por um jogador onde cada é jogado em várias fases ou Goals"""

    def __init__(self, name, time, maxlevel, goal, **kwargs):
        self.name, self.time, self.maxlevel = name, time, maxlevel
        self.goal = [Goal(**a_goal) for a_goal in self.goal]

    def visit(self, visitor):
        visitor.visit_game(self, goal=self.goals, name=self.name, time=self.time, maxlevel=self.maxlevel)


class Goal:
    """Uma fase de um jogo jogada em várias tentativas ou Trials"""

    def __init__(self, time, level, markers, houses, headings, trial, **kwargs):
        self.time, self.level, self.markers, self.houses, self.headings = time, level, markers, houses, headings
        self.trials = [Trial(a_trial) for a_trial in trial]

    def visit(self, visitor):
        visitor.visit_goal(self, trial=self.trials, time=self.time, level=self.level,
                           markers=self.markers, houses=self.houses, headings=self.headings)


class Trial:
    """Uma tentativa de jogar uma fase onde são feitas diversas jogadas ou Moves"""

    def __init__(self, trial, **kwargs):
        self.moves = [Move(**moves) for moves in trial]

    def visit(self, visitor):
        visitor.visit_trial(self, moves=self.moves)


class Move:
    """Cada uma das jogadas executadas para completar uma tentativa"""

    def __init__(self, xpos, house, ypos, player, state, score, result, time, marker,
                 delta=0, categoria=0, cor=0, acertos=0, outros=0, forma=0, numero=0,
                 carta_resposta=0, itpl_delta=0, shape=""):
        self.xpos, self.house, self.ypos, self.player, self.state, self.score, self.result, self.time, self.marker = \
            xpos, house, ypos, player, state, score, result, time, marker
        self.categoria, self.delta, self.itpl_delta, self.shape = categoria, delta, itpl_delta, shape
        self.cor, self.acertos, self.outros, self.forma, self.numero, self.carta_resposta = \
            cor, acertos, outros, forma, numero, carta_resposta
        # print("      Trial", xpos, house, ypos, player, state, score, result, time, delta)

    def pack_params(self):
        return dict(
            xpos=self.xpos, house=self.house, ypos=self.ypos, player=self.player, state=self.state, score=self.score,
            result=self.result, time=self.time, marker=self.marker, delta=self.delta, categoria=self.categoria,
            cor=self.cor, acertos=self.acertos, outros=self.outros, forma=self.forma,
            numero=self.numero, carta_resposta=self.carta_resposta, shape=self.shape)

    def visit(self, visitor):
        kwargs = self.pack_params()
        visitor.visit_move(self, **kwargs)


class _Move:
    def __init__(self, xpos, house, ypos, player, state, score, result, time, marker, **kwargs):
        self.xpos, self.house, self.ypos, self.player, self.state = xpos, house, ypos, player, state
        self.score, self.result, self.time, self.marker = score, result, time, marker

    def visit(self, visitor):
        kwargs = dict(xpos=self.xpos, house=self.house, ypos=self.ypos, player=self.player, state=self.state,
                      score=self.score, result=self.result, time=self.time, marker=self.marker)
        visitor.visit_move(self, **kwargs)


# %%
class Visitor:
    def __init__(self, leaf_action={}):
        self.action_digest = {leaf: lambda *_, **__: True for leaf in "sample player game goal trial move".split()}
        self.action_digest.update(leaf_action)
        self.current = None
        # print("Visitor", self.action_digest)

    def visit_sample(self, sample, players=(), **kwargs):
        # print("visit_sample", sample, players[:2])
        return [element.visit(self) for element in players] \
            if self.action_digest["sample"](sample, players=players) else []
        pass

    def visit_player(self, player, games=(), **kwargs):
        # print("visit_player", games[:2])
        return [element.visit(self) for element in games] \
            if self.action_digest["player"](player, games=games, **kwargs) else []
        pass

    # def visit_game(self, game, name=None, time=None, maxlevel=None, goal=(), **kwargs):
    def visit_game(self, game, goal=(), **kwargs):
        return [element.visit(self) for element in goal] \
            if self.action_digest["game"](game, goal=goal, **kwargs) else []

    def visit_goal(self, goal, time=None, level=None, markers=None, houses=None, headings=None,
                   trial=(), **kwargs):
        vkwargs = dict(time=time, level=level, markers=markers, houses=houses, headings=headings, trial=trial)
        vkwargs.update(**kwargs)
        return [element.visit(self) for element in trial] \
            if self.action_digest["goal"](goal, **vkwargs) else []

    def visit_trial(self, trial, moves=(), **kwargs):
        return [element.visit(self) for element in moves] \
            if self.action_digest["trial"](trial, moves=moves, **kwargs) else []

    def visit_move(self, move, xpos=0, house=None, ypos=0, player=None, state=None, score=0,
                   result=None, time=None, marker=None, delta=0, categoria=0, cor=0, acertos=0,
                   outros=0, forma=0, numero=0, carta_resposta=0, itpl_delta=0, **kwargs):
        kwargs = move.pack_params()
        self.action_digest["move"](move, **kwargs)


# %%
class Rio20Stats:
    def __init__(self, date="2012", start_count=(0, 2000), pic_file="sample.dat"):
        self.games = {}
        self.activ_reader = activ_reader = Activ()
        self.sample_stream = activ_reader.get_jogadores(date=date, start_count=start_count)
        self.sample = None
        try:
            with open(pic_file, "rb") as pkf:
                import pickle
                self.sample = pickle.load(pkf)
        except IOError as _:
            self.sample = Sample(sample=[activ_reader.one_player(player) for player in self.sample_stream])
        self.visitor = Visitor(leaf_action=dict(game=self.count_game_play, sample=self.count_sample_play))

    def file_pickle_sample(self, name="sample.dat"):
        print("sample:", self.sample.players[0].session)
        import csv
        import pickle
        with open(name, 'wb') as pickle_file:
            pickle.dump(self.sample, pickle_file)

    def plot_stats(self, x, xticks, y):
        # print("plot_stats", x, xticks, y, self.games)
        plt.xticks(x, xticks)
        plt.ylabel("number of participants")
        _ = plt.bar(x, y)

    def main(self):
        self.sample.visit(self.visitor)
        self.plot_stats(range(len(self.games)), *zip(*self.games.items()))
        return self

    def count_sample_play(self, sample, players, **kwargs):
        # print("count_game_play", sample, players[:2])
        return True

    def count_game_play(self, game, goal, name, **kwargs):
        #print("count_game_play", game, goal, name)
        self.games.update({name: self.games.setdefault(name, 0)+1})
        return False


# %%

class Rio20Select:

    def __init__(self):
        self.games = {}
        self.selector = 'tol'
        self.trials = {}
        self.goals = {}
        self.activ_reader = activ_reader = Activ()
        self.sample = Sample(sample=[activ_reader.one_player(player) for player in activ_reader.get_jogadores()])
        self.visitor = Visitor(
            leaf_action=dict(game=self.count_game_play, goal=self.count_trials))

    def plot_stats(self, x, xticks, y, label="number of participants", title="count"):
        # print("plot_stats", x, xticks, y, self.games)
        fig = plt.figure()
        plt.xticks(x, xticks)
        fig.suptitle(title)
        plt.ylabel(label)
        _ = plt.bar(x, y)
        _ = plt.show()

    def plot_trials(self):
        trials = sorted(self.trials.items())
        self.plot_stats(range(len(self.trials)), *zip(*trials), label="number of trials", title='Trials')
        return self

    def plot_goals(self):
        goals = sorted(self.goals.items())
        self.plot_stats(range(len(self.goals)), *zip(*goals), label="number of goals", title='Goals')
        return self

    def main(self, selector='tol'):
        self.games = {}
        self.selector = selector
        self.trials = {}
        self.goals = {}
        self.sample.visit(self.visitor)
        return self

    def count_goals(self, _, goal, **kwargs):
        # print("count_game_play", game, goal, name)
        n_trials = len(goal)
        self.goals.update({n_trials: self.goals.setdefault(n_trials, 0) + 1})
        return True

    def count_trials(self, _, trial, **kwargs):
        # print("count_game_play", game, goal, name)
        n_trials = len(trial)
        self.trials.update({n_trials: self.trials.setdefault(n_trials, 0) + 1})
        return False

    def count_game_play(self, game, goal, name, **kwargs):
        # print("count_game_play", game, goal, name)
        if name == self.selector:
            self.games.update({name: self.games.setdefault(name, 0) + 1})
            self.count_goals(game, goal=goal)
            return True
        return False


# %%
