from obsws_python import ReqClient
import os


class Gravador():
    def __init__(self):
        try:
            self.cl = ReqClient(host='localhost', port=4455, password='OdHZpnPs0COOYJTH')
        except Exception as e:
            print(e)
        # self.caminho = rf'D:\Usuarios\gabrielalves\Documents\Formação Dev\Fundamentos\Trilha Inicial\Iniciando com Programacao'

    def Status(self):       
        return self.cl.get_record_status()
       
    def Remove(self,name:str, caminho:str):
        name = name.replace('/','').replace('?','')
        file = fr'{caminho}\{name}.mkv'  
        os.remove(file)

    def Start(self, name:str,caminho:str):
        try:
            nome_com_data = name.replace('/','').replace('?','')
            self.cl.set_record_directory(caminho)
            self.cl.set_profile_parameter("Output","FilenameFormatting", nome_com_data)            

            # Iniciar a gravação
            self.cl.start_record()
        except Exception as e:
            print(f"Erro ao iniciar gravação: {e}")
    
    def Stop(self,caminho:str, show_succ_msg:bool=True):
        try:            
            self.cl.stop_record()
            if show_succ_msg:
                print(f"\nGravação Finalizado com sucesso.\nGravado em: {caminho}")
        except Exception as e:
            print(f"Erro ao finalizar gravação: {e}")
        