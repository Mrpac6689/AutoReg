import os
import csv
import time
import random
import pandas as pd
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from autoreg.chrome_options import get_chrome_options
from datetime import datetime

def exames_ambulatorio_solicita():
    print("Solicitação de exames ambulatoriais")
    
    navegador = None
    
    chrome_options = get_chrome_options()
    navegador = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(navegador, 20)
    
    # Lê credenciais do SISREG
    config = configparser.ConfigParser()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, '..', 'config.ini')
    config.read(config_path)
    usuario_sisreg = config['SISREG-REG']['usuarioreg']
    senha_sisreg = config['SISREG-REG']['senhareg']
    
    def fazer_login():
        """Realiza o login no SISREG"""
        print("Acessando a página de login...")
        navegador.get("https://sisregiii.saude.gov.br")
        
        print("Localizando campo de usuário...")
        usuario_field = wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
        print("Campo de usuário localizado.")

        print("Localizando campo de senha...")
        senha_field = wait.until(EC.presence_of_element_located((By.NAME, "senha")))
        print("Campo de senha localizado.")

        print("Preenchendo usuário...")
        usuario_field.clear()
        usuario_field.send_keys(usuario_sisreg)
        print("Usuário preenchido.")
        
        print("Preenchendo senha...")
        senha_field.clear()
        senha_field.send_keys(senha_sisreg)
        print("Senha preenchida.")
        
        print("Aguardando antes de clicar no botão de login...")
        time.sleep(5)

        print("Localizando botão de login...")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='entrar' and @value='entrar']")))
        print("Botão de login localizado.")

        print("Clicando no botão de login...")
        login_button.click()
        print("Botão de login clicado.")
        
        time.sleep(5)
        print("Login realizado com sucesso!")
    
    def verificar_erro_sistema():
        """Verifica se há erro de sistema na página atual"""
        try:
            # Procura por tabela com título "ERRO DE SISTEMA"
            erro_elementos = navegador.find_elements(By.XPATH, "//table//*[contains(text(), 'ERRO DE SISTEMA')]")
            if erro_elementos:
                print("   ⚠️  ERRO DE SISTEMA detectado na página!")
                return True
            
            # Também verifica no texto da página
            page_text = navegador.find_element(By.TAG_NAME, "body").text
            if "ERRO DE SISTEMA" in page_text.upper():
                print("   ⚠️  ERRO DE SISTEMA detectado na página!")
                return True
                
            return False
        except Exception as e:
            # Se houver erro ao verificar, assume que não há erro
            return False
    
    # Realiza o login inicial
    fazer_login()
    
    # Verifica erro após login
    if verificar_erro_sistema():
        print("   🔄 Refazendo login devido a erro de sistema...")
        fazer_login()


    # Configuração dos diretórios e arquivos
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_exames = os.path.join(user_dir, 'exames_solicitar.csv')
    
    # verificar se o csv existe
    print("\n📋 Etapa 1: Extraindo informações dos exames a solicitar...")
    try:
        # Verifica se o arquivo existe para pegar o cabeçalho
        if os.path.exists(csv_exames):
            df = pd.read_csv(csv_exames)
            colunas = df.columns.tolist()
            print(f"   ✅ Arquivo encontrado com colunas: {', '.join(colunas)}")
            if 'ra' not in colunas:
                print(f"   ❌ Coluna 'ra' não encontrada no arquivo. Colunas disponíveis: {', '.join(colunas)}")
                return None
            
            # Remove linhas em branco (onde 'ra' está vazio, é NaN ou contém apenas espaços)
            linhas_antes = len(df)
            
            # Remove linhas onde 'ra' está vazio, é NaN ou contém apenas espaços (coluna principal obrigatória)
            df = df[df['ra'].notna()]  # Remove NaN
            df = df[df['ra'].astype(str).str.strip() != '']  # Remove strings vazias ou apenas espaços
            
            linhas_depois = len(df)
            linhas_removidas = linhas_antes - linhas_depois
            if linhas_removidas > 0:
                print(f"   🧹 {linhas_removidas} linha(s) em branco removida(s). {linhas_depois} linha(s) válida(s) restante(s).")
            else:
                print(f"   ✅ Nenhuma linha em branco encontrada. {linhas_depois} linha(s) válida(s).")
        else:
            print(f"   ❌ Arquivo não encontrado: {csv_exames}, crie o arquivo com o cabeçalho: 'ra' e insira a lista de prontuarios a pesquisar")
            return None

    except Exception as e:
        print(f"❌ Erro ao extrair informações dos exames a solicitar: {e}")
        return None

    # Garante que as colunas necessárias existem no DataFrame
    if 'procedimento' not in df.columns:
        df['procedimento'] = ''
    if 'contraste' not in df.columns:
        df['contraste'] = ''
    if 'dividir' not in df.columns:
        df['dividir'] = ''
    if 'chave' not in df.columns:
        df['chave'] = ''
    if 'solicitacao' not in df.columns:
        df['solicitacao'] = ''
    if 'erro' not in df.columns:
        df['erro'] = ''
    
    # Processa divisão de procedimentos múltiplos quando 'dividir' = 's'
    print("\n📋 Etapa 1.5: Verificando necessidade de divisão de procedimentos...")
    linhas_antes_divisao = len(df)
    linhas_para_expandir = []
    indices_para_remover = []
    
    for index, row in df.iterrows():
        dividir = str(row.get('dividir', '')).strip().upper() if pd.notna(row.get('dividir')) else ''
        procedimento = str(row.get('procedimento', '')).strip() if pd.notna(row.get('procedimento')) else ''
        
        # Verifica se precisa dividir e se há procedimentos múltiplos
        if dividir == 'S' and procedimento and '|' in procedimento:
            # Divide os procedimentos pelo delimitador '|'
            procedimentos_lista = [p.strip() for p in procedimento.split('|') if p.strip()]
            
            if len(procedimentos_lista) > 1:
                # Cria novas linhas para cada procedimento
                for proc in procedimentos_lista:
                    nova_linha = row.copy()
                    nova_linha['procedimento'] = proc
                    nova_linha['dividir'] = ''  # Remove o 's' para evitar erros
                    linhas_para_expandir.append(nova_linha)
                
                # Marca a linha original para remoção
                indices_para_remover.append(index)
    
    # Remove linhas originais que foram divididas
    if indices_para_remover:
        df = df.drop(indices_para_remover)
        print(f"   🗑️  {len(indices_para_remover)} linha(s) original(is) removida(s) para divisão.")
    
    # Adiciona as novas linhas expandidas
    if linhas_para_expandir:
        df_novas_linhas = pd.DataFrame(linhas_para_expandir)
        df = pd.concat([df, df_novas_linhas], ignore_index=True)
        df = df.reset_index(drop=True)  # Garante índices sequenciais
        linhas_depois_divisao = len(df)
        linhas_criadas = linhas_depois_divisao - linhas_antes_divisao + len(indices_para_remover)
        print(f"   ✅ {linhas_criadas} nova(s) linha(s) criada(s) a partir da divisão de procedimentos múltiplos.")
        print(f"   📊 Total de linhas após divisão: {linhas_depois_divisao} (antes: {linhas_antes_divisao})")
        
        # Salva o CSV após a divisão
        try:
            df.to_csv(csv_exames, index=False)
            print(f"   💾 CSV atualizado e salvo com as linhas divididas em: {csv_exames}")
        except Exception as e:
            print(f"   ⚠️  Erro ao salvar CSV após divisão: {e}")
    else:
        print(f"   ✅ Nenhuma divisão necessária. Todas as linhas estão prontas para processamento.")
    
    # Dicionário de correlação GHOSP → SISREG
    dicionario_correlacao = {
        'ANGIO-TC DA AORTA TORÁCICA': 'ANGIO-TC DA AORTA TORÁCICA',
        'ANGIO-TC DAS ARTÉRIAS CERVICAIS': 'ANGIO-TC DAS ARTÉRIAS CERVICAIS',
        'ANGIO-TC DE AORTA ABDOMINAL': 'ANGIOTOMOGRAFIA DE ABDOMEN SUPERIOR',
        'ANGIO-TC DE ARTÉRIAS ILÍACAS': 'ANGIOTOMOGRAFIA DE ABDOMEM INFERIOR',
        'ANGIOTOMOGRAFIA CEREBRAL': 'ANGIOTOMOGRAFIA CEREBRAL',
        'ANGIOTOMOGRAFIA DE ABDOMEM INFERIOR': 'ANGIOTOMOGRAFIA DE ABDOMEM INFERIOR',
        'ANGIOTOMOGRAFIA DE ABDOMEM SUPERIOR': 'ANGIOTOMOGRAFIA DE ABDOMEN SUPERIOR',
        'TOMOGRAFIA COMPUTADORIZADA COLUNA CERVICAL - INTERNADOS': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA CERVICAL C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA COLUNA CERVICAL - INTERNADOS - COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA CERVICAL C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA COLUNA CERVICAL - INTERNADOS - SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA CERVICAL C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA COLUNA DORSAL - INTERNADOS - COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA TORACICA C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA COLUNA DORSAL - INTERNADOS - SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA TORACICA C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA COLUNA LOMBAR - INTERNADOS -COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA LOMBO-SACRA C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA COLUNA LOMBAR - INTERNADOS- SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA LOMBO-SACRA C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA DA COXA DIREITA - INTERNADOS -COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE ARTICULACOES DE MEMBRO INFERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DA COXA DIREITA - INTERNADOS - SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE ARTICULACOES DE MEMBRO INFERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DA MAO ESQUERDA - INTERNADOS - COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE ARTICULACOES DE MEMBRO SUPERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DA MAO ESQUERDA - INTERNADOS- SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE ARTICULACOES DE MEMBRO SUPERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DA PERNA DIREITA - INTERNADOS - COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE ARTICULACOES DE MEMBRO INFERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DA PERNA DIREITA - INTERNADOS - SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE ARTICULACOES DE MEMBRO INFERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DAS ARTICULACOES JOELHOS - INTERNADOS -COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DAS ARTICULACOES- JOELHOS',
        'TOMOGRAFIA COMPUTADORIZADA DAS ARTICULACOES JOELHOS - INTERNADOS - SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DAS ARTICULACOES- JOELHOS',
        'TOMOGRAFIA COMPUTADORIZADA DE ARTICULACOES DE MEMBRO INFERIOR': 'TOMOGRAFIA COMPUTADORIZADA DE ARTICULACOES DE MEMBRO INFERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DE ARTICULACOES DE MEMBRO SUPERIOR': 'TOMOGRAFIA COMPUTADORIZADA DE ARTICULACOES DE MEMBRO SUPERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DE COLUNA CERVICAL C/ OU S/ CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA CERVICAL C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA DE COLUNA LOMBO-SACRA C/ OU S/ CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA LOMBO-SACRA C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA DE COLUNA LOMBO-SACRA - INTERNADOS': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA LOMBO-SACRA C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA DE COLUNA TORACICA C/ OU S/ CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA TORACICA C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA DE COLUNA TORACICA - INTERNADOS': 'TOMOGRAFIA COMPUTADORIZADA DE COLUNA TORACICA C/ OU S/ CONTRASTE',
        'TOMOGRAFIA COMPUTADORIZADA DE CRANIO - INTERNADOS': 'TOMOGRAFIA COMPUTADORIZADA DO CRANIO',
        'TOMOGRAFIA COMPUTADORIZADA DE CRANIO - INTERNADOS - COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DO CRANIO',
        'TOMOGRAFIA COMPUTADORIZADA DE CRANIO - INTERNADOS - SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DO CRANIO',
        'TOMOGRAFIA COMPUTADORIZADA DO CRANIO': 'TOMOGRAFIA COMPUTADORIZADA DO CRANIO',
        'TOMOGRAFIA COMPUTADORIZADA DE FACE OU SEIOS DE FACE - INTERNADOS - COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE FACE / SEIOS DA FACE',
        'TOMOGRAFIA COMPUTADORIZADA DE FACE OU SEIOS DE FACE - INTERNADOS - SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE FACE / SEIOS DA FACE',
        'TOMOGRAFIA COMPUTADORIZADA DE FACE / SEIOS DA FACE / ARTICULACOES - INTERNADOS': 'TOMOGRAFIA COMPUTADORIZADA DE FACE / SEIOS DA FACE',
        'TOMOGRAFIA COMPUTADORIZADA DE FACE / SEIOS DA FACE / ARTICULACOES TEMPORO-MANDIBULARES': 'TOMOGRAFIA COMPUTADORIZADA DE FACE / SEIOS DA FACE',
        'TOMOGRAFIA COMPUTADORIZADA DE MASTOIDES OU OUVIDOS - INTERNADOS - COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE MASTOIDES OU OUVIDOS',
        'TOMOGRAFIA COMPUTADORIZADA DE MASTOIDES OU OUVIDOS - INTERNADOS - SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE MASTOIDES OU OUVIDOS',
        'TOMOGRAFIA COMPUTADORIZADA DE PELVE / BACIA / ABDOMEN INFERIOR - INTERNADOS': 'TOMOGRAFIA COMPUTADORIZADA DE PELVE / BACIA / ABDOMEN INFERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DE PELVE / BACIA / ABDOMEN INFERIOR - COM CONTARSTE': 'TOMOGRAFIA COMPUTADORIZADA DE PELVE / BACIA / ABDOMEN INFERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DE PELVE / BACIA / ABDOMEN INFERIOR - COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE PELVE / BACIA / ABDOMEN INFERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DE PELVE OU BACIA - INTERNADOS - COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE PELVE / BACIA / ABDOMEN INFERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DE PELVE OU BACIA - INTERNADOS - SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DE PELVE / BACIA / ABDOMEN INFERIOR',
        'ANGIOTOMOGRAFIA DE ABDOMEN SUPERIOR - COM CONTARSTE': 'ANGIOTOMOGRAFIA DE ABDOMEN SUPERIOR',
        'ANGIOTOMOGRAFIA DE ABDOMEN SUPERIOR - COM CONTRASTE': 'ANGIOTOMOGRAFIA DE ABDOMEN SUPERIOR',
        'TOMOGRAFIA COMPUTADORIZADA DE PESCOCO - INTERNADOS': 'TOMOGRAFIA COMPUTADORIZADA DO PESCOCO',
        'TOMOGRAFIA COMPUTADORIZADA DE PESCOCO - INTERNADOS - COM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DO PESCOCO',
        'TOMOGRAFIA COMPUTADORIZADA DE PESCOCO - INTERNADOS - SEM CONTRASTE': 'TOMOGRAFIA COMPUTADORIZADA DO PESCOCO',
        'TOMOGRAFIA COMPUTADORIZADA DO PESCOCO': 'TOMOGRAFIA COMPUTADORIZADA DO PESCOCO'
    }
    
    def normalizar_texto(texto):
        """Normaliza texto para comparação (maiúsculas, remove espaços extras)"""
        return ' '.join(texto.upper().strip().split())
    
    def identificar_tipo_exame(procedimento):
        """
        Identifica o tipo de exame no procedimento.
        
        Args:
            procedimento: Procedimento do CSV
        
        Returns:
            'TOMOGRAFIA', 'ANGIO-TC', 'ANGIOTOMOGRAFIA' ou None
        """
        proc_normalizado = normalizar_texto(procedimento)
        
        if 'ANGIO-TC' in proc_normalizado or 'ANGIO TC' in proc_normalizado:
            return 'ANGIO-TC'
        elif 'ANGIOTOMOGRAFIA' in proc_normalizado:
            return 'ANGIOTOMOGRAFIA'
        elif 'TOMOGRAFIA' in proc_normalizado:
            return 'TOMOGRAFIA'
        
        return None
    
    def identificar_parte_corpo(procedimento):
        """
        Identifica a parte do corpo no procedimento.
        
        Args:
            procedimento: Procedimento do CSV
        
        Returns:
            String com a parte do corpo identificada ou None
        """
        proc_normalizado = normalizar_texto(procedimento)
        
        # Lista de partes do corpo em ordem de especificidade (mais específicas primeiro)
        # Cada item é uma tupla: (termo_busca, parte_identificada)
        partes_corpo = [
            ('AORTA TORÁCICA', 'AORTA TORÁCICA'),
            ('AORTA TORACICA', 'AORTA TORÁCICA'),
            ('TORAX', 'TORAX'),
            ('TÓRAX', 'TORAX'),
            ('ARTÉRIAS CERVICAIS', 'ARTÉRIAS CERVICAIS'),
            ('ARTÉRIAS ILÍACAS', 'ARTÉRIAS ILÍACAS'),
            ('ARTÉRIAS ILIACAS', 'ARTÉRIAS ILÍACAS'),
            ('AORTA ABDOMINAL', 'AORTA ABDOMINAL'),
            ('CEREBRAL', 'CEREBRAL'),
            ('PELVE / BACIA / ABDOMEN INFERIOR', 'PELVE / BACIA / ABDOMEN INFERIOR'),
            ('PELVE / BACIA / ABDOMEM INFERIOR', 'PELVE / BACIA / ABDOMEN INFERIOR'),
            ('PELVE OU BACIA', 'PELVE / BACIA / ABDOMEN INFERIOR'),
            ('PELVE', 'PELVE / BACIA / ABDOMEN INFERIOR'),
            ('BACIA', 'PELVE / BACIA / ABDOMEN INFERIOR'),
            ('ABDOMEM INFERIOR', 'ABDOMEM INFERIOR'),
            ('ABDOMEN INFERIOR', 'ABDOMEM INFERIOR'),
            ('ABDOMEM SUPERIOR', 'ABDOMEM SUPERIOR'),
            ('ABDOMEN SUPERIOR', 'ABDOMEM SUPERIOR'),
            ('COLUNA LOMBO-SACRA', 'COLUNA LOMBO-SACRA'),
            ('COLUNA LOMBAR', 'COLUNA LOMBAR'),
            ('COLUNA DORSAL', 'COLUNA DORSAL'),
            ('COLUNA CERVICAL', 'COLUNA CERVICAL'),
            ('ARTICULACOES JOELHOS', 'ARTICULACOES JOELHOS'),
            ('ARTICULAÇÕES JOELHOS', 'ARTICULACOES JOELHOS'),
            ('JOELHOS', 'ARTICULACOES JOELHOS'),
            ('COXA DIREITA', 'COXA DIREITA'),
            ('COXA ESQUERDA', 'COXA ESQUERDA'),
            ('PERNA DIREITA', 'PERNA DIREITA'),
            ('PERNA ESQUERDA', 'PERNA ESQUERDA'),
            ('MAO DIREITA', 'MAO DIREITA'),
            ('MAO ESQUERDA', 'MAO ESQUERDA'),
            ('MÃO DIREITA', 'MAO DIREITA'),
            ('MÃO ESQUERDA', 'MAO ESQUERDA'),
            ('SEIOS DA FACE', 'SEIOS DA FACE'),
            ('SEIOS DE FACE', 'SEIOS DA FACE'),
            ('FACE', 'FACE'),
            ('MASTOIDES OU OUVIDOS', 'MASTOIDES OU OUVIDOS'),
            ('MASTÓIDES OU OUVIDOS', 'MASTOIDES OU OUVIDOS'),
            ('CRANIO', 'CRANIO'),
            ('CRÂNIO', 'CRANIO'),
            ('PESCOCO', 'PESCOCO'),
            ('PESCOÇO', 'PESCOCO')
        ]
        
        for termo_busca, parte_identificada in partes_corpo:
            # Busca o termo no texto normalizado
            if termo_busca in proc_normalizado:
                # Para termos de uma palavra como "TORAX", verifica se não é parte de outro termo
                # Ex: "TORAX" não deve ser encontrado dentro de "AORTA TORÁCICA"
                if termo_busca == 'TORAX' or termo_busca == 'TÓRAX':
                    # Verifica se não está dentro de "AORTA TORÁCICA" (que já foi verificado antes na lista)
                    if 'AORTA TORÁCICA' not in proc_normalizado and 'AORTA TORACICA' not in proc_normalizado:
                        return parte_identificada
                else:
                    return parte_identificada
        
        return None
    
    def determinar_tipo_contraste(ghosp_exame, contraste_csv):
        """
        Determina qual tipo de contraste deve ser selecionado no SISREG.
        
        Args:
            ghosp_exame: Procedimento do GHOSP (vem do CSV como 'procedimento')
            contraste_csv: Valor da coluna 'contraste' do CSV ('S' ou vazio)
        
        Returns:
            'COM_CONTRASTE', 'SEM_CONTRASTE' ou None
        """
        ghosp_normalizado = normalizar_texto(ghosp_exame)
        contraste_solicitado = contraste_csv and contraste_csv.upper() == 'S'
        
        # Se contraste='S' no CSV, obrigatoriamente escolher COM CONTRASTE
        if contraste_solicitado:
            return 'COM_CONTRASTE'
        
        # Caso contrário, seguir a lógica baseada no texto do GHOSP
        if 'C/ OU S/ CONTRASTE' in ghosp_normalizado or 'C/ OU S/ CONTARSTE' in ghosp_normalizado:
            return 'SEM_CONTRASTE'
        elif 'COM CONTRASTE' in ghosp_normalizado or 'COM CONTARSTE' in ghosp_normalizado:
            return 'COM_CONTRASTE'
        else:
            return 'SEM_CONTRASTE'
    
    def calcular_similaridade_termos_chave(proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste_necessario):
        """
        Calcula similaridade baseada em termos-chave: tipo de exame, parte do corpo e contraste.
        
        Args:
            proc_csv: Procedimento do CSV
            texto_opcao: Texto da opção na tabela SISREG
            tipo_exame: Tipo de exame identificado ('TOMOGRAFIA', 'ANGIO-TC', 'ANGIOTOMOGRAFIA')
            parte_corpo: Parte do corpo identificada
            tipo_contraste_necessario: 'COM_CONTRASTE' ou 'SEM_CONTRASTE'
        
        Returns:
            Score de similaridade (0.0 a 1.0)
        """
        proc_normalizado = normalizar_texto(proc_csv)
        opcao_normalizada = normalizar_texto(texto_opcao)
        
        score = 0.0
        
        # 1. Verifica tipo de exame (peso alto: 0.4)
        tipo_exame_encontrado = False
        if tipo_exame:
            if tipo_exame == 'ANGIO-TC':
                if 'ANGIO-TC' in opcao_normalizada or 'ANGIO TC' in opcao_normalizada or 'ANGIOTOMOGRAFIA' in opcao_normalizada:
                    score += 0.4
                    tipo_exame_encontrado = True
            elif tipo_exame == 'ANGIOTOMOGRAFIA':
                if 'ANGIOTOMOGRAFIA' in opcao_normalizada or 'ANGIO-TC' in opcao_normalizada or 'ANGIO TC' in opcao_normalizada:
                    score += 0.4
                    tipo_exame_encontrado = True
            elif tipo_exame == 'TOMOGRAFIA':
                # Para TOMOGRAFIA, verifica se tem "TOMOGRAFIA" mas NÃO "ANGIOTOMOGRAFIA"
                # Isso evita que "TOMOGRAFIA" seja encontrado dentro de "ANGIOTOMOGRAFIA"
                if 'TOMOGRAFIA' in opcao_normalizada and 'ANGIOTOMOGRAFIA' not in opcao_normalizada:
                    score += 0.4
                    tipo_exame_encontrado = True
                    # Bônus adicional se tem "TOMOGRAFIA COMPUTADORIZADA" (mais específico)
                    if 'TOMOGRAFIA COMPUTADORIZADA' in opcao_normalizada:
                        score += 0.1
        
        # 2. Verifica parte do corpo (peso muito alto: 0.5)
        if parte_corpo:
            # Normaliza variações comuns (incluindo ABDOMEN/ABDOMEM)
            parte_normalizada = parte_corpo.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
            parte_normalizada = parte_normalizada.replace('Ç', 'C')
            # Normaliza ABDOMEN/ABDOMEM para comparação flexível
            parte_normalizada = parte_normalizada.replace('ABDOMEM', 'ABDOMEN')
            
            opcao_sem_acentos = opcao_normalizada.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
            opcao_sem_acentos = opcao_sem_acentos.replace('Ç', 'C')
            # Normaliza ABDOMEN/ABDOMEM na opção também
            opcao_sem_acentos = opcao_sem_acentos.replace('ABDOMEM', 'ABDOMEN')
            
            # Verifica correspondência exata
            if parte_normalizada in opcao_sem_acentos:
                score += 0.5
            else:
                # Tenta correspondência parcial (palavras-chave)
                # Remove caracteres especiais para comparação
                parte_limpa = parte_normalizada.replace('/', ' ').replace('-', ' ').replace('  ', ' ')
                opcao_limpa = opcao_sem_acentos.replace('/', ' ').replace('-', ' ').replace('  ', ' ')
                
                palavras_parte = [p for p in parte_limpa.split() if len(p) > 2]
                palavras_opcao = opcao_limpa.split()
                
                # Conta quantas palavras-chave da parte do corpo aparecem na opção
                palavras_encontradas = sum(1 for palavra in palavras_parte if palavra in palavras_opcao)
                
                if palavras_encontradas > 0:
                    # Calcula score proporcional
                    proporcao = palavras_encontradas / len(palavras_parte)
                    score += 0.4 * proporcao
                    
                    # Bônus se encontrou palavras-chave importantes
                    palavras_importantes = ['PELVE', 'BACIA', 'ABDOMEN', 'ABDOMEM', 'COLUNA', 'CERVICAL', 
                                          'DORSAL', 'LOMBAR', 'CRANIO', 'FACE', 'PESCOCO', 'JOELHOS', 'SUPERIOR', 'INFERIOR', 'TORAX', 'TÓRAX']
                    palavras_importantes_encontradas = sum(1 for palavra in palavras_parte if palavra in palavras_importantes and palavra in palavras_opcao)
                    if palavras_importantes_encontradas > 0:
                        # Se encontrou palavras importantes, garante score mínimo
                        bonus = 0.15 * min(1.0, palavras_importantes_encontradas / len(palavras_parte))
                        score += bonus
                        
                        # Se encontrou todas as palavras importantes, garante score alto
                        if palavras_importantes_encontradas == len([p for p in palavras_parte if p in palavras_importantes]):
                            score = max(score, 0.5)  # Garante pelo menos 0.5 se todas palavras importantes foram encontradas
        
        # 3. Verifica contraste (peso: 0.1 se corresponder, pequena penalização se não corresponder)
        tem_com_contraste = 'COM CONTRASTE' in opcao_normalizada or 'COM CONTARSTE' in opcao_normalizada
        tem_sem_contraste = 'SEM CONTRASTE' in opcao_normalizada or 'SEM CONTARSTE' in opcao_normalizada
        tem_c_ou_s_contraste = 'C/ OU S/ CONTRASTE' in opcao_normalizada or 'C/ OU S/ CONTARSTE' in opcao_normalizada
        nao_mentiona_contraste = not tem_com_contraste and not tem_sem_contraste and not tem_c_ou_s_contraste
        
        # Salva o score antes de aplicar contraste para garantir mínimo se tipo e parte estão corretos
        score_base = score
        
        if tipo_contraste_necessario == 'COM_CONTRASTE':
            if tem_com_contraste or tem_c_ou_s_contraste:
                # Bônus se tem o contraste correto
                score += 0.1
            elif nao_mentiona_contraste:
                # Se não menciona contraste, aceita (pode ser que não esteja explícito)
                score += 0.05
            else:
                # Penaliza levemente se tem SEM CONTRASTE quando deveria ter COM
                # Mas não deixa cair abaixo de 0.5 se tipo e parte estão corretos
                if tipo_exame_encontrado and score_base >= 0.4:
                    score = max(score * 0.7, 0.5)
                else:
                    score *= 0.7
        elif tipo_contraste_necessario == 'SEM_CONTRASTE':
            if tem_sem_contraste or tem_c_ou_s_contraste or nao_mentiona_contraste:
                # Bônus se tem SEM CONTRASTE, C/ OU S/ CONTRASTE, ou não menciona
                score += 0.1
            else:
                # Penaliza levemente se tem COM CONTRASTE quando deveria ser SEM
                # Mas não deixa cair abaixo de 0.5 se tipo e parte estão corretos
                if tipo_exame_encontrado and score_base >= 0.4:
                    score = max(score * 0.7, 0.5)
                else:
                    score *= 0.7
        
        return min(1.0, score)
    
    # Itera sobre os links do CSV
    for index, row in df.iterrows():
        try:
            # Verifica se a linha já foi processada (tem conteúdo em solicitacao e chave)
            chave = row.get('chave', '').strip() if pd.notna(row.get('chave')) else ''
            solicitacao = row.get('solicitacao', '').strip() if pd.notna(row.get('solicitacao')) else ''
            
            if chave and solicitacao:
                print(f"\n[{index + 1}/{len(df)}] ⏭️  Linha já processada (chave: {chave}, solicitação: {solicitacao}). Pulando...")
                continue
            
            cns_val = row.get('cns', '')
            procedimento = row.get('procedimento', '').strip() if pd.notna(row.get('procedimento')) else ''
            contraste = row.get('contraste', '').strip() if pd.notna(row.get('contraste')) else ''
            
            # Valida e converte CNS para número
            if pd.notna(cns_val) and str(cns_val).strip() != '':
                try:
                    cns_float = float(cns_val)
                    # Remove o .0 se for um número inteiro
                    cns = int(cns_float) if cns_float.is_integer() else cns_float
                except (ValueError, TypeError):
                    print(f"   ❌ Erro: valor inválido na coluna 'cns': '{cns_val}'. Pulando registro...")
                    continue
            else:
                print(f"   ❌ Erro: coluna 'cns' está vazia. Pulando registro...")
                continue
            print(f"\n[{index + 1}/{len(df)}] Processando Solicitação para o CNS: {cns}")
            if contraste and contraste.upper() == 'S':
                print(f"   ℹ️  Contraste obrigatório: apenas procedimentos 'COM CONTRASTE' serão selecionados")
            navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
            time.sleep(2)
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Retorna à página de marcação após login
                navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
            
            # Aguarda a página carregar e localiza o campo CNS
            print("   Aguardando campo CNS carregar...")
            cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
            print(f"   Campo CNS localizado. Inserindo CNS: {cns}")
            
            # Limpa o campo e insere o CNS
            cns_field.clear()
            cns_field.send_keys(str(cns))
            print("   CNS inserido com sucesso.")
            
            # Localiza e clica no botão pesquisar
            print("   Localizando botão pesquisar...")
            pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
            print("   Botão pesquisar localizado. Clicando...")
            pesquisar_button.click()
            print("   Botão pesquisar clicado com sucesso.")
            
            time.sleep(2)  # Aguarda a pesquisa ser processada
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Retorna à página de marcação após login
                navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
                # Reinsere o CNS e clica em pesquisar novamente
                cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                cns_field.clear()
                cns_field.send_keys(str(cns))
                pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                pesquisar_button.click()
                time.sleep(2)
            
            # Localiza e clica no botão continuar
            print("   Localizando botão continuar...")
            continuar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_continuar")))
            print("   Botão continuar localizado. Clicando...")
            continuar_button.click()
            print("   Botão continuar clicado com sucesso.")
            
            time.sleep(2)  # Aguarda a próxima tela carregar
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Retorna ao fluxo após login
                navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
                cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                cns_field.clear()
                cns_field.send_keys(str(cns))
                pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                pesquisar_button.click()
                time.sleep(2)
                continuar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_continuar")))
                continuar_button.click()
                time.sleep(2)
            
            # Seleciona o procedimento no dropdown "pa"
            print("   Localizando dropdown de procedimento (pa)...")
            pa_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "pa")))
            pa_select = Select(pa_dropdown)
            print("   Selecionando 'XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS'...")
            
            # Tenta selecionar pelo value primeiro
            try:
                pa_select.select_by_value("0045000")
                print("   Procedimento selecionado com sucesso (por value).")
            except Exception as e:
                print(f"   ⚠️  Não foi possível selecionar por value, tentando por texto...")
                # Fallback: tenta selecionar pelo texto
                try:
                    pa_select.select_by_visible_text("XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS")
                    print("   Procedimento selecionado com sucesso (por texto).")
                except Exception as e2:
                    print(f"   ❌ Erro ao selecionar procedimento: {e2}")
                    # Tenta buscar por texto parcial
                    try:
                        for option in pa_select.options:
                            if "TOMOGRAFIA COMPUTADORIZADA - INTERNADOS" in option.text:
                                pa_select.select_by_visible_text(option.text)
                                print(f"   Procedimento selecionado com sucesso (por texto parcial): {option.text}")
                                break
                        else:
                            raise Exception("Nenhuma opção de tomografia encontrada no dropdown")
                    except Exception as e3:
                        print(f"   ❌ Erro ao selecionar procedimento por texto parcial: {e3}")
                        raise
            
            # Preenche o campo CID10
            print("   Localizando campo CID10...")
            cid10_field = wait.until(EC.presence_of_element_located((By.NAME, "cid10")))
            print("   Campo CID10 localizado. Inserindo 'R68'...")
            cid10_field.clear()
            cid10_field.send_keys("R68")
            print("   CID10 inserido com sucesso.")
            
            # Seleção aleatória no dropdown de profissional
            print("   Localizando dropdown de profissional (cpfprofsol)...")
            cpfprofsol_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "cpfprofsol")))
            cpfprofsol_select = Select(cpfprofsol_dropdown)
            
            # Obtém todas as opções disponíveis (exceto a primeira que geralmente é vazia)
            opcoes = [opt for opt in cpfprofsol_select.options if opt.get_attribute("value")]
            if opcoes:
                opcao_aleatoria = random.choice(opcoes)
                valor_aleatorio = opcao_aleatoria.get_attribute("value")
                texto_aleatorio = opcao_aleatoria.text
                print(f"   Selecionando profissional aleatório: {texto_aleatorio} (value: {valor_aleatorio})...")
                cpfprofsol_select.select_by_value(valor_aleatorio)
                print("   Profissional selecionado com sucesso.")
            else:
                print("   ⚠️  Nenhuma opção disponível no dropdown de profissional.")
            
            # Seleciona a unidade de execução
            print("   Localizando dropdown de unidade de execução (upsexec)...")
            upsexec_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "upsexec")))
            upsexec_select = Select(upsexec_dropdown)
            print("   Selecionando unidade com value '6861849'...")
            upsexec_select.select_by_value("6861849")
            print("   Unidade de execução selecionada com sucesso.")
            
            # Clica no botão OK
            print("   Localizando botão OK...")
            ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK']")))
            print("   Botão OK localizado. Clicando...")
            ok_button.click()
            print("   Botão OK clicado com sucesso.")
            
            time.sleep(2)  # Aguarda a próxima tela carregar
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Retorna ao fluxo após login (precisa refazer todo o processo)
                navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
                cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                cns_field.clear()
                cns_field.send_keys(str(cns))
                pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                pesquisar_button.click()
                time.sleep(2)
                continuar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_continuar")))
                continuar_button.click()
                time.sleep(2)
                # Refaz seleções
                pa_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "pa")))
                pa_select = Select(pa_dropdown)
                try:
                    pa_select.select_by_value("0045000")
                except:
                    pa_select.select_by_visible_text("XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS")
                cid10_field = wait.until(EC.presence_of_element_located((By.NAME, "cid10")))
                cid10_field.clear()
                cid10_field.send_keys("R68")
                cpfprofsol_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "cpfprofsol")))
                cpfprofsol_select = Select(cpfprofsol_dropdown)
                opcoes = [opt for opt in cpfprofsol_select.options if opt.get_attribute("value")]
                if opcoes:
                    opcao_aleatoria = random.choice(opcoes)
                    cpfprofsol_select.select_by_value(opcao_aleatoria.get_attribute("value"))
                upsexec_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "upsexec")))
                upsexec_select = Select(upsexec_dropdown)
                upsexec_select.select_by_value("6861849")
                ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK']")))
                ok_button.click()
                time.sleep(2)

            # Compara os procedimentos do CSV com as opções disponíveis na tabela
            if procedimento:
                # Separa os procedimentos pelo delimitador "|"
                procedimentos_lista = [p.strip() for p in procedimento.split('|') if p.strip()]
                print(f"   Encontrados {len(procedimentos_lista)} procedimento(s) para processar")
                
                # Aguarda a tabela carregar
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
                
                # Encontra todos os checkboxes na tabela
                checkboxes = navegador.find_elements(By.XPATH, "//table[@class='table_listagem']//input[@type='checkbox']")
                
                checkboxes_marcados = []
                
                # Para cada procedimento do CSV
                for proc_idx, proc_csv in enumerate(procedimentos_lista, 1):
                    print(f"   [{proc_idx}/{len(procedimentos_lista)}] Buscando procedimento correspondente a: {proc_csv}")
                    
                    # Identifica termos-chave: tipo de exame e parte do corpo
                    tipo_exame = identificar_tipo_exame(proc_csv)
                    parte_corpo = identificar_parte_corpo(proc_csv)
                    tipo_contraste = determinar_tipo_contraste(proc_csv, contraste)
                    
                    if not tipo_exame:
                        print(f"      ⚠️  Não foi possível identificar o tipo de exame em '{proc_csv}'")
                        continue
                    
                    if not parte_corpo:
                        print(f"      ⚠️  Não foi possível identificar a parte do corpo em '{proc_csv}'")
                        continue
                    
                    print(f"      🔍 Tipo de exame identificado: {tipo_exame}")
                    print(f"      🔍 Parte do corpo identificada: {parte_corpo}")
                    print(f"      ℹ️  Tipo de contraste necessário: {tipo_contraste}")
                    
                    melhor_similaridade = 0.0
                    checkbox_selecionado = None
                    texto_selecionado = ""
                    
                    # Compara cada opção da tabela usando termos-chave
                    for checkbox in checkboxes:
                        # Pula checkboxes já marcados
                        if checkbox in checkboxes_marcados:
                            continue
                            
                        # Obtém o texto da opção (texto do elemento pai td)
                        try:
                            td = checkbox.find_element(By.XPATH, "./..")
                            texto_opcao = td.text.strip()
                            
                            # Calcula similaridade baseada em termos-chave
                            similaridade = calcular_similaridade_termos_chave(
                                proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste
                            )
                            
                            if similaridade > melhor_similaridade:
                                melhor_similaridade = similaridade
                                checkbox_selecionado = checkbox
                                texto_selecionado = texto_opcao
                        except Exception as e:
                            continue
                    
                    # Marca o checkbox encontrado (threshold mínimo de 0.5)
                    if checkbox_selecionado and melhor_similaridade >= 0.5:
                        print(f"      ✅ Procedimento encontrado: {texto_selecionado} (similaridade: {melhor_similaridade:.2%})")
                        if not checkbox_selecionado.is_selected():
                            checkbox_selecionado.click()
                        checkboxes_marcados.append(checkbox_selecionado)
                        print(f"      ✅ Checkbox marcado com sucesso.")
                    else:
                        if checkbox_selecionado:
                            print(f"      ⚠️  Nenhum procedimento correspondente encontrado para '{proc_csv}'")
                            print(f"      📊 Melhor opção encontrada: '{texto_selecionado}' (similaridade: {melhor_similaridade:.2%}, threshold: 0.50)")
                        else:
                            print(f"      ⚠️  Nenhum procedimento correspondente encontrado para '{proc_csv}' (nenhuma opção com similaridade > 0)")
                
                print(f"   ✅ Total de {len(checkboxes_marcados)} checkbox(es) marcado(s) de {len(procedimentos_lista)} procedimento(s)")
            else:
                print("   ⚠️  Procedimento não informado no CSV, pulando seleção.")
            
            # Clica no botão Confirmar
            print("   Localizando botão Confirmar...")
            confirmar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnConfirmar")))
            print("   Botão Confirmar localizado. Clicando...")
            confirmar_button.click()
            print("   Botão Confirmar clicado com sucesso.")
            
            time.sleep(2)  # Aguarda a próxima tela carregar
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Retorna ao fluxo após login (precisa refazer todo o processo)
                navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                time.sleep(2)
                cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                cns_field.clear()
                cns_field.send_keys(str(cns))
                pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                pesquisar_button.click()
                time.sleep(2)
                continuar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_continuar")))
                continuar_button.click()
                time.sleep(2)
                # Refaz seleções
                pa_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "pa")))
                pa_select = Select(pa_dropdown)
                try:
                    pa_select.select_by_value("0045000")
                except:
                    pa_select.select_by_visible_text("XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS")
                cid10_field = wait.until(EC.presence_of_element_located((By.NAME, "cid10")))
                cid10_field.clear()
                cid10_field.send_keys("R68")
                cpfprofsol_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "cpfprofsol")))
                cpfprofsol_select = Select(cpfprofsol_dropdown)
                opcoes = [opt for opt in cpfprofsol_select.options if opt.get_attribute("value")]
                if opcoes:
                    opcao_aleatoria = random.choice(opcoes)
                    cpfprofsol_select.select_by_value(opcao_aleatoria.get_attribute("value"))
                upsexec_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "upsexec")))
                upsexec_select = Select(upsexec_dropdown)
                upsexec_select.select_by_value("6861849")
                ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK']")))
                ok_button.click()
                time.sleep(2)
                # Refaz marcação de checkboxes se houver procedimentos
                if procedimento:
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
                    checkboxes = navegador.find_elements(By.XPATH, "//table[@class='table_listagem']//input[@type='checkbox']")
                    checkboxes_marcados = []
                    procedimentos_lista = [p.strip() for p in procedimento.split('|') if p.strip()]
                    for proc_csv in procedimentos_lista:
                        # Identifica termos-chave: tipo de exame e parte do corpo
                        tipo_exame = identificar_tipo_exame(proc_csv)
                        parte_corpo = identificar_parte_corpo(proc_csv)
                        tipo_contraste = determinar_tipo_contraste(proc_csv, contraste)
                        
                        if not tipo_exame or not parte_corpo:
                            continue
                        
                        melhor_similaridade = 0.0
                        checkbox_selecionado = None
                        
                        # Compara cada opção da tabela usando termos-chave
                        for checkbox in checkboxes:
                            if checkbox in checkboxes_marcados:
                                continue
                            try:
                                td = checkbox.find_element(By.XPATH, "./..")
                                texto_opcao = td.text.strip()
                                
                                # Calcula similaridade baseada em termos-chave
                                similaridade = calcular_similaridade_termos_chave(
                                    proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste
                                )
                                
                                if similaridade > melhor_similaridade:
                                    melhor_similaridade = similaridade
                                    checkbox_selecionado = checkbox
                            except:
                                continue
                        
                        if checkbox_selecionado and melhor_similaridade >= 0.5:
                            if not checkbox_selecionado.is_selected():
                                checkbox_selecionado.click()
                            checkboxes_marcados.append(checkbox_selecionado)
                    
                    confirmar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnConfirmar")))
                    confirmar_button.click()
                    time.sleep(2)
        
            # Localiza e clica no link que expande a tabela de vagas
            print("   Localizando link para expandir tabela de vagas...")
            try:
                # Procura pelo elemento com onclick contendo controleVagas('divUnidade0')
                vagas_link = wait.until(EC.element_to_be_clickable((
                    By.XPATH, 
                    "//td[@onclick=\"controleVagas('divUnidade0');\"]"
                )))
                print("   Link encontrado. Clicando para expandir tabela...")
                vagas_link.click()
                print("   Link clicado com sucesso.")
                time.sleep(1)  # Aguarda a tabela expandir
                
                # Verifica erro de sistema após mudança de página
                if verificar_erro_sistema():
                    print("   🔄 Refazendo login devido a erro de sistema...")
                    fazer_login()
                    # Se houver erro após clicar em vagas, precisa refazer todo o processo
                    print("   ⚠️  Erro após seleção de vagas. Processo precisa ser reiniciado manualmente.")
                    continue
            except TimeoutException:
                print("   ⚠️  Link de expansão não encontrado, tentando localizar tabela diretamente...")
            
            # Aguarda a tabela de vagas aparecer
            print("   Aguardando tabela de vagas carregar...")
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
            
            # Seleciona o primeiro radio button disponível
            print("   Localizando primeiro radio button disponível...")
            try:
                # Encontra o primeiro radio button com name="vagas" que está visível
                primeiro_radio = wait.until(EC.presence_of_element_located((
                    By.XPATH,
                    "//input[@type='radio' and @name='vagas']"
                )))
                
                # Verifica se está visível e clicável
                if primeiro_radio.is_displayed():
                    print("   Primeiro radio button encontrado. Selecionando...")
                    primeiro_radio.click()
                    print("   Radio button selecionado com sucesso.")
                else:
                    # Tenta usar JavaScript para clicar se não estiver visível
                    navegador.execute_script("arguments[0].click();", primeiro_radio)
                    print("   Radio button selecionado via JavaScript.")
            except TimeoutException:
                print("   ⚠️  Nenhum radio button disponível encontrado.")
            
            time.sleep(1)  # Aguarda a seleção ser processada
            
            
            # Clica no botão Próxima Etapa
            print("   Localizando botão Próxima Etapa...")
            proxima_etapa_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnProximaEtapa")))
            print("   Botão Próxima Etapa localizado. Clicando...")
            proxima_etapa_button.click()
            print("   Botão Próxima Etapa clicado com sucesso.")
            
            time.sleep(2)  # Aguarda a próxima tela carregar
            
            # Verifica erro de sistema após mudança de página
            if verificar_erro_sistema():
                print("   🔄 Refazendo login devido a erro de sistema...")
                fazer_login()
                # Se houver erro após próxima etapa, precisa refazer todo o processo
                print("   ⚠️  Erro após próxima etapa. Processo precisa ser reiniciado manualmente.")
                continue

            # Extrai a chave da solicitação
            print("   Extraindo chave da solicitação...")
            chave_valor = ''
            try:
                chave_element = wait.until(EC.presence_of_element_located((
                    By.XPATH,
                    '//*[@id="fichaCompleta"]/table[1]/tbody/tr[2]/td/b'
                )))
                chave_valor = chave_element.text.strip()
                print(f"   ✅ Chave extraída: {chave_valor}")
                df.at[index, 'chave'] = chave_valor
            except TimeoutException:
                print("   ⚠️  Campo de chave não encontrado.")
                df.at[index, 'chave'] = ''
            except Exception as e:
                print(f"   ❌ Erro ao extrair chave: {e}")
                df.at[index, 'chave'] = ''
            
            # Extrai o número da solicitação
            print("   Extraindo número da solicitação...")
            solicitacao_valor = ''
            try:
                solicitacao_element = wait.until(EC.presence_of_element_located((
                    By.XPATH,
                    '/html/body/div[2]/form/div[1]/div/table[5]/tbody/tr[3]/td[1]/font/b'
                )))
                solicitacao_valor = solicitacao_element.text.strip()
                print(f"   ✅ Solicitação extraída: {solicitacao_valor}")
                df.at[index, 'solicitacao'] = solicitacao_valor
            except TimeoutException:
                print("   ⚠️  Campo de solicitação não encontrado.")
                df.at[index, 'solicitacao'] = ''
            except Exception as e:
                print(f"   ❌ Erro ao extrair solicitação: {e}")
                df.at[index, 'solicitacao'] = ''
            
            # Verifica se chave e solicitação foram extraídas; se não, captura o conteúdo da página
            if not chave_valor and not solicitacao_valor:
                print("   ⚠️  Chave e solicitação não encontradas. Capturando conteúdo da página...")
                try:
                    # Captura o texto visível da página
                    conteudo_pagina = navegador.find_element(By.TAG_NAME, "body").text.strip()
                    # Limita o tamanho para não sobrecarregar o CSV (primeiros 500 caracteres)
                    conteudo_erro = conteudo_pagina[:500] if len(conteudo_pagina) > 500 else conteudo_pagina
                    if len(conteudo_pagina) > 500:
                        conteudo_erro += "... (conteúdo truncado)"
                    df.at[index, 'erro'] = conteudo_erro
                    print(f"   ✅ Conteúdo da página capturado e salvo na coluna 'erro'")
                except Exception as e:
                    print(f"   ❌ Erro ao capturar conteúdo da página: {e}")
                    df.at[index, 'erro'] = f"Erro ao capturar conteúdo: {str(e)}"
            else:
                # Limpa a coluna erro se a solicitação foi bem-sucedida
                df.at[index, 'erro'] = ''
            
            # Salva o CSV após extrair os dados
            try:
                df.to_csv(csv_exames, index=False)
                print(f"   💾 CSV atualizado com chave, solicitação e erro (se houver)")
            except Exception as e:
                print(f"   ⚠️  Erro ao salvar CSV: {e}")

        
        except Exception as e:
            print(f"❌ Erro ao processar solicitação para o CNS: {e}")
            continue
    
    # Salva o CSV final após processar todos os registros
    print("\n💾 Salvando CSV final...")
    try:
        df.to_csv(csv_exames, index=False)
        print(f"✅ CSV salvo com sucesso em: {csv_exames}")
        print(f"📊 Total de registros processados: {len(df)}")
    except Exception as e:
        print(f"❌ Erro ao salvar CSV final: {e}")
    
    # Verifica se há registros pendentes e reprocessa
    max_tentativas = 3  # Limite de tentativas para evitar loop infinito
    tentativa = 0
    
    while tentativa < max_tentativas:
        # Recarrega o CSV para verificar registros pendentes
        try:
            df_atualizado = pd.read_csv(csv_exames)
            
            # Garante que as colunas necessárias existem no DataFrame atualizado
            if 'procedimento' not in df_atualizado.columns:
                df_atualizado['procedimento'] = ''
            if 'contraste' not in df_atualizado.columns:
                df_atualizado['contraste'] = ''
            if 'erro' not in df_atualizado.columns:
                df_atualizado['erro'] = ''
            
            # Identifica registros pendentes (sem chave ou sem solicitacao)
            registros_pendentes = df_atualizado[
                (df_atualizado['chave'].isna() | (df_atualizado['chave'].astype(str).str.strip() == '')) |
                (df_atualizado['solicitacao'].isna() | (df_atualizado['solicitacao'].astype(str).str.strip() == ''))
            ]
            
            if len(registros_pendentes) == 0:
                print("\n✅ Todos os registros foram processados com sucesso!")
                break
            
            tentativa += 1
            print(f"\n🔄 Tentativa {tentativa}/{max_tentativas}: Encontrados {len(registros_pendentes)} registro(s) pendente(s)")
            print("   Reprocessando registros pendentes...")
            
            # Processa apenas os registros pendentes
            for index, row in registros_pendentes.iterrows():
                try:
                    # Verifica novamente se ainda está pendente (pode ter sido processado em outra tentativa)
                    chave_val = row.get('chave', '')
                    chave = str(chave_val).strip() if pd.notna(chave_val) and chave_val != '' else ''
                    
                    solicitacao_val = row.get('solicitacao', '')
                    solicitacao = str(solicitacao_val).strip() if pd.notna(solicitacao_val) and solicitacao_val != '' else ''
                    
                    if chave and solicitacao:
                        print(f"   ⏭️  Registro {index + 1} já foi processado. Pulando...")
                        continue
                    
                    cns_val = row.get('cns', '')
                    procedimento_val = row.get('procedimento', '')
                    procedimento = str(procedimento_val).strip() if pd.notna(procedimento_val) and procedimento_val != '' else ''
                    contraste_val = row.get('contraste', '')
                    contraste = str(contraste_val).strip() if pd.notna(contraste_val) and contraste_val != '' else ''
                    
                    # Valida e converte CNS para número
                    if pd.notna(cns_val) and str(cns_val).strip() != '':
                        try:
                            cns_float = float(cns_val)
                            cns = int(cns_float) if cns_float.is_integer() else cns_float
                        except (ValueError, TypeError):
                            print(f"   ❌ Erro: valor inválido na coluna 'cns': '{cns_val}'. Pulando registro...")
                            continue
                    else:
                        print(f"   ❌ Erro: coluna 'cns' está vazia. Pulando registro...")
                        continue
                    print(f"\n[{index + 1}/{len(registros_pendentes)}] Reprocessando CNS: {cns}")
                    if contraste and contraste.upper() == 'S':
                        print(f"   ℹ️  Contraste obrigatório: apenas procedimentos 'COM CONTRASTE' serão selecionados")
                    
                    navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                    time.sleep(2)
                    
                    # Verifica erro de sistema após mudança de página
                    if verificar_erro_sistema():
                        print("   🔄 Refazendo login devido a erro de sistema...")
                        fazer_login()
                        # Retorna à página de marcação após login
                        navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                        time.sleep(2)
                    
                    # Aguarda a página carregar e localiza o campo CNS
                    print("   Aguardando campo CNS carregar...")
                    cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                    print(f"   Campo CNS localizado. Inserindo CNS: {cns}")
                    
                    # Limpa o campo e insere o CNS
                    cns_field.clear()
                    cns_field.send_keys(str(cns))
                    print("   CNS inserido com sucesso.")
                    
                    # Localiza e clica no botão pesquisar
                    print("   Localizando botão pesquisar...")
                    pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                    print("   Botão pesquisar localizado. Clicando...")
                    pesquisar_button.click()
                    print("   Botão pesquisar clicado com sucesso.")
                    
                    time.sleep(2)  # Aguarda a pesquisa ser processada
                    
                    # Verifica erro de sistema após mudança de página
                    if verificar_erro_sistema():
                        print("   🔄 Refazendo login devido a erro de sistema...")
                        fazer_login()
                        # Retorna à página de marcação após login
                        navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                        time.sleep(2)
                        # Reinsere o CNS e clica em pesquisar novamente
                        cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                        cns_field.clear()
                        cns_field.send_keys(str(cns))
                        pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                        pesquisar_button.click()
                        time.sleep(2)
                    
                    # Continua com o restante do processamento...
                    # (código similar ao loop principal, mas sem repetir tudo aqui)
                    # Por simplicidade, vou reutilizar a mesma lógica do loop principal
                    # mas apenas para os registros pendentes
                    
                    # Seleciona o procedimento no dropdown "pa"
                    print("   Localizando dropdown de procedimento (pa)...")
                    pa_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "pa")))
                    pa_select = Select(pa_dropdown)
                    print("   Selecionando 'XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS'...")
                    
                    try:
                        pa_select.select_by_value("0045000")
                        print("   Procedimento selecionado com sucesso (por value).")
                    except Exception as e:
                        print(f"   ⚠️  Não foi possível selecionar por value, tentando por texto...")
                        try:
                            pa_select.select_by_visible_text("XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS")
                            print("   Procedimento selecionado com sucesso (por texto).")
                        except Exception as e2:
                            print(f"   ❌ Erro ao selecionar procedimento: {e2}")
                            continue
                    
                    # Preenche o campo CID10
                    print("   Localizando campo CID10...")
                    cid10_field = wait.until(EC.presence_of_element_located((By.NAME, "cid10")))
                    print("   Campo CID10 localizado. Inserindo 'R68'...")
                    cid10_field.clear()
                    cid10_field.send_keys("R68")
                    print("   CID10 inserido com sucesso.")
                    
                    # Seleção aleatória no dropdown de profissional
                    print("   Localizando dropdown de profissional (cpfprofsol)...")
                    cpfprofsol_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "cpfprofsol")))
                    cpfprofsol_select = Select(cpfprofsol_dropdown)
                    
                    opcoes = [opt for opt in cpfprofsol_select.options if opt.get_attribute("value")]
                    if opcoes:
                        opcao_aleatoria = random.choice(opcoes)
                        valor_aleatorio = opcao_aleatoria.get_attribute("value")
                        texto_aleatorio = opcao_aleatoria.text
                        print(f"   Selecionando profissional aleatório: {texto_aleatorio} (value: {valor_aleatorio})...")
                        cpfprofsol_select.select_by_value(valor_aleatorio)
                        print("   Profissional selecionado com sucesso.")
                    else:
                        print("   ⚠️  Nenhuma opção disponível no dropdown de profissional.")
                    
                    # Seleciona a unidade de execução
                    print("   Localizando dropdown de unidade de execução (upsexec)...")
                    upsexec_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "upsexec")))
                    upsexec_select = Select(upsexec_dropdown)
                    print("   Selecionando unidade com value '6861849'...")
                    upsexec_select.select_by_value("6861849")
                    print("   Unidade de execução selecionada com sucesso.")
                    
                    # Clica no botão OK
                    print("   Localizando botão OK...")
                    ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK']")))
                    print("   Botão OK localizado. Clicando...")
                    ok_button.click()
                    print("   Botão OK clicado com sucesso.")
                    
                    time.sleep(2)  # Aguarda a próxima tela carregar
                    
                    # Verifica erro de sistema após mudança de página
                    if verificar_erro_sistema():
                        print("   🔄 Refazendo login devido a erro de sistema...")
                        fazer_login()
                        # Retorna ao fluxo após login (precisa refazer todo o processo)
                        navegador.get(f"https://sisregiii.saude.gov.br/cgi-bin/cadweb50?url=/cgi-bin/marcar")
                        time.sleep(2)
                        cns_field = wait.until(EC.presence_of_element_located((By.NAME, "nu_cns")))
                        cns_field.clear()
                        cns_field.send_keys(str(cns))
                        pesquisar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_pesquisar")))
                        pesquisar_button.click()
                        time.sleep(2)
                        continuar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btn_continuar")))
                        continuar_button.click()
                        time.sleep(2)
                        # Refaz seleções
                        pa_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "pa")))
                        pa_select = Select(pa_dropdown)
                        try:
                            pa_select.select_by_value("0045000")
                        except:
                            pa_select.select_by_visible_text("XXXXXXXXXX - GRUPO - TOMOGRAFIA COMPUTADORIZADA - INTERNADOS")
                        cid10_field = wait.until(EC.presence_of_element_located((By.NAME, "cid10")))
                        cid10_field.clear()
                        cid10_field.send_keys("R68")
                        cpfprofsol_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "cpfprofsol")))
                        cpfprofsol_select = Select(cpfprofsol_dropdown)
                        opcoes = [opt for opt in cpfprofsol_select.options if opt.get_attribute("value")]
                        if opcoes:
                            opcao_aleatoria = random.choice(opcoes)
                            cpfprofsol_select.select_by_value(opcao_aleatoria.get_attribute("value"))
                        upsexec_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "upsexec")))
                        upsexec_select = Select(upsexec_dropdown)
                        upsexec_select.select_by_value("6861849")
                        ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK']")))
                        ok_button.click()
                        time.sleep(2)
                    
                    # Compara os procedimentos do CSV com as opções disponíveis na tabela
                    if procedimento:
                        procedimentos_lista = [p.strip() for p in procedimento.split('|') if p.strip()]
                        print(f"   Encontrados {len(procedimentos_lista)} procedimento(s) para processar")
                        
                        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
                        checkboxes = navegador.find_elements(By.XPATH, "//table[@class='table_listagem']//input[@type='checkbox']")
                        checkboxes_marcados = []
                        
                        for proc_idx, proc_csv in enumerate(procedimentos_lista, 1):
                            print(f"   [{proc_idx}/{len(procedimentos_lista)}] Buscando procedimento correspondente a: {proc_csv}")
                            
                            # Identifica termos-chave: tipo de exame e parte do corpo
                            tipo_exame = identificar_tipo_exame(proc_csv)
                            parte_corpo = identificar_parte_corpo(proc_csv)
                            tipo_contraste = determinar_tipo_contraste(proc_csv, contraste)
                            
                            if not tipo_exame:
                                print(f"      ⚠️  Não foi possível identificar o tipo de exame em '{proc_csv}'")
                                continue
                            
                            if not parte_corpo:
                                print(f"      ⚠️  Não foi possível identificar a parte do corpo em '{proc_csv}'")
                                continue
                            
                            print(f"      🔍 Tipo de exame identificado: {tipo_exame}")
                            print(f"      🔍 Parte do corpo identificada: {parte_corpo}")
                            print(f"      ℹ️  Tipo de contraste necessário: {tipo_contraste}")
                            
                            melhor_similaridade = 0.0
                            checkbox_selecionado = None
                            texto_selecionado = ""
                            
                            # Compara cada opção da tabela usando termos-chave
                            for checkbox in checkboxes:
                                # Pula checkboxes já marcados
                                if checkbox in checkboxes_marcados:
                                    continue
                                    
                                # Obtém o texto da opção (texto do elemento pai td)
                                try:
                                    td = checkbox.find_element(By.XPATH, "./..")
                                    texto_opcao = td.text.strip()
                                    
                                    # Calcula similaridade baseada em termos-chave
                                    similaridade = calcular_similaridade_termos_chave(
                                        proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste
                                    )
                                    
                                    if similaridade > melhor_similaridade:
                                        melhor_similaridade = similaridade
                                        checkbox_selecionado = checkbox
                                        texto_selecionado = texto_opcao
                                except Exception as e:
                                    continue
                            
                            # Marca o checkbox encontrado (threshold mínimo de 0.5)
                            if checkbox_selecionado and melhor_similaridade >= 0.5:
                                print(f"      ✅ Procedimento encontrado: {texto_selecionado} (similaridade: {melhor_similaridade:.2%})")
                                if not checkbox_selecionado.is_selected():
                                    checkbox_selecionado.click()
                                checkboxes_marcados.append(checkbox_selecionado)
                                print(f"      ✅ Checkbox marcado com sucesso.")
                            else:
                                print(f"      ⚠️  Nenhum procedimento correspondente encontrado para '{proc_csv}' (melhor similaridade: {melhor_similaridade:.2%})")
                        
                        print(f"   ✅ Total de {len(checkboxes_marcados)} checkbox(es) marcado(s) de {len(procedimentos_lista)} procedimento(s)")
                    else:
                        print("   ⚠️  Procedimento não informado no CSV, pulando seleção.")
                    
                    # Clica no botão Confirmar
                    print("   Localizando botão Confirmar...")
                    confirmar_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnConfirmar")))
                    print("   Botão Confirmar localizado. Clicando...")
                    confirmar_button.click()
                    print("   Botão Confirmar clicado com sucesso.")
                    
                    time.sleep(2)  # Aguarda a próxima tela carregar
                    
                    # Verifica erro de sistema após mudança de página
                    if verificar_erro_sistema():
                        print("   🔄 Refazendo login devido a erro de sistema...")
                        fazer_login()
                        # Se houver erro após confirmar, precisa refazer todo o processo
                        print("   ⚠️  Erro após confirmar. Processo precisa ser reiniciado manualmente.")
                        continue
                    
                    # Localiza e clica no link que expande a tabela de vagas
                    print("   Localizando link para expandir tabela de vagas...")
                    try:
                        vagas_link = wait.until(EC.element_to_be_clickable((
                            By.XPATH, 
                            "//td[@onclick=\"controleVagas('divUnidade0');\"]"
                        )))
                        print("   Link encontrado. Clicando para expandir tabela...")
                        vagas_link.click()
                        print("   Link clicado com sucesso.")
                        time.sleep(1)
                        
                        # Verifica erro de sistema após mudança de página
                        if verificar_erro_sistema():
                            print("   🔄 Refazendo login devido a erro de sistema...")
                            fazer_login()
                            print("   ⚠️  Erro após seleção de vagas. Processo precisa ser reiniciado manualmente.")
                            continue
                    except TimeoutException:
                        print("   ⚠️  Link de expansão não encontrado, tentando localizar tabela diretamente...")
                    
                    # Aguarda a tabela de vagas aparecer
                    print("   Aguardando tabela de vagas carregar...")
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
                    
                    # Seleciona o primeiro radio button disponível
                    print("   Localizando primeiro radio button disponível...")
                    try:
                        primeiro_radio = wait.until(EC.presence_of_element_located((
                            By.XPATH,
                            "//input[@type='radio' and @name='vagas']"
                        )))
                        
                        if primeiro_radio.is_displayed():
                            print("   Primeiro radio button encontrado. Selecionando...")
                            primeiro_radio.click()
                            print("   Radio button selecionado com sucesso.")
                        else:
                            navegador.execute_script("arguments[0].click();", primeiro_radio)
                            print("   Radio button selecionado via JavaScript.")
                    except TimeoutException:
                        print("   ⚠️  Nenhum radio button disponível encontrado.")
                    
                    time.sleep(1)
                    
                    # Clica no botão Próxima Etapa
                    print("   Localizando botão Próxima Etapa...")
                    proxima_etapa_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnProximaEtapa")))
                    print("   Botão Próxima Etapa localizado. Clicando...")
                    proxima_etapa_button.click()
                    print("   Botão Próxima Etapa clicado com sucesso.")
                    
                    time.sleep(2)
                    
                    # Verifica erro de sistema após mudança de página
                    if verificar_erro_sistema():
                        print("   🔄 Refazendo login devido a erro de sistema...")
                        fazer_login()
                        # Se houver erro após próxima etapa, precisa refazer todo o processo
                        print("   ⚠️  Erro após próxima etapa. Processo precisa ser reiniciado manualmente.")
                        continue
                    
                    # Extrai a chave da solicitação
                    print("   Extraindo chave da solicitação...")
                    chave_valor = ''
                    try:
                        chave_element = wait.until(EC.presence_of_element_located((
                            By.XPATH,
                            '//*[@id="fichaCompleta"]/table[1]/tbody/tr[2]/td/b'
                        )))
                        chave_valor = chave_element.text.strip()
                        print(f"   ✅ Chave extraída: {chave_valor}")
                        df_atualizado.at[index, 'chave'] = chave_valor
                    except TimeoutException:
                        print("   ⚠️  Campo de chave não encontrado.")
                        df_atualizado.at[index, 'chave'] = ''
                    except Exception as e:
                        print(f"   ❌ Erro ao extrair chave: {e}")
                        df_atualizado.at[index, 'chave'] = ''
                    
                    # Extrai o número da solicitação
                    print("   Extraindo número da solicitação...")
                    solicitacao_valor = ''
                    try:
                        solicitacao_element = wait.until(EC.presence_of_element_located((
                            By.XPATH,
                            '/html/body/div[2]/form/div[1]/div/table[5]/tbody/tr[3]/td[1]/font/b'
                        )))
                        solicitacao_valor = solicitacao_element.text.strip()
                        print(f"   ✅ Solicitação extraída: {solicitacao_valor}")
                        
                        # Remove o .0 da solicitação se for um número inteiro
                        try:
                            solicitacao_float = float(solicitacao_valor)
                            solicitacao_valor = str(int(solicitacao_float)) if solicitacao_float.is_integer() else str(solicitacao_float)
                        except (ValueError, TypeError):
                            pass
                        
                        df_atualizado.at[index, 'solicitacao'] = solicitacao_valor
                    except TimeoutException:
                        print("   ⚠️  Campo de solicitação não encontrado.")
                        df_atualizado.at[index, 'solicitacao'] = ''
                    except Exception as e:
                        print(f"   ❌ Erro ao extrair solicitação: {e}")
                        df_atualizado.at[index, 'solicitacao'] = ''
                    
                    # Verifica se chave e solicitação foram extraídas; se não, captura o conteúdo da página
                    if not chave_valor and not solicitacao_valor:
                        print("   ⚠️  Chave e solicitação não encontradas. Capturando conteúdo da página...")
                        try:
                            # Captura o texto visível da página
                            conteudo_pagina = navegador.find_element(By.TAG_NAME, "body").text.strip()
                            # Limita o tamanho para não sobrecarregar o CSV (primeiros 500 caracteres)
                            conteudo_erro = conteudo_pagina[:500] if len(conteudo_pagina) > 500 else conteudo_pagina
                            if len(conteudo_pagina) > 500:
                                conteudo_erro += "... (conteúdo truncado)"
                            df_atualizado.at[index, 'erro'] = conteudo_erro
                            print(f"   ✅ Conteúdo da página capturado e salvo na coluna 'erro'")
                        except Exception as e:
                            print(f"   ❌ Erro ao capturar conteúdo da página: {e}")
                            df_atualizado.at[index, 'erro'] = f"Erro ao capturar conteúdo: {str(e)}"
                    else:
                        # Limpa a coluna erro se a solicitação foi bem-sucedida
                        df_atualizado.at[index, 'erro'] = ''
                    
                    # Salva o CSV após extrair os dados
                    try:
                        df_atualizado.to_csv(csv_exames, index=False)
                        print(f"   💾 CSV atualizado com chave, solicitação e erro (se houver)")
                    except Exception as e:
                        print(f"   ⚠️  Erro ao salvar CSV: {e}")
                    
                except Exception as e:
                    print(f"❌ Erro ao reprocessar registro {index + 1}: {e}")
                    continue
            
            # Atualiza o DataFrame principal com os dados atualizados
            df = df_atualizado
            
        except Exception as e:
            print(f"❌ Erro ao verificar registros pendentes: {e}")
            break
    
    if tentativa >= max_tentativas:
        print(f"\n⚠️  Limite de {max_tentativas} tentativas atingido. Alguns registros podem estar pendentes.")
    
    # Salva o CSV final após todas as tentativas
    print("\n💾 Salvando CSV final...")
    try:
        df.to_csv(csv_exames, index=False)
        print(f"✅ CSV salvo com sucesso em: {csv_exames}")
        print(f"📊 Total de registros processados: {len(df)}")
    except Exception as e:
        print(f"❌ Erro ao salvar CSV final: {e}")
    
    # Fecha o navegador
    if navegador:
        navegador.quit()
        print("✅ Navegador fechado")
    
    return