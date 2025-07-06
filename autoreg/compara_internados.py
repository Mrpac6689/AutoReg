import os
import csv
import unicodedata
import logging

def compara_internados():
    logging.basicConfig(
        filename=os.path.expanduser('~/AutoReg/compara_internados.log'),
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )

    print("Comparando dados...")
    logging.info("Comparando dados...")
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    arquivo_sisreg = os.path.join(user_dir, 'internados_sisreg.csv')
    arquivo_ghosp = os.path.join(user_dir, 'internados_ghosp.csv')
    arquivo_saida = os.path.join(user_dir, 'pacientes_de_alta.csv')

    if not os.path.exists(arquivo_sisreg) or not os.path.exists(arquivo_ghosp):
        print("Os arquivos internados_sisreg.csv ou internados_ghosp.csv não foram encontrados!")
        logging.error("Os arquivos internados_sisreg.csv ou internados_ghosp.csv não foram encontrados!")
        return

    with open(arquivo_sisreg, 'r', encoding='utf-8') as sisreg_file:
        sisreg_nomes_lista = [normalizar_nome(linha[0].strip()) for linha in csv.reader(sisreg_file) if linha]

    sisreg_nomes = set(sisreg_nomes_lista[1:])

    with open(arquivo_ghosp, 'r', encoding='utf-8') as ghosp_file:
        ghosp_nomes = {normalizar_nome(linha[0].strip()) for linha in csv.reader(ghosp_file) if linha}

    pacientes_a_dar_alta = sisreg_nomes - ghosp_nomes

    if pacientes_a_dar_alta:
        print("\n---===> PACIENTES A DAR ALTA <===---")
        logging.info("Pacientes a dar alta encontrados:")
        for nome in sorted(pacientes_a_dar_alta):
            print(nome)
            logging.info(f"Paciente a dar alta: {nome}")

        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Nome'])
            for nome in sorted(pacientes_a_dar_alta):
                writer.writerow([nome])

        print(f"\nA lista de pacientes a dar alta foi salva em '{arquivo_saida}'. \n")
        logging.info(f"A lista de pacientes a dar alta foi salva em '{arquivo_saida}'.")
    else:
        print("\nNenhum paciente a dar alta encontrado!")
        logging.info("Nenhum paciente a dar alta encontrado!")

def normalizar_nome(nome):
    nfkd = unicodedata.normalize('NFKD', nome)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()
