#!/usr/bin/env python3
"""
AutoReg - Coordenador de Workflow
Automatização de Sistemas de Saúde - SISREG & G-HOSP
Versão 8.0.3 - Julho de 2025
Autor: Michel Ribeiro Paes (MrPaC6689)
"""

import argparse
import sys
import os
import subprocess
import configparser
from pathlib import Path

from autoreg import extrai_codigos_internacao
from autoreg import interna_pacientes
from autoreg import extrai_internados_sisreg
from autoreg import extrai_internados_ghosp
from autoreg import compara_internados
from autoreg import motivo_alta
from autoreg import extrai_codigos_sisreg_alta
from autoreg import executa_alta
from autoreg import atualiza_restos
from autoreg import extrai_internacoes_duplicadas
from autoreg import trata_duplicados
from autoreg import devolvidos

# Dicionário com as funções e suas descrições
FUNCOES = {
    'extrai_codigos_internacao': {
        'func': extrai_codigos_internacao,
        'desc': 'Extrai códigos de internação do SISREG'
    },
    'interna_pacientes': {
        'func': interna_pacientes,
        'desc': 'Realiza internação de pacientes no SISREG'
    },
    'extrai_internados_sisreg': {
        'func': extrai_internados_sisreg,
        'desc': 'Extrai lista de internados do SISREG'
    },
    'extrai_internados_ghosp': {
        'func': extrai_internados_ghosp,
        'desc': 'Extrai lista de internados do G-HOSP'
    },
    'compara_internados': {
        'func': compara_internados,
        'desc': 'Compara listas de internados entre sistemas'
    },
    'motivo_alta': {
        'func': motivo_alta,
        'desc': 'Captura motivos de alta no G-HOSP'
    },
    'extrai_codigos_sisreg_alta': {
        'func': extrai_codigos_sisreg_alta,
        'desc': 'Extrai códigos SISREG para alta'
    },
    'executa_alta': {
        'func': executa_alta,
        'desc': 'Executa altas no SISREG'
    },
    'atualiza_restos': {
        'func': atualiza_restos,
        'desc': 'Atualiza arquivo de pacientes restantes'
    },
    'extrai_internacoes_duplicadas': {
        'func': extrai_internacoes_duplicadas,
        'desc': 'Identifica internações duplicadas'
    },
    'trata_duplicados': {
        'func': trata_duplicados,
        'desc': 'Processa pacientes com duplicações'
    },
    'devolvidos': {
        'func': devolvidos,
        'desc': 'Processa solicitações devolvidas'
    }
}

def mostrar_informacoes():
    """Exibe informações do programa"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                    AutoReg                                    ║
║                    Automatização de Sistemas de Saúde                         ║
║                               SISREG & G-HOSP                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Versão: 8.0.3-1                                                               ║
║ Autor: Michel Ribeiro Paes (MrPaC6689)                                        ║
║ Contato: michelrpaes@gmail.com                                                ║
║ Repositório: https://github.com/Mrpac6689/AutoReg                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝

DESCRIÇÃO:
    Coordenador de workflow para automatização de processos de internação e alta
    em sistemas hospitalares SISREG e G-HOSP.

FUNÇÕES DISPONÍVEIS:
""")
    
    # Lista as funções disponíveis com suas flags
    flags = [
        ('-eci', '--extrai-codigos-internacao', 'extrai_codigos_internacao'),
        ('-ip', '--interna-pacientes', 'interna_pacientes'),
        ('-eis', '--extrai-internados-sisreg', 'extrai_internados_sisreg'),
        ('-eig', '--extrai-internados-ghosp', 'extrai_internados_ghosp'),
        ('-ci', '--compara-internados', 'compara_internados'),
        ('-ma', '--motivo-alta', 'motivo_alta'),
        ('-ecsa', '--extrai-codigos-sisreg-alta', 'extrai_codigos_sisreg_alta'),
        ('-ea', '--executa-alta', 'executa_alta'),
        ('-ar', '--atualiza-restos', 'atualiza_restos'),
        ('-eid', '--extrai-internacoes-duplicadas', 'extrai_internacoes_duplicadas'),
        ('-td', '--trata-duplicados', 'trata_duplicados'),
        ('-dev', '--devolvidos', 'devolvidos')
    ]
    
    for short, long, func_name in flags:
        desc = FUNCOES[func_name]['desc']
        print(f"    {short:<6} {long:<32} {desc}")
    
    print(f"""
FUNÇÕES ESPECIAIS:
    -all   --all                         Executa todas as funções em sequência (exceto devolvidos)
    -cfg   --config                      Edita arquivo de configuração
    -dir   --directory                   Abre pasta de arquivos do AutoReg

EXEMPLOS DE USO:
    python autoreg.py -eci               Extrai códigos de internação
    python autoreg.py -eci -ip           Executa duas funções em sequência
    python autoreg.py --all              Executa workflow completo
    python autoreg.py --config           Edita configuração
    python autoreg.py --help             Mostra esta ajuda

Para mais informações, consulte o README.md
""")

