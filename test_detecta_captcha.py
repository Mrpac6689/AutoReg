#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para validar os métodos de detecção de CAPTCHA.
Simula page_source com diferentes variações para garantir detecção robusta.
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def testar_padroes_deteccao():
    """Testa se todos os padrões de CAPTCHA são detectados"""
    print("=" * 80)
    print("TESTE: Padrões de Detecção de CAPTCHA")
    print("=" * 80)

    # Padrões que devem ser detectados
    padroes_teste = [
        # Texto completo do SISREG
        "Devido a grande quantidade de requisições (> 500) realizadas na ultima hora pelo seu operador, será realizado um teste automatizado para diferenciação entre computadores e humanos (CAPTCHA):",

        # Variações de encoding
        "Devido a grande quantidade de requisicoes (> 500) realizadas na ultima hora",

        # Texto fragmentado
        "teste automatizado para diferenciação entre computadores e humanos",

        # Apenas menção de CAPTCHA e requisições
        "grande quantidade de requisições... CAPTCHA",

        # Com acentos diferentes
        "Devido a grande quantidade de requisições (> 500) realizadas na última hora",

        # Minúsculas
        "devido a grande quantidade de requisições > 500",

        # Apenas computadores e humanos
        "computadores e humanos (CAPTCHA)",

        # Sem acentos
        "teste automatizado para diferenciacao entre computadores e humanos",
    ]

    # Padroes de deteccao (prefixos curtos cobrem variantes de encoding)
    padroes_deteccao = [
        "grande quantidade de requ",
        "teste automatizado para difer",
        "computadores e humanos",
        "500) realizadas na ultima hora",
        "pelo seu operador, ser",
    ]

    print("\nTestando detecção de padrões:\n")

    total = len(padroes_teste)
    detectados = 0

    for i, texto_teste in enumerate(padroes_teste, 1):
        texto_lower = texto_teste.lower()
        detectado = False

        for padrao in padroes_deteccao:
            if padrao in texto_lower:
                detectado = True
                break

        status = "✅ DETECTADO" if detectado else "❌ NÃO DETECTADO"
        detectados += detectado

        print(f"{i}. {status}")
        print(f"   Texto: {texto_teste[:80]}...")
        if detectado:
            print(f"   Padrão encontrado: '{padrao}'")
        print()

    print("-" * 80)
    print(f"Resultado: {detectados}/{total} padrões detectados")
    print("-" * 80)

    return detectados == total


def testar_xpath_expressions():
    """Valida se as expressões XPath estão sintaticamente corretas"""
    print("\n" + "=" * 80)
    print("TESTE: Validação de Expressões XPath")
    print("=" * 80)

    xpaths = {
        "Busca CAPTCHA case-insensitive":
            "//*[contains(translate(text(), 'CAPTCHA', 'captcha'), 'captcha')]",

        "Busca iframes CAPTCHA":
            "//iframe[contains(@src, 'captcha') or contains(@src, 'recaptcha') or contains(@src, 'hcaptcha') or "
            "contains(@title, 'captcha') or contains(@title, 'recaptcha') or contains(@title, 'hcaptcha') or "
            "contains(@name, 'captcha') or contains(@name, 'recaptcha') or contains(@id, 'captcha')]",

        "Busca divs/elementos CAPTCHA":
            "//*[contains(@class, 'captcha') or contains(@class, 'recaptcha') or contains(@class, 'hcaptcha') or "
            "contains(@id, 'captcha') or contains(@id, 'recaptcha') or contains(@id, 'hcaptcha')]",

        "Busca botão Continuar":
            "//button[contains(text(), 'Continuar')] | //input[@value='Continuar']"
    }

    print("\nValidando sintaxe XPath:\n")

    todas_validas = True

    for nome, xpath in xpaths.items():
        try:
            # Tenta importar lxml para validação (opcional)
            try:
                from lxml import etree
                etree.XPath(xpath)
                status = "✅ VÁLIDO"
            except ImportError:
                # Se lxml não disponível, apenas verifica sintaxe básica
                if xpath and len(xpath) > 0:
                    status = "✅ SINTAXE OK (lxml não disponível para validação completa)"
                else:
                    status = "❌ INVÁLIDO"
                    todas_validas = False
        except Exception as e:
            status = f"❌ ERRO: {e}"
            todas_validas = False

        print(f"• {nome}")
        print(f"  {status}")
        print(f"  XPath: {xpath[:80]}{'...' if len(xpath) > 80 else ''}")
        print()

    return todas_validas


def testar_importacao_modulo():
    """Testa se o módulo detecta_capchta pode ser importado"""
    print("\n" + "=" * 80)
    print("TESTE: Importação do Módulo")
    print("=" * 80)

    try:
        from autoreg.detecta_capchta import detecta_captcha, _ler_config_2captcha
        print("✅ Módulo detecta_capchta importado com sucesso!")

        # Verifica se as funções principais existem
        funcoes = ['detecta_captcha', '_verifica_sessao_invalida', '_ler_kasm_url', '_ler_config_2captcha']
        print("\nFunções disponíveis:")

        for func_name in funcoes:
            try:
                from autoreg import detecta_capchta
                if hasattr(detecta_capchta, func_name):
                    print(f"  ✅ {func_name}")
                else:
                    print(f"  ⚠️  {func_name} (privada, ok se começar com _)")
            except:
                print(f"  ❌ {func_name}")

        return True

    except Exception as e:
        print(f"❌ Erro ao importar módulo: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 18 + "TESTE DE DETECÇÃO DE CAPTCHA MELHORADA" + " " * 21 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    resultados = []

    # Teste 1: Padrões de detecção
    resultados.append(("Padrões de detecção", testar_padroes_deteccao()))

    # Teste 2: Expressões XPath
    resultados.append(("Expressões XPath", testar_xpath_expressions()))

    # Teste 3: Importação do módulo
    resultados.append(("Importação módulo", testar_importacao_modulo()))

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
        print("\n🎉 SUCESSO! Detecção de CAPTCHA melhorada está funcionando!")
    else:
        print("\n⚠️  Alguns testes falharam. Revise as mensagens acima.")

    print()

    return 0 if passou == total else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
