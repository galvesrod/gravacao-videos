import os
import platform

LOCK_FILE = './utils/lock.lock'

def processo_existe(pid):
    """Verifica se o processo existe"""
    try:
        if platform.system() == 'Windows':
            import subprocess
            result = subprocess.run(['tasklist','/FI', f'PID eq {pid}'], capture_output=True, text=True )
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except (OSError, subprocess.SubprocessError):
        return False

def criar_lock():
    """Cria arquivo de lock com o PID do processo"""
    try:
        if os.path.exists(LOCK_FILE):
            # Verifica se o processo ainda está rodando
            try:
                with open(LOCK_FILE, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        # Arquivo vazio, remove
                        os.remove(LOCK_FILE)
                    else:
                        pid = int(content)
                        
                        if processo_existe(pid):
                            print(f"Script já está em execução (PID: {pid})")
                            return False
                        else:
                            # Processo não existe mais, remove o lock órfão
                            print(f"Removendo lock órfão (PID: {pid})")
                            os.remove(LOCK_FILE)
                            
            except (ValueError, FileNotFoundError, OSError) as e:
                # Erro ao ler arquivo ou processo não existe, remove o lock
                try:
                    os.remove(LOCK_FILE)
                except OSError:
                    pass
        
        # Cria o diretório se não existir
        os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
        
        # Cria o arquivo de lock
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        print(f"Lock criado com sucesso (PID: {os.getpid()})")
        return True
        
    except Exception as e:
        print(f"Erro ao criar lock: {e}")
        return False

def remover_lock():
    """Remove o arquivo de lock"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except OSError as e:
        print(f"Erro ao remover lock: {e}")

