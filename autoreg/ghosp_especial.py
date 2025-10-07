import os
import time
import pandas as pd
from selenium import webdriver
from autoreg.chrome_options import get_chrome_options
from autoreg.ler_credenciais import ler_credenciais
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
def ghosp_especial():
    print("\n---===> ACESSO AO GHOSP - EXTRAÇÃO PERSONALIZADA <===---")
    
    usuario_ghosp, senha_ghosp, caminho_ghosp, _, _ = ler_credenciais()

    # Inicializa o navegador (Chrome)
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    print("Iniciando o Chromedriver...")

    # Acesse a página de login do G-HOSP na porta 4002
    url_login = f"{caminho_ghosp}:4002/users/sign_in"
    driver.get(url_login)


    # Localiza e preenche o campo de e-mail
    print("Localizando campo de e-mail...")
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_field.send_keys(usuario_ghosp)

    # Localiza e preenche o campo de senha (//*[@id="password"])
    print("Localizando campo de senha...")
    senha_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
    )
    senha_field.send_keys(senha_ghosp)

    # Localiza e clica no botão de login (//*[@id="new_user"]/div/input)
    print("Localizando botão de login...")
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/div/input'))
    )
    login_button.click()

    print("Login realizado com sucesso!")
    # Localiza o menu dropdown e passa o mouse para abrir
    from selenium.webdriver.common.action_chains import ActionChains


    time.sleep(2)

    # Bloco de manipulação do CSV
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    csv_path = os.path.join(user_dir, 'especial.csv')
    df = pd.read_csv(csv_path, dtype=str)
    resultados = []
    total = len(df)
    for idx, row in df.iterrows():
        pront = str(row['pront'])
        print(f"\n[{idx+1}/{total}] Processando prontuário: {pront}")

        driver.get(f"{caminho_ghosp}:4002/prontuarios")
        nome = ''
        internacoes = ''
        dn = ''
        cirurgias = {}
        # Insere o valor no campo prontuário
        try:
            campo_prontuario = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="prontuario"]'))
            )
            campo_prontuario.clear()
            campo_prontuario.send_keys(pront)
            print(f"Valor {pront} inserido no campo prontuário.")

            # Clica no botão de busca
            botao_busca = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="cabecalho"]/form/fieldset/div[10]/div/input'))
            )
            botao_busca.click()
            print("Botão de busca clicado.")
        except Exception as e:
            print(f"Erro ao inserir prontuário ou clicar no botão: {e}")
            continue

        # Verifica se o diálogo de justificativa de acesso aparece
        try:
            dialog = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="form_justificativa"]'))
            )
            print("Diálogo de justificativa encontrado!")

            # Seleciona 'Enfermagem' no dropdown
            dropdown = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="acesso_prontuario_tabela_id"]'))
            )
            from selenium.webdriver.support.ui import Select
            select = Select(dropdown)
            select.select_by_visible_text("Enfermagem")
            print("Opção 'Enfermagem' selecionada.")

            # Preenche justificativa com 'NIR'
            justificativa = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="acesso_prontuario_justificativa"]'))
            )
            justificativa.clear()
            justificativa.send_keys("NIR")
            print("Justificativa preenchida com 'NIR'.")

            # Clica em salvar
            salvar_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="new_acesso_prontuario"]/div[3]/input'))
            )
            salvar_btn.click()
            print("Botão 'Salvar' clicado.")

            # Aguarda 1 segundo
            time.sleep(1)

            # Clica no botão de confirmação
            confirmar_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[11]/div/button/span'))
            )
            confirmar_btn.click()
            print("Botão de confirmação clicado.")
        except Exception as e:
            print(f"Diálogo de justificativa não encontrado ou erro no preenchimento: {e}")

        # Após o fluxo de justificativa, captura o nome do paciente
        try:
            nome_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/h2'))
            )
            nome = nome_elem.text
            print(f"Nome do paciente: {nome}")

            # Extração das datas de internação
            try:
                div_internacoes = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/article/div/div[1]/div/div[4]/div[1]/div[1]'))
                )
                rows = div_internacoes.find_elements(By.CLASS_NAME, 'row')
                datas = []
                for row_ in rows:
                    try:
                        small = row_.find_element(By.CLASS_NAME, 'cB')
                        span = small.find_element(By.CLASS_NAME, 'ml5')
                        data = span.text.strip().replace('\n', ' ').replace('  ', ' ')
                        if data:
                            datas.append(data)
                    except Exception:
                        continue
                import re
                todas_datas = []
                for texto in datas:
                    datas_encontradas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
                    todas_datas.extend(datas_encontradas)
                internacoes = ' '.join(todas_datas)
                print(f"Internações: {internacoes}")
            except Exception as e:
                print(f"Erro ao extrair datas de internação: {e}")
                internacoes = ''

            try:
                # Obtém o href do link do prontuário
                link_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/p/a'))
                )
                href = link_elem.get_attribute('href')
                if href.startswith('/'):
                    url_pront = f"{caminho_ghosp}:4002{href}"
                else:
                    url_pront = href
                print(f"Acessando página do prontuário: {url_pront}")
                driver.get(url_pront)

                # Na nova página, clique no link do h4/a
                try:
                    h4_link = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="paciente"]/div[2]/div/div[2]/h4/a'))
                    )
                    h4_link.click()
                    print("Link do h4/a clicado.")

                    # Obtém a data de nascimento
                    dn_elem = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[2]/fieldset/small/div[2]'))
                    )
                    dn = dn_elem.text
                    print(f"Data de nascimento: {dn}")

                    # Clica para voltar
                    voltar_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/div[6]/div[1]/a/span'))
                    )
                    voltar_btn.click()
                    print("Botão de voltar clicado.")
                except Exception as e:
                    print(f"Erro ao clicar ou obter dados na página do paciente: {e}")
                    dn = ''

                # Clica na aba de cirurgias realizadas
                try:
                    aba_cirurgias = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="aba"]/ul/li[9]/a'))
                    )
                    aba_cirurgias.click()
                    print("Aba de cirurgias clicada.")

                    fieldset = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/article/div/div/fieldset'))
                    )
                    print("Campo fieldset encontrado.")

                    linhas = fieldset.find_elements(By.XPATH, './/table//tbody/tr')
                    for i, linha in enumerate(linhas, 1):
                        cols = linha.find_elements(By.TAG_NAME, 'td')
                        if len(cols) >= 3:
                            cirurgias[f'atendimento{str(i).zfill(2)}'] = cols[0].text.strip().replace('\n', ' ')
                            cirurgias[f'procedimento{str(i).zfill(2)}'] = cols[1].text.strip().replace('\n', ' ')
                            cirurgias[f'profissional{str(i).zfill(2)}'] = cols[2].text.strip().replace('\n', ' ')
                except Exception as e:
                    print(f"Erro ao extrair cirurgias: {e}")
            except Exception as e:
                print(f"Erro ao capturar dados do paciente: {e}")
                dn = ''

            # Monta o dicionário de resultado
            resultado = {
                'pront': pront,
                'nome': nome,
                'internacoes': internacoes,
                'dn': dn,
            }
            resultado.update(cirurgias)
            resultados.append(resultado)
        except Exception as e:
            print(f"Erro ao processar dados do prontuário {pront}: {e}")
            continue

    # Salva o resultado no especial.csv
    df_result = pd.DataFrame(resultados)
    df_result.to_csv(csv_path, index=False)
    print(f"\nExtração finalizada. Resultados salvos em {csv_path}")

    # Fecha o navegador
    driver.quit()