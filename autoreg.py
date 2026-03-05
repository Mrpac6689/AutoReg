#!/usr/bin/env python3
"""
AutoReg - Coordenador de Workflow
Automatização de Sistemas de Saúde - SISREG & G-HOSP
Versão 9.8.1 - Universe - Fevereiro de 2026
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
from autoreg import ghosp_especial_parallel  # Importa a versão paralela
from autoreg import solicita_inf_aih  # Importa a função solicita_inf_aih
from autoreg import solicita_sisreg  # Importa a função solicita_sisreg
from autoreg import solicita_nota  # Importa a função solicita_nota
from autoreg import solicita_pre_aih  # Importa a função solicita_pre_aih
from autoreg import consulta_solicitacao_sisreg  # Importa a função consulta_solicitacao_sisreg
from autoreg import internados_ghosp_avancado  # Importa a função internados_ghosp_avancado
from autoreg import extrai_internados_ghosp_avancado  # Importa a função extrai_internados_ghosp_avancado
from autoreg import internados_ghosp_nota  # Importa a função internados_ghosp_nota
from autoreg import solicita_trata_dados  # Importa a função solicita_trata_dados
from autoreg import producao_ambulatorial  # Importa a função producao_ambulatorial
from autoreg import producao_ambulatorial_dados  # Importa a função producao_ambulatorial_dados
from autoreg import producao_ambulatorial_gmus  # Importa a função producao_ambulatorial_gmus
from autoreg import exames_ambulatorio_extrai  # Importa a função exames_ambulatorio_extrai
from autoreg import exames_ambulatorio_solicita  # Importa a função exames_ambulatorio_solicita
from autoreg import exames_ambulatorio_relatorio  # Importa a função exames_ambulatorio_relatorio
from autoreg import exames_ambulatoriais_consulta  # Importa a função exames_ambulatoriais_consulta
from autoreg import motivo_alta_avancado  # Importa a função motivo_alta_avancado
from autoreg import executa_alta_avancado  # Importa a função executa_alta_avancado
from autoreg import producao_relatorio  # Registro de produção via AUTOREG-API

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
    'extrai_internados_ghosp_avancado': {
        'func': extrai_internados_ghosp_avancado,
        'desc': 'Consulta permanencia de pacientes no GHOSP, que se encontram como internados no SISREG'
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
    'ghosp_especial_parallel': {
        'func': ghosp_especial_parallel,
        'desc': 'Extração paralela de dados personalizados do GHOSP (mais rápida)'
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
    },
    'producao_ambulatorial': {
        'func': producao_ambulatorial,
        'desc': 'Extrai dados de produção ambulatorial do SISREG'
    },
    'producao_ambulatorial_dados': {
        'func': producao_ambulatorial_dados,
        'desc': 'Extrai códigos de solicitação de produção ambulatorial do SISREG'
    },
    'producao_ambulatorial_gmus': {
        'func': producao_ambulatorial_gmus,
        'desc': 'Extrai dados de produção ambulatorial GMUs do SISREG'
    },
    'exames_ambulatorio_extrai': {
        'func': exames_ambulatorio_extrai,
        'desc': 'Extrai dados de exames a solicitar do G-Hosp'
    },
    'exames_ambulatorio_solicita': {
        'func': exames_ambulatorio_solicita,
        'desc': 'Executa solicitações de exames no SISREG'
    },
    'exames_ambulatorio_relatorio': {
        'func': exames_ambulatorio_relatorio,
        'desc': 'Extrai relatórios de exames solicitados no SISREG'
    },
    'exames_ambulatoriais_consulta': {
        'func': exames_ambulatoriais_consulta,
        'desc': 'Consulta prévia existência de solicitação no SISREG para o mesmo paciente e exame, lançada recentemente.'
    },
    'motivo_alta_avancado': {
        'func': motivo_alta_avancado,
        'desc': 'Verifica altas e extrai motivos'
    },
    'executa_alta_avancado': {
        'func': executa_alta_avancado,
        'desc': 'Execução de altas no SISREG - versão avançada'
    }
}

# Mapeamento de flags CLI (curtas e longas) → chave em FUNCOES
# Usado para executar funções NA ORDEM em que foram passadas na linha de comando
FLAG_TO_FUNC = {
    '-eci': 'extrai_codigos_internacao',        '--extrai-codigos-internacao': 'extrai_codigos_internacao',
    '-ip':  'interna_pacientes',                '--interna-pacientes': 'interna_pacientes',
    '-eis': 'extrai_internados_sisreg',         '--extrai-internados-sisreg': 'extrai_internados_sisreg',
    '-eig': 'extrai_internados_ghosp',          '--extrai-internados-ghosp': 'extrai_internados_ghosp',
    '-ci':  'compara_internados',               '--compara-internados': 'compara_internados',
    '-ma':  'motivo_alta',                      '--motivo-alta': 'motivo_alta',
    '-maa': 'motivo_alta_avancado',             '--motivo-alta-avancado': 'motivo_alta_avancado',
    '-ecsa':'extrai_codigos_sisreg_alta',       '--extrai-codigos-sisreg-alta': 'extrai_codigos_sisreg_alta',
    '-ea':  'executa_alta',                     '--executa-alta': 'executa_alta',
    '-eaa': 'executa_alta_avancado',            '--executa-alta-avancado': 'executa_alta_avancado',
    '-ar':  'atualiza_restos',                  '--atualiza-restos': 'atualiza_restos',
    '-eid': 'extrai_internacoes_duplicadas',    '--extrai-internacoes-duplicadas': 'extrai_internacoes_duplicadas',
    '-td':  'trata_duplicados',                 '--trata-duplicados': 'trata_duplicados',
    '-tat': 'trata_altas',                      '--trata-altas': 'trata_altas',
    '-clc': 'limpa_cache',                      '--limpa-cache': 'limpa_cache',
    '-dev': 'devolvidos',                       '--devolvidos': 'devolvidos',
    '-p2c': 'pdf2csv',                          '--pdf2csv': 'pdf2csv',
    '-ghn': 'ghosp_nota',                       '--ghosp-nota': 'ghosp_nota',
    '-ghc': 'ghosp_cns',                        '--ghosp-cns': 'ghosp_cns',
    '-iga': 'internados_ghosp_avancado',        '--internados-ghosp-avancado': 'internados_ghosp_avancado',
    '-eiga':'extrai_internados_ghosp_avancado', '--extrai-internados-ghosp-avancado': 'extrai_internados_ghosp_avancado',
    '-ign': 'internados_ghosp_nota',            '--internados-ghosp-nota': 'internados_ghosp_nota',
    '-especial':         'ghosp_especial',          '--especial': 'ghosp_especial',
    '-especial-parallel':'ghosp_especial_parallel', '--especial-parallel': 'ghosp_especial_parallel',
    '-sia': 'solicita_inf_aih',                 '--solicita-inf-aih': 'solicita_inf_aih',
    '-spa': 'solicita_pre_aih',                 '--solicita-pre-aih': 'solicita_pre_aih',
    '-ssr': 'solicita_sisreg',                  '--solicita-sisreg': 'solicita_sisreg',
    '-snt': 'solicita_nota',                    '--solicita-nota': 'solicita_nota',
    '-std': 'solicita_trata_dados',             '--solicita-trata-dados': 'solicita_trata_dados',
    '-css': 'consulta_solicitacao_sisreg',       '--consulta-solicitacao-sisreg': 'consulta_solicitacao_sisreg',
    '-pra': 'producao_ambulatorial',            '--producao-ambulatorial': 'producao_ambulatorial',
    '-pad': 'producao_ambulatorial_dados',      '--producao-ambulatorial-dados': 'producao_ambulatorial_dados',
    '-pag': 'producao_ambulatorial_gmus',       '--producao-ambulatorial-gmus': 'producao_ambulatorial_gmus',
    '-eae': 'exames_ambulatorio_extrai',        '--exames-ambulatorio-extrai': 'exames_ambulatorio_extrai',
    '-eas': 'exames_ambulatorio_solicita',      '--exames-ambulatorio-solicita': 'exames_ambulatorio_solicita',
    '-ear': 'exames_ambulatorio_relatorio',     '--exames-ambulatorio-relatorio': 'exames_ambulatorio_relatorio',
    '-eac': 'exames_ambulatoriais_consulta',    '--exames-ambulatoriais-consulta': 'exames_ambulatoriais_consulta',
}


def mostrar_informacoes():
    """Exibe informações do programa"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                    AutoReg                                    ║
