#!/usr/bin/env python3
"""
Script temporário para copiar coluna 'dn' de especialdn.csv para especial.csv
Autor: Michel Ribeiro Paes
"""

import os
import pandas as pd

def corrige_dn():
    """
    Lê especialdn.csv e especial.csv, busca por RA correspondente e
    adiciona a coluna 'dn' em especial.csv
    """
    # Definir caminhos
    user_dir = os.path.expanduser('~/AutoReg')
    especial_path = os.path.join(user_dir, 'especial.csv')
    especialdn_path = os.path.join(user_dir, 'especialdn.csv')
    
    print("🔧 Iniciando correção de DN...")
    
    # Verificar se os arquivos existem
    if not os.path.exists(especial_path):
        print(f"❌ Arquivo não encontrado: {especial_path}")
        return
    
    if not os.path.exists(especialdn_path):
        print(f"❌ Arquivo não encontrado: {especialdn_path}")
        return
    
    # Ler os arquivos CSV
    print(f"📖 Lendo {especial_path}...")
    df_especial = pd.read_csv(especial_path, dtype=str)
    
    print(f"📖 Lendo {especialdn_path}...")
    df_especialdn = pd.read_csv(especialdn_path, dtype=str)
    
    # Verificar se as colunas necessárias existem
    if 'ra' not in df_especial.columns:
        print("❌ Coluna 'ra' não encontrada em especial.csv")
        return
    
    if 'ra' not in df_especialdn.columns or 'dn' not in df_especialdn.columns:
        print("❌ Colunas 'ra' ou 'dn' não encontradas em especialdn.csv")
        return
    
    print(f"📊 Total de registros em especial.csv: {len(df_especial)}")
    print(f"📊 Total de registros em especialdn.csv: {len(df_especialdn)}")
    
    # Criar coluna 'dn' em especial.csv se não existir
    if 'dn' not in df_especial.columns:
        df_especial['dn'] = ''
        print("✅ Coluna 'dn' criada em especial.csv")
    
    # Criar um dicionário para busca rápida: ra -> dn
    dn_dict = dict(zip(df_especialdn['ra'], df_especialdn['dn']))
    
    # Contador de correspondências
    encontrados = 0
    nao_encontrados = 0
    
    # Percorrer especial.csv e buscar DN correspondente
    for idx, row in df_especial.iterrows():
        ra = str(row['ra']).strip()
        
        if ra in dn_dict:
            dn_valor = dn_dict[ra]
            df_especial.at[idx, 'dn'] = dn_valor
            encontrados += 1
            print(f"  ✓ [{idx+1}] RA {ra}: DN = {dn_valor}")
        else:
            nao_encontrados += 1
            print(f"  ⚠️  [{idx+1}] RA {ra}: DN não encontrado em especialdn.csv")
    
    # Salvar o arquivo especial.csv atualizado
    df_especial.to_csv(especial_path, index=False)
    print(f"\n✅ Arquivo atualizado: {especial_path}")
    
    # Exibir estatísticas
    print(f"\n📊 Estatísticas:")
    print(f"   ✅ DNs encontrados e copiados: {encontrados}")
    print(f"   ⚠️  RAs sem DN correspondente: {nao_encontrados}")
    print(f"   📋 Total processado: {len(df_especial)}")
    
    print("\n🎉 Correção concluída!")


if __name__ == "__main__":
    try:
        corrige_dn()
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
