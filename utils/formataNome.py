
from typing import Literal


def formataNome(nome:str, type: Literal['DIR', 'FL'] = 'FL')-> str:
    # ignorar: \/:*?"<>|
    nome = nome.replace('/','')
    nome = nome.replace(':','')
    nome = nome.replace('*','')
    nome = nome.replace('\"','\'')
    nome = nome.replace('?','')
    nome = nome.replace('>','')
    nome = nome.replace('<','')
    if type == 'FL':
        nome = nome.replace('\\','')
        
    return nome