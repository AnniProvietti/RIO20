import matplotlib.pyplot as plt
# from matplotlib.pyplot import bar, show
from json import loads  # utilizou o loads para pegar todas as coisas do jason que estão vindo em string
from urllib.request import urlopen  # bibliioteca para licar com localizadores universais
#     Erequest é um pedido para esse recurso  #urlopen: vai abrir o recurso
from pickle import dump, load

from numpy import average
from datetime import datetime as dt
from datetime import datetime
import pywt

MICROSECONDS_COUNT = 1000

DELTA_STREAM_SPAN = 5

WAVELET_MODE = pywt.MODES.sp1

Y_M_D_H_M_S = "%Y-%m-%d %H:%M:%S.%f"

M_S__F = '%Y-%m-%d %H:%M:%S.%f'

URL = "http://activufrj.nce.ufrj.br/api/getlist"
URLREG = "http://activufrj.nce.ufrj.br/api/getsession?id="

TRIAL_ARGS = ('xpos, house, ypos, player, state, score, result, marker, ' +
              'categoria, cor, acertos, outros, forma, numero, carta_resposta').split(", ")
DICT_TRIAL = {arg: 0 for arg in TRIAL_ARGS}


class Activ:
    def __init__(self):  # underline em python quer dizer que é um nome reservado, um nome com significado predefinido
        self.jogadores = self.legends = None

    def one_player(self, play_url='90235c60e284c8ec5b8fc4107300f398'):
        dataset = urlopen(URL)  # por favor abra o pacote
        pyset = loads(dataset.read())  # vai transformar os strings do json
        registros = pyset['applist']  # registro principal que esta com o Mauricio
        registros2018 = [numreg for data, numreg in registros if data and "2018" in data]
        print(len(registros2018), registros2018)
        urlreg1 = URLREG + play_url  # vai somar colocando no link
        pass
        aluno1 = urlopen(urlreg1)
        pyset = loads(aluno1.read())
        print(len(pyset), pyset["session"])
        jogador = Jogador(games=pyset["games"], **pyset["session"])
        pic = open("jogador.plk", "rb")
        dump(jogador, pic)
        jogador = load(pic)
        self.jogadores = [jogador]
        # print(list(pyset["games"][0]["goal"][0]["trial"][0][0].keys()))
        print(jogador.games[0].goal[0].trial[0].house)

    def get_jogadores(self):
        def load_registros():
            dataset = urlopen(URL)  # por favor abra o pacote
            pyset = loads(dataset.read())  # vai transformar os strings do json
            registros = pyset['applist']  # registro principal que esta com o Mauricio
            registros2018 = [numreg for data, numreg in registros if data and "2018" in data]
            print(len(registros2018), registros2018)
            return registros2018

        def get_jogador(urlreg):
            urlreg1 = URLREG + urlreg
            aluno1 = urlopen(urlreg1)
            pyset = loads(aluno1.read())
            print(len(pyset), pyset["session"])
            jogador = Jogador(games=pyset["games"], **pyset["session"])
            return jogador

        pic = open("jogador.plk", "wb")
        self.jogadores = [get_jogador(jog_url) for jog_url in load_registros()]
        dump(self, pic)

    @staticmethod
    def load_jogadores():
        pic = open("jogador.plk", "rb")
        return load(pic)

    def get_gamers(self, name="train"):
        return {
            ind: [game for game in player.games
                  if game.has_game(name) and (len(game.goal[0].trial) > 1)] for ind, player in
            enumerate(self.jogadores)}

    @staticmethod
    def convert_to_orange_tab_format(stream):
        clazzes = {}  # {c: 0 for c in range(2**(DELTA_STREAM_SPAN+2))}

        def wavelet(dat, slicer=4):
            if not dat or len(dat) < slicer:
                return []
            # dat = dat[:4]
            data_span = (float(max(dat)) - float(min(dat)))
            data_scale = 1000.0 / data_span if data_span else 1
            data_floor = float(min(dat))
            scaled_data = [int(((datum - data_floor) * data_scale) // 10) for datum in dat]

            w = pywt.Wavelet('bior1.5')
            # w = pywt.Wavelet('sym5')
            _, waveleter = pywt.dwt(scaled_data, w, WAVELET_MODE)
            print("fan in wavelet", len(scaled_data), waveleter)
            wavelet_profile = list(waveleter)
            return wavelet_profile

        def discriminate_state(row, c=1, base=3.0):
            row = wavelet(row)
            span = (float(max(row)) - float(min(row)))
            span = span if abs(span) > 0.01 else 1.0
            data_floor = float(min(row))
            normalize = [(d + data_floor) / span for d in row]
            # mid = average(row)
            discriminator = 1.0 / base
            assert abs(discriminator) > 0.01
            clazz = int(sum(base**i*int(c / discriminator) for i, c in enumerate(normalize)))
            clazzes[clazz] = 1*c + clazzes.setdefault(clazz, 0)
            return clazz
        pat_cnt = DELTA_STREAM_SPAN
        min_class_count = 40
        stream = [row + [discriminate_state(row)] for row in stream]
        table_header = [
            ['n']+list(f"t{count}" for count in range(-DELTA_STREAM_SPAN//2, DELTA_STREAM_SPAN//2))+["s"],
            list('c'+'c'*pat_cnt+"d"),
            list('m'+' '*pat_cnt+"c")]
        table_body = [
            [name]+list(row)
            for name, row in enumerate(stream) if all(row) and clazzes[row[-1]] > min_class_count]
        table_file = table_header + table_body
        for line in table_file:
            print(line)
        from csv import writer
        print("clazzes", len([c for c in clazzes.values() if c > min_class_count]),
              list(f"{cz}:{ct}" for cz, ct in clazzes.items() if ct > min_class_count))
        with open("prospect_states.tab", "w") as tab_file:
            csvwriter = writer(tab_file, delimiter='\t')
            for row in table_file:
                csvwriter.writerow(row)
        pass

    def resync_interpolated_deltas_with_original_click_timing(self, interpolated_deltas, name="tol"):
        """ Also split into surrounding time window span"""
        stream = []
        for jogador in self.jogadores:
            for game in jogador.games:
                if game.has_game(name):
                    for goal in game.goal:
                        interpolation_key = ":".join([jogador.starttime, str(goal.level)])
                        if (interpolation_key not in interpolated_deltas) or not goal.trial:
                            continue
                        original_timing = [trial.time for trial in goal.trial[0]]
                        current_interpolation = interpolated_deltas[interpolation_key]
                        delta_stream = [0] * DELTA_STREAM_SPAN
                        time_stream = [0]*(DELTA_STREAM_SPAN//2)
                        goal.interpolated = []
                        current_timing = original_timing.pop(0)
                        for time, delta in current_interpolation:
                            if not original_timing:
                                break
                            if time_stream[0] >= current_timing:
                                current_timing = original_timing.pop(0)
                                goal.interpolated.append(delta_stream)
                            delta_stream = delta_stream[1:]+[delta]
                            time_stream = time_stream[1:]+[time]
                        stream.extend(goal.interpolated)
        self.convert_to_orange_tab_format(stream)

    def report_gamers_interpolated_resonance(self, name="tol"):
        MIN_TIME_SPAN = 50000
        MAX_DELTA_RANGE = 16000
        self.legends = range(len(self.jogadores))
        report = [(":".join([player.starttime, str(goal.level)]), goal.interpolate_deltas())
                  for player in self.jogadores[1:64]
                  for game in player.games if game.has_game(name)  # and game.goal[0].trial
                  for goal in game.goal if len(goal.trial) > 1
                  ]
        for game in report:
            print(game)
        interpolated_deltas = {i: [(j.time, j.delta) for j in goal] for i, goal in report}
        report = [[(j.time, j.delta) for j in goal] for i, goal in report
                  ]
        self.resync_interpolated_deltas_with_original_click_timing(interpolated_deltas)
        report = [trial for trial in report if trial and
                  abs(max(trial, key=lambda item: item[1])[1]) < MAX_DELTA_RANGE and
                  max(trial, key=lambda item: item[0])[0] > MIN_TIME_SPAN]
        print("report")
        # for game in report:
        #     for act in game:
        #         print(act)
        report = [(lambda gam: list(zip(*gam)) + [tuple(len(gam) * ['r'])])(list(game)) for game in report]
        # for game in report:
        #     print(game)

        self.plot_resonance(report, self.legends)

    def report_gamers_resonance(self, name="tol"):
        from itertools import chain
        self.legends = range(len(self.jogadores))
        report = [chain(goal.generate_delta_and_leap())
                  for player in self.jogadores
                  for game in player.games if game.has_game(name)  # and game.goal[0].trial
                  for goal in game.goal if len(goal.trial) > 1
                  ]
        report = [chain([(j.time, j.delta) for j in trial] for trial in goal)
                  for goal in report
                  ]

        # report = [([j.time for j in game.goal[0].trial[0]],
        #            [j.delta for j in game.goal[0].trial[0]])
        #           for player in self.jogadores
        #           for game in player.games if game.has_game(name) and game.goal[0].trial
        #           ]
        report = [(lambda gam: list(zip(*gam)) + [tuple(len(gam) * ['r'])])(list(game)[0][:30]) for game in report]
        # for game in report:
        #     print(game)

        self.plot_resonance(report, self.legends)

    def plot_gamer_stats(self, activ):
        # print(activ.jogadores[0].games[0].goal[0].trial[0][0].house)
        x_y_axis = []
        x_y_trials = []
        x_y_time = []
        for k, i in activ.get_gamers().items():
            if i and i[0].goal and i[0].goal[0].trial:
                x_y_axis.append((k, i[0].show_game()[0]))
                trials = [i[0] for i in i[0].show_game()[1]]
                x_y_trials.append((k + 0.3, average(trials)))
                x_y_time0, x_y_time1 = i[0].show_game()[-1][0][0]
                interval = datetime.strptime(x_y_time1, M_S__F) - datetime.strptime(x_y_time0, M_S__F)
                x_y_time.append((k + 0.6, interval.seconds / 10))
                print("jogador", k, interval.seconds, i[0].show_game())

        x_axis, y_axis, = zip(*x_y_axis)
        x_axis_t, y_trials, = zip(*x_y_trials)
        x_axis_i, y_time, = zip(*x_y_time)
        bar_color = 'blue'

        plt.bar(x_axis, y_axis, width=0.25, color=bar_color)
        plt.bar(x_axis_t, y_trials, width=0.25, color='red')
        plt.bar(x_axis_i, y_time, width=0.25, color='green')
        plt.show()

    def plot_resonance(self, patt, labels):
        from itertools import cycle
        lines = ["-", "-", "-", "--", "--", "--", ":", ":", ":"]
        # lines = ["-"]*GEN_CNT + ["--"]*GEN_CNT +  [":"]*GEN_CNT
        # lines = ["-", "--", "-.", ":"]
        linecycler = cycle(lines)
        fig = plt.figure()
        fig.suptitle('Derivative Microgenetic Resonance ', fontsize=14, fontweight='bold')

        ax = fig.add_subplot(111)
        fig.subplots_adjust(top=0.92, left=0.05, right=0.98, bottom=0.08)
        # ax.set_title('axes title')
        ax.set_xticklabels(labels)
        plt.xticks(list(range(0, len(labels) * 100, 10)))
        # handles = ax.get_legend()
        handles, labels = ax.get_legend_handles_labels()
        labels = ['title{}'.format(range(len(patt)))]
        ax.legend(handles, labels)
        # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        axes = plt.gca()
        # axes.set_ylim([-34000, 34000])
        axes.set_ylim([-14000, 14000])
        axes.set_xlim([0, 500])
        ax.set_xlabel('time')
        ax.set_ylabel('delta2')
        plt.xticks(rotation=90)
        for _x, _y, _c in patt:
            _x = list(range(len(_y)))
            if not _x:
                continue
            # x_sm = np.array(_x)
            # x_smooth = np.linspace(x_sm.min(), x_sm.max(), 200)
            # y_smooth = spline(_x, npy.log([y+0.001 for y in _y]), x_smooth)
            # y_smooth = spline(_x, [y if y > COUNT_MIN else 0 for y in _y], x_smooth)
            # plt.plot(x_smooth, y_smooth, next(linecycler))
            plt.plot(_x, _y, next(linecycler))
            # plt.plot(range(len(_y)), _y, _c)
        plt.legend(self.legends, loc='upper right')

        plt.show()


class Estado:
    STATE_DIGEST = {}
    STATE_INVENTORY = {}
    STATE_INDEX = []
    INDEX_STATE = {}

    def __init__(self, tipo, tempo):
        """
        Estado é um estágio de processamento da máquina EICA.

        :param tipo: Tipo do estado no máquina EICA
        :param tempo: Evento de ocorrência do estado
        """
        self.tempo, self.tipo = tempo, tipo
        self.profile = set()
        # self.machine_count = {key: 0 for key in CARDS}
        self.user_count = {}
        self.user_latency = []
        self.user_duration = []
        self.user_interval = []

    @staticmethod
    def wavelet(dat, slicer=4):
        if not dat or len(dat) < slicer:
            return []
        dat = dat[:4]
        data_span = (float(max(dat)) - float(min(dat)))
        data_scale = 1000.0 / data_span if data_span else 1
        data_floor = float(min(dat))
        scaled_data = [int(((datum - data_floor) * data_scale) // 10) for datum in dat]

        w = pywt.Wavelet('bior1.5')
        # w = pywt.Wavelet('sym5')
        _, wavelet = pywt.dwt(scaled_data, w, WAVELET_MODE)
        print("fan in wavelet", len(scaled_data), wavelet)
        wavelet_profile = list(wavelet)
        return wavelet_profile

    @staticmethod
    def identify(dat, slicer=4):
        wavelet_profile = Estado.wavelet(dat, slicer=slicer)[:3]
        span = (float(max(wavelet_profile)) - float(min(wavelet_profile)))
        data_scale = 27.0 / span if span else 1
        data_floor = float(min(wavelet_profile))
        print("classify_by_normatized_isomorphism", data_scale, wavelet_profile)
        data_isomorphism_lattice = "".join(str(int(((datum - data_floor) * data_scale) // 10))
                                           for datum in wavelet_profile).strip("0") or "0"
        if data_isomorphism_lattice not in Estado.STATE_DIGEST:
            Estado.STATE_DIGEST[data_isomorphism_lattice] = data_isomorphism_lattice
        return (data_isomorphism_lattice in Estado.STATE_DIGEST) and Estado.STATE_DIGEST[data_isomorphism_lattice]

    def update(self, jogo, user, data):
        # self.machine_count[jogo] += 1
        self.profile.add(data)
        if user[0] not in self.user_count:
            self.user_count[user[0]] = 1
        else:
            self.user_count[user[0]] += 1

    @staticmethod
    def scan_data_for_minutia(janela_jogadas, user=[0], jogo="tol"):
        isoclazz = Estado.STATE_INDEX
        stated_marked_time_series = []

        for time_slice in zip(*(iter(janela_jogadas),) * 4):
            if len(time_slice) < 3:
                break
            tempo, data = list(zip(*time_slice))
            # print("time_slice", data[:slicer])
            # data = tuple(Estado.wavelet(data))
            data_span = (float(max(data)) - float(min(data)))
            data_scale = 30.0 / data_span if data_span else 1
            data_floor = float(min(data))
            scaled_data = tuple(int(((datum - data_floor) * data_scale) // 10) for datum in data)
            # data = scaled_data
            # scaled_data = tuple(Estado.wavelet(data))
            print("scan_data_for_minutia", scaled_data)
            clazz = Estado.identify(data)
            if clazz not in isoclazz:
                isoclazz.append(clazz)
                Estado.INDEX_STATE[clazz] = len(isoclazz)
                Estado.STATE_INVENTORY[Estado.INDEX_STATE[clazz]] = estado = Estado(clazz, 0)
                estado.update(jogo, user, data)
            else:
                Estado.STATE_INVENTORY[Estado.INDEX_STATE[clazz]].update(jogo, user, data)
            stated_marked_time_series += [(Estado.INDEX_STATE[clazz], *full_state)
                                          for full_state in zip(tempo, data, jogo, user)]
        return stated_marked_time_series


class Trial:
    def __init__(self, xpos, house, ypos, player, state, score, result, time, marker,
                 delta=0, categoria=0, cor=0, acertos=0, outros=0, forma=0, numero=0, carta_resposta=0, itpl_delta=0):
        self.xpos, self.house, self.ypos, self.player, self.state, self.score, self.result, self.time, self.marker = \
            xpos, house, ypos, player, state, score, result, time, marker
        self.categoria, self.delta, self.itpl_delta = categoria, delta, itpl_delta
        self.cor, self.acertos, self.outros, self.forma, self.numero, self.carta_resposta = \
            cor, acertos, outros, forma, numero, carta_resposta
        # print("      Trial", xpos, house, ypos, player, state, score, result, time, delta)

    def pack_params(self):
        return dict(
            xpos=self.xpos, house=self.house, ypos=self.ypos, player=self.player, state=self.state, score=self.score,
            result=self.result, time=self.time, marker=self.marker, delta=self.delta, categoria=self.categoria,
            cor=self.cor, acertos=self.acertos, outros=self.outros, forma=self.forma,
            numero=self.numero, carta_resposta=self.carta_resposta)


class Gol:
    def __init__(self, houses, criteria, markers, trial, headings, time, level):
        self.houses, self.criteria, self.markers, self.trial, self.headings, self.time, self.level = \
            houses, criteria, markers, trial, headings, time, level
        print("   Gol", houses, criteria, markers, headings, time, level)
        self.last_time = self.last_delta = 0
        self.first_time = 0
        self.interpolated = []
        if trial:
            # self.trial = [[Trial(**params) for params in a_trial] for a_trial in trial]
            self.trial = [[Trial(**params) for params in a_trial] for a_trial in trial]

    def interpolate_deltas(self, delta=100):  # 0.5):
        from scipy.interpolate import interp1d  # , splev, splrep, UnivariateSpline
        import numpy as np
        self.generate_delta_and_leap()
        interpolate_deltas = [(jogo.time, jogo.delta) for jogo in self.trial[0] if jogo]  # [1:100]
        # print("interpolate_deltas", len(self.trial[0]), self.trial, interpolate_deltas)
        x, y = zip(*interpolate_deltas)
        interpolating_function = interp1d(x, y)
        linear_time_space = np.linspace(x[0], x[-1], (x[-1] - x[0]) / delta)
        self.interpolated = [Trial(time=time, delta=delta, **DICT_TRIAL)
                             for time, delta in zip(linear_time_space, interpolating_function(linear_time_space))]
        return self.interpolated

    def generate_delta_and_leap(self):
        self.last_time = self.last_delta = self.first_time = 0

        def do_total(time):
            return time.seconds * MICROSECONDS_COUNT + time.microseconds // MICROSECONDS_COUNT

        def do_delta(params):
            the_time = params['time']
            the_time = dt.strptime(the_time, Y_M_D_H_M_S)  # .replace(tzinfo=timezone.utc)
            if self.last_time:
                self.last_time, delta_time = the_time, do_total(the_time - self.last_time)
                self.last_delta, leap_time = delta_time, delta_time - self.last_delta
                the_time = do_total((the_time - self.first_time))
            else:
                delta_time = leap_time = 0
                # leap_ = 0

                self.last_time = the_time
                self.first_time = the_time
                # print(delta_time, self.last_time, self.first_time)
                the_time = 0
            params["time"], params["delta"] = the_time, leap_time

            return params

        if self.trial:
            # self.trial = [[Trial(**params) for params in a_trial] for a_trial in trial]
            self.trial = [[Trial(**do_delta(params.pack_params())) for params in a_trial]
                          for a_trial in self.trial]
            return self.trial
        return []


class Games:
    def __init__(self, maxlevel, goal, name, time):
        self.maxlevel, self.goal, self.name, self.time = maxlevel, goal, name, time
        print("  Games", maxlevel, name, time)
        self.goal = [Gol(**params) for params in goal]

    def has_game(self, name):
        return name == self.name

    def show_game(self):
        return len(self.goal), [[len(trial) for trial in goal.trial] for goal in self.goal if goal.trial], \
               [[(trial[0].time, trial[-1].time) for trial in goal.trial if trial] for goal in self.goal if goal.trial]


class Jogador:
    def __init__(self, starttime, idade1, idade2, ano1, ano2, escola, sexo1, sexo2,
                 tipoescola, endtime, games):
        self.starttime = starttime
        self.idade1 = idade1
        self.idade2 = idade2
        self.ano1 = ano1
        self.ano2 = ano2
        self.escola = escola
        self.sexo1 = sexo1
        self.sexo2 = sexo2
        self.tipoescola = tipoescola
        self.endtime = endtime
        print("Jogador", starttime, idade1, idade2, ano1, ano2, escola, sexo1, sexo2, tipoescola, endtime)
        self.games = [Games(**params) for params in games]


def main():
    activ = Activ.load_jogadores()
    activ.report_gamers_interpolated_resonance()
    # activ.report_gamers_resonance()
    '''
    for k, i in activ.get_gamers().items():
        if i and i[0].goal and i[0].goal[0].trial:
            a_goal = i[0].goal
            for each in a_goal:
                print("  goal", each.level)
                if not each.trial:
                    continue
                for turn in each.trial[0]:
                    print("      jogada", turn.house, turn.marker, turn.time)
                # print(k, i[0].goal[0].trial[0][0].house if i[0].goal[0].trial else [])
    '''
    return


if __name__ == '__main__':
    # Activ().get_jogadores()  # só descomentar quando for recarregar o banco de dados do Activ
    main()
