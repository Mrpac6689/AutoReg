# Rotina de alta

Para humanos e IAs. Sequência: `-eis` → `-eiga` → `-maa` → `-eaa` → `-rap` (atalho `-alta`).

## Regra
**Nenhuma internação aberta no SISREG pode ser esquecida.** Cada uma tem um RA
do G-HOSP ou está em `altas_pendentes.csv`. **Nunca** dar alta só porque o
paciente não foi achado no G-HOSP: não achar não prova que saiu.

## Etapas
| Flag | Módulo | Faz |
|---|---|---|
| `-eis` | `extrai_internados_sisreg.py` | Lista internados no SISREG: CNS, data de internação, nascimento, mãe, prontuário (da ficha) |
| `-eiga` | `extrai_internados_ghosp_avancado.py` | Descobre o RA (ordem abaixo) |
| `-maa` | `motivo_alta_avancado.py` | Lê o resumo de alta do RA |
| `-eaa` | `executa_alta_avancado.py` | Efetua a saída. **Ação real e irreversível pelo AutoReg** |
| `-rap` | `vinculos.py` | Atualiza a fila; roda mesmo se uma etapa anterior falhar |

## Como o `-eiga` acha o RA (para na primeira que servir)
0. `vinculos_manuais.csv` (uma pessoa informou).
1. CNS do SISREG.
2. CPF/CNS do `historico_solicitacoes.csv`, só se o RA solicitado estiver na lista do paciente.
3. Prontuário escrito na ficha do SISREG, com nome conferido e RA HUERB na época.
4. Nome (só sem histórico). Homônimos: desempate por nascimento + RA HUERB na época.
5. RA do histórico de solicitações.
6. `vinculos_ghosp.csv` (memória do `-ign`): lembrete com o nº da solicitação, ou nome completo + data. Só com um candidato.

"Na época": entrada entre 15 dias antes e 3 depois da data de internação do SISREG.
Quando a busca abre o paciente, vale o **RA HUERB mais recente**, mesmo que
difira do solicitado (pode ser segunda internação). Decisão de 24/11/2026; a diferença só vai para o log.
**Limitação conhecida:** o mais recente também pode ser um retorno posterior à internação (11 casos em 24/11/2026).

## Arquivos (`~/AutoReg`; vínculos e fila são preservados por `-clc`)
| Arquivo | Quem escreve | Conteúdo |
|---|---|---|
| `vinculos_manuais.csv` | Pessoa | `solicitacao,ra,observacao` |
| `vinculos_ghosp.csv` | `-ign` | RAs vistos internados, entrada e nºs citados nos lembretes |
| `internados_sisreg.csv` | `-eis` a `-eaa` | Estado do ciclo; `tipo_saida` (`-maa`) e `obs_motivo` (`-eaa`, uso do coringa). Refeito a cada ciclo |
| `altas_pendentes.csv` | `-rap` | Fila; `desde` é a idade, `resolvida_em` vazio = aberta |

## Tratar uma pendência
1. Veja `motivo` e `candidatos` em `altas_pendentes.csv` (ou no WhatsApp: 🟡 24 h, 🔴 72 h).
2. Confira no G-HOSP. Achou o RA: acrescente a linha em `vinculos_manuais.csv`.
3. Já saiu e não há RA: dê a saída no SISREG; a linha se resolve sozinha.
4. Anote a causa: se for recorrente, vira correção no código. Análise com dados de paciente fica em `~/AutoReg/diagnostico/`, nunca no repositório.

### `Segue internado` fora da lista de internados
Em geral o RA mais recente é um atendimento de PS/retorno sem alta e a internação
já terminou em um RA anterior (solicitações 698666653 e 699402472, 24/11/2026).
Em `/historicopacs/{prontuario}`, procure o RA com leito na época da solicitação
(nesses casos, "RA: 1"; os de PS, "RA: 2") e leia `/pr/altas?intern_id={RA}`.
Se tem alta e o paciente não está internado em outro RA, informe esse RA em
`vinculos_manuais.csv`; o próximo `-alta` dá a saída.

## Armadilhas
- `Segue internado` = página lida, sem resumo. `Erro ao verificar` = a página **não** foi lida: não é normal e vira pendência. Se metade ou mais dos RAs der erro, o `-maa` falha, o `-eaa` não roda e o WhatsApp avisa (🚨).
- A seção de resumo mostra o botão "INSERIR" quando está vazia; não é alta (`texto_resumo_valido`).
- Motivo não reconhecido ou vazio sai com o coringa **ALTA MELHORADO** (decisão de 24/11/2026; marcado em `obs_motivo` e no log). Travas (`bloqueio_coringa`), que viram pendência: texto de óbito ou permanência, RA ou nome na lista de internados do G-HOSP, ou lista ausente/velha.
- Motivo vazio costuma ser RA de PS/retorno posterior à internação: a tela mostra "Tipo de saída" em vez de "Motivo de Cobrança". Esse texto (`tipo_saida`) **não** é o motivo da internação; só alimenta as travas.
- `-eaa` grava "Alta efetivada" após o clique, sem confirmar no SISREG.
- Prontuário (ex. 1234567) não é RA (ex. 600001): `/historicopacs/{prontuario}`, `/pr/interns/{RA}`.
- A ficha do SISREG não mostra CPF do paciente; os CPFs nela são de médicos.

Testes: `python test_vinculos.py`.
