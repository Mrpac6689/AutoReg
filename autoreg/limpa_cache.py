def limpa_cache():
    import os
    
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    
    # Arquivos que devem ser mantidos
    arquivos_protegidos = ['solicita_inf_aih.csv', 'internados_ghosp_avancado.csv']
    
    # Verifica se o diretório existe
    if not os.path.exists(user_dir):
        print(f"Diretório não encontrado: {user_dir}")
        return
    
    # Lista todos os arquivos no diretório
    try:
        arquivos_removidos = 0
        arquivos_mantidos = 0
        
        for arquivo in os.listdir(user_dir):
            arquivo_path = os.path.join(user_dir, arquivo)
            
            # Pula se for um diretório
            if os.path.isdir(arquivo_path):
                continue
            
            # Mantém apenas os arquivos protegidos
            if arquivo in arquivos_protegidos:
                arquivos_mantidos += 1
                print(f"✓ Mantido: {arquivo}")
            else:
                try:
                    os.remove(arquivo_path)
                    arquivos_removidos += 1
                    print(f"✗ Removido: {arquivo}")
                except Exception as e:
                    print(f"⚠ Erro ao remover {arquivo}: {e}")
        
        print(f"\n📊 Resumo da limpeza:")
        print(f"   Arquivos removidos: {arquivos_removidos}")
        print(f"   Arquivos mantidos: {arquivos_mantidos}")
        print(f"   Diretório: {user_dir}")
        
    except Exception as e:
        print(f"❌ Erro ao limpar cache: {e}")