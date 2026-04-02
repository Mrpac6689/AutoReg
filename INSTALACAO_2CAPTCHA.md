# Guia de Instalação - Integração 2Captcha

## Passo a Passo Completo

### 1. Atualizar Ambiente Conda

```bash
cd /home/michel/code/AutoReg

# Atualizar ambiente com nova dependência
conda activate autoreg_env
conda env update -f environment.yml --prune
```

### 2. Verificar Instalação

```bash
# Testar importação
python -c "from twocaptcha import TwoCaptcha; print('2Captcha instalado com sucesso!')"

# Executar suite de testes
python test_2captcha_integration.py
```

### 3. Configurar API Key

1. Criar conta em https://2captcha.com
2. Adicionar créditos (mínimo ~$3)
3. Copiar API Key do painel

4. Editar `config.ini`:

```bash
nano config.ini
```

Adicionar ao final:

```ini
[2CAPTCHA]
enabled = true
api_key = SUA_CHAVE_API_AQUI
```

### 4. Testar Configuração

```bash
python test_2captcha_integration.py
```

Você deve ver:

```
✅ PASSOU - Importação biblioteca
✅ PASSOU - Configuração config.ini
✅ PASSOU - Conexão API 2Captcha
✅ PASSOU - Módulo resolvedor_captcha

🎉 SUCESSO! Integração com 2Captcha está funcionando!
```

### 5. Usar Normalmente

```bash
# O sistema agora resolverá CAPTCHAs automaticamente
python autoreg.py -interna
python autoreg.py -alta
python autoreg.py --all
```

## Troubleshooting

### Biblioteca não encontrada

```bash
# Reinstalar dependência
pip install 2captcha-python==2.0.5
```

### API Key inválida

- Verifique se copiou corretamente do painel 2Captcha
- Sem espaços antes/depois da chave
- Chave tem formato: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (32 caracteres)

### Saldo insuficiente

- Adicione créditos em https://2captcha.com
- Mínimo recomendado: $3-5 USD

## Desabilitar

Para desabilitar sem remover configuração:

```ini
[2CAPTCHA]
enabled = false
api_key = sua_chave_fica_aqui
```

## Arquivos Modificados/Criados

✅ **Novos arquivos:**
- `autoreg/resolvedor_captcha.py` - Módulo de resolução automática
- `CAPTCHA_2CAPTCHA.md` - Documentação completa
- `INSTALACAO_2CAPTCHA.md` - Este guia
- `test_2captcha_integration.py` - Script de teste

✅ **Arquivos modificados:**
- `autoreg/detecta_capchta.py` - Integração com resolvedor
- `config.ini.example` - Template com seção [2CAPTCHA]
- `environment.yml` - Dependência adicionada

✅ **Nenhuma alteração necessária em:**
- `autoreg.py` - Funciona transparentemente
- Demais módulos - Sem alterações
