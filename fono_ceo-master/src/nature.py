#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'ipynb'))
	print(os.getcwd())
except:
	pass
#%% [markdown]
# # Tratamento de dados da Rio+20
# 
# Os dados da __Rio+20__ estão armazenados no banco do __ActivUFRJ__
# 
# Recupere usando a _API_ de acesso com dois comandos:
#  - A raiz comum é "http://activufrj.nce.ufrj.br/api"
#  - para consultar use o comando "getlist" que vai retornar um dataset em _JSON_
#      - os dados virão sob o item "applist" com a data no formato "2012-05-31 13:28:17.394373" e o ID do registro
#  - para recuperar um registro use o comando "getsession?id=xxx" onde xxx é o ID desejado
#      - no primeiro nível _JSON_ teremos os ítens \_rev,session,games,\_id
#      - o session tem os itens sexo2,idade1,idade2,ano1,ano2,escola,sexo1,starttime,tipoescola,endtime
#      - cada item game tem os subitens maxlevel,goal,name,time
#      - cada subitem goal tem os subitens trial,criteria,markers,houses,headings,time,level
# 

#%%
URL = "http://activufrj.nce.ufrj.br/api/"
URLGET = f"{URL}getlist"
URLREG = f"{URL}getsession?id={{}}"

#%% [markdown]
# ## A estrutura dos dados dos registros
# 
# A estrutura pode ser representada pela seguintes classes:

#%%
class Jogador:
    """Todos os dados de um jogador, que joga uma coleção de Games"""
    pass
    
class Games:
    """Todos os games jogados por um jogador onde cada é jogado em várias fases ou Goals"""
    pass
    
class Gol:
    """Uma fase de um jogo jogada em várias tentativas ou Trials"""
    pass

class Trial:
    """Uma tentativa de jogar uma fase onde são feitas diversas jogadas ou Moves"""
    pass

class Move:
    """Cada uma das jogadas executadas para completar uma tentativa"""
    pass


