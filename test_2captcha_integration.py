#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para validar a integração com 2Captcha.
NÃO EXECUTA RESOLUÇÃO REAL - apenas testa a configuração.
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def testar_importacao():
    """Testa se o módulo 2captcha está instalado"""
    print("=" * 80)
    print("TESTE 1: Importação da biblioteca 2captcha-python")
    print("=" * 80)

    try:
        from twocaptcha import TwoCaptcha
        print("✅ Biblioteca 2captcha-python instalada com sucesso!")
        return True
    except ImportError as e:
        print("❌ Biblioteca 2captcha-python NÃO instalada")
        print(f"   Erro: {e}")
        print("\n   Execute: pip install 2captcha-python")
        return False


def testar_configuracao():
    """Testa se a configuração do config.ini está correta"""
    print("\n" + "=" * 80)
    print("TESTE 2: Leitura da configuração do config.ini")
    print("=" * 80)

    try:
        from autoreg.detecta_capchta import _ler_config_2captcha

        config = _ler_config_2captcha()

        print(f"Enabled: {config['enabled']}")
        print(f"API Key configurada: {'Sim' if config['api_key'] else 'Não'}")

        if config['api_key']:
            # Mostra apenas os primeiros e últimos caracteres
            key = config['api_key']
            masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
            print(f"API Key (mascarada): {masked_key}")

        if config['enabled'] and not config['api_key']:
            print("\n⚠️  ATENÇÃO: 2Captcha está habilitado mas API key não está configurada!")
            return False

        if config['enabled'] and config['api_key']:
            print("\n✅ Configuração válida!")
        else:
            print("\n✅ Configuração lida (2Captcha desabilitado)")

        return True

    except Exception as e:
        print(f"❌ Erro ao ler configuração: {e}")
        return False


def testar_conexao_api():
    """Testa conexão com a API do 2Captcha (verifica saldo)"""
    print("\n" + "=" * 80)
    print("TESTE 3: Conexão com API do 2Captcha")
    print("=" * 80)

    try:
        from autoreg.detecta_capchta import _ler_config_2captcha
        from twocaptcha import TwoCaptcha

        config = _ler_config_2captcha()

        if not config['enabled']:
            print("⏭️  Pulado - 2Captcha desabilitado no config.ini")
            return True

        if not config['api_key']:
            print("❌ API key não configurada")
            return False

        print("Conectando à API 2Captcha...")
        solver = TwoCaptcha(config['api_key'])

        print("Verificando saldo da conta...")
        saldo = solver.balance()

        print(f"\n✅ Conexão bem-sucedida!")
        print(f"   Saldo da conta: ${saldo}")

        if float(saldo) < 0.01:
            print("\n⚠️  ATENÇÃO: Saldo muito baixo! Adicione créditos em https://2captcha.com")

        return True

    except ImportError:
        print("⏭️  Pulado - biblioteca 2captcha-python não instalada")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        print("\n   Verifique:")
        print("   1. Sua API key está correta?")
        print("   2. Você tem conexão com a internet?")
        print("   3. A API do 2Captcha está funcionando?")
        return False


def testar_modulo_resolvedor():
    """Testa se o módulo resolvedor_captcha pode ser importado"""
    print("\n" + "=" * 80)
    print("TESTE 4: Importação do módulo resolvedor_captcha")
    print("=" * 80)

    try:
        from autoreg import resolvedor_captcha
        print("✅ Módulo resolvedor_captcha importado com sucesso!")

        # Verifica se as funções principais existem
        funcoes = [
            'resolver_captcha_automatico',
            '_identificar_tipo_captcha',
            '_resolver_recaptcha_v2',
            '_resolver_recaptcha_v3',
            '_resolver_hcaptcha',
            '_resolver_captcha_imagem'
        ]

        print("\nFunções disponíveis:")
        for func in funcoes:
            if hasattr(resolvedor_captcha, func):
                print(f"  ✅ {func}")
            else:
                print(f"  ❌ {func} - NÃO ENCONTRADA")

        return True

    except Exception as e:
        print(f"❌ Erro ao importar módulo: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TESTE DE INTEGRAÇÃO 2CAPTCHA" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    resultados = []

    # Teste 1: Importação
    resultados.append(("Importação biblioteca", testar_importacao()))

    # Teste 2: Configuração
    resultados.append(("Configuração config.ini", testar_configuracao()))

    # Teste 3: Conexão API (apenas se biblioteca instalada)
    if resultados[0][1]:
        resultados.append(("Conexão API 2Captcha", testar_conexao_api()))

    # Teste 4: Módulo resolvedor
    resultados.append(("Módulo resolvedor_captcha", testar_modulo_resolvedor()))

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)

    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{status} - {nome}")

    total = len(resultados)
    passou = sum(1 for _, r in resultados if r)

    print("\n" + "-" * 80)
    print(f"Resultado final: {passou}/{total} testes passaram")
    print("-" * 80)

    if passou == total:
        print("\n🎉 SUCESSO! Integração com 2Captcha está funcionando!")
    else:
        print("\n⚠️  Alguns testes falharam. Revise as mensagens acima.")

    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