def editar_config():
    """Abre o arquivo config.ini para edição"""
    config_path = Path.cwd() / 'config.ini'
    
    if not config_path.exists():
        print("❌ Arquivo config.ini não encontrado!")
        return
    
    print("📝 Escolha o editor para abrir config.ini:")
    print("1. nano")
    print("2. vi/vim")
    print("3. Editor padrão do sistema")
    
    try:
        escolha = input("Digite sua opção (1-3): ").strip()
        
        if escolha == '1':
            subprocess.run(['nano', str(config_path)])
        elif escolha == '2':
            subprocess.run(['vi', str(config_path)])
        elif escolha == '3':
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', str(config_path)])
            elif sys.platform.startswith('linux'):  # Linux
                subprocess.run(['xdg-open', str(config_path)])
            else:  # Windows (fallback)
                os.startfile(str(config_path))
        else:
            print("❌ Opção inválida!")
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada.")
    except Exception as e:
        print(f"❌ Erro ao abrir editor: {e}")

def abrir_diretorio():
    """Abre a pasta ~/AutoReg para consulta de arquivos"""
    home = Path.home()
    autoreg_dir = home / 'AutoReg'
    
    if not autoreg_dir.exists():
        print("📁 Criando diretório ~/AutoReg...")
        autoreg_dir.mkdir(exist_ok=True)
    
    try:
        print(f"📂 Abrindo diretório: {autoreg_dir}")
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', str(autoreg_dir)])
        elif sys.platform.startswith('linux'):  # Linux
            subprocess.run(['xdg-open', str(autoreg_dir)])
        else:  # Windows (fallback)
            os.startfile(str(autoreg_dir))
    except Exception as e:
        print(f"❌ Erro ao abrir diretório: {e}")
        print(f"📍 Caminho do diretório: {autoreg_dir}")

def executar_funcao(func_name):
    """Executa uma função específica"""
    if func_name in FUNCOES:
        print(f"🚀 Executando: {FUNCOES[func_name]['desc']}")
        try:
            FUNCOES[func_name]['func']()
            print(f"✅ Concluído: {FUNCOES[func_name]['desc']}")
        except Exception as e:
            print(f"❌ Erro ao executar {func_name}: {e}")
            return False
        return True
    else:
        print(f"❌ Função {func_name} não encontrada!")
        return False

def executar_todas():
    """Executa todas as funções em sequência, exceto devolvidos"""
    funcoes_sequencia = [
        'extrai_codigos_internacao',
        'interna_pacientes', 
        'extrai_internados_sisreg',
        'extrai_internados_ghosp',
        'compara_internados',
        'motivo_alta',
        'extrai_codigos_sisreg_alta',
        'executa_alta',
        'atualiza_restos',
        'extrai_internacoes_duplicadas',
        'trata_duplicados'
        # devolvidos não incluído conforme solicitado
    ]
    
    print("🔄 Iniciando execução sequencial de todas as funções...")
    print(f"📋 Total de funções: {len(funcoes_sequencia)}")
    
    sucesso = 0
    for i, func_name in enumerate(funcoes_sequencia, 1):
        print(f"\n[{i}/{len(funcoes_sequencia)}] ", end="")
        if executar_funcao(func_name):
            sucesso += 1
        else:
            print(f"❌ Parando execução devido ao erro em {func_name}")
            break
    
    print(f"\n📊 Execução concluída: {sucesso}/{len(funcoes_sequencia)} funções executadas com sucesso")

