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

As etapas acima acham o **paciente** (a 0 já dá o RA final). O RA é escolhido assim:

### Cadeia da internação (desde 10.2.0)
1. RA inicial: o que gerou a solicitação (`historico_solicitacoes.csv`); sem registro, a única internação da época (`ra_da_internacao`); senão, a memória do `-ign` (`vinculos_ghosp.csv`).
2. Segue para o próximo RA de internação que comece até **24 h** após a saída do anterior, ou se o anterior estiver aberto (troca de setor).
3. Vale o **último RA da cadeia**. Retorno/PS e segunda internação não entram.
4. Dúvida, ou lista de RAs ilegível: fica pendente, nunca usa o RA inicial sem checar a continuação.

Se o RA inicial não está na lista do paciente aberto (cadastro duplicado, solicitação 699718318), usa a lista do prontuário dono do RA.

No histórico, "RA: 1" é internação (119 de 119 com leito) e "RA: 2" é PS/ambulatório (161 de 161 sem); 99 não é usado. O corte de 24 h vem de 168 pares reais: 2 com 1,6 h e o seguinte só com 48,2 h (24/11/2026). Revise se aparecer troca de setor fora dele.

"Na época": entrada entre 15 dias antes e 3 depois da data de internação do SISREG; com mais de uma, a única a até 3 dias.
Até a 10.1.1 valia o RA HUERB mais recente, que podia ser um retorno.

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

### Conferir o RA à mão
Em `/historicopacs/{prontuario}`, procure o "RA: 1" da época da solicitação e leia
`/pr/altas?intern_id={RA}` ("Alta médica:" é a data; `for="resumoalta"` se repete no texto do resumo).
Se tem alta e o paciente não está internado em outro RA, informe esse RA em
`vinculos_manuais.csv`; o próximo `-alta` dá a saída.

## Armadilhas
- `Segue internado` = página lida, sem resumo. `Erro ao verificar` = a página **não** foi lida: não é normal e vira pendência. Se metade ou mais dos RAs der erro, o `-maa` falha, o `-eaa` não roda e o WhatsApp avisa (🚨).
- A seção de resumo mostra o botão "INSERIR" quando está vazia; não é alta (`texto_resumo_valido`).
- Motivo não reconhecido ou vazio sai com o coringa **ALTA MELHORADO** (decisão de 24/11/2026; marcado em `obs_motivo` e no log). Travas (`bloqueio_coringa`), que viram pendência: texto de óbito ou permanência, RA ou nome na lista de internados do G-HOSP, ou lista ausente/velha.
- Motivo vazio costumava ser RA de PS/retorno posterior à internação (antes da 10.2.0): a tela mostra "Tipo de saída" em vez de "Motivo de Cobrança". Esse texto (`tipo_saida`) **não** é o motivo da internação; só alimenta as travas.
- `-eaa` grava "Alta efetivada" após o clique, sem confirmar no SISREG.
- Prontuário (ex. 1234567) não é RA (ex. 600001): `/historicopacs/{prontuario}`, `/pr/interns/{RA}`.
- A ficha do SISREG não mostra CPF do paciente; os CPFs nela são de médicos.

Testes: `python test_vinculos.py`.
