class Sample:
    """Todos os jogadores de uma amostra"""
    def __init__(self, sample, **kwargs):
        self.players = [Player(**player)  for player in sample]

    def visit(self, visitor):
        visitor.visit_sample(self, players=self.players)


class Player:
    """Todos os dados de um jogador, que joga uma coleção de Games"""
    def __init__(self, session, games, **kwargs):
        self.session = session
        self.games = [Game(**game)  for game in games]

    def visit(self, visitor):
        visitor.visit_player(self, session=self.session, games=self.games)


class Game:
    """Todos os games jogados por um jogador onde cada é jogado em várias fases ou Goals"""
    def __init__(self, name, time, maxlevel, goal, **kwargs):
        self.name, self.time, self.maxlevel = name, time, maxlevel
        self.goals = [Goal(**a_goal) for a_goal in goal]

    def visit(self, visitor):
        visitor.visit_game(self, goal=self.goals, name=self.name, time=self.time, maxlevel=self.maxlevel)


class Goal:
    """Uma fase de um jogo jogada em várias tentativas ou Trials"""
    def __init__(self, time, level, markers, houses, headings, trial, **kwargs):
        self.time, self.level, self.markers, self.houses, self.headings = time, level, markers, houses, headings
        self.trials = [Trial(a_trial) for a_trial in trial]

    def visit(self, visitor):
        visitor.visit_goal(self, trial=self.trials , time=self.time, level=self.level,
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
