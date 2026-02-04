# autoreg/exames_utils.py
# Módulo compartilhado com funções auxiliares para identificação e comparação de exames
# Extraído de exames_ambulatorio_solicita.py para reutilização

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
        ('COLUNA TORACICA', 'COLUNA TORACICA'),
        ('COLUNA TORÁCICA', 'COLUNA TORACICA'),
        ('COLUNA DORSAL', 'COLUNA DORSAL'),
        ('COLUNA CERVICAL', 'COLUNA CERVICAL'),
        # JOELHO/JOELHOS - termos com lateralidade primeiro (mais específicos)
        ('JOELHO DIREITO', 'ARTICULACOES JOELHOS'),
        ('JOELHO DIREITA', 'ARTICULACOES JOELHOS'),
        ('JOELHO ESQUERDO', 'ARTICULACOES JOELHOS'),
        ('JOELHO ESQUERDA', 'ARTICULACOES JOELHOS'),
        ('JOELHOS DIREITO', 'ARTICULACOES JOELHOS'),
        ('JOELHOS DIREITA', 'ARTICULACOES JOELHOS'),
        ('JOELHOS ESQUERDO', 'ARTICULACOES JOELHOS'),
        ('JOELHOS ESQUERDA', 'ARTICULACOES JOELHOS'),
        # JOELHO/JOELHOS - termos sem lateralidade depois
        ('ARTICULACOES JOELHOS', 'ARTICULACOES JOELHOS'),
        ('ARTICULAÇÕES JOELHOS', 'ARTICULACOES JOELHOS'),
        ('JOELHO', 'ARTICULACOES JOELHOS'),
        ('JOELHOS', 'ARTICULACOES JOELHOS'),
        ('COXA', 'COXA'),
        ('COXA DIREITA', 'COXA'),
        ('COXA DIREITO', 'COXA'),
        ('COXA ESQUERDA', 'COXA'),
        ('COXA ESQUERDO', 'COXA'),
        ('PERNA', 'PERNA'),
        ('PERNA DIREITA', 'PERNA'),
        ('PERNA DIREITO', 'PERNA'),
        ('PERNA ESQUERDA', 'PERNA'),
        ('PERNA ESQUERDO', 'PERNA'),
        ('MAO', 'MAO'),
        ('MÃO', 'MAO'),
        ('MAO DIREITA', 'MAO'),
        ('MAO DIREITO', 'MAO'),
        ('MÃO DIREITA', 'MAO'),
        ('MÃO DIREITO', 'MAO'),
        ('MAO ESQUERDA', 'MAO'),
        ('MAO ESQUERDO', 'MAO'),
        ('MÃO ESQUERDA', 'MAO'),
        ('MÃO ESQUERDO', 'MAO'),
        ('PESCOCO', 'PESCOCO'),
        ('PESCOÇO', 'PESCOCO'),
        ('PE', 'PE'),
        ('PE DIREITO', 'PE'),
        ('PE DIREITA', 'PE'),
        ('PE ESQUERDO', 'PE'),
        ('PE ESQUERDA', 'PE'),
        ('OMBRO', 'OMBRO'),
        ('OMBRO DIREITO', 'OMBRO'),
        ('OMBRO DIREITA', 'OMBRO'),
        ('OMBRO ESQUERDO', 'OMBRO'),
        ('OMBRO ESQUERDA', 'OMBRO'),
        ('PUNHO', 'PUNHO'),
        ('PUNHO DIREITO', 'PUNHO'),
        ('PUNHO DIREITA', 'PUNHO'),
        ('PUNHO ESQUERDO', 'PUNHO'),
        ('PUNHO ESQUERDA', 'PUNHO'),
        ('TORNOZELO', 'TORNOZELO'),
        ('TORNOZELO DIREITO', 'TORNOZELO'),
        ('TORNOZELO DIREITA', 'TORNOZELO'),
        ('TORNOZELO ESQUERDO', 'TORNOZELO'),
        ('TORNOZELO ESQUERDA', 'TORNOZELO'),
        ('COTOVELO', 'COTOVELO'),
        ('COTOVELO DIREITO', 'COTOVELO'),
        ('COTOVELO DIREITA', 'COTOVELO'),
        ('COTOVELO ESQUERDO', 'COTOVELO'),
        ('COTOVELO ESQUERDA', 'COTOVELO'),
        ('BRACO', 'BRACO'),
        ('BRAÇO', 'BRACO'),
        ('BRACO DIREITO', 'BRACO'),
        ('BRACO DIREITA', 'BRACO'),
        ('BRAÇO DIREITO', 'BRACO'),
        ('BRAÇO DIREITA', 'BRACO'),
        ('BRACO ESQUERDO', 'BRACO'),
        ('BRACO ESQUERDA', 'BRACO'),
        ('BRAÇO ESQUERDO', 'BRACO'),
        ('BRAÇO ESQUERDA', 'BRACO'),
        ('ANTEBRACO', 'ANTEBRACO'),
        ('ANTEBRAÇO', 'ANTEBRACO'),
        ('ANTEBRACO DIREITO', 'ANTEBRACO'),
        ('ANTEBRACO DIREITA', 'ANTEBRACO'),
        ('ANTEBRAÇO DIREITO', 'ANTEBRACO'),
        ('ANTEBRAÇO DIREITA', 'ANTEBRACO'),
        ('ANTEBRACO ESQUERDO', 'ANTEBRACO'),
        ('ANTEBRACO ESQUERDA', 'ANTEBRACO'),
        ('ANTEBRAÇO ESQUERDO', 'ANTEBRACO'),
        ('ANTEBRAÇO ESQUERDA', 'ANTEBRACO'),
        ('SEIOS DA FACE', 'SEIOS DA FACE'),
        ('SEIOS DE FACE', 'SEIOS DA FACE'),
        ('FACE', 'FACE'),
        ('MASTOIDES OU OUVIDOS', 'MASTOIDES OU OUVIDOS'),
        ('MASTÓIDES OU OUVIDOS', 'MASTOIDES OU OUVIDOS'),
        ('CRANIO', 'CRANIO'),
        ('CRÂNIO', 'CRANIO'),
        ('ORBITA', 'CRANIO'),
        ('ÓRBITA', 'CRANIO')
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
            # Para termos de uma palavra como "JOELHO", verifica se não é parte de "JOELHOS"
            elif termo_busca == 'JOELHO':
                # Verifica se não está dentro de "JOELHOS" (plural) - se estiver, continua procurando
                if 'JOELHOS' in proc_normalizado:
                    continue  # Continua procurando por termos mais específicos
                return parte_identificada
            # Para termos de uma palavra como "PE", verifica se não é parte de "PESCOCO"
            elif termo_busca == 'PE':
                # Verifica se não está dentro de "PESCOCO" ou "PESCOÇO" - se estiver, continua procurando
                if 'PESCOCO' in proc_normalizado or 'PESCOÇO' in proc_normalizado:
                    continue  # Continua procurando por termos mais específicos
                return parte_identificada
            else:
                return parte_identificada
    
    return None

def identificar_lateralidade(procedimento):
    """
    Identifica a lateralidade (DIREITO/ESQUERDO) no procedimento.
    
    Args:
        procedimento: Procedimento do CSV
    
    Returns:
        'DIREITO', 'ESQUERDO' ou None
    """
    proc_normalizado = normalizar_texto(procedimento)
    
    # Verifica se há menção a DIREITO ou DIREITA
    if 'DIREITO' in proc_normalizado or 'DIREITA' in proc_normalizado:
        return 'DIREITO'
    # Verifica se há menção a ESQUERDO ou ESQUERDA
    elif 'ESQUERDO' in proc_normalizado or 'ESQUERDA' in proc_normalizado:
        return 'ESQUERDO'
    
    return None
