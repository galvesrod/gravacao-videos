from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException,StaleElementReferenceException
import pandas as pd
import sqlite3
from time import sleep

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
    
    def insert_trilhas(self, trilha):
        conn = self.conn
        cursor = conn.cursor()
        sql = '''insert or ignore into trilhas (indice, nome, url, id_formacao) values (?, ?, ?, ?)'''
        cursor.execute(sql, trilha)
        conn.commit()

    def inserir_cursos(self, curso):
        conn = self.conn
        cursor = conn.cursor()
        sql = '''insert or ignore into cursos (indice, nome, url, id_trilha) values (?, ?, ?, ?)'''
        cursor.execute(sql, curso)
        conn.commit()

    def inserir_capitulos(self, cap):
        conn = self.conn
        cursor = conn.cursor()
        sql = '''insert or ignore into capitulos (id, id_curso, nome) values (?, ?, ?)'''
        cursor.execute(sql, cap)
        conn.commit()
    
    def inserir_aulas(self, aula):
        conn = self.conn
        cursor = conn.cursor()
        sql = '''insert or ignore into aulas (aula_id, indice, nome, id_capitulo, id_curso  ) values (?, ?, ?, ?, ?)'''
        cursor.execute(sql, aula)
        conn.commit()

    def run(self, page:webdriver):

        formacoes = self.obter_formacoes()
        for formacao in formacoes:
            page.get(formacao[3])
            trilhas = page.find_elements(By.CSS_SELECTOR,'a[href].w-full.h-full.relative.overflow-hidden')
            for index,trilha in enumerate(trilhas,start=1):
                titulo = trilha.find_element(By.CSS_SELECTOR,'span>div>div>div:nth-child(2)' ).get_attribute("textContent")
                link = trilha.get_attribute("href")
                self.insert_trilhas((index,titulo,link,formacao[0]))
                
            print(f'Inserido todas as trilhas da formação {formacao[2]}')
        
        trilhas = self.obter_trilhas()
        for trilha in trilhas:
            page.get(trilha[3])
            cursos = page.find_elements(By.CSS_SELECTOR,'a[href].w-full.h-full')
            for index, curso in enumerate(cursos, start=1):
                titulo = curso.find_element(By.CSS_SELECTOR,'.font-black.text-lg').get_attribute("textContent")
                link = curso.get_attribute("href")
                self.inserir_cursos((index,titulo,link,trilha[0]))

            print(f'Inserido todos os cursos da formação {formacao[2]}')

        cursos = self.obter_cursos()  
        for curso in cursos:
            page.get(curso[3])
            caps = page.find_element(By.CSS_SELECTOR, f'div.flex.bg-zinc-950\\/50.py-\\[4px\\].rounded-lg.pl-\\[4px\\]')
            caps = caps.find_elements(By.CSS_SELECTOR,f'div[id^="cap"]')
            for cap_index, cap in enumerate(caps, start=1):
                id = cap_index
                nome = cap.find_element(By.CSS_SELECTOR,f'span').text
                curso_id = curso[0]
                self.inserir_capitulos((id, curso_id, nome))


                parent = cap.find_element(By.XPATH, '..')
                aulas = parent.find_elements(By.CSS_SELECTOR,"div[data-lesson-id]")

                for aula_index, aula in enumerate(aulas, start=1):
                    aula_id = aula.get_attribute("data-lesson-id")
                    indice = aula_index
                    nome = aula.find_element(By.CSS_SELECTOR,'.text-sm.overflow-hidden').text
                    cap_id = cap_index
                    
                    self.inserir_aulas( (aula_id, indice, nome, cap_id, curso_id) )
                    
                print(f'Inserido todas as aulas da formação {formacao[2]}')