║                    Automatização de Sistemas de Saúde                         ║
║                               SISREG & G-HOSP                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Versão: 9.7.0 - Universe                                                      ║
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
        ('-maa', '--motivo-alta-avancado', 'motivo_alta_avancado'),
        ('-ecsa', '--extrai-codigos-sisreg-alta', 'extrai_codigos_sisreg_alta'),
        ('-ea', '--executa-alta', 'executa_alta'),
        ('-eaa', '--executa-alta-avancado', 'executa_alta_avancado'),
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
        ('-eiga', '--extrai-internados-ghosp-avancado', 'extrai_internados_ghosp_avancado'),
        ('-ign', '--internados-ghosp-nota', 'internados_ghosp_nota'),
        ('-especial', '--especial', 'ghosp_especial'),
        ('-especial-parallel', '--especial-parallel', 'ghosp_especial_parallel'),
        ('-sia', '--solicita-inf-aih', 'solicita_inf_aih'),
        ('-spa', '--solicita-pre-aih', 'solicita_pre_aih'),
        ('-ssr', '--solicita-sisreg', 'solicita_sisreg'),
        ('-snt', '--solicita-nota', 'solicita_nota'),
        ('-std', '--solicita-trata-dados', 'solicita_trata_dados'),
        ('-css', '--consulta-solicitacao-sisreg', 'consulta_solicitacao_sisreg'),
        ('-pra', '--producao-ambulatorial', 'producao_ambulatorial'),
        ('-pad', '--producao-ambulatorial-dados', 'producao_ambulatorial_dados'),
        ('-pag', '--producao-ambulatorial-gmus', 'producao_ambulatorial_gmus'),
        ('-eae', '--exames-ambulatorio-extrai', 'exames_ambulatorio_extrai'),
        ('-eas', '--exames-ambulatorio-solicita', 'exames_ambulatorio_solicita'),
        ('-ear', '--exames-ambulatorio-relatorio', 'exames_ambulatorio_relatorio'),
        ('-eac', '--exames-ambulatoriais-consulta', 'exames_ambulatoriais_consulta'),
        ('-interna', '--interna', None),
        ('-alta', '--alta', None),
        ('-solicita', '--solicita', None),
        ('-aihs', '--aihs', None),
        ('-R', '--registro-producao', None)
    ]
    
    for short, long, func_name in flags:
        if func_name:
            desc = FUNCOES[func_name]['desc']
        elif short == '-interna':
            desc = 'Executa sequência de internação: -eci -ip'
        elif short == '-alta':
            desc = 'Executa sequência de alta: -eis -eiga -maa -eaa'
        elif short == '-solicita':
            desc = 'Executa rotina de Solicitação: -spa -sia -ssr -snt'
        elif short == '-aihs':
            desc = 'Executa rotina de notas: -iga -ign -std'
        elif short == '-R':
            desc = 'Registra produção na AUTOREG-API (use com -solicita, -interna ou -alta)'
        else:
            desc = ''
        print(f"    {short:<6} {long:<32} {desc}")
    
    print(f"""
FUNÇÕES ESPECIAIS:
    -all   --all                         Executa workflow completo: -interna -analisa -alta
    -cfg   --config                      Edita arquivo de configuração
    -dir   --directory                   Abre pasta de arquivos do AutoReg
    -R     --registro-producao           Registra produção na AUTOREG-API (use com -solicita, -interna ou -alta)

EXEMPLOS DE USO:
    python autoreg.py -eci               Extrai códigos de internação
    python autoreg.py -eci -ip           Executa duas funções em sequência
    python autoreg.py --all              Executa workflow completo
    python autoreg.py --config           Edita configuração
    python autoreg.py --help             Mostra esta ajuda
    python autoreg.py -solicita -R       Executa rotina de solicitação e registra produção na API
    python autoreg.py -interna -R       Executa rotina de internação e registra produção na API
    python autoreg.py -alta -R          Executa rotina de alta e registra produção na API

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
    print("\nEste workflow executará sequencialmente: INTERNA → ALTA")
    print("Total de 6 funções por ciclo completo\n")
    
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
        
        # Sequência 2: ALTA
        print("\n" + "="*80)
        print(f"CICLO {ciclo}/{repeticoes} - SEQUÊNCIA 2/2: ALTA (-eis -eiga -maa -eaa)")
        print("="*80)
        seq_alta = ['extrai_internados_sisreg', 'extrai_internados_ghosp_avancado', 'motivo_alta_avancado', 'executa_alta_avancado']
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
    total_funcoes = len(seq_interna) + len(seq_alta)
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
  %(prog)s -solicita -R         Executa rotina de solicitação e registra produção na API
  %(prog)s -interna -R         Executa rotina de internação e registra produção na API
  %(prog)s -alta -R            Executa rotina de alta e registra produção na API
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
    parser.add_argument('-maa', '--motivo-alta-avancado', action='store_true',
                       help='Verifica altas e extrai motivos')
    parser.add_argument('-ecsa', '--extrai-codigos-sisreg-alta', action='store_true',
                       help='Extrai códigos SISREG para alta')
    parser.add_argument('-ea', '--executa-alta', action='store_true',
                       help='Executa altas no SISREG')
    parser.add_argument('-eaa', '--executa-alta-avancado', action='store_true',
                       help='Execução de altas no SISREG - versão avançada')
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
    parser.add_argument('-eiga', '--extrai-internados-ghosp-avancado', action='store_true',
                       help='Consulta permanencia de pacientes no GHOSP, que se encontram como internados no SISREG')
    parser.add_argument('-ign', '--internados-ghosp-nota', action='store_true',
                       help='Extrai o conteúdo das notas dos prontuários do GHOSP')
    parser.add_argument('-especial', '--especial', action='store_true',
                       help='Extração de dados personalizados do GHOSP')
    parser.add_argument('-especial-parallel', '--especial-parallel', action='store_true',
                       help='Extração paralela de dados personalizados do GHOSP (mais rápida)')
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
    parser.add_argument('-pra', '--producao-ambulatorial', action='store_true',
                       help='Extrai dados de produção ambulatorial do SISREG')
    parser.add_argument('-pad', '--producao-ambulatorial-dados', action='store_true',
                       help='Extrai códigos de solicitação de produção ambulatorial do SISREG')
    parser.add_argument('-pag', '--producao-ambulatorial-gmus', action='store_true',
                       help='Extrai dados de produção ambulatorial GMUs do SISREG')
    parser.add_argument('-eae', '--exames-ambulatorio-extrai', action='store_true',
                       help='Extrai dados de exames a solicitar do G-Hosp')
    parser.add_argument('-eas', '--exames-ambulatorio-solicita', action='store_true',
                       help='Executa solicitações de exames no SISREG')
    parser.add_argument('-ear', '--exames-ambulatorio-relatorio', action='store_true',
                       help='Extrai relatórios de exames solicitados no SISREG')
    parser.add_argument('-eac', '--exames-ambulatoriais-consulta', action='store_true',
                       help='Consulta prévia existência de solicitação no SISREG para o mesmo paciente e exame, lançada recentemente.')
    # Novas funções de workflow
    parser.add_argument('-interna', '--interna', action='store_true',
                       help='Executa sequência de internação: -eci -ip')
    parser.add_argument('-alta', '--alta', action='store_true',
                       help='Executa sequência de alta: -tat -ecsa -ea -ar -eid -td -clc')
    parser.add_argument('-solicita', '--solicita', action='store_true',
                       help='Executa rotina de Solicitação: -spa -sia -ssr -snt')
    parser.add_argument('-aihs', '--aihs', action='store_true',
                       help='Executa rotina de notas: -iga -ign -std')
    parser.add_argument('-R', '--registro-producao', action='store_true',
                       help='Registra produção na AUTOREG-API (válido com -solicita, -interna ou -alta)')
    
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
    
    # Processa funções especiais (workflows compostos) primeiro
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
        if args.registro_producao:
            producao_relatorio.registrar_producao('Internar Pacientes', 'codigos_internacao.csv')
        return

    if args.alta:
        if args.registro_producao:
            producao_relatorio.registrar_producao_altas('Altas', 'internados_sisreg.csv')
        print("🔄 Executando sequência de alta (-eis -eiga -maa -eaa)...")
        seq = ['extrai_internados_sisreg', 'extrai_internados_ghosp_avancado', 'motivo_alta_avancado', 'executa_alta_avancado']
        for i, func_name in enumerate(seq, 1):
            print(f"\n[{i}/{len(seq)}] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                break
        return

    if args.solicita:
        if args.registro_producao:
            producao_relatorio.registrar_producao('Solicitar Internações', 'internados_ghosp_avancado.csv')
        print("🔄 Executando rotina de Solicitação (-spa -sia -ssr -snt)...")
        seq = ['solicita_pre_aih', 'solicita_inf_aih', 'solicita_sisreg', 'solicita_nota']
        for i, func_name in enumerate(seq, 1):
            print(f"\n[{i}/{len(seq)}] ", end="")
            if not executar_funcao(func_name):
                print(f"❌ Parando execução devido ao erro em {func_name}")
                break
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

    # -----------------------------------------------------------------------
    # Executa funções individuais na ORDEM EXATA em que foram passadas
    # na linha de comando (percorre sys.argv, não um dict de ordem fixa)
    # Exemplo: "autoreg.py -eid -td" executa eid ANTES de td
    # -----------------------------------------------------------------------
    funcoes_para_executar = []
    argv_tokens = sys.argv[1:]
    skip_next = False
    for idx, token in enumerate(argv_tokens):
        if skip_next:
            skip_next = False
            continue
        if token in FLAG_TO_FUNC:
            func_name = FLAG_TO_FUNC[token]
            if func_name == 'pdf2csv':
                # -p2c pode receber um caminho opcional como próximo token
                next_token = argv_tokens[idx + 1] if idx + 1 < len(argv_tokens) else None
                if next_token and not next_token.startswith('-'):
                    funcoes_para_executar.append((func_name, next_token))
                    skip_next = True
                else:
                    funcoes_para_executar.append((func_name, None))
            else:
                funcoes_para_executar.append((func_name, None))

    if funcoes_para_executar:
        total = len(funcoes_para_executar)
        print(f"🔄 Executando {total} função(ões) em sequência...")
        for i, (func_name, extra_arg) in enumerate(funcoes_para_executar, 1):
            print(f"\n[{i}/{total}] ", end="")
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
