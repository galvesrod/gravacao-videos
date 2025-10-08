
from typing import Literal
import re


def formataNome(nome:str, type: Literal['DIR', 'FL'] = 'FL')-> str:
    # ignorar: \/:*?"<>|

    primeiro_dois_pontos = nome.find(':')
    nome =  nome[:primeiro_dois_pontos+1] + nome[primeiro_dois_pontos+1:].replace(':','')
    nome = nome.replace('/','')
    nome = nome.replace('*','')
    nome = nome.replace('\"','\'')
    nome = nome.replace('?','')
    nome = nome.replace('>','')
    nome = nome.replace('<','')
    
    if type == 'FL':
        nome = nome.replace('\\','')
        nome = nome.replace(':','') 
    
            
    return nome.strip()