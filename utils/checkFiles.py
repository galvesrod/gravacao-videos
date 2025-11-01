import os
import sqlite3
from datetime import datetime
import logger as log
from formataNome import formataNome
################# teste

class CheckFiles:
    def __init__(self):
        self.conn = sqlite3.connect('./data/aulas.db')
        pass

    def check_file_exists(self, caminho:str, arquivo:str) -> bool:
        caminho=caminho
        arquivo=arquivo
        video_path = caminho + "\\" + arquivo
        print(video_path)
        
        if os.path.exists(video_path + ".mkv") or os.path.exists(video_path + ".html"):
            return True
        
        return False

    def obter_lista(self) -> list[any]:
        conn = self.conn
        cursor = conn.cursor()
        sql = '''
            select
                a.id aula_id,
                replace((trim(f.PATH) || trim(t.PATH) || trim(c.PATH) || trim(cap.PATH)),'D:\','F:\') win_path,
                a.nome aula
            from formacoes f

            inner join trilhas t on
                f.id = t.id_formacao

            inner join cursos c on
                t.id  = c.id_trilha

            inner join capitulos cap on
                c.id = cap.id_curso

            inner join aulas a on
                cap.id = a.id_capitulo
                and c.id = a.id_curso
            where gravado = 0
            order by f.indice, t.indice, c.indice, cap.id, a.indice
            '''
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def concluir_aula(self, aula_id):
        conn = self.conn
        cursor = conn.cursor()
        sql = f'''update aulas set gravado = 1 where id = {aula_id}'''
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        pass

    def run(self):      
        
        aulas = self.obter_lista()
        for aula in aulas:
            aula_id, caminho, aula = aula
            
            caminho = formataNome(caminho,'DIR')
            aula = formataNome(aula,'FL')

            gravado = c.check_file_exists(caminho=caminho, arquivo=aula )
            
            if gravado:
                self.concluir_aula(aula_id=aula_id)
            else:
                logs.info( f'Aula Não Gravada: ID: {aula_id}, caminho: {caminho}, aula: {aula}' )
        
if __name__ == '__main__':
    logs = log.Logger()
    c = CheckFiles()
    c.run()