def limpa_cache():
    import os
    
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    
    # Arquivo que deve ser mantido
    arquivo_protegido = 'solicita_inf_aih.csv'
    
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
            
            # Mantém apenas o arquivo protegido
            if arquivo == arquivo_protegido:
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