def trata_altas():
    import pandas as pd
    import os
    
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'pacientes_de_alta.csv')
    
    # Verifica se o arquivo existe
    if not os.path.exists(csv_path):
        print(f"Arquivo não encontrado: {csv_path}")
        return
    
    # Lê o CSV
    try:
        df = pd.read_csv(csv_path)
        
        # Verifica se a coluna "Motivo da Alta" existe
        if "Motivo da Alta" not in df.columns:
            print("Coluna 'Motivo da Alta' não encontrada no CSV")
            return
        
        # Substitui "PERMANENCIA POR OUTROS MOTIVOS" por "ALTA MELHORADO"
        df["Motivo da Alta"] = df["Motivo da Alta"].replace(
            "PERMANENCIA POR OUTROS MOTIVOS", 
            "ALTA MELHORADO"
        )
        
        # Substitui valores em branco (NaN) por "ALTA MELHORADO"
        df["Motivo da Alta"] = df["Motivo da Alta"].fillna("ALTA MELHORADO")
        
        # Salva o CSV corrigido
        df.to_csv(csv_path, index=False)
        print(f"Arquivo corrigido: {csv_path}")
        print(f"Total de registros processados: {len(df)}")
        
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")