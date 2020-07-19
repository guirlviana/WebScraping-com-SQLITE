# use previous solution code to show how to perform an update
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import base
from models.db_models import Produto
import os
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as CondicaoExperada
import itertools


def iniciar():
    conexao = configurar_banco_de_dados()
    for i in range (1,3):
        buscar_produtos(conexao=conexao, npag=i)

def buscar_produtos(conexao, npag):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--lang=pt-BR")
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(executable_path= os.getcwd() + os.sep + 'chromedriver.exe', options=chrome_options)
    driver.get(f'https://cursoautomacao.netlify.app/produtos{npag}.html')
    wait = WebDriverWait(
        driver,
        10,
        poll_frequency=1,
        ignored_exceptions=[
            NoSuchElementException,
            ElementNotVisibleException,
            ElementNotSelectableException,
            ElementNotInteractableException
        ]
    )
    buscar_infos(driver, wait, conexao)

def configurar_banco_de_dados():
    engine = create_engine('sqlite:///produtos.db', echo=True)
    base.metadata.drop_all(bind=engine)  # Dropa estrutura atual
    base.metadata.create_all(bind=engine)  # Cria tabelas baseados na
    Conexao = sessionmaker(bind=engine)
    conexao = Conexao()
    return conexao

def buscar_infos(driver, wait, conexao):
    try:
        nomes = wait.until(CondicaoExperada.visibility_of_all_elements_located(
            (By.XPATH, '//h5[@class = "name"]' )))
        
        descricoes = wait.until(CondicaoExperada.visibility_of_all_elements_located(
            (By.XPATH, "//div[@class = 'description']")))
        
        precos = wait.until(CondicaoExperada.visibility_of_all_elements_located(
            (By.XPATH, '//p [@class="price-container"]')))

        for nome, descricao, preco in itertools.zip_longest(nomes, descricoes, precos): 
            inserir_produtos(nome.text, descricao.text, preco.text, conexao)
    except Exception as erro:
        print("Algo deu errado. Feche e tente novamente")
        
    else:
        print("Busca com sucesso")

def inserir_produtos(nome, descricao, preco, conexao):
    novo_produto = Produto()
    novo_produto.nome = nome
    novo_produto.descricao = descricao
    novo_produto.preco = preco
    conexao.add(novo_produto)
    conexao.commit()
    
if __name__ == "__main__":
    iniciar()
