from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException,StaleElementReferenceException
import sqlite3
from datetime import datetime
################# teste
from utils.configurarChrome import configurarChrome
from logar import logar
# from logar import logar

class Progresso:
    def __init__(self):
        self.conn = sqlite3.connect('./data/aulas.db')
        pass

    def obter_formacoes(self) -> list[any]:
        conn = self.conn
        cursor = conn.cursor()
        cursor.execute('select * from formacoes order by id')
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def obter_trilhas(self) -> list[any]:
        conn = self.conn
        cursor = conn.cursor()
        cursor.execute('select * from trilhas order by id, indice')
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def obter_cursos(self) -> list[any]:
        conn = self.conn
        cursor = conn.cursor()
        cursor.execute('select * from cursos order by id, indice')
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def obter_lista_gravacao(self) -> list[any]:
        conn = self.conn
        cursor = conn.cursor()
        sql = '''
            select
                f.nome formacao,
                t.nome trilha,
                c.nome curso,
                cap.nome capitulo,
                a.nome aula,
	            c.url || '?aula=' || a.aula_id link,
                a.id aula_id,
                a.indice,
                (select max(a2.indice) qtde_aulas from aulas a2 where a.id_curso = a2.id_curso   ) qtde_aulas,
                a.aula_id cd_aula,
                f.path || t.path || c.path || cap.path win_path
                /*replace(f.path_linux || t.path || c.path || cap.path,'\\','/') linux_path*/
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


    def insert_trilhas(self, trilha):
        conn = self.conn
        cursor = conn.cursor()
        sql = '''insert or ignore into trilhas (indice, nome, url, id_formacao, path) values (?, ?, ?, ?, ?)'''
        cursor.execute(sql, trilha)
        conn.commit()
        cursor.close()

    def inserir_cursos(self, curso):
        conn = self.conn
        cursor = conn.cursor()
        sql = '''insert or ignore into cursos (indice, nome, url, id_trilha, path) values (?, ?, ?, ?, ?)'''
        cursor.execute(sql, curso)
        conn.commit()
        cursor.close()

    def inserir_capitulos(self, cap):
        conn = self.conn
        cursor = conn.cursor()
        sql = '''insert or ignore into capitulos (id, id_curso, nome, path) values (?, ?, ?, ?)'''
        cursor.execute(sql, cap)
        conn.commit()
        cursor.close()

    def inserir_aulas(self, aula):
        conn = self.conn
        cursor = conn.cursor()
        sql = '''insert or ignore into aulas (aula_id, indice, nome, id_capitulo, id_curso  ) values (?, ?, ?, ?, ?)'''
        cursor.execute(sql, aula)
        conn.commit()
        cursor.close()

    def concluir_aula(self, aula_id):
        conn = self.conn
        cursor = conn.cursor()
        sql = f'''update aulas set gravado = 1 where id = {aula_id}'''
        cursor.execute(sql)
        conn.commit()
        cursor.close()

        pass

    def run(self, page:webdriver):
        data_inicio = datetime.now()
        formacoes = self.obter_formacoes()
        for formacao in formacoes:
            page.get(formacao[3])
            trilhas = page.find_elements(By.CSS_SELECTOR,'a[href].w-full.h-full.relative.overflow-hidden')
            for index,trilha in enumerate(trilhas,start=1):
                titulo = trilha.find_element(By.CSS_SELECTOR,'span>div>div>div:nth-child(2)' ).get_attribute("textContent")
                link = trilha.get_attribute("href")
                caminho = f'\\{index} - Trilha {titulo.replace('/','').replace('?','')}'
                self.insert_trilhas((index,titulo,link,formacao[0],caminho))
                print(f'Inserido trilha: {index},{titulo},{link},{formacao[0]}')

            print(f'Inserido todas as trilhas da formação {formacao[2]}')

        trilhas = self.obter_trilhas()
        for trilha in trilhas:
            page.get(trilha[3])
            cursos = page.find_elements(By.CSS_SELECTOR,'a[href].w-full.h-full')
            for index, curso in enumerate(cursos, start=1):
                titulo = curso.find_element(By.CSS_SELECTOR,'.font-black.text-lg').get_attribute("textContent")
                link = curso.get_attribute("href")
                caminho = f'\\{index} - {titulo.replace('/','').replace('?','')}'
                self.inserir_cursos((index,titulo,link,trilha[0], caminho))
                print(f'Inserido cursos: {index},{titulo},{link},{trilha[0]}')

            print(f'Inserido todos os cursos da trilha {trilha[2]}')

        cursos = self.obter_cursos()
        for curso in cursos:
            page.get(curso[3])
            caps = page.find_element(By.CSS_SELECTOR, f'div.flex.bg-zinc-950\\/50.py-\\[4px\\].rounded-lg.pl-\\[4px\\]')
            caps = caps.find_elements(By.CSS_SELECTOR,f'div[id^="cap"]')
            indice_aula = 1
            for cap_index, cap in enumerate(caps, start=1):
                id = cap_index
                nome = cap.find_element(By.CSS_SELECTOR,f'span').get_attribute('textContent')
                curso_id = curso[0]
                caminho = f'\\{id} - {nome.replace('/','').replace('?','')}'
                self.inserir_capitulos((id, curso_id, nome,caminho))


                parent = cap.find_element(By.XPATH, '..')
                aulas = parent.find_elements(By.CSS_SELECTOR,"div[data-lesson-id]")

                for aula_index, aula in enumerate(aulas, start=1):
                    aula_id = aula.get_attribute("data-lesson-id")
                    indice = indice_aula
                    # nome = aula.find_element(By.CSS_SELECTOR,'.text-sm.overflow-hidden').text
                    nome = aula.find_element(By.CSS_SELECTOR,'.text-sm.overflow-hidden').get_attribute('textContent')
                    if nome == '' or nome is None:
                        print(nome)
                    cap_id = cap_index
                    

                    self.inserir_aulas( (aula_id, indice, nome, cap_id, curso_id) )
                    print(f'Inserido aula: {aula_id},{cap_id},{nome},{curso_id}')
                    indice_aula += 1

            print(f'Inserido todas as aulas do curso {curso[2]}')
            
        data_terminio = datetime.now()
        print(f'Iniciou em {data_inicio} e finalizou em {data_terminio}')

if __name__ == '__main__':
    print('Executar Processo de Banco de Dados')
    page = configurarChrome(True)
    page = logar(page)
    p = Progresso()
    p.run(page=page)