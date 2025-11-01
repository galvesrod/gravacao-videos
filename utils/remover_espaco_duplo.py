import os

def renomear_arquivos_espacos_duplos(pasta):
    """
    Percorre todos os arquivos de uma pasta e renomeia aqueles que contêm
    espaços duplos, substituindo-os por espaços simples.
    
    Args:
        pasta (str): Caminho da pasta a ser processada
    """
    # Verifica se a pasta existe
    if not os.path.exists(pasta):
        print(f"Erro: A pasta '{pasta}' não existe!")
        return
    
    if not os.path.isdir(pasta):
        print(f"Erro: '{pasta}' não é uma pasta!")
        return
    
    # Conta quantos arquivos foram renomeados
    arquivos_renomeados = 0
    
    # Percorre recursivamente todos os arquivos da pasta e subpastas
    for raiz, diretorios, arquivos in os.walk(pasta):
        for arquivo in arquivos:
            # Monta o caminho completo
            caminho_completo = os.path.join(raiz, arquivo)
            
            # Verifica se o nome contém espaços duplos
            if "  " in arquivo:
                # Remove espaços duplos (substitui por espaço simples)
                novo_nome = arquivo
                while "  " in novo_nome:
                    novo_nome = novo_nome.replace("  ", " ")
                
                novo_caminho = os.path.join(raiz, novo_nome)
                
                # Verifica se já não existe um arquivo com o novo nome
                if os.path.exists(novo_caminho):
                    print(f"Aviso: Não foi possível renomear '{caminho_completo}' -> '{novo_nome}' (arquivo já existe)")
                else:
                    # Renomeia o arquivo
                    os.rename(caminho_completo, novo_caminho)
                    print(f"Renomeado: '{caminho_completo}' -> '{novo_caminho}'")
                    arquivos_renomeados += 1
    
    print(f"\nTotal de arquivos renomeados: {arquivos_renomeados}")


# Exemplo de uso
if __name__ == "__main__":
    # Substitua pelo caminho da sua pasta
    pasta_alvo = "F:\\Formação Dev"  # "." significa a pasta atual
    
    # Você pode especificar um caminho específico, por exemplo:
    # pasta_alvo = "/home/usuario/documentos"
    # pasta_alvo = "C:\\Users\\Usuario\\Documentos"
    
    renomear_arquivos_espacos_duplos(pasta_alvo)