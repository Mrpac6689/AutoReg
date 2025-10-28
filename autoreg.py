#!/usr/bin/env python3
"""
AutoReg - Coordenador de Workflow
Automatização de Sistemas de Saúde - SISREG & G-HOSP
Versão 9.6.2 - Outubro de 2025
Autor: Michel Ribeiro Paes (MrPaC6689)
"""

import argparse
import sys
import os
import configparser
import subprocess
import time
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
from autoreg import trata_altas
from autoreg import limpa_cache
from autoreg import devolvidos
from autoreg import pdf2csv
from autoreg import ghosp_nota  # Adicione este import
from autoreg import ghosp_cns  # Importa a função ghosp_cns
from autoreg import ghosp_especial  # Importa a função ghosp_especial
from autoreg import solicita_inf_aih  # Importa a função solicita_inf_aih
from autoreg import solicita_sisreg  # Importa a função solicita_sisreg
from autoreg import solicita_nota  # Importa a função solicita_nota
from autoreg import solicita_pre_aih  # Importa a função solicita_pre_aih
from autoreg import consulta_solicitacao_sisreg  # Importa a função consulta_solicitacao_sisreg
from autoreg import internados_ghosp_avancado  # Importa a função internados_ghosp_avancado
from autoreg import internados_ghosp_nota  # Importa a função internados_ghosp_nota
from autoreg import solicita_trata_dados  # Importa a função solicita_trata_dados