def main():
    """Função principal do coordenador de workflow"""
    parser = argparse.ArgumentParser(
        description='AutoReg - Coordenador de Workflow para SISREG & G-HOSP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s -eci                 Extrai códigos de internação
  %(prog)s -eci -ip             Executa duas funções em sequência
  %(prog)s --all                Executa workflow completo
  %(prog)s --config             Edita configuração
        """
    )
    
    # Flags para cada função
    parser.add_argument('-eci', '--extrai-codigos-internacao', action='store_true',
                       help='Extrai códigos de internação do SISREG')
    parser.add_argument('-ip', '--interna-pacientes', action='store_true',
                       help='Realiza internação de pacientes no SISREG')
    parser.add_argument('-eis', '--extrai-internados-sisreg', action='store_true',
                       help='Extrai lista de internados do SISREG')
    parser.add_argument('-eig', '--extrai-internados-ghosp', action='store_true',
                       help='Extrai lista de internados do G-HOSP')
    parser.add_argument('-ci', '--compara-internados', action='store_true',
                       help='Compara listas de internados entre sistemas')
    parser.add_argument('-ma', '--motivo-alta', action='store_true',
                       help='Captura motivos de alta no G-HOSP')
    parser.add_argument('-ecsa', '--extrai-codigos-sisreg-alta', action='store_true',
                       help='Extrai códigos SISREG para alta')
    parser.add_argument('-ea', '--executa-alta', action='store_true',
                       help='Executa altas no SISREG')
    parser.add_argument('-ar', '--atualiza-restos', action='store_true',
                       help='Atualiza arquivo de pacientes restantes')
    parser.add_argument('-eid', '--extrai-internacoes-duplicadas', action='store_true',
                       help='Identifica internações duplicadas')
    parser.add_argument('-td', '--trata-duplicados', action='store_true',
                       help='Processa pacientes com duplicações')
    parser.add_argument('-dev', '--devolvidos', action='store_true',
                       help='Processa solicitações devolvidas')
    
    # Funções especiais
    parser.add_argument('-all', '--all', action='store_true',
                       help='Executa todas as funções em sequência (exceto devolvidos)')
    parser.add_argument('-cfg', '--config', action='store_true',
                       help='Edita arquivo de configuração config.ini')
    parser.add_argument('-dir', '--directory', action='store_true',
                       help='Abre pasta ~/AutoReg para consulta de arquivos')
    
    args = parser.parse_args()
    
    # Se nenhum argumento foi fornecido, mostra informações
    if len(sys.argv) == 1:
        mostrar_informacoes()
        return
    
    # Mapeamento de argumentos para funções
    arg_to_func = {
        'extrai_codigos_internacao': 'extrai_codigos_internacao',
        'interna_pacientes': 'interna_pacientes',
        'extrai_internados_sisreg': 'extrai_internados_sisreg',
        'extrai_internados_ghosp': 'extrai_internados_ghosp',
        'compara_internados': 'compara_internados',
        'motivo_alta': 'motivo_alta',
        'extrai_codigos_sisreg_alta': 'extrai_codigos_sisreg_alta',
        'executa_alta': 'executa_alta',
        'atualiza_restos': 'atualiza_restos',
        'extrai_internacoes_duplicadas': 'extrai_internacoes_duplicadas',
        'trata_duplicados': 'trata_duplicados',
        'devolvidos': 'devolvidos'
    }
    
    # Processa funções especiais primeiro
    if args.all:
        executar_todas()
        return
    
    if args.config:
        editar_config()
        return
        
    if args.directory:
        abrir_diretorio()
        return
    
    # Executa funções regulares em sequência
    funcoes_para_executar = []
    for arg, func_name in arg_to_func.items():
        if getattr(args, arg.replace('-', '_')):
            funcoes_para_executar.append(func_name)
    
    if funcoes_para_executar:
        print(f"🔄 Executando {len(funcoes_para_executar)} função(ões) em sequência...")
        for i, func_name in enumerate(funcoes_para_executar, 1):
            print(f"\n[{i}/{len(funcoes_para_executar)}] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                break
    else:
        print("❌ Nenhuma função válida foi especificada!")
        print("💡 Use --help para ver as opções disponíveis")

if __name__ == "__main__":
    main()  
