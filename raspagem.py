# Importar as bibliotecas necessárias

# Para automatizar o navegador
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Para localizar os elementos na página
from selenium.webdriver.common.by import By         
from selenium.webdriver.chrome.options import Options

# Para esperar os carregamentos da página
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC

# Para manipular e exportar dados
import pandas as pd

# Para controlar pausas no código
import time


# Mostra do executável do ChromeDriver
service = Service(r"C:\Program Files\chromedriver-win64\chromedriver.exe")


options = Options()
# Faz com que rode em segundo plano, sem precisar abrir o navegador
options.add_argument("--headless") 
driver = webdriver.Chrome(service=service, options=options)

# URL do site
url = "https://masander.github.io/AlimenticiaLTDA/#/humanresources"
driver.get(url)

# Função para extrair os dados da tabela 
def extrair_tabela():
    # Espera a tabela aparecer
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    tabela = driver.find_element(By.TAG_NAME, "table")
    linhas = tabela.find_elements(By.TAG_NAME, "tr")

    dados = []
    # Percorre cada linha da tabela
    for linha in linhas:
        # Armazena os dados em td e th
        colunas = linha.find_elements(By.TAG_NAME, "td")
        if not colunas:  # Se não for uma linha de dados, é o cabeçalho
            colunas = linha.find_elements(By.TAG_NAME, "th")
        dados.append([coluna.text.strip() for coluna in colunas])
        # Retorna uma lista de listas
    return dados

# Utiliza a função para extrair os dados da tabela default de quando abre a URL
dados_frequencia = extrair_tabela()

# Depois localiza o botão "Funcionários" para mudar de tela
botao_funcionarios = driver.find_element(By.XPATH, "//button[contains(text(), 'Funcionários')]")
botao_funcionarios.click()

time.sleep(5)  # Espera 5 segundos para carregar a página  

# Chama a função novamente para extrair os dados da aba Funcionários
dados_funcionarios = extrair_tabela()


# Depois localiza o botão "Turnos" para mudar de tela
botao_turnos = driver.find_element(By.XPATH, "//button[contains(text(), 'Turnos')]")
botao_turnos.click()

time.sleep(5)  # Espera 5 segundos para carregar a página  

# Chama a função novamente para extrair os dados da aba orçamento
dados_turnos = extrair_tabela()


# Exporta os dados das duas tabelas em duas abas de um único Excel
with pd.ExcelWriter("Dados_RH.xlsx") as writer:
    pd.DataFrame(dados_frequencia[1:], columns=dados_frequencia[0]).to_excel(writer, sheet_name="Frequencia", index=False)
    pd.DataFrame(dados_funcionarios[1:], columns=dados_funcionarios[0]).to_excel(writer, sheet_name="Funcionários", index=False)
    pd.DataFrame(dados_turnos[1:], columns=dados_turnos[0]).to_excel(writer, sheet_name="Turnos", index=False)

print("Dados de pessoal exportados com sucesso!")
driver.quit()