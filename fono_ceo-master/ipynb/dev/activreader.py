from json import loads  # utilizou o loads para pegar todas as coisas do jason que estão vindo em string
from urllib.request import urlopen  # bibliioteca para licar com localizadores universais

URL = "http://activufrj.nce.ufrj.br/api/"
URLGET = f"{URL}getlist"
URLREG = f"{URL}getsession?id="


class Activ:
    PARAMS = "ano1 idade1 sexo1 starttime endtime tipoescola escola".split()

    def __init__(self):  # underline em python quer dizer que é um nome reservado, um nome com significado predefinido
        self.jogadores = self.legends = None

    def one_player(self, play_url='90235c60e284c8ec5b8fc4107300f398'):
        urlreg1 = URLREG + play_url  # vai somar colocando no link
        aluno1 = urlopen(urlreg1)
        pyset = loads(aluno1.read())
        return pyset
        # print(len(pyset), )

    def get_jogadores(self, date="2018", start_count=(0, 100)):
        a, b = start_count
        dataset = urlopen(URLGET)  # por favor abra o pacote
        pyset = loads(dataset.read())  # vai transformar os strings do json
        registros = pyset['applist']  # registro principal que esta com o Mauricio
        registros = [numreg for data, numreg in registros if data and date in data]
        return registros[a:b]

    def file_demographics(self, date="2018", start_count=(0, 100), name="demo.csv"):
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

    def file_game_demographics(self, date="2018", start_count=(0, 100), name="demo.csv"):
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


