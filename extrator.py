from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import configparser

# Função para ler as credenciais do arquivo config.ini
def ler_credenciais():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    usuario_sisreg = config['SISREG']['usuario']
    senha_sisreg = config['SISREG']['senha']
    
    return usuario_sisreg, senha_sisreg

# Exemplo de uso no script extrator.py
usuario, senha = ler_credenciais()

# Caminho para o ChromeDriver
chrome_driver_path = "chromedriver.exe"

# Cria um serviço para o ChromeDriver
service = Service(executable_path=chrome_driver_path)

# Inicializa o navegador (Chrome neste caso) usando o serviço
driver = webdriver.Chrome(service=service)

# Acesse a página principal do SISREG
driver.get('https://sisregiii.saude.gov.br/')

try:
    print("Tentando localizar o campo de usuário...")
    usuario_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "usuario"))
    )
    print("Campo de usuário encontrado!")
    
    print("Tentando localizar o campo de senha...")
    senha_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "senha"))
    )
    print("Campo de senha encontrado!")

    # Preencha os campos de login
    print("Preenchendo o campo de usuário...")
    usuario_field.send_keys(usuario)
    
    print("Preenchendo o campo de senha...")
    senha_field.send_keys(senha)

    # Pressiona o botão de login
    print("Tentando localizar o botão de login...")
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']"))
    )
    
    print("Botão de login encontrado. Tentando fazer login...")
    login_button.click()

    time.sleep(5)
    print("Login realizado com sucesso!")

    # Agora, clica no link "Saída/Permanência"
    print("Tentando localizar o link 'Saída/Permanência'...")
    saida_permanencia_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='/cgi-bin/config_saida_permanencia' and text()='saída/permanência']"))
    )
    
    print("Link 'Saída/Permanência' encontrado. Clicando no link...")
    saida_permanencia_link.click()

    time.sleep(5)
    print("Página de Saída/Permanência acessada com sucesso!")

    # Mudança de foco para o iframe correto
    print("Tentando mudar o foco para o iframe...")
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'f_principal')))
    print("Foco alterado para o iframe.")

    # Clica no botão "PESQUISAR"
    print("Tentando localizar o botão PESQUISAR dentro do iframe...")
    pesquisar_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@name='pesquisar' and @value='PESQUISAR']"))
    )
    
    print("Botão PESQUISAR encontrado!")
    pesquisar_button.click()
    print("Botão PESQUISAR clicado!")

    time.sleep(5)

    # Extração de dados
    nomes = []
    while True:
        # Localiza as linhas da tabela com os dados
        linhas = driver.find_elements(By.XPATH, "//tr[contains(@class, 'linha_selecionavel')]")

        for linha in linhas:
            # Extrai o nome do segundo <td> dentro de cada linha
            nome = linha.find_element(By.XPATH, './td[2]').text
            nomes.append(nome)

        # Tenta localizar o botão "Próxima página"
        try:
            print("Tentando localizar a seta para a próxima página...")
            next_page_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, 'exibirPagina')]/img[@alt='Proxima']"))
            )
            print("Seta de próxima página encontrada. Clicando na seta...")
            next_page_button.click()
            time.sleep(5)  # Aguarda carregar a próxima página
        except:
            # Se não encontrar o botão "Próxima página", encerra o loop
            print("Não há mais páginas.")
            break

    # Cria um DataFrame com os nomes extraídos
    df = pd.DataFrame(nomes, columns=["Nome"])

    # Salva os dados em uma planilha CSV
    df.to_csv('internados_sisreg.csv', index=False)
    print("Dados salvos em 'internados_sisreg.csv'.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
finally:
    driver.quit()
