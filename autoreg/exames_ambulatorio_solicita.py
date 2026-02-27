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
from datetime import datetime, timedelta

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
    if 'solicita' not in df.columns:
        df['solicita'] = ''
    if 'erro' not in df.columns:
        df['erro'] = ''
    # Garante tipo object para colunas que recebem string (evita FutureWarning ao atribuir)
    for col in ['chave', 'solicitacao', 'erro', 'solicita']:
        if col in df.columns:
            df[col] = df[col].astype(object)
    
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
    
    # Importa as funções auxiliares do módulo compartilhado
    from autoreg import exames_utils
    
    # Cria aliases locais para manter compatibilidade com o código existente
    normalizar_texto = exames_utils.normalizar_texto
    identificar_tipo_exame = exames_utils.identificar_tipo_exame
    identificar_parte_corpo = exames_utils.identificar_parte_corpo
    identificar_lateralidade = exames_utils.identificar_lateralidade
    
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
    
    # As funções normalizar_texto, identificar_tipo_exame, identificar_parte_corpo e identificar_lateralidade
    # agora são importadas do módulo compartilhado exames_utils (definidas acima como aliases locais)
    
    def verificar_cranio_e_orbita(procedimento):
        """
        Verifica se o procedimento menciona tanto CRANIO quanto ÓRBITA.
        Neste caso, CRANIO deve ser selecionado duas vezes.
        
        Args:
            procedimento: Procedimento do CSV
        
        Returns:
            True se há menção a ambos CRANIO e ÓRBITA, False caso contrário
        """
        proc_normalizado = normalizar_texto(procedimento)
        
        tem_cranio = 'CRANIO' in proc_normalizado or 'CRÂNIO' in proc_normalizado
        tem_orbita = 'ORBITA' in proc_normalizado or 'ÓRBITA' in proc_normalizado
        
        return tem_cranio and tem_orbita
    
    def opcao_corresponde_tipo_exame(texto_opcao, tipo_exame):
        """
        Verifica se a opção corresponde ao tipo de exame especificado.
        
        Args:
            texto_opcao: Texto da opção na tabela SISREG
            tipo_exame: Tipo de exame identificado ('TOMOGRAFIA', 'ANGIO-TC', 'ANGIOTOMOGRAFIA')
        
        Returns:
            True se corresponde, False caso contrário
        """
        opcao_normalizada = normalizar_texto(texto_opcao)
        
        if tipo_exame == 'ANGIO-TC':
            return 'ANGIO-TC' in opcao_normalizada or 'ANGIO TC' in opcao_normalizada or 'ANGIOTOMOGRAFIA' in opcao_normalizada
        elif tipo_exame == 'ANGIOTOMOGRAFIA':
            return 'ANGIOTOMOGRAFIA' in opcao_normalizada or 'ANGIO-TC' in opcao_normalizada or 'ANGIO TC' in opcao_normalizada
        elif tipo_exame == 'TOMOGRAFIA':
            # Para TOMOGRAFIA, verifica se tem "TOMOGRAFIA" mas NÃO "ANGIOTOMOGRAFIA"
            return 'TOMOGRAFIA' in opcao_normalizada and 'ANGIOTOMOGRAFIA' not in opcao_normalizada
        
        return False
    
    def opcao_corresponde_parte_corpo(texto_opcao, parte_corpo):
        """
        Verifica se a opção corresponde à parte do corpo especificada.
        Usa verificação rigorosa para evitar correspondências incorretas.
        
        Args:
            texto_opcao: Texto da opção na tabela SISREG
            parte_corpo: Parte do corpo identificada
        
        Returns:
            True se corresponde, False caso contrário
        """
        opcao_normalizada = normalizar_texto(texto_opcao)
        
        # Normaliza variações comuns (incluindo ABDOMEN/ABDOMEM)
        parte_normalizada = parte_corpo.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        parte_normalizada = parte_normalizada.replace('Ç', 'C')
        parte_normalizada = parte_normalizada.replace('ABDOMEM', 'ABDOMEN')
        
        opcao_sem_acentos = opcao_normalizada.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        opcao_sem_acentos = opcao_sem_acentos.replace('Ç', 'C')
        opcao_sem_acentos = opcao_sem_acentos.replace('ABDOMEM', 'ABDOMEN')
        
        # Verifica correspondência exata primeiro
        if parte_normalizada in opcao_sem_acentos:
            return True
        
        # Remove lateralidade para comparação (DIREITO, ESQUERDO, DIREITA, ESQUERDA)
        parte_sem_lateralidade = parte_normalizada
        opcao_sem_lateralidade = opcao_sem_acentos
        for lat in ['DIREITO', 'DIREITA', 'ESQUERDO', 'ESQUERDA']:
            parte_sem_lateralidade = parte_sem_lateralidade.replace(lat, '').strip()
            opcao_sem_lateralidade = opcao_sem_lateralidade.replace(lat, '').strip()
        
        # Normaliza espaços após remover lateralidade
        parte_sem_lateralidade = ' '.join(parte_sem_lateralidade.split())
        opcao_sem_lateralidade = ' '.join(opcao_sem_lateralidade.split())
        
        # Verifica correspondência sem lateralidade
        if parte_sem_lateralidade in opcao_sem_lateralidade:
            return True
        
        # Tenta correspondência parcial (palavras-chave)
        parte_limpa = parte_sem_lateralidade.replace('/', ' ').replace('-', ' ').replace('  ', ' ')
        opcao_limpa = opcao_sem_lateralidade.replace('/', ' ').replace('-', ' ').replace('  ', ' ')
        
        palavras_parte = [p for p in parte_limpa.split() if len(p) > 2]
        palavras_opcao = opcao_limpa.split()
        
        # Lista de palavras-chave específicas que não devem ser confundidas
        palavras_especificas = {
            'JOELHOS': ['JOELHOS', 'JOELHO', 'ARTICULACOES', 'ARTICULAÇÕES'],
            'COXA': ['COXA'],
            'PERNA': ['PERNA'],
            'MAO': ['MAO', 'MÃO'],
            'PE': ['PE'],
            'OMBRO': ['OMBRO'],
            'PUNHO': ['PUNHO'],
            'TORNOZELO': ['TORNOZELO'],
            'COTOVELO': ['COTOVELO'],
            'BRACO': ['BRACO', 'BRAÇO'],
            'ANTEBRACO': ['ANTEBRACO', 'ANTEBRAÇO'],
            'PESCOCO': ['PESCOCO', 'PESCOÇO'],
            'CRANIO': ['CRANIO', 'CRÂNIO', 'ORBITA', 'ÓRBITA'],
            'FACE': ['FACE', 'SEIOS'],
            'COLUNA': ['COLUNA'],
            'CERVICAL': ['CERVICAL'],
            'DORSAL': ['DORSAL'],
            'LOMBAR': ['LOMBAR'],
            'TORACICA': ['TORACICA'],
            'ABDOMEN': ['ABDOMEN', 'ABDOMEM'],
            'PELVE': ['PELVE', 'BACIA']
        }
        
        # Verifica correspondência especial: ÓRBITA/ORBITA corresponde a CRANIO
        tem_orbita_parte = 'ORBITA' in palavras_parte or 'ÓRBITA' in palavras_parte
        tem_cranio_opcao = 'CRANIO' in palavras_opcao or 'CRÂNIO' in palavras_opcao
        
        # Se a parte tem ÓRBITA/ORBITA e a opção tem CRANIO, corresponde
        if tem_orbita_parte and tem_cranio_opcao:
            return True
        
        # Verifica correspondência entre singular/plural para JOELHO/JOELHOS
        tem_joelho_parte = 'JOELHO' in palavras_parte or 'JOELHOS' in palavras_parte
        tem_joelho_opcao = 'JOELHO' in palavras_opcao or 'JOELHOS' in palavras_opcao
        tem_articulacoes_parte = 'ARTICULACOES' in palavras_parte or 'ARTICULAÇÕES' in palavras_parte
        tem_articulacoes_opcao = 'ARTICULACOES' in palavras_opcao or 'ARTICULAÇÕES' in palavras_opcao
        
        # Se a parte tem JOELHO/JOELHOS e a opção também tem, aceita mesmo sem ARTICULACOES na opção
        if tem_joelho_parte and tem_joelho_opcao:
            # Se ambas têm ARTICULACOES, aceita
            if tem_articulacoes_parte and tem_articulacoes_opcao:
                return True
            # Se nenhuma tem ARTICULACOES, aceita
            if not tem_articulacoes_parte and not tem_articulacoes_opcao:
                return True
            # Se a parte tem ARTICULACOES mas a opção não tem, ainda aceita se ambas têm JOELHO/JOELHOS
            if tem_articulacoes_parte and not tem_articulacoes_opcao:
                return True
        
        # Verifica se há palavras específicas que não devem ser confundidas
        for palavra_especifica, variacoes in palavras_especificas.items():
            tem_palavra_parte = any(var in palavras_parte for var in variacoes)
            tem_palavra_opcao = any(var in palavras_opcao for var in variacoes)
            
            # Se a parte tem uma palavra específica, a opção DEVE ter a mesma
            if tem_palavra_parte and not tem_palavra_opcao:
                # Exceção: JOELHO/JOELHOS são equivalentes
                if palavra_especifica == 'JOELHOS' and ('JOELHO' in palavras_opcao or 'JOELHOS' in palavras_opcao):
                    continue
                return False
            # Se a opção tem uma palavra específica diferente, não corresponde
            if tem_palavra_opcao and not tem_palavra_parte:
                # Exceção: JOELHO/JOELHOS são equivalentes
                if palavra_especifica == 'JOELHOS' and ('JOELHO' in palavras_parte or 'JOELHOS' in palavras_parte):
                    continue
                # Verifica se não é uma palavra que pode estar em outra parte
                outras_palavras_especificas = [p for p, vars in palavras_especificas.items() if p != palavra_especifica]
                outras_variacoes = []
                for p in outras_palavras_especificas:
                    outras_variacoes.extend(palavras_especificas[p])
                
                # Se a parte tem outra palavra específica diferente, não corresponde
                if any(var in palavras_parte for var in outras_variacoes):
                    return False
        
        # Verifica se todas as palavras-chave importantes da parte do corpo aparecem na opção
        palavras_importantes = ['PELVE', 'BACIA', 'ABDOMEN', 'ABDOMEM', 'COLUNA', 'CERVICAL', 
                              'DORSAL', 'LOMBAR', 'CRANIO', 'CRÂNIO', 'ORBITA', 'ÓRBITA', 'FACE', 'PESCOCO', 'JOELHOS', 'JOELHO',
                              'SUPERIOR', 'INFERIOR', 'TORAX', 'TÓRAX', 'ARTICULACOES', 'ARTICULAÇÕES',
                              'COXA', 'PERNA', 'MAO', 'MÃO', 'PE', 'OMBRO', 'PUNHO', 'TORNOZELO',
                              'COTOVELO', 'BRACO', 'BRAÇO', 'ANTEBRACO', 'ANTEBRAÇO']
        
        palavras_parte_importantes = [p for p in palavras_parte if p in palavras_importantes]
        
        if palavras_parte_importantes:
            # Todas as palavras importantes devem estar na opção
            return all(palavra in palavras_opcao for palavra in palavras_parte_importantes)
        
        # Se não há palavras importantes específicas, verifica correspondência parcial geral
        palavras_encontradas = sum(1 for palavra in palavras_parte if palavra in palavras_opcao)
        return palavras_encontradas > 0 and palavras_encontradas == len(palavras_parte)
    
    def opcao_corresponde_lateralidade(texto_opcao, lateralidade):
        """
        Verifica se a opção corresponde à lateralidade especificada.
        
        Args:
            texto_opcao: Texto da opção na tabela SISREG
            lateralidade: Lateralidade identificada ('DIREITO', 'ESQUERDO' ou None)
        
        Returns:
            True se corresponde, False caso contrário
        """
        opcao_normalizada = normalizar_texto(texto_opcao)
        
        tem_direito_opcao = 'DIREITO' in opcao_normalizada or 'DIREITA' in opcao_normalizada
        tem_esquerdo_opcao = 'ESQUERDO' in opcao_normalizada or 'ESQUERDA' in opcao_normalizada
        nao_mentiona_lateralidade_opcao = not tem_direito_opcao and not tem_esquerdo_opcao
        
        if lateralidade == 'DIREITO':
            return tem_direito_opcao
        elif lateralidade == 'ESQUERDO':
            return tem_esquerdo_opcao
        else:
            # Se não há lateralidade especificada, aceita opções sem lateralidade
            return nao_mentiona_lateralidade_opcao
    
    def opcao_corresponde_contraste(texto_opcao, tipo_contraste_necessario):
        """
        Verifica se a opção corresponde ao tipo de contraste necessário.
        
        Args:
            texto_opcao: Texto da opção na tabela SISREG
            tipo_contraste_necessario: 'COM_CONTRASTE', 'SEM_CONTRASTE' ou None
        
        Returns:
            True se corresponde, False caso contrário
        """
        if not tipo_contraste_necessario:
            return True  # Se não há requisito de contraste, aceita qualquer opção
        
        opcao_normalizada = normalizar_texto(texto_opcao)
        
        tem_com_contraste = 'COM CONTRASTE' in opcao_normalizada or 'COM CONTARSTE' in opcao_normalizada
        tem_sem_contraste = 'SEM CONTRASTE' in opcao_normalizada or 'SEM CONTARSTE' in opcao_normalizada
        tem_c_ou_s_contraste = 'C/ OU S/ CONTRASTE' in opcao_normalizada or 'C/ OU S/ CONTARSTE' in opcao_normalizada
        
        if tipo_contraste_necessario == 'COM_CONTRASTE':
            # Aceita COM CONTRASTE ou C/ OU S/ CONTRASTE
            return tem_com_contraste or tem_c_ou_s_contraste
        elif tipo_contraste_necessario == 'SEM_CONTRASTE':
            # Aceita SEM CONTRASTE ou C/ OU S/ CONTRASTE (que pode ser SEM)
            return tem_sem_contraste or tem_c_ou_s_contraste
        
        return True
    
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
    
    def calcular_similaridade_termos_chave(proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste_necessario, lateralidade=None):
        """
        Calcula similaridade baseada em termos-chave: tipo de exame, parte do corpo, contraste e lateralidade.
        
        Args:
            proc_csv: Procedimento do CSV
            texto_opcao: Texto da opção na tabela SISREG
            tipo_exame: Tipo de exame identificado ('TOMOGRAFIA', 'ANGIO-TC', 'ANGIOTOMOGRAFIA')
            parte_corpo: Parte do corpo identificada
            tipo_contraste_necessario: 'COM_CONTRASTE' ou 'SEM_CONTRASTE'
            lateralidade: Lateralidade identificada ('DIREITO', 'ESQUERDO' ou None)
        
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
                
                # Função auxiliar para verificar correspondência considerando singular/plural
                def palavra_corresponde(palavra_parte, palavras_opcao_lista):
                    """Verifica se palavra_parte corresponde a alguma palavra em palavras_opcao_lista"""
                    if palavra_parte in palavras_opcao_lista:
                        return True
                    # Trata singular/plural para JOELHO/JOELHOS
                    if palavra_parte == 'JOELHO' and 'JOELHOS' in palavras_opcao_lista:
                        return True
                    if palavra_parte == 'JOELHOS' and 'JOELHO' in palavras_opcao_lista:
                        return True
                    # Trata ARTICULACOES - se a parte tem ARTICULACOES mas a opção tem JOELHO/JOELHOS, aceita
                    if palavra_parte == 'ARTICULACOES' or palavra_parte == 'ARTICULAÇÕES':
                        if 'JOELHO' in palavras_opcao_lista or 'JOELHOS' in palavras_opcao_lista:
                            return True
                    return False
                
                # Conta quantas palavras-chave da parte do corpo aparecem na opção
                palavras_encontradas = sum(1 for palavra in palavras_parte if palavra_corresponde(palavra, palavras_opcao))
                
                if palavras_encontradas > 0:
                    # Calcula score proporcional
                    proporcao = palavras_encontradas / len(palavras_parte)
                    score += 0.4 * proporcao
                    
                    # Bônus se encontrou palavras-chave importantes
                    palavras_importantes = ['PELVE', 'BACIA', 'ABDOMEN', 'ABDOMEM', 'COLUNA', 'CERVICAL', 
                                          'DORSAL', 'LOMBAR', 'TORACICA', 'TORÁCICA', 'CRANIO', 'CRÂNIO', 'ORBITA', 'ÓRBITA', 'FACE', 'PESCOCO', 'JOELHOS', 'JOELHO',
                                          'SUPERIOR', 'INFERIOR', 'TORAX', 'TÓRAX', 'ARTICULACOES', 'ARTICULAÇÕES',
                                          'COXA', 'PERNA', 'MAO', 'MÃO', 'PE', 'OMBRO', 'PUNHO', 'TORNOZELO',
                                          'COTOVELO', 'BRACO', 'BRAÇO', 'ANTEBRACO', 'ANTEBRAÇO']
                    # Verifica palavras importantes considerando singular/plural e ARTICULACOES
                    palavras_importantes_encontradas = 0
                    for palavra in palavras_parte:
                        if palavra in palavras_importantes:
                            # Verifica correspondência direta ou através de equivalências
                            if palavra_corresponde(palavra, palavras_opcao):
                                palavras_importantes_encontradas += 1
                            # Se é ARTICULACOES e encontrou JOELHO/JOELHOS, conta como encontrado
                            elif (palavra == 'ARTICULACOES' or palavra == 'ARTICULAÇÕES') and ('JOELHO' in palavras_opcao or 'JOELHOS' in palavras_opcao):
                                palavras_importantes_encontradas += 1
                    if palavras_importantes_encontradas > 0:
                        # Se encontrou palavras importantes, garante score mínimo
                        bonus = 0.15 * min(1.0, palavras_importantes_encontradas / len(palavras_parte))
                        score += bonus
                        
                        # Se encontrou todas as palavras importantes, garante score alto
                        if palavras_importantes_encontradas == len([p for p in palavras_parte if p in palavras_importantes]):
                            score = max(score, 0.5)  # Garante pelo menos 0.5 se todas palavras importantes foram encontradas
        
        # 3. Verifica lateralidade (peso alto: 0.2 se corresponder, penalização forte se não corresponder)
        if lateralidade:
            # Verifica lateralidade na opção
            tem_direito_opcao = 'DIREITO' in opcao_normalizada or 'DIREITA' in opcao_normalizada
            tem_esquerdo_opcao = 'ESQUERDO' in opcao_normalizada or 'ESQUERDA' in opcao_normalizada
            nao_mentiona_lateralidade_opcao = not tem_direito_opcao and not tem_esquerdo_opcao
            
            if lateralidade == 'DIREITO':
                if tem_direito_opcao:
                    # Bônus se tem DIREITO na opção também
                    score += 0.2
                elif nao_mentiona_lateralidade_opcao:
                    # Penalização forte se CSV tem DIREITO mas opção não menciona
                    score *= 0.3
                else:
                    # Penalização muito forte se CSV tem DIREITO mas opção tem ESQUERDO
                    score *= 0.1
            elif lateralidade == 'ESQUERDO':
                if tem_esquerdo_opcao:
                    # Bônus se tem ESQUERDO na opção também
                    score += 0.2
                elif nao_mentiona_lateralidade_opcao:
                    # Penalização forte se CSV tem ESQUERDO mas opção não menciona
                    score *= 0.3
                else:
                    # Penalização muito forte se CSV tem ESQUERDO mas opção tem DIREITO
                    score *= 0.1
        else:
            # Se não há lateralidade no CSV, prefere opções sem lateralidade
            tem_direito_opcao = 'DIREITO' in opcao_normalizada or 'DIREITA' in opcao_normalizada
            tem_esquerdo_opcao = 'ESQUERDO' in opcao_normalizada or 'ESQUERDA' in opcao_normalizada
            nao_mentiona_lateralidade_opcao = not tem_direito_opcao and not tem_esquerdo_opcao
            
            if nao_mentiona_lateralidade_opcao:
                # Bônus se opção também não menciona lateralidade
                score += 0.1
            else:
                # Penalização leve se opção tem lateralidade mas CSV não tem
                score *= 0.8
        
        # 4. Verifica contraste (peso: 0.1 se corresponder, pequena penalização se não corresponder)
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

    # ---------------------------------------------------------------------------
    # Funções de pre-check para evitar solicitações duplicadas no SISREG
    # ---------------------------------------------------------------------------

    def _buscar_campo_ficha_solicita(rotulo_texto):
        """
        Busca o valor de um campo na ficha ambulatorial do SISREG pelo rótulo.
        O valor fica na linha (tr) seguinte à linha que contém o rótulo.
        Retorna o texto encontrado ou None.
        """
        try:
            for xpath_busca in [
                f'//*[@id="fichaAmbulatorial"]//td[contains(., "{rotulo_texto}")]',
                f'//*[@id="fichaAmbulatorial"]//td[contains(., "{rotulo_texto.replace(":", "").strip()}")]',
            ]:
                try:
                    elementos = navegador.find_elements(By.XPATH, xpath_busca)
                    if not elementos:
                        continue
                    rotulo_el = elementos[0]
                    tr_rotulo = rotulo_el.find_element(By.XPATH, './ancestor::tr')
                    tr_valor = tr_rotulo.find_element(By.XPATH, './following-sibling::tr[1]')
                    td_valor = tr_valor.find_element(By.XPATH, './td[1]')
                    try:
                        b_el = td_valor.find_element(By.XPATH, './b')
                        texto = b_el.text.strip()
                    except Exception:
                        texto = td_valor.text.strip()
                    if texto and not texto.endswith(':'):
                        return texto
                except Exception:
                    continue
        except Exception:
            pass
        return None

    def verificar_solicitacao_duplicada(cns_str, tipo_exame_req, parte_corpo_req, lateralidade_req):
        """
        Verifica se já existe solicitação no SISREG para o mesmo CNS e procedimento
        nos últimos 7 dias. Navega para o gerenciador de solicitações, pesquisa o CNS
        e inspeciona cada ficha recente.

        Returns:
            tuple: (chave, solicitacao) se encontrou duplicata, ou (None, None) se não encontrou.
        """
        try:
            print(f"      🔍 Pre-check SISREG: verificando duplicata para CNS {cns_str}...")
            navegador.get("https://sisregiii.saude.gov.br/cgi-bin/gerenciador_solicitacao")
            time.sleep(2)

            # Preenche o campo CNS do paciente
            try:
                cns_paciente_field = WebDriverWait(navegador, 10).until(
                    EC.presence_of_element_located((By.NAME, "cns_paciente"))
                )
                cns_paciente_field.clear()
                cns_paciente_field.send_keys(cns_str)
            except TimeoutException:
                print(f"      ⚠️  Campo 'cns_paciente' não encontrado no gerenciador. Pulando pre-check.")
                return None, None

            try:
                btn_pesquisar_dup = WebDriverWait(navegador, 10).until(
                    EC.element_to_be_clickable((By.NAME, "pesquisar"))
                )
                btn_pesquisar_dup.click()
                time.sleep(3)
            except TimeoutException:
                print(f"      ⚠️  Botão 'pesquisar' não encontrado no gerenciador. Pulando pre-check.")
                return None, None

            data_atual = datetime.now()
            data_limite = data_atual - timedelta(days=7)

            linhas_tabela = navegador.find_elements(By.XPATH, "//table//tbody//tr")
            if not linhas_tabela:
                print(f"      ℹ️  Nenhuma solicitação anterior encontrada para CNS {cns_str}.")
                return None, None

            print(f"      📋 {len(linhas_tabela)} solicitação(ões) anterior(es) a verificar.")

            for linha in linhas_tabela:
                try:
                    celulas = linha.find_elements(By.TAG_NAME, "td")
                    if not celulas:
                        continue

                    # Procura uma data válida entre as células da linha
                    texto_data = None
                    for celula in celulas:
                        texto_celula = celula.text.strip()
                        if '/' in texto_celula and 8 <= len(texto_celula) <= 20:
                            texto_data = texto_celula
                            break

                    if not texto_data:
                        continue

                    # Faz parse da data no formato DD/MM/YYYY
                    texto_data_limpo = texto_data.split()[0] if ' ' in texto_data else texto_data
                    data_solicitacao = None
                    for fmt in ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']:
                        try:
                            data_solicitacao = datetime.strptime(texto_data_limpo, fmt)
                            break
                        except Exception:
                            continue

                    if not data_solicitacao or data_solicitacao < data_limite:
                        continue  # Fora do prazo de 7 dias

                    print(f"      📅 Registro recente ({texto_data}). Verificando procedimento...")

                    # Clica na linha para abrir a ficha
                    clicou = False
                    try:
                        linha.click()
                        clicou = True
                    except Exception:
                        try:
                            link_el = linha.find_element(By.TAG_NAME, "a")
                            link_el.click()
                            clicou = True
                        except Exception:
                            pass

                    if not clicou:
                        continue

                    time.sleep(2)

                    # Aguarda a ficha ambulatorial carregar
                    try:
                        WebDriverWait(navegador, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="fichaAmbulatorial"]'))
                        )
                    except Exception:
                        print(f"      ⚠️  Ficha ambulatorial não carregou. Voltando...")
                        try:
                            navegador.back()
                            time.sleep(2)
                        except Exception:
                            pass
                        continue

                    # Inspeciona todos os tds da ficha em busca de procedimentos de tomografia/angio
                    todos_tds = navegador.find_elements(By.XPATH, '//*[@id="fichaAmbulatorial"]//td')
                    for td in todos_tds:
                        try:
                            texto_td = td.text.strip()
                            if not texto_td or texto_td.endswith(':'):
                                continue
                            texto_upper = texto_td.upper()
                            if 'TOMOGRAFIA' not in texto_upper and 'ANGIO' not in texto_upper:
                                continue

                            tipo_ficha = identificar_tipo_exame(texto_td)
                            parte_ficha = identificar_parte_corpo(texto_td)
                            lat_ficha = identificar_lateralidade(texto_td)

                            if not tipo_ficha or not parte_ficha:
                                continue

                            mesmo_tipo = tipo_ficha == tipo_exame_req
                            mesma_parte = parte_ficha == parte_corpo_req
                            mesma_lat = (lat_ficha == lateralidade_req or
                                         (not lat_ficha and not lateralidade_req))

                            if mesmo_tipo and mesma_parte and mesma_lat:
                                # Encontrou o mesmo exame! Captura chave e número da solicitação
                                chave_dup = _buscar_campo_ficha_solicita("Chave de Confirmação:")
                                solicitacao_dup = _buscar_campo_ficha_solicita("Código da Solicitação:")
                                if solicitacao_dup:
                                    print(f"      🔴 DUPLICATA: Tipo={tipo_ficha}, Parte={parte_ficha}")
                                    print(f"         Solicitação já existente: {solicitacao_dup} | Chave: {chave_dup}")
                                    return chave_dup or '', solicitacao_dup
                        except Exception:
                            continue

                    # Exame diferente; volta à lista e re-pesquisa o CNS
                    print(f"      ℹ️  Exame diferente nesta ficha. Voltando à lista...")
                    try:
                        navegador.back()
                        time.sleep(2)
                        cns_f2 = WebDriverWait(navegador, 5).until(
                            EC.presence_of_element_located((By.NAME, "cns_paciente"))
                        )
                        cns_f2.clear()
                        cns_f2.send_keys(cns_str)
                        btn_p2 = WebDriverWait(navegador, 5).until(
                            EC.element_to_be_clickable((By.NAME, "pesquisar"))
                        )
                        btn_p2.click()
                        time.sleep(3)
                        linhas_tabela = navegador.find_elements(By.XPATH, "//table//tbody//tr")
                    except Exception as e_nav:
                        print(f"      ⚠️  Erro ao restaurar lista: {e_nav}. Interrompendo pre-check.")
                        break

                except Exception:
                    continue

            print(f"      ✅ Nenhuma solicitação duplicada encontrada para CNS {cns_str}.")
            return None, None

        except Exception as e:
            print(f"      ⚠️  Erro no pre-check de duplicata SISREG: {e}. Prosseguindo com a solicitação.")
            return None, None

    # ---------------------------------------------------------------------------

    # Itera sobre os links do CSV
    for index, row in df.iterrows():
        try:
            # Verifica se a linha já foi processada: pula quando solicitacao está preenchida E (solicita está vazio OU solicita != 'S')
            solicitacao = str(row.get('solicitacao', '')).strip() if pd.notna(row.get('solicitacao')) else ''
            # Normaliza solicita para maiúsculo (aceita 's' ou 'S')
            solicita = str(row.get('solicita', '')).strip().upper() if pd.notna(row.get('solicita')) else ''
            # Se solicitacao está preenchida E (solicita está vazio OU solicita != 'S'), não processar
            if solicitacao and (not solicita or solicita != 'S'):
                print(f"\n[{index + 1}/{len(df)}] ⏭️  Linha já processada (solicitação: {solicitacao}, solicita: '{solicita}'). Pulando...")
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

            # ---------------------------------------------------------------
            # Pre-check: verifica se já existe solicitação no SISREG para
            # este CNS + procedimento antes de abrir a tela de marcação.
            # Bloqueia duplicidades mesmo que consulta.py não tenha rodado.
            # ---------------------------------------------------------------
            if procedimento:
                primeiro_proc = procedimento.split('|')[0].strip()
                tipo_req = identificar_tipo_exame(primeiro_proc)
                parte_req = identificar_parte_corpo(primeiro_proc)
                lat_req = identificar_lateralidade(primeiro_proc)
                if tipo_req and parte_req:
                    chave_dup, sol_dup = verificar_solicitacao_duplicada(
                        str(cns), tipo_req, parte_req, lat_req
                    )
                    if sol_dup:
                        print(f"   ⛔ DUPLICATA BLOQUEADA: Solicitação '{sol_dup}' já existe para este exame.")
                        print(f"      Salvando solicitação existente no CSV e pulando nova solicitação.")
                        df.at[index, 'chave'] = chave_dup
                        df.at[index, 'solicitacao'] = sol_dup
                        df.at[index, 'solicita'] = ''
                        df.at[index, 'erro'] = ''
                        try:
                            df.to_csv(csv_exames, index=False)
                            print(f"   💾 CSV atualizado com solicitação existente")
                        except Exception as e_csv:
                            print(f"   ⚠️  Erro ao salvar CSV: {e_csv}")
                        continue
            # ---------------------------------------------------------------

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
                
                # Verifica se há CRANIO e ÓRBITA na lista de procedimentos
                tem_cranio = False
                tem_orbita = False
                for proc in procedimentos_lista:
                    parte_proc = identificar_parte_corpo(proc)
                    if parte_proc == 'CRANIO':
                        tem_cranio = True
                    proc_normalizado = normalizar_texto(proc)
                    if 'ORBITA' in proc_normalizado or 'ÓRBITA' in proc_normalizado:
                        tem_orbita = True
                
                precisa_marcar_cranio_duas_vezes = tem_cranio and tem_orbita
                if precisa_marcar_cranio_duas_vezes:
                    print(f"   ⚠️  Detectado CRANIO e ÓRBITA na lista: será marcado CRANIO duas vezes")
                
                # Aguarda a tabela carregar
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
                
                # Encontra todos os checkboxes na tabela
                checkboxes = navegador.find_elements(By.XPATH, "//table[@class='table_listagem']//input[@type='checkbox']")
                
                checkboxes_marcados = []
                opcoes_cranio_coletadas = []  # Para armazenar opções de CRANIO encontradas
                
                # Para cada procedimento do CSV
                for proc_idx, proc_csv in enumerate(procedimentos_lista, 1):
                    print(f"   [{proc_idx}/{len(procedimentos_lista)}] Buscando procedimento correspondente a: {proc_csv}")
                    
                    # Identifica termos-chave: tipo de exame, parte do corpo e lateralidade
                    tipo_exame = identificar_tipo_exame(proc_csv)
                    parte_corpo_original = identificar_parte_corpo(proc_csv)
                    lateralidade = identificar_lateralidade(proc_csv)
                    tipo_contraste = determinar_tipo_contraste(proc_csv, contraste)
                    
                    # Se a parte do corpo é ÓRBITA/ORBITA, trata como CRANIO
                    if parte_corpo_original == 'CRANIO' or (parte_corpo_original and 'ORBITA' in parte_corpo_original.upper()):
                        parte_corpo = 'CRANIO'
                        if parte_corpo_original != 'CRANIO':
                            print(f"      🔄 Parte do corpo '{parte_corpo_original}' mapeada para CRANIO")
                    else:
                        parte_corpo = parte_corpo_original
                    
                    # Verifica se precisa marcar CRANIO duas vezes (quando há CRANIO e ÓRBITA na lista)
                    este_proc_eh_cranio_ou_orbita = parte_corpo == 'CRANIO'
                    
                    if not tipo_exame:
                        print(f"      ⚠️  Não foi possível identificar o tipo de exame em '{proc_csv}'")
                        continue
                    
                    if not parte_corpo:
                        print(f"      ⚠️  Não foi possível identificar a parte do corpo em '{proc_csv}'")
                        continue
                    
                    print(f"      🔍 Tipo de exame identificado: {tipo_exame}")
                    print(f"      🔍 Parte do corpo identificada: {parte_corpo}")
                    if lateralidade:
                        print(f"      🔍 Lateralidade identificada: {lateralidade}")
                    else:
                        print(f"      🔍 Lateralidade: não especificada")
                    print(f"      ℹ️  Tipo de contraste necessário: {tipo_contraste}")
                    if precisa_marcar_cranio_duas_vezes and este_proc_eh_cranio_ou_orbita:
                        print(f"      ⚠️  Este procedimento contribui para marcação dupla de CRANIO")
                    
                    # Se precisa marcar CRANIO duas vezes e este procedimento é CRANIO ou ÓRBITA, coleta opções
                    if precisa_marcar_cranio_duas_vezes and este_proc_eh_cranio_ou_orbita:
                        # Busca todas as opções de CRANIO que correspondem para este procedimento
                        for checkbox in checkboxes:
                            # Pula checkboxes já marcados (mas permite coletar para marcação dupla)
                            if checkbox in checkboxes_marcados:
                                continue
                                
                            try:
                                td = checkbox.find_element(By.XPATH, "./..")
                                texto_opcao = td.text.strip()
                                
                                # FILTRO 1: Verifica tipo de exame (OBRIGATÓRIO)
                                if not opcao_corresponde_tipo_exame(texto_opcao, tipo_exame):
                                    continue
                                
                                # FILTRO 2: Verifica parte do corpo (OBRIGATÓRIO) - deve ser CRANIO
                                if not opcao_corresponde_parte_corpo(texto_opcao, parte_corpo):
                                    continue
                                
                                # FILTRO 3: Verifica lateralidade (OBRIGATÓRIO se especificada)
                                if lateralidade and not opcao_corresponde_lateralidade(texto_opcao, lateralidade):
                                    continue
                                
                                # Se passou por todos os filtros hierárquicos, calcula similaridade
                                similaridade = calcular_similaridade_termos_chave(
                                    proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste, lateralidade
                                )
                                
                                if similaridade >= 0.5:
                                    # Adiciona à lista coletada (evita duplicatas)
                                    ja_existe = any(cb == checkbox for cb, _, _ in opcoes_cranio_coletadas)
                                    if not ja_existe:
                                        opcoes_cranio_coletadas.append((checkbox, texto_opcao, similaridade))
                            except Exception as e:
                                continue
                        
                        # Não marca ainda, apenas coleta - marcação será feita ao final
                        print(f"      📋 Opções de CRANIO coletadas para marcação dupla: {len(opcoes_cranio_coletadas)}")
                    else:
                        # Lógica normal para outros procedimentos
                        melhor_similaridade = 0.0
                        checkbox_selecionado = None
                        texto_selecionado = ""
                        
                        # FILTRAGEM HIERÁRQUICA:
                        # 1. Primeiro filtra por tipo de exame
                        # 2. Depois filtra por parte do corpo (dentro do tipo já filtrado)
                        # 3. Por último filtra por lateralidade (dentro do tipo + parte já filtrados)
                        # O contraste será considerado apenas na similaridade (sem filtro obrigatório)
                        
                        # Compara cada opção da tabela usando filtragem hierárquica
                        for checkbox in checkboxes:
                            # Pula checkboxes já marcados
                            if checkbox in checkboxes_marcados:
                                continue
                                
                            # Obtém o texto da opção (texto do elemento pai td)
                            try:
                                td = checkbox.find_element(By.XPATH, "./..")
                                texto_opcao = td.text.strip()
                                
                                # FILTRO 1: Verifica tipo de exame (OBRIGATÓRIO)
                                if not opcao_corresponde_tipo_exame(texto_opcao, tipo_exame):
                                    continue  # Pula esta opção se não corresponde ao tipo de exame
                                
                                # FILTRO 2: Verifica parte do corpo (OBRIGATÓRIO)
                                if not opcao_corresponde_parte_corpo(texto_opcao, parte_corpo):
                                    continue  # Pula esta opção se não corresponde à parte do corpo
                                
                                # FILTRO 3: Verifica lateralidade (OBRIGATÓRIO se especificada)
                                if lateralidade and not opcao_corresponde_lateralidade(texto_opcao, lateralidade):
                                    continue  # Pula esta opção se não corresponde à lateralidade
                                
                                # Se passou por todos os filtros hierárquicos, calcula similaridade
                                # O contraste será considerado apenas na similaridade (sem filtro obrigatório)
                                similaridade = calcular_similaridade_termos_chave(
                                    proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste, lateralidade
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
                
                # Se precisa marcar CRANIO duas vezes e coletou opções, marca agora
                if precisa_marcar_cranio_duas_vezes and opcoes_cranio_coletadas:
                    print(f"   🔄 Processando marcação dupla de CRANIO com {len(opcoes_cranio_coletadas)} opção(ões) encontrada(s)...")
                    
                    # Ordena por similaridade (maior primeiro)
                    opcoes_cranio_coletadas.sort(key=lambda x: x[2], reverse=True)
                    
                    # Marca até duas opções diferentes de CRANIO
                    opcoes_marcadas = 0
                    for checkbox_cranio, texto_cranio, similaridade_cranio in opcoes_cranio_coletadas:
                        if opcoes_marcadas >= 2:
                            break
                        
                        # Verifica se já foi marcado
                        if checkbox_cranio not in checkboxes_marcados:
                            print(f"      ✅ Procedimento CRANIO encontrado: {texto_cranio} (similaridade: {similaridade_cranio:.2%})")
                            if not checkbox_cranio.is_selected():
                                checkbox_cranio.click()
                            checkboxes_marcados.append(checkbox_cranio)
                            opcoes_marcadas += 1
                            print(f"      ✅ Checkbox CRANIO marcado ({opcoes_marcadas}/2)")
                    
                    # Se encontrou menos de 2 opções diferentes, marca a mesma opção duas vezes
                    if opcoes_marcadas < 2 and opcoes_cranio_coletadas:
                        checkbox_cranio, texto_cranio, similaridade_cranio = opcoes_cranio_coletadas[0]
                        print(f"      ✅ Marcando CRANIO segunda vez: {texto_cranio}")
                        # Clica novamente no mesmo checkbox
                        if checkbox_cranio.is_selected():
                            checkbox_cranio.click()  # Desmarca
                            checkbox_cranio.click()  # Marca novamente
                        else:
                            checkbox_cranio.click()
                        opcoes_marcadas += 1
                        print(f"      ✅ Checkbox CRANIO marcado segunda vez ({opcoes_marcadas}/2)")
                    
                    if opcoes_marcadas == 2:
                        print(f"   ✅ CRANIO marcado duas vezes com sucesso!")
                
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
                    
                    # Verifica se há CRANIO e ÓRBITA na lista de procedimentos
                    tem_cranio = False
                    tem_orbita = False
                    for proc in procedimentos_lista:
                        parte_proc = identificar_parte_corpo(proc)
                        if parte_proc == 'CRANIO':
                            tem_cranio = True
                        proc_normalizado = normalizar_texto(proc)
                        if 'ORBITA' in proc_normalizado or 'ÓRBITA' in proc_normalizado:
                            tem_orbita = True
                    
                    precisa_marcar_cranio_duas_vezes = tem_cranio and tem_orbita
                    opcoes_cranio_coletadas_fallback = []
                    
                    for proc_csv in procedimentos_lista:
                        # Identifica termos-chave: tipo de exame, parte do corpo e lateralidade
                        tipo_exame = identificar_tipo_exame(proc_csv)
                        parte_corpo_original = identificar_parte_corpo(proc_csv)
                        lateralidade = identificar_lateralidade(proc_csv)
                        tipo_contraste = determinar_tipo_contraste(proc_csv, contraste)
                        
                        # Se a parte do corpo é ÓRBITA/ORBITA, trata como CRANIO
                        if parte_corpo_original == 'CRANIO' or (parte_corpo_original and 'ORBITA' in parte_corpo_original.upper()):
                            parte_corpo = 'CRANIO'
                        else:
                            parte_corpo = parte_corpo_original
                        
                        este_proc_eh_cranio_ou_orbita = parte_corpo == 'CRANIO'
                        
                        if not tipo_exame or not parte_corpo:
                            continue
                        
                        # Se precisa marcar CRANIO duas vezes e este procedimento é CRANIO ou ÓRBITA, coleta opções
                        if precisa_marcar_cranio_duas_vezes and este_proc_eh_cranio_ou_orbita:
                            for checkbox in checkboxes:
                                if checkbox in checkboxes_marcados:
                                    continue
                                try:
                                    td = checkbox.find_element(By.XPATH, "./..")
                                    texto_opcao = td.text.strip()
                                    
                                    if not opcao_corresponde_tipo_exame(texto_opcao, tipo_exame):
                                        continue
                                    if not opcao_corresponde_parte_corpo(texto_opcao, parte_corpo):
                                        continue
                                    if lateralidade and not opcao_corresponde_lateralidade(texto_opcao, lateralidade):
                                        continue
                                    
                                    similaridade = calcular_similaridade_termos_chave(
                                        proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste, lateralidade
                                    )
                                    
                                    if similaridade >= 0.5:
                                        ja_existe = any(cb == checkbox for cb, _, _ in opcoes_cranio_coletadas_fallback)
                                        if not ja_existe:
                                            opcoes_cranio_coletadas_fallback.append((checkbox, texto_opcao, similaridade))
                                except:
                                    continue
                        else:
                            melhor_similaridade = 0.0
                            checkbox_selecionado = None
                            
                            # FILTRAGEM HIERÁRQUICA:
                            # 1. Primeiro filtra por tipo de exame
                            # 2. Depois filtra por parte do corpo (dentro do tipo já filtrado)
                            # 3. Por último filtra por lateralidade (dentro do tipo + parte já filtrados)
                            # O contraste será considerado apenas na similaridade (sem filtro obrigatório)
                            
                            # Compara cada opção da tabela usando filtragem hierárquica
                            for checkbox in checkboxes:
                                if checkbox in checkboxes_marcados:
                                    continue
                                try:
                                    td = checkbox.find_element(By.XPATH, "./..")
                                    texto_opcao = td.text.strip()
                                    
                                    # FILTRO 1: Verifica tipo de exame (OBRIGATÓRIO)
                                    if not opcao_corresponde_tipo_exame(texto_opcao, tipo_exame):
                                        continue
                                    
                                    # FILTRO 2: Verifica parte do corpo (OBRIGATÓRIO)
                                    if not opcao_corresponde_parte_corpo(texto_opcao, parte_corpo):
                                        continue
                                    
                                    # FILTRO 3: Verifica lateralidade (OBRIGATÓRIO se especificada)
                                    if lateralidade and not opcao_corresponde_lateralidade(texto_opcao, lateralidade):
                                        continue
                                    
                                    # Se passou por todos os filtros hierárquicos, calcula similaridade
                                    # O contraste será considerado apenas na similaridade (sem filtro obrigatório)
                                    similaridade = calcular_similaridade_termos_chave(
                                        proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste, lateralidade
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
                    
                    # Se precisa marcar CRANIO duas vezes e coletou opções, marca agora
                    if precisa_marcar_cranio_duas_vezes and opcoes_cranio_coletadas_fallback:
                        opcoes_cranio_coletadas_fallback.sort(key=lambda x: x[2], reverse=True)
                        
                        opcoes_marcadas = 0
                        for checkbox_cranio, texto_cranio, similaridade_cranio in opcoes_cranio_coletadas_fallback:
                            if opcoes_marcadas >= 2:
                                break
                            if checkbox_cranio not in checkboxes_marcados:
                                if not checkbox_cranio.is_selected():
                                    checkbox_cranio.click()
                                checkboxes_marcados.append(checkbox_cranio)
                                opcoes_marcadas += 1
                        
                        if opcoes_marcadas < 2 and opcoes_cranio_coletadas_fallback:
                            checkbox_cranio, texto_cranio, similaridade_cranio = opcoes_cranio_coletadas_fallback[0]
                            if checkbox_cranio.is_selected():
                                checkbox_cranio.click()
                                checkbox_cranio.click()
                            else:
                                checkbox_cranio.click()
                            opcoes_marcadas += 1
                    
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
            
            # Apaga 'solicita' após processar com sucesso para o fallback não reprocessar de novo
            df.at[index, 'solicita'] = ''
            
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
            if 'solicita' not in df_atualizado.columns:
                df_atualizado['solicita'] = ''
            # Garante tipo object para colunas que recebem string (evita FutureWarning ao atribuir)
            for col in ['chave', 'solicitacao', 'erro', 'solicita']:
                if col in df_atualizado.columns:
                    df_atualizado[col] = df_atualizado[col].astype(object)
            
            # Identifica registros pendentes: sem solicitacao ou com solicita='s' (re-solicitar)
            # Não considera chave no filtro
            col_solicitacao = df_atualizado['solicitacao'].fillna('').astype(str).str.strip()
            # Normaliza solicita para maiúsculo (aceita 's' ou 'S')
            col_solicita = df_atualizado['solicita'].fillna('').astype(str).str.strip().str.upper()
            sem_solicitacao = (col_solicitacao == '')
            quer_re_solicitar = (col_solicita == 'S')
            # Pendentes: sem solicitacao OU com solicita='s' (re-solicitar)
            registros_pendentes = df_atualizado[sem_solicitacao | quer_re_solicitar]
            
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
                    solicitacao_val = row.get('solicitacao', '')
                    solicitacao = str(solicitacao_val).strip() if pd.notna(solicitacao_val) and str(solicitacao_val).strip() != '' else ''
                    
                    solicita_val = row.get('solicita', '')
                    # Normaliza solicita para maiúsculo (aceita 's' ou 'S')
                    solicita = str(solicita_val).strip().upper() if pd.notna(solicita_val) and str(solicita_val).strip() != '' else ''
                    # Se solicitacao está preenchida E (solicita está vazio OU solicita != 'S'), não processar
                    if solicitacao and (not solicita or solicita != 'S'):
                        print(f"   ⏭️  Registro {index + 1} já foi processado (solicitação: {solicitacao}, solicita: '{solicita}'). Pulando...")
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
                        
                        # Verifica se há CRANIO e ÓRBITA na lista de procedimentos
                        tem_cranio = False
                        tem_orbita = False
                        for proc in procedimentos_lista:
                            parte_proc = identificar_parte_corpo(proc)
                            if parte_proc == 'CRANIO':
                                tem_cranio = True
                            proc_normalizado = normalizar_texto(proc)
                            if 'ORBITA' in proc_normalizado or 'ÓRBITA' in proc_normalizado:
                                tem_orbita = True
                        
                        precisa_marcar_cranio_duas_vezes = tem_cranio and tem_orbita
                        if precisa_marcar_cranio_duas_vezes:
                            print(f"   ⚠️  Detectado CRANIO e ÓRBITA na lista: será marcado CRANIO duas vezes")
                        
                        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table_listagem")))
                        checkboxes = navegador.find_elements(By.XPATH, "//table[@class='table_listagem']//input[@type='checkbox']")
                        checkboxes_marcados = []
                        opcoes_cranio_coletadas_reproc = []
                        
                        for proc_idx, proc_csv in enumerate(procedimentos_lista, 1):
                            print(f"   [{proc_idx}/{len(procedimentos_lista)}] Buscando procedimento correspondente a: {proc_csv}")
                            
                            # Identifica termos-chave: tipo de exame, parte do corpo e lateralidade
                            tipo_exame = identificar_tipo_exame(proc_csv)
                            parte_corpo_original = identificar_parte_corpo(proc_csv)
                            lateralidade = identificar_lateralidade(proc_csv)
                            tipo_contraste = determinar_tipo_contraste(proc_csv, contraste)
                            
                            # Se a parte do corpo é ÓRBITA/ORBITA, trata como CRANIO
                            if parte_corpo_original == 'CRANIO' or (parte_corpo_original and 'ORBITA' in parte_corpo_original.upper()):
                                parte_corpo = 'CRANIO'
                                if parte_corpo_original != 'CRANIO':
                                    print(f"      🔄 Parte do corpo '{parte_corpo_original}' mapeada para CRANIO")
                            else:
                                parte_corpo = parte_corpo_original
                            
                            este_proc_eh_cranio_ou_orbita = parte_corpo == 'CRANIO'
                            
                            if not tipo_exame:
                                print(f"      ⚠️  Não foi possível identificar o tipo de exame em '{proc_csv}'")
                                continue
                            
                            if not parte_corpo:
                                print(f"      ⚠️  Não foi possível identificar a parte do corpo em '{proc_csv}'")
                                continue
                            
                            print(f"      🔍 Tipo de exame identificado: {tipo_exame}")
                            print(f"      🔍 Parte do corpo identificada: {parte_corpo}")
                            if lateralidade:
                                print(f"      🔍 Lateralidade identificada: {lateralidade}")
                            else:
                                print(f"      🔍 Lateralidade: não especificada")
                            print(f"      ℹ️  Tipo de contraste necessário: {tipo_contraste}")
                            if precisa_marcar_cranio_duas_vezes and este_proc_eh_cranio_ou_orbita:
                                print(f"      ⚠️  Este procedimento contribui para marcação dupla de CRANIO")
                            
                            # Se precisa marcar CRANIO duas vezes e este procedimento é CRANIO ou ÓRBITA, coleta opções
                            if precisa_marcar_cranio_duas_vezes and este_proc_eh_cranio_ou_orbita:
                                for checkbox in checkboxes:
                                    if checkbox in checkboxes_marcados:
                                        continue
                                    
                                    try:
                                        td = checkbox.find_element(By.XPATH, "./..")
                                        texto_opcao = td.text.strip()
                                        
                                        if not opcao_corresponde_tipo_exame(texto_opcao, tipo_exame):
                                            continue
                                        if not opcao_corresponde_parte_corpo(texto_opcao, parte_corpo):
                                            continue
                                        if lateralidade and not opcao_corresponde_lateralidade(texto_opcao, lateralidade):
                                            continue
                                        
                                        similaridade = calcular_similaridade_termos_chave(
                                            proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste, lateralidade
                                        )
                                        
                                        if similaridade >= 0.5:
                                            ja_existe = any(cb == checkbox for cb, _, _ in opcoes_cranio_coletadas_reproc)
                                            if not ja_existe:
                                                opcoes_cranio_coletadas_reproc.append((checkbox, texto_opcao, similaridade))
                                    except Exception as e:
                                        continue
                                
                                print(f"      📋 Opções de CRANIO coletadas para marcação dupla: {len(opcoes_cranio_coletadas_reproc)}")
                            else:
                                melhor_similaridade = 0.0
                                checkbox_selecionado = None
                                texto_selecionado = ""
                                
                                # FILTRAGEM HIERÁRQUICA:
                                # 1. Primeiro filtra por tipo de exame
                                # 2. Depois filtra por parte do corpo (dentro do tipo já filtrado)
                                # 3. Por último filtra por lateralidade (dentro do tipo + parte já filtrados)
                                # O contraste será considerado apenas na similaridade (sem filtro obrigatório)
                                
                                # Compara cada opção da tabela usando filtragem hierárquica
                                for checkbox in checkboxes:
                                    # Pula checkboxes já marcados
                                    if checkbox in checkboxes_marcados:
                                        continue
                                        
                                    # Obtém o texto da opção (texto do elemento pai td)
                                    try:
                                        td = checkbox.find_element(By.XPATH, "./..")
                                        texto_opcao = td.text.strip()
                                        
                                        # FILTRO 1: Verifica tipo de exame (OBRIGATÓRIO)
                                        if not opcao_corresponde_tipo_exame(texto_opcao, tipo_exame):
                                            continue  # Pula esta opção se não corresponde ao tipo de exame
                                        
                                        # FILTRO 2: Verifica parte do corpo (OBRIGATÓRIO)
                                        if not opcao_corresponde_parte_corpo(texto_opcao, parte_corpo):
                                            continue  # Pula esta opção se não corresponde à parte do corpo
                                        
                                        # FILTRO 3: Verifica lateralidade (OBRIGATÓRIO se especificada)
                                        if lateralidade and not opcao_corresponde_lateralidade(texto_opcao, lateralidade):
                                            continue  # Pula esta opção se não corresponde à lateralidade
                                        
                                        # Se passou por todos os filtros hierárquicos, calcula similaridade
                                        # O contraste será considerado apenas na similaridade (sem filtro obrigatório)
                                        similaridade = calcular_similaridade_termos_chave(
                                            proc_csv, texto_opcao, tipo_exame, parte_corpo, tipo_contraste, lateralidade
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
                        
                        # Se precisa marcar CRANIO duas vezes e coletou opções, marca agora
                        if precisa_marcar_cranio_duas_vezes and opcoes_cranio_coletadas_reproc:
                            print(f"   🔄 Processando marcação dupla de CRANIO com {len(opcoes_cranio_coletadas_reproc)} opção(ões) encontrada(s)...")
                            
                            opcoes_cranio_coletadas_reproc.sort(key=lambda x: x[2], reverse=True)
                            
                            opcoes_marcadas = 0
                            for checkbox_cranio, texto_cranio, similaridade_cranio in opcoes_cranio_coletadas_reproc:
                                if opcoes_marcadas >= 2:
                                    break
                                if checkbox_cranio not in checkboxes_marcados:
                                    print(f"      ✅ Procedimento CRANIO encontrado: {texto_cranio} (similaridade: {similaridade_cranio:.2%})")
                                    if not checkbox_cranio.is_selected():
                                        checkbox_cranio.click()
                                    checkboxes_marcados.append(checkbox_cranio)
                                    opcoes_marcadas += 1
                                    print(f"      ✅ Checkbox CRANIO marcado ({opcoes_marcadas}/2)")
                            
                            if opcoes_marcadas < 2 and opcoes_cranio_coletadas_reproc:
                                checkbox_cranio, texto_cranio, similaridade_cranio = opcoes_cranio_coletadas_reproc[0]
                                print(f"      ✅ Marcando CRANIO segunda vez: {texto_cranio}")
                                if checkbox_cranio.is_selected():
                                    checkbox_cranio.click()
                                    checkbox_cranio.click()
                                else:
                                    checkbox_cranio.click()
                                opcoes_marcadas += 1
                                print(f"      ✅ Checkbox CRANIO marcado segunda vez ({opcoes_marcadas}/2)")
                            
                            if opcoes_marcadas == 2:
                                print(f"   ✅ CRANIO marcado duas vezes com sucesso!")
                        
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
                    
                    # Apaga 'solicita' após processar com sucesso para o fallback não reprocessar de novo
                    df_atualizado.at[index, 'solicita'] = ''
                    
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