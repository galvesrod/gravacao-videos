import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()

def logar(page:webdriver) -> webdriver:
    MAIN_URL = 'https://escola.formacao.dev/'
    LOGIN_NAME = os.getenv('LOGIN_NAME')
    PWD = os.getenv('PWD')
    page.get(MAIN_URL)
    
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/div[1]/div/input').send_keys(LOGIN_NAME)
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/div[2]/div/input').send_keys(PWD)
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/button[1]').click()
    page.find_element(By.XPATH,'//*[@id="__next"]/div[1]/div[2]/div/div')
    return page