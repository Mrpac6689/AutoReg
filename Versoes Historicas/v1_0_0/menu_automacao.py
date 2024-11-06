import os
import csv
import subprocess
import platform
import unicodedata
from colorama import init, Fore, Style

# Para captura da tecla espaço
if platform.system() == "Windows":
    import msvcrt
else:
    import sys, tty, termios

# Inicializa a colorama para cores no terminal
init(autoreset=True)

# Função para limpar a tela
def limpar_tela():
    sistema_operacional = platform.system()
    if sistema_operacional == "Windows":
        os.system("cls")
    else:
        os.system("clear")

# Função para exibir o cabeçalho do programa
def exibir_cabecalho():
    print(Fore.CYAN + "| * -------------------------------------------------------------*|")
    print(Fore.CYAN + "|          Automação de pacientes a dar alta - SISREG             |")
    print(Fore.CYAN + "|                       Versão 1.5 - Setembro de 2024             |")
    print(Fore.CYAN + "|                Michel R. Paes - Turbinado por ChatGPT           |")
    print(Fore.CYAN + "| * -------------------------------------------------------------*|")

# Função para exibir o menu de opções
def exibir_menu():
    print(Fore.YELLOW + "\n[1] Extrair internados SISREG")
    print(Fore.YELLOW + "[2] Extrair internados G-HOSP")
    print(Fore.YELLOW + "[3] Comparar e tratar dados")
    print(Fore.YELLOW + "[4] Capturar motivo da alta")
    print(Fore.YELLOW + "[5] Sair")

# Função para executar os scripts externos
def executar_script(script):
    if platform.system() == "Windows":
        subprocess.run(["python", script], shell=True)
    else:
        subprocess.run(["python3", script])

# Função para normalizar o nome (remover acentos, transformar em minúsculas)
def normalizar_nome(nome):
    # Remove acentos e transforma em minúsculas
    nfkd = unicodedata.normalize('NFKD', nome)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()

# Função para esperar pela tecla espaço
def esperar_tecla_espaco():
    print(Fore.CYAN + "\nPressione espaço para continuar...")
    
    if platform.system() == "Windows":
        while True:
            if msvcrt.getch() == b' ':
                break
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            while True:
                ch = sys.stdin.read(1)
                if ch == ' ':
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Função para comparar os arquivos CSV e salvar os pacientes a dar alta
def comparar_dados():
    # Caminho para os arquivos
    arquivo_sisreg = 'internados_sisreg.csv'
    arquivo_ghosp = 'internados_ghosp.csv'

    # Verifica se os arquivos existem
    if not os.path.exists(arquivo_sisreg) or not os.path.exists(arquivo_ghosp):
        print(Fore.RED + "\nOs arquivos internados_sisreg.csv ou internados_ghosp.csv não foram encontrados!")
        return

    # Lê os arquivos CSV
    with open(arquivo_sisreg, 'r', encoding='utf-8') as sisreg_file:
        sisreg_nomes_lista = [normalizar_nome(linha[0].strip()) for linha in csv.reader(sisreg_file) if linha]

    # Ignora a primeira linha (cabeçalho)
    sisreg_nomes = set(sisreg_nomes_lista[1:])

    with open(arquivo_ghosp, 'r', encoding='utf-8') as ghosp_file:
        ghosp_nomes = {normalizar_nome(linha[0].strip()) for linha in csv.reader(ghosp_file) if linha}

    # Encontra os pacientes a dar alta (presentes no SISREG e ausentes no G-HOSP)
    pacientes_a_dar_alta = sisreg_nomes - ghosp_nomes

    if pacientes_a_dar_alta:
        print(Fore.GREEN + "\n---===> PACIENTES A DAR ALTA <===---")
        for nome in sorted(pacientes_a_dar_alta):
            print(Fore.LIGHTYELLOW_EX + nome)  # Alterado para amarelo neon
        
        # Salva a lista em um arquivo CSV
        with open('pacientes_de_alta.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Nome'])  # Cabeçalho
            for nome in sorted(pacientes_a_dar_alta):
                writer.writerow([nome])
        
        print(Fore.CYAN + "\nA lista de pacientes a dar alta foi salva em 'pacientes_de_alta.csv'.")
        esperar_tecla_espaco()
    else:
        print(Fore.RED + "\nNenhum paciente a dar alta encontrado!")
        esperar_tecla_espaco()

# Função principal
def main():
    while True:
        limpar_tela()
        exibir_cabecalho()
        exibir_menu()

        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            limpar_tela()
            print(Fore.GREEN + "Executando extração dos internados SISREG...")
            executar_script('extrator.py')
        elif opcao == '2':
            limpar_tela()
            print(Fore.GREEN + "Executando extração dos internados G-HOSP...")
            executar_script('internhosp.py')
        elif opcao == '3':
            limpar_tela()
            print(Fore.YELLOW + "Comparando e tratando dados...")
            comparar_dados()
        elif opcao == '4':
            limpar_tela()
            print(Fore.GREEN + "Capturando motivos de alta...")
            executar_script('motivo_alta.py')
        elif opcao == '5':
            limpar_tela()
            print(Fore.CYAN + "Encerrando o programa. Até mais!")
            break
        else:
            print(Fore.RED + "Opção inválida! Tente novamente.")
            time.sleep(2)

if __name__ == '__main__':
    main()