# Dicionário com as funções e suas descrições
FUNCOES = {
    'extrai_codigos_internacao': {
        'func': extrai_codigos_internacao,
        'desc': 'Extrai códigos de internação do SISREG'
    },
    'internados_ghosp_avancado': {
        'func': internados_ghosp_avancado,
        'desc': 'Extrai pacientes internados no GHOSP com informações adicionais'
    },
    'internados_ghosp_nota': {
        'func': internados_ghosp_nota,
        'desc': 'Extrai o conteúdo das notas dos prontuários do GHOSP'
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
    'trata_altas': {
        'func': trata_altas,
        'desc': 'Trata Motivos de Alta capturados'
    },
    'limpa_cache': {
        'func': limpa_cache,
        'desc': 'Limpa todos os arquivos da pasta ~/AutoReg, mantendo apenas solicita_inf_aih.csv'
    },
    'devolvidos': {
        'func': devolvidos,
        'desc': 'Processa solicitações devolvidas'
    },
    'pdf2csv': {
        'func': pdf2csv,
        'desc': 'Converte PDF de solicitações em CSV'
    },
    'ghosp_nota': {
        'func': ghosp_nota,
        'desc': 'Extrair notas de prontuários Ghosp'
    },
    'ghosp_cns': {
        'func': ghosp_cns,
        'desc': 'Extrai CNSs dos prontuários e cria lista_same_cns.csv'
    },
    'ghosp_especial': {
        'func': ghosp_especial,
        'desc': 'Extração de dados personalizados do GHOSP'
    },
    'solicita_inf_aih': {
        'func': solicita_inf_aih,
        'desc': 'Extrai informações da AIH'
    },
    'solicita_pre_aih': {
        'func': solicita_pre_aih,
        'desc': 'Extrai link para solicitação de aih do GHOSP'
    },
    'solicita_sisreg': {
        'func': solicita_sisreg,
        'desc': 'Executa Solicitações no Sistema SISREG'
    },
    'solicita_nota': {
        'func': solicita_nota,
        'desc': 'Insere numero da solicitação SISREG na nota de prontuário'
    },
    'consulta_solicitacao_sisreg': {
        'func': consulta_solicitacao_sisreg,
        'desc': 'Consulta o estado da Solicitação no sistema SISREG'
    },
    'solicita_trata_dados': {
        'func': solicita_trata_dados,
        'desc': 'Ajusta CSV para tratamento das solicitações de AIH previamente ao SISREG'
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
║ Versão: 9.6.2                                                                 ║
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
        ('-tat', '--trata-altas', 'trata_altas'),
        ('-clc', '--limpa-cache', 'limpa_cache'),
        ('-dev', '--devolvidos', 'devolvidos'),
        ('-p2c', '--pdf2csv', 'pdf2csv'),
        ('-ghn', '--ghosp-nota', 'ghosp_nota'),
        ('-ghc', '--ghosp-cns', 'ghosp_cns'),
        ('-iga', '--internados-ghosp-avancado', 'internados_ghosp_avancado'),
        ('-ign', '--internados-ghosp-nota', 'internados_ghosp_nota'),
        ('-especial', '--especial', 'ghosp_especial'),
        ('-sia', '--solicita-inf-aih', 'solicita_inf_aih'),
        ('-spa', '--solicita-pre-aih', 'solicita_pre_aih'),
        ('-ssr', '--solicita-sisreg', 'solicita_sisreg'),
        ('-snt', '--solicita-nota', 'solicita_nota'),
        ('-std', '--solicita-trata-dados', 'solicita_trata_dados'),
        ('-css', '--consulta-solicitacao-sisreg', 'consulta_solicitacao_sisreg'),
        ('-interna', '--interna', None),
        ('-analisa', '--analisa', None),
        ('-alta', '--alta', None),
        ('-solicita', '--solicita', None),
        ('-aihs', '--aihs', None)
    ]
    
    for short, long, func_name in flags:
        if func_name:
            desc = FUNCOES[func_name]['desc']
        elif short == '-interna':
            desc = 'Executa sequência de internação: -eci -ip'
        elif short == '-analisa':
            desc = 'Executa sequência de análise: -eis -eig -ci -ma'
        elif short == '-alta':
            desc = 'Executa sequência de alta: -tat -ecsa -ea -ar -eid -td -clc'
        elif short == '-solicita':
            desc = 'Executa rotina de Solicitação: -spa -sia -ssr -snt'
        elif short == '-aihs':
            desc = 'Executa rotina de notas: -iga -ign -std'
        else:
            desc = ''
        print(f"    {short:<6} {long:<32} {desc}")
    
    print(f"""
FUNÇÕES ESPECIAIS:
    -all   --all                         Executa workflow completo: -interna -analisa -alta
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
    """Executa todas as funções em sequência: -interna -analisa -alta"""
    
    # Prompt para repetição
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                    EXECUÇÃO COMPLETA DO WORKFLOW AUTOREG                      ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print("\nEste workflow executará sequencialmente: INTERNA → ANALISA → ALTA")
    print("Total de 13 funções por ciclo completo\n")
    
    while True:
        try:
            repeticoes = input("🔄 Quantas vezes deseja executar o workflow completo? (padrão: 1): ").strip()
            
            # Se o usuário não digitar nada, assume 1
            if repeticoes == "":
                repeticoes = 1
            else:
                repeticoes = int(repeticoes)
            
            # Valida se é um número positivo
            if repeticoes < 1:
                print("❌ Por favor, digite um número maior ou igual a 1.")
                continue
            
            break
        except ValueError:
            print("❌ Por favor, digite um número válido.")
        except KeyboardInterrupt:
            print("\n❌ Operação cancelada pelo usuário.")
            return
    
    print(f"\n{'='*80}")
    print(f"📋 CONFIGURAÇÃO: Executar workflow {repeticoes} vez(es)")
    print(f"{'='*80}\n")
    
    # Loop de repetição
    for ciclo in range(1, repeticoes + 1):
        print(f"\n{'#'*80}")
        print(f"#{'CICLO ' + str(ciclo) + '/' + str(repeticoes):^78}#")
        print(f"{'#'*80}\n")
        
        # Sequência 1: INTERNA
        print("="*80)
        print(f"CICLO {ciclo}/{repeticoes} - SEQUÊNCIA 1/3: INTERNAÇÃO (-eci -ip)")
        print("="*80)
        seq_interna = ['extrai_codigos_internacao', 'interna_pacientes']
        for i, func_name in enumerate(seq_interna, 1):
            print(f"\n[CICLO {ciclo} | INTERNA {i}/{len(seq_interna)}] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                return
        
        # Sequência 2: ANALISA
        print("\n" + "="*80)
        print(f"CICLO {ciclo}/{repeticoes} - SEQUÊNCIA 2/3: ANÁLISE (-eis -eig -ci -ma)")
        print("="*80)
        seq_analisa = ['extrai_internados_sisreg', 'extrai_internados_ghosp', 'compara_internados', 'motivo_alta']
        for i, func_name in enumerate(seq_analisa, 1):
            print(f"\n[CICLO {ciclo} | ANALISA {i}/{len(seq_analisa)}] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                return
        
        # Sequência 3: ALTA
        print("\n" + "="*80)
        print(f"CICLO {ciclo}/{repeticoes} - SEQUÊNCIA 3/3: ALTA (-tat -ecsa -ea -ar -eid -td -clc)")
        print("="*80)
        seq_alta = ['trata_altas', 'extrai_codigos_sisreg_alta', 'executa_alta', 'atualiza_restos', 'extrai_internacoes_duplicadas', 'trata_duplicados', 'limpa_cache']
        for i, func_name in enumerate(seq_alta, 1):
            print(f"\n[CICLO {ciclo} | ALTA {i}/{len(seq_alta)}] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                return
        
        print(f"\n{'='*80}")
        print(f"✅ CICLO {ciclo}/{repeticoes} CONCLUÍDO COM SUCESSO!")
        print(f"{'='*80}")
        
        # Se não for o último ciclo, mostra mensagem de continuação
        if ciclo < repeticoes:
            print(f"\n⏳ Iniciando próximo ciclo ({ciclo + 1}/{repeticoes})...\n")
    
    # Resumo final
    print(f"\n{'#'*80}")
    print(f"#{'WORKFLOW COMPLETO FINALIZADO':^78}#")
    print(f"{'#'*80}")
    total_funcoes = len(seq_interna) + len(seq_analisa) + len(seq_alta)
    print(f"📊 Ciclos executados: {repeticoes}")
    print(f"📊 Funções por ciclo: {total_funcoes}")
    print(f"📊 Total de funções executadas: {total_funcoes * repeticoes}")
    print(f"{'#'*80}\n")

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
    parser.add_argument('-tat', '--trata-altas', action='store_true',
                       help='Trata Motivos de Alta capturados')
    parser.add_argument('-clc', '--limpa-cache', action='store_true',
                       help='Limpa todos os arquivos da pasta ~/AutoReg, mantendo apenas solicita_inf_aih.csv')
    parser.add_argument('-dev', '--devolvidos', action='store_true',
                       help='Processa solicitações devolvidas')
    parser.add_argument('-p2c', '--pdf2csv', nargs='?', metavar='PDF', help='Converte PDF de solicitações em CSV')
    parser.add_argument('-ghn', '--ghosp-nota', action='store_true',
                       help='Extrair notas de prontuários Ghosp')
    parser.add_argument('-ghc', '--ghosp-cns', action='store_true',
                       help='Extrai CNSs dos prontuários e cria lista_same_cns.csv')
    parser.add_argument('-iga', '--internados-ghosp-avancado', action='store_true',
                       help='Extrai pacientes internados no GHOSP com informações adicionais')
    parser.add_argument('-ign', '--internados-ghosp-nota', action='store_true',
                       help='Extrai o conteúdo das notas dos prontuários do GHOSP')
    parser.add_argument('-especial', '--especial', action='store_true',
                       help='Extração de dados personalizados do GHOSP')
    parser.add_argument('-sia', '--solicita-inf-aih', action='store_true',
                       help='Extrai informações da AIH')
    parser.add_argument('-spa', '--solicita-pre-aih', action='store_true',
                       help='Extrai link para solicitação de aih do GHOSP')
    parser.add_argument('-ssr', '--solicita-sisreg', action='store_true',
                       help='Executa Solicitações no Sistema SISREG')
    parser.add_argument('-snt', '--solicita-nota', action='store_true',
                       help='Insere numero da solicitação SISREG na nota de prontuário')
    parser.add_argument('-std', '--solicita-trata-dados', action='store_true',
                       help='Ajusta CSV para tratamento das solicitações de AIH previamente ao SISREG')
    parser.add_argument('-css', '--consulta-solicitacao-sisreg', action='store_true',
                       help='Consulta o estado da Solicitação no sistema SISREG')
    # Novas funções de workflow
    parser.add_argument('-interna', '--interna', action='store_true',
                       help='Executa sequência de internação: -eci -ip')
    parser.add_argument('-analisa', '--analisa', action='store_true',
                       help='Executa sequência de análise: -eis -eig -ci -ma')
    parser.add_argument('-alta', '--alta', action='store_true',
                       help='Executa sequência de alta: -tat -ecsa -ea -ar -eid -td -clc')
    parser.add_argument('-solicita', '--solicita', action='store_true',
                       help='Executa rotina de Solicitação: -spa -sia -ssr -snt')
    parser.add_argument('-aihs', '--aihs', action='store_true',
                       help='Executa rotina de notas: -iga -ign -std')
    
    # Funções especiais
    parser.add_argument('-all', '--all', action='store_true',
                       help='Executa workflow completo: -interna -analisa -alta')
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
        'trata_altas': 'trata_altas',
        'limpa_cache': 'limpa_cache',
        'devolvidos': 'devolvidos',
        'pdf2csv': 'pdf2csv',
        'ghosp_nota': 'ghosp_nota',
        'ghosp_cns': 'ghosp_cns',
        'ghosp_especial': 'ghosp_especial',
        'internados_ghosp_avancado': 'internados_ghosp_avancado',
        'internados_ghosp_nota': 'internados_ghosp_nota',
        'solicita_inf_aih': 'solicita_inf_aih',
        'solicita_pre_aih': 'solicita_pre_aih',
        'solicita_sisreg': 'solicita_sisreg',
        'solicita_nota': 'solicita_nota',
        'solicita_trata_dados': 'solicita_trata_dados',
        'consulta_solicitacao_sisreg': 'consulta_solicitacao_sisreg'
    }
    
    # Processa funções especiais primeiro
    if args.all:
        executar_todas()
        return

    if args.interna:
        print("🔄 Executando sequência de internação (-eci -ip)...")
        for i, func_name in enumerate(['extrai_codigos_internacao', 'interna_pacientes'], 1):
            print(f"\n[{i}/2] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                break
        return

    if args.analisa:
        print("🔄 Executando sequência de análise (-eis -eig -ci -ma)...")
        seq = ['extrai_internados_sisreg', 'extrai_internados_ghosp', 'compara_internados', 'motivo_alta']
        for i, func_name in enumerate(seq, 1):
            print(f"\n[{i}/{len(seq)}] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                break
        return

    if args.alta:
        print("🔄 Executando sequência de alta (-tat -ecsa -ea -ar -eid -td -clc)...")
        seq = ['trata_altas', 'extrai_codigos_sisreg_alta', 'executa_alta', 'atualiza_restos', 'extrai_internacoes_duplicadas', 'trata_duplicados', 'limpa_cache']
        for i, func_name in enumerate(seq, 1):
            print(f"\n[{i}/{len(seq)}] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                break
        return

    if args.solicita:
        print("🔄 Executando rotina de Solicitação (-spa -sia -ssr -snt)...")
        seq = ['solicita_pre_aih', 'solicita_inf_aih', 'solicita_sisreg', 'solicita_nota']
        for i, func_name in enumerate(seq, 1):
            print(f"\n[{i}/{len(seq)}] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                break
            # Adiciona pausa de 1 segundo entre funções, exceto após a última
            if i < len(seq):
                time.sleep(1)
        return

    if args.aihs:
        print("🔄 Executando rotina de AIHS (-iga -ign -std)...")
        seq = ['internados_ghosp_avancado', 'internados_ghosp_nota', 'solicita_trata_dados']
        for i, func_name in enumerate(seq, 1):
            print(f"\n[{i}/{len(seq)}] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                break
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
        # pdf2csv recebe argumento de caminho
        if arg == 'pdf2csv' and getattr(args, 'pdf2csv'):
            funcoes_para_executar.append((func_name, getattr(args, 'pdf2csv')))
        else:
            # Corrige o nome do atributo para a função especial
            if arg == 'ghosp_especial':
                arg_name = 'especial'
            else:
                arg_name = arg.replace('-', '_')
            if hasattr(args, arg_name) and getattr(args, arg_name):
                funcoes_para_executar.append((func_name, None))

    if funcoes_para_executar:
        print(f"🔄 Executando {len(funcoes_para_executar)} função(ões) em sequência...")
        for i, (func_name, extra_arg) in enumerate(funcoes_para_executar, 1):
            print(f"\n[{i}/{len(funcoes_para_executar)}] ", end="")
            if func_name == 'pdf2csv' and extra_arg:
                try:
                    FUNCOES[func_name]['func'](extra_arg)
                    print(f"✅ Concluído: {FUNCOES[func_name]['desc']}")
                except Exception as e:
                    print(f"❌ Erro ao executar {func_name}: {e}")
                    break
            else:
                if not executar_funcao(func_name):
                    print(f"❌ Parando execução devido ao erro em {func_name}")
                    break
    else:
        print("❌ Nenhuma função válida foi especificada!")
        print("💡 Use --help para ver as opções disponíveis")

if __name__ == "__main__":
    main()
