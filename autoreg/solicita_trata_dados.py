def solicita_trata_dados():
    import pandas as pd
    import os
    import re
    from datetime import datetime, timedelta
    
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'internados_ghosp_avancado.csv')
    
    # Verifica se o arquivo existe
    if not os.path.exists(csv_path):
        print(f"Arquivo não encontrado: {csv_path}")
        return
    
    # Lê o CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"Total de registros antes do tratamento: {len(df)}")
        
        # Remove linhas onde a coluna "setor" é PEDIATRIA ou RPA-POS ANESTESICA
        setores_excluir = ['PEDIATRIA', 'RPA-POS ANESTESICA']
        df_filtrado = df[~df['setor'].isin(setores_excluir)]
        
        registros_removidos = len(df) - len(df_filtrado)
        print(f"Registros removidos (PEDIATRIA e RPA-POS ANESTESICA): {registros_removidos}")
        
        # Remove linhas onde setor é OBSERVAÇÃO ADULTO e data < 48 horas
        data_limite = datetime.now() - timedelta(hours=48)
        
        # Cria uma coluna temporária para comparação de datas (mantém a original intacta)
        # Usa dayfirst=True para formato brasileiro e aceita múltiplos formatos
        df_filtrado['data_temp'] = pd.to_datetime(df_filtrado['data'], dayfirst=True, errors='coerce')
        
        # Identifica linhas a remover (OBSERVAÇÃO ADULTO com menos de 48h)
        # Remove apenas se a data foi parseada com sucesso (notna) e é recente (> data_limite)
        mask_observacao = (df_filtrado['setor'] == 'OBSERVAÇÃO ADULTO') & (df_filtrado['data_temp'].notna()) & (df_filtrado['data_temp'] > data_limite)
        registros_observacao_removidos = mask_observacao.sum()
        
        # Aplica o filtro
        df_filtrado = df_filtrado[~mask_observacao]
        
        # Remove a coluna temporária
        df_filtrado = df_filtrado.drop(columns=['data_temp'])
        
        print(f"Registros removidos (OBSERVAÇÃO ADULTO < 48h): {registros_observacao_removidos}")
        
        # Remove linhas onde a coluna "dados" contém datas próximas (±15 dias) da data de internação
        def verificar_datas_proximas(row):
            """Verifica se há datas na coluna 'dados' próximas à data de internação (±15 dias)"""
            if pd.isna(row['dados']) or pd.isna(row['data']):
                return False
            
            # Converte a data de internação
            try:
                data_internacao = pd.to_datetime(row['data'], dayfirst=True)
            except:
                return False
            
            # Extrai todas as datas da coluna 'dados'
            # Padrões: dd/mm/aaaa ou dd/mm
            padrao_data_completa = r'\b(\d{2})/(\d{2})/(\d{4}|\d{2})\b'
            padrao_data_curta = r'\b(\d{2})/(\d{2})\b'
            
            texto_dados = str(row['dados'])
            datas_encontradas = []
            
            # Busca datas no formato dd/mm/aaaa ou dd/mm/aa
            matches = re.finditer(padrao_data_completa, texto_dados)
            for match in matches:
                dia, mes, ano = match.groups()
                # Se ano tem 2 dígitos, assume 20xx
                if len(ano) == 2:
                    ano = '20' + ano
                try:
                    data = datetime(int(ano), int(mes), int(dia))
                    datas_encontradas.append(data)
                except:
                    continue
            
            # Busca datas no formato dd/mm (sem ano)
            # Remove as datas completas já encontradas para evitar duplicação
            texto_sem_completas = re.sub(padrao_data_completa, '', texto_dados)
            matches = re.finditer(padrao_data_curta, texto_sem_completas)
            for match in matches:
                dia, mes = match.groups()
                # Usa o ano da data de internação
                ano_internacao = data_internacao.year
                try:
                    data = datetime(ano_internacao, int(mes), int(dia))
                    datas_encontradas.append(data)
                except:
                    continue
            
            # Verifica se alguma data está dentro do intervalo de ±15 dias
            limite_inferior = data_internacao - timedelta(days=15)
            limite_superior = data_internacao + timedelta(days=15)
            
            for data in datas_encontradas:
                if limite_inferior <= data <= limite_superior:
                    return True
            
            return False
        
        # Aplica a verificação
        mask_datas_proximas = df_filtrado.apply(verificar_datas_proximas, axis=1)
        registros_datas_proximas = mask_datas_proximas.sum()
        
        # Remove as linhas com datas próximas
        df_filtrado = df_filtrado[~mask_datas_proximas]
        
        print(f"Registros removidos (datas próximas na coluna 'dados'): {registros_datas_proximas}")
        
        # Move linhas com coluna "dados" vazia para o topo
        # Cria uma máscara para identificar linhas vazias (NaN, None, string vazia ou só espaços)
        mask_vazio = df_filtrado['dados'].isna() | (df_filtrado['dados'].astype(str).str.strip() == '') | (df_filtrado['dados'].astype(str) == 'nan')
        
        df_sem_dados = df_filtrado[mask_vazio]
        df_com_dados = df_filtrado[~mask_vazio]
        
        # Concatena: linhas vazias primeiro, depois as com dados
        df_filtrado = pd.concat([df_sem_dados, df_com_dados], ignore_index=True)
        
        print(f"Linhas com coluna 'dados' vazia movidas para o topo: {len(df_sem_dados)}")
        
        # Salva o CSV corrigido
        df_filtrado.to_csv(csv_path, index=False)
        print(f"Arquivo corrigido: {csv_path}")
        print(f"Total de registros após o tratamento: {len(df_filtrado)}")
        
        
        # Abre o arquivo CSV com o programa padrão de planilhas
        # Comentado: abertura automática desabilitada
        # try:
        #     import subprocess
        #     import platform
        #     
        #     print(f"📂 Abrindo arquivo: {csv_path}")
        #     sistema = platform.system()
        #     
        #     if sistema == 'Windows':
        #         os.startfile(csv_path)
        #     elif sistema == 'Darwin':  # macOS
        #         subprocess.run(['open', csv_path])
        #     else:  # Linux
        #         subprocess.run(['xdg-open', csv_path])
        #         
        #     print("✅ Arquivo aberto com sucesso!")
        # except Exception as e:
        #     print(f"⚠️ Não foi possível abrir o arquivo automaticamente: {e}")
        #     print(f"📍 Você pode abrir manualmente em: {csv_path}")
        
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        