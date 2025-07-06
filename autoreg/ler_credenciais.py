# autoreg/ler_credenciais.py
#      Automatiza a extração dos códigos de internação de pacientes na página de internação do SISREG III utilizando Selenium.
#      Esta função realiza o login no sistema SISREG III,
#      navega até a seção de internação e percorre todos os registros de pacientes disponíveis,
#      extraindo o nome de cada paciente e o código de internação ("ficha").
#      Os dados extraídos são salvos em um arquivo CSV no diretório ~/AutoReg do usuário.
import sys
import os
import configparser

def ler_credenciais():
    config = configparser.ConfigParser()
    if getattr(sys, 'frozen', False):
        # Executável PyInstaller
        base_dir = os.path.dirname(sys.executable)
    else:
        # Script Python
        base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, '..', 'config.ini')
    config.read(config_path)
    usuario_sisreg = config['SISREG']['usuario']
    senha_sisreg = config['SISREG']['senha']
    usuario_ghosp = config['G-HOSP']['usuario']
    senha_ghosp = config['G-HOSP']['senha']
    caminho_ghosp = config['G-HOSP']['caminho']
    return usuario_ghosp, senha_ghosp, caminho_ghosp, usuario_sisreg, senha_sisreg
