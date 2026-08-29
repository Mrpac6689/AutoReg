import os
import pandas as pd


def solicita_pre_aih_bridge():
    """
    Substitui a etapa interativa -spa no fluxo automático (-solicita-auto).

    Remove do CSV os registros que o -spaa deixou sem 'link' (categoria
    MANUAL: nenhum laudo compatível encontrado automaticamente). Esses
    registros não são tocados no G-HOSP — apenas somem do CSV desta
    execução e ficam pendentes de revisão manual futura via -spa.
    """
    print("\n---===> PONTE AUTOMÁTICA SOLICITA PRÉ-AIH (-spb) <===---")

    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_solicita = os.path.join(user_dir, 'solicita_inf_aih.csv')

    if not os.path.exists(csv_solicita):
        print(f"❌ Arquivo não encontrado: {csv_solicita}")
        return None

    try:
        df = pd.read_csv(csv_solicita)
    except Exception as e:
        print(f"❌ Erro ao ler {csv_solicita}: {e}")
        return None

    if 'link' not in df.columns:
        print("❌ Arquivo CSV não contém a coluna 'link'")
        return None

    total_antes = len(df)
    mask_sem_link = df['link'].isna() | (df['link'] == '')
    removidos = int(mask_sem_link.sum())

    df_restante = df[~mask_sem_link].reset_index(drop=True)
    df_restante.to_csv(csv_solicita, index=False)

    print(f"   📋 {total_antes} registro(s) recebido(s) de -spaa")
    print(f"   🗑️  {removidos} registro(s) removido(s) (sem laudo compatível — pendente de revisão manual)")
    print(f"   ➡️  {len(df_restante)} registro(s) seguem para -sia")

    return df_restante
