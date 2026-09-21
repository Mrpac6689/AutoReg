"""Catálogo estático de comandos do AutoReg usado pela TUI.

Este módulo não importa `autoreg.py` nem o pacote `autoreg/` — é uma cópia
deliberada, com metadados extras (categoria, CSVs afetados, se é interativo,
se aceita um PDF opcional), das flags já definidas em `FLAG_TO_FUNC`/
`FUNCOES` dentro de `autoreg.py`. Mantenha em sincronia manualmente quando
uma flag for adicionada/removida por lá.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Comando:
    flag: str  # flag curta, exatamente como o argparse de autoreg.py espera
    desc: str
    csvs: tuple[str, ...] = ()
    interativo: bool = False
    aceita_pdf: bool = False
    obsoleto: bool = False


@dataclass(frozen=True)
class Categoria:
    nome: str
    comandos: tuple[Comando, ...]


@dataclass(frozen=True)
class Workflow:
    flag: str
    titulo: str
    descricao: str
    passos: str  # descrição curta da sequência, só para exibição
    interativo: bool = False


# ---------------------------------------------------------------------------
# Os 5 botões principais da tela inicial
# ---------------------------------------------------------------------------

PRINCIPAIS: tuple[Workflow, ...] = (
    Workflow(
        flag="-interna",
        titulo="Interna",
        descricao="Ciclo completo de internação de pacientes no SISREG",
        passos="-eci → -ip",
    ),
    Workflow(
        flag="-alta",
        titulo="Alta",
        descricao="Ciclo completo de alta de pacientes internados",
        passos="-eis → -eiga → -maa → -eaa",
    ),
    Workflow(
        flag="-td",
        titulo="Trata Duplicados",
        descricao="Identifica e trata internações duplicadas (inclui extração)",
        passos="extração + tratamento de duplicados",
    ),
    Workflow(
        flag="-aihs",
        titulo="Busca AIHs não solicitadas",
        descricao="Pré-processa GHOSP → SISREG para descobrir pacientes que ainda precisam de solicitação de AIH",
        passos="-iga → -ign → -std",
    ),
    Workflow(
        flag="-solicita",
        titulo="Solicita AIHs",
        descricao="Solicitação de AIH com revisão humana (pausável/pulável)",
        passos="-spaa → -spa → -sia → -ssr → -snt",
        interativo=True,
    ),
)

# "Ciclo Completo" (equivalente a --all) não é uma flag repassada direto ao
# autoreg.py — a TUI pergunta o N de repetições e dispara -interna/-alta
# como jobs separados, evitando o input() bloqueante de executar_todas().
CICLO_COMPLETO_FLAG = "-all"


# ---------------------------------------------------------------------------
# Demais comandos, agrupados por categoria (tela "Comandos")
# ---------------------------------------------------------------------------

CATEGORIAS: tuple[Categoria, ...] = (
    Categoria(
        "Internação",
        (
            Comando("-eci", "Extrai códigos de internação do SISREG", csvs=("codigos_internacao.csv",)),
            Comando("-ip", "Realiza internação de pacientes no SISREG", csvs=("codigos_internacao.csv",)),
            Comando("-ci", "Compara listas de internados entre sistemas"),
        ),
    ),
    Categoria(
        "Alta",
        (
            Comando("-eis", "Extrai lista de internados do SISREG", csvs=("internados_sisreg.csv",)),
            Comando("-eig", "Extrai lista de internados do G-HOSP", csvs=("internados_ghosp.csv",)),
            Comando("-eiga", "Consulta permanência de pacientes no GHOSP que estão internados no SISREG", csvs=("internados_sisreg.csv",)),
            Comando("-ma", "Captura motivos de alta no G-HOSP"),
            Comando("-maa", "Verifica altas e extrai motivos", csvs=("internados_sisreg.csv",)),
            Comando("-ecsa", "Extrai códigos SISREG para alta"),
            Comando("-eaa", "Execução de altas no SISREG - versão avançada", csvs=("internados_sisreg.csv",)),
            Comando("-ea", "Executa altas no SISREG (substituído por -eaa)", obsoleto=True),
            Comando("-ar", "Atualiza arquivo de pacientes restantes", csvs=("restos.csv", "restos-atualizado.csv"), obsoleto=True),
            Comando("-tat", "Trata Motivos de Alta capturados (substituído por -maa)", obsoleto=True),
        ),
    ),
    Categoria(
        "Duplicados",
        (
            Comando("-td", "Identifica e processa pacientes com duplicações (inclui extração, antes feita por -eid)", csvs=("internacoes_duplicadas.csv",)),
            Comando("-eid", "Identifica internações duplicadas (agora roda automaticamente dentro de -td)", csvs=("internacoes_duplicadas.csv",), obsoleto=True),
        ),
    ),
    Categoria(
        "Pré-processamento AIH (GHOSP)",
        (
            Comando("-iga", "Extrai pacientes internados no GHOSP com informações adicionais", csvs=("internados_ghosp_avancado.csv",)),
            Comando("-ign", "Extrai o conteúdo das notas dos prontuários do GHOSP"),
            Comando("-std", "Ajusta CSV para tratamento das solicitações de AIH previamente ao SISREG", csvs=("solicita_inf_aih.csv",)),
        ),
    ),
    Categoria(
        "Solicitação de AIH",
        (
            Comando("-sia", "Extrai informações da AIH", csvs=("solicita_inf_aih.csv",)),
            Comando("-spaa", "Pré-processa AIHs automaticamente (sem interação do usuário)", csvs=("solicita_inf_aih.csv",)),
            Comando("-spb", "Substitui a etapa manual -spa no fluxo automático (-solicita-auto)", csvs=("solicita_inf_aih.csv",)),
            Comando("-spa", "Extrai link para solicitação de AIH do GHOSP (revisão humana)", csvs=("solicita_inf_aih.csv",), interativo=True),
            Comando("-ssr", "Executa Solicitações no Sistema SISREG", csvs=("solicita_inf_aih.csv",)),
            Comando("-snt", "Insere número da solicitação SISREG na nota de prontuário", csvs=("solicita_inf_aih.csv",)),
            Comando("-sresg", "Resgata solicitações com erro \"Procedimento nao habilitado!\" (troca código residual, retoma -ssr/-snt)", csvs=("solicita_inf_aih.csv",)),
            Comando("-css", "Consulta o estado da Solicitação no SISREG", csvs=("consulta_solicitacao_sisreg.csv",)),
            Comando("-p2c", "Converte PDF de solicitações em CSV", aceita_pdf=True, obsoleto=True),
        ),
    ),
    Categoria(
        "Produção Ambulatorial",
        (
            Comando("-pra", "Extrai dados de produção ambulatorial do SISREG", csvs=("producao_ambulatorial.csv",)),
            Comando("-pad", "Extrai códigos de solicitação de produção ambulatorial do SISREG", csvs=("producao_ambulatorial_dados.csv",)),
            Comando("-pag", "Extrai dados de produção ambulatorial GMUs do SISREG", csvs=("producao_ambulatorial_gmus.csv",)),
        ),
    ),
    Categoria(
        "Exames Ambulatoriais",
        (
            Comando("-eac", "Consulta prévia de solicitação já lançada para o mesmo paciente/exame"),
            Comando("-eae", "Extrai dados de exames a solicitar do G-Hosp", csvs=("exames_solicitar.csv",)),
            Comando("-eas", "Executa solicitações de exames no SISREG", csvs=("exames_solicitar.csv",)),
            Comando("-ear", "Extrai relatórios de exames solicitados no SISREG"),
        ),
    ),
    Categoria(
        "Pipelines Especiais (one-off)",
        (
            Comando("-especial-prepara", "Extrai NOME/SETOR/DATA de um PDF de avaliações profissionais (gera saida_especial.csv)", csvs=("saida_especial.csv",), aceita_pdf=True),
            Comando("-especial-extrai", "Localiza no GHOSP o profissional e data/hora de cada avaliação", csvs=("saida_especial.csv",)),
            Comando("-especial-med-prepara", "Extrai RA/Internamento/Alta do PDF \"Altas por período\" (rc008) do G-HOSP", csvs=("especial-med-resultado.csv",), aceita_pdf=True),
            Comando("-especial-med-extrai", "Localiza no GHOSP o médico que deu alta (via RA) para cada linha", csvs=("especial-med-resultado.csv",)),
            Comando("-especial", "Extração de dados personalizados do GHOSP", obsoleto=True),
            Comando("-especial-parallel", "Extração paralela de dados personalizados do GHOSP (mais rápida)", obsoleto=True),
        ),
    ),
    Categoria(
        "Utilitários",
        (
            Comando("-clc", "Limpa todos os arquivos de ~/AutoReg, mantendo apenas solicita_inf_aih.csv"),
            Comando("-dev", "Processa solicitações devolvidas"),
            Comando("-ghn", "Extrai notas de prontuários GHOSP"),
            Comando("-ghc", "Extrai CNSs dos prontuários e cria lista_same_cns.csv", csvs=("lista_same_cns.csv",)),
            Comando("-dir", "Abre a pasta ~/AutoReg para consulta de arquivos"),
        ),
    ),
)

# Flags que disparam confirmação antes de rodar (ações destrutivas/pouco óbvias)
CONFIRMAR_ANTES = {"-clc"}

# Flags cujo processo deve ser tratado com cuidado extra ao ser interrompido
# à força (o módulo correspondente não tem try/finally cobrindo o loop
# principal, então matar o processo pode deixar Chrome órfão).
RISCO_CHROME_ORFAO = {"-solicita", "-spa"}


def todos_comandos() -> tuple[Comando, ...]:
    return tuple(c for cat in CATEGORIAS for c in cat.comandos)


def buscar_comando(flag: str) -> Comando | None:
    for c in todos_comandos():
        if c.flag == flag:
            return c
    return None


# Sub-flags reais de cada workflow encadeado (espelha main() em autoreg.py),
# usado só para descobrir quais CSVs mostrar no painel de "arquivos
# afetados" do Monitor — -td e -sresg já são Comando e resolvem sozinhos.
WORKFLOW_SUBFLAGS: dict[str, tuple[str, ...]] = {
    "-interna": ("-eci", "-ip"),
    "-alta": ("-eis", "-eiga", "-maa", "-eaa"),
    "-aihs": ("-iga", "-ign", "-std"),
    "-solicita": ("-spaa", "-spa", "-sia", "-ssr", "-snt"),
    "-solicita-auto": ("-spaa", "-spb", "-sia", "-ssr", "-snt"),
}


def arquivos_para_flags(flags: list[str]) -> tuple[str, ...]:
    """Resolve, best-effort, quais CSVs de ~/AutoReg um argv (uma flag de
    workflow ou uma lista de flags individuais) provavelmente afeta."""
    vistos: list[str] = []
    for flag in flags:
        subflags = WORKFLOW_SUBFLAGS.get(flag, (flag,))
        for sub in subflags:
            cmd = buscar_comando(sub)
            if cmd is None:
                continue
            for csv in cmd.csvs:
                if csv not in vistos:
                    vistos.append(csv)
    return tuple(vistos)
