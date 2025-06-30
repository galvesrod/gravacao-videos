
def formataNome(nome:str)-> str:
    # ignorar: \/:*?"<>|
    nome = nome.replace('/','')
    nome = nome.replace('\\','')
    nome = nome.replace(':','')
    nome = nome.replace('*','')
    nome = nome.replace('\"','\'')
    nome = nome.replace('?','')
    nome = nome.replace('>','')
    nome = nome.replace('<','')
    return nome