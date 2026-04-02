# Integração 2Captcha - Resolução Automática de CAPTCHA

## Visão Geral

O AutoReg agora suporta resolução automática de CAPTCHA usando o serviço [2Captcha](https://2captcha.com). Quando habilitado, o sistema tenta resolver CAPTCHAs automaticamente sem intervenção manual.

## Como Funciona

1. **Detecção Automática**: O sistema detecta quando um CAPTCHA aparece no SISREG III
2. **Tentativa de Resolução Automática**: Se o 2Captcha estiver habilitado, tenta resolver automaticamente
3. **Fallback Manual**: Se a resolução automática falhar, volta para o modo manual tradicional

## Configuração

### 1. Instalar Dependências

```bash
# Atualizar ambiente conda
conda env update -f environment.yml

# OU instalar manualmente com pip
pip install 2captcha-python
```

### 2. Obter API Key do 2Captcha

1. Crie uma conta em [https://2captcha.com](https://2captcha.com)
2. Adicione créditos à sua conta (cobrado por CAPTCHA resolvido)
3. Copie sua API key do painel de controle

### 3. Configurar config.ini

Edite seu arquivo `config.ini` e adicione/configure a seção `[2CAPTCHA]`:

```ini
[2CAPTCHA]

# Habilitar resolucao automatica de CAPTCHA usando servico 2Captcha
# Valores: true ou false
enabled = true

# Chave de API do 2Captcha (obtenha em https://2captcha.com)
api_key = SUA_CHAVE_API_AQUI
```

**Exemplo com resolução automática DESABILITADA:**
```ini
[2CAPTCHA]
enabled = false
api_key =
```

## Tipos de CAPTCHA Suportados

O módulo tenta resolver automaticamente os seguintes tipos:

- ✅ **reCAPTCHA v2** - O CAPTCHA mais comum do Google
- ✅ **reCAPTCHA v3** - Versão invisível do Google
- ✅ **hCaptcha** - Alternativa ao reCAPTCHA
- ✅ **Imagem simples** - CAPTCHA de texto em imagem

## Custo

O 2Captcha cobra por CAPTCHA resolvido:

- **reCAPTCHA v2**: ~$2.99 por 1000 resoluções
- **reCAPTCHA v3**: ~$2.99 por 1000 resoluções
- **hCaptcha**: ~$2.99 por 1000 resoluções
- **Imagem normal**: ~$0.50 por 1000 resoluções

Verifique preços atualizados em: https://2captcha.com/pricing

## Uso

Não é necessário modificar seu workflow. O sistema funciona automaticamente:

```bash
# Executar normalmente
python autoreg.py -interna

# O sistema:
# 1. Detecta CAPTCHA
# 2. Se 2Captcha estiver habilitado → resolve automaticamente
# 3. Se falhar ou desabilitado → modo manual
```

## Mensagens no Console

### Com 2Captcha Habilitado e Funcionando

```
================================================================================
CAPTCHA DETECTADO!
================================================================================

URL da pagina com CAPTCHA: https://sisregiii.saude.gov.br/...

[RESOLUCAO AUTOMATICA] 2Captcha habilitado
[2Captcha] Iniciando resolucao automatica...
[2Captcha] Saldo da conta: $5.23
[2Captcha] Tipo de CAPTCHA: recaptcha_v2
[2Captcha] Enviando reCAPTCHA v2 para resolucao...
[2Captcha] Token recebido, aplicando na pagina...

[SUCESSO] CAPTCHA resolvido automaticamente em 23s!
Retomando processamento...
```

### Com 2Captcha Desabilitado

```
================================================================================
CAPTCHA DETECTADO!
================================================================================

URL da pagina com CAPTCHA: https://sisregiii.saude.gov.br/...

[MODO MANUAL] Resolucao automatica desabilitada no config.ini

Ambiente local detectado
O navegador deve estar visivel na sua tela
Resolva o CAPTCHA manualmente no navegador

Aguardando resolucao do CAPTCHA...
   Tempo maximo: 300 segundos (5 minutos)
```

### Falha na Resolução Automática

```
[FALHA] Nao foi possivel resolver automaticamente: Timeout
Alternando para modo manual...

Aguardando resolucao do CAPTCHA...
```

## Verificação de Saldo

O sistema verifica automaticamente o saldo antes de tentar resolver. Se o saldo for insuficiente:

```
[FALHA] Nao foi possivel resolver automaticamente: Saldo insuficiente na conta 2Captcha: $0.00
Alternando para modo manual...
```

## Logs

Todas as tentativas de resolução são registradas em `~/AutoReg/autoreg.log`:

```
2026-03-25 10:15:23 - WARNING - CAPTCHA DETECTADO no SISREG!
2026-03-25 10:15:23 - INFO - Tentando resolucao automatica com 2Captcha...
2026-03-25 10:15:23 - INFO - Saldo da conta 2Captcha: $5.23
2026-03-25 10:15:23 - INFO - Tipo de CAPTCHA identificado: recaptcha_v2
2026-03-25 10:15:46 - INFO - CAPTCHA resolvido automaticamente em 23s
```

## Troubleshooting

### Biblioteca não instalada

**Problema:**
```
[AVISO] 2Captcha habilitado mas biblioteca nao instalada
        Execute: pip install 2captcha-python
```

**Solução:**
```bash
pip install 2captcha-python
# OU
conda env update -f environment.yml
```

### API Key não configurada

**Problema:**
```
[FALHA] Nao foi possivel resolver automaticamente: API key do 2Captcha nao configurada
```

**Solução:**
Edite `config.ini` e adicione sua API key na seção `[2CAPTCHA]`

### Tipo de CAPTCHA não suportado

**Problema:**
```
[FALHA] Nao foi possivel resolver automaticamente: Tipo de CAPTCHA nao suportado: desconhecido
```

**Solução:**
Alguns tipos de CAPTCHA não são suportados. O sistema alterna automaticamente para modo manual.

### Timeout

**Problema:**
```
[FALHA] Nao foi possivel resolver automaticamente: Timeout: CAPTCHA nao foi resolvido a tempo
```

**Solução:**
- Verifique sua conexão com a internet
- O 2Captcha pode estar com alta demanda (tente novamente)
- O sistema alternará para modo manual

## Segurança

- ✅ A API key é armazenada localmente em `config.ini` (gitignored)
- ✅ Comunicação criptografada com servidores 2Captcha
- ✅ Nunca compartilhe sua API key
- ✅ Monitore uso e custos no painel 2Captcha

## Desabilitar Temporariamente

Para desabilitar sem remover a API key:

```ini
[2CAPTCHA]
enabled = false
api_key = SUA_CHAVE_PERMANECE_AQUI
```

## Código Fonte

- **Detecção**: [`autoreg/detecta_capchta.py`](autoreg/detecta_capchta.py)
- **Resolução**: [`autoreg/resolvedor_captcha.py`](autoreg/resolvedor_captcha.py)
- **Configuração**: [`config.ini.example`](config.ini.example)

## Suporte

- 2Captcha: https://2captcha.com/support
- AutoReg: https://github.com/seu-usuario/AutoReg/issues
