def solicita_trata_dados():
    import pandas as pd
    import os
    import re
    from datetime import datetime, timedelta
    import logging
    from autoreg.ras_paciente import (
        filtrar_lembretes_nao_lidos, filtrar_ra_anterior_solicitado, remover_lembretes_uti, tem_data_proxima,
    )

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'internados_ghosp_avancado.csv')
    
    # Verifica se o arquivo existe
    if not os.path.exists(csv_path):
        print(f"Arquivo não encontrado: {csv_path}")
        return
    
    def _ras(df_parte):
        if 'internacao' not in df_parte.columns or df_parte.empty:
            return 'nenhum'
        return ', '.join(str(ra) for ra in df_parte['internacao'])

    def _log_removidos(motivo, df_antes, df_depois):
        removidos = df_antes[~df_antes.index.isin(df_depois.index)] if 'internacao' not in df_antes.columns \
            else df_antes[~df_antes['internacao'].isin(df_depois['internacao'])]
        if not removidos.empty:
            logging.info(f"-std: removidos ({motivo}): {_ras(removidos)}")

    # Lê o CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"Total de registros antes do tratamento: {len(df)}")
        logging.info(f"-std: {len(df)} registro(s) recebido(s): {_ras(df)}")

        # Remove RAs cujos lembretes -ign não confirmou ter lido: sem a leitura
        # não há como saber se já foram solicitados (falha fechada)
        df_antes = df
        df, registros_nao_lidos = filtrar_lembretes_nao_lidos(df)
        _log_removidos('lembretes não lidos pelo -ign — próximo ciclo', df_antes, df)
        print(f"Registros removidos (lembretes não lidos pelo -ign — ficam para o próximo ciclo): {registros_nao_lidos}")
        if registros_nao_lidos:
            logging.warning(f"-std: {registros_nao_lidos} RA(s) removido(s) por lembretes não lidos pelo -ign")
        if df.empty:
            df.to_csv(csv_path, index=False)
            print(f"Nenhum registro com lembretes lidos — execute -ign (ou -aihs) antes. Arquivo salvo vazio: {csv_path}")
            return

        # Remove RAs cujo RA anterior do mesmo paciente (mesma data/24h) já foi
        # solicitado — marcados por -ign na coluna ra_anterior_solicitado
        df_antes = df
        df, registros_ra_anterior = filtrar_ra_anterior_solicitado(df)
        _log_removidos('RA anterior na mesma data/24h já solicitado', df_antes, df)
        print(f"Registros removidos (RA anterior na mesma data/24h já solicitado): {registros_ra_anterior}")

        # Remove linhas onde a coluna "setor" é PEDIATRIA ou RPA-POS ANESTESICA
        setores_excluir = ['PEDIATRIA', 'RPA-POS ANESTESICA']
        df_filtrado = df[~df['setor'].isin(setores_excluir)]
        
        registros_removidos = len(df) - len(df_filtrado)
        _log_removidos('setor PEDIATRIA/RPA-POS ANESTESICA', df, df_filtrado)
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
        if registros_observacao_removidos:
            logging.info(f"-std: removidos (OBSERVAÇÃO ADULTO < 48h): {_ras(df_filtrado[mask_observacao])}")
        
        # Aplica o filtro
        df_filtrado = df_filtrado[~mask_observacao]
        
        # Remove a coluna temporária
        df_filtrado = df_filtrado.drop(columns=['data_temp'])
        
        print(f"Registros removidos (OBSERVAÇÃO ADULTO < 48h): {registros_observacao_removidos}")
        
        # Remove linhas onde a coluna "dados" contém datas próximas (±15 dias) da data de internação,
        # desconsiderando lembretes de UTI
        def verificar_datas_proximas(row):
            """Verifica se há datas na coluna 'dados' próximas à data de internação (±15 dias)"""
            if pd.isna(row['dados']) or pd.isna(row['data']):
                return False
            try:
                data_internacao = pd.to_datetime(row['data'], dayfirst=True)
            except:
                return False
            # Solicitação de UTI não conta como solicitação já realizada
            return tem_data_proxima(remover_lembretes_uti(row['dados']), data_internacao)

        # Aplica a verificação
        mask_datas_proximas = df_filtrado.apply(verificar_datas_proximas, axis=1)
        registros_datas_proximas = mask_datas_proximas.sum()
        if registros_datas_proximas:
            logging.info(
                f"-std: removidos (lembrete não-UTI com data a ±15 dias da internação — já solicitado): "
                f"{_ras(df_filtrado[mask_datas_proximas])}"
            )
        
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
        logging.info(f"-std: {len(df_filtrado)} registro(s) seguem para solicitação: {_ras(df_filtrado)}")
        
        
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
        logging.exception(f"-std: erro ao processar {csv_path} — arquivo NÃO foi filtrado: {e}")
        