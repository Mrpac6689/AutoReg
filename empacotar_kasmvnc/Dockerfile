FROM kasmweb/ubuntu-jammy-desktop:1.17.0

USER root

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    wget unzip gnupg curl software-properties-common \
    python3 python3-pip python3-venv python3-dev git nano \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala Google Chrome (versão 138.0.7204.94)
RUN wget https://storage.googleapis.com/chrome-for-testing-public/142.0.7444.59/linux64/chrome-linux64.zip \
    && unzip chrome-linux64.zip \
    && mv chrome-linux64 /opt/chrome \
    && ln -sf /opt/chrome/chrome /usr/bin/google-chrome


# Instala ChromeDriver compatível (mesma versão)
RUN wget https://storage.googleapis.com/chrome-for-testing-public/142.0.7444.59/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver

# Instala dependências Python
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Prepara estrutura do AutoReg
RUN mkdir -p /home/kasm-user/.autoreg /home/kasm-user/AutoReg \
    && touch /home/kasm-user/AutoReg/autoreg.log \
    && chown -R 1000:1000 /home/kasm-user

# Clona AutoReg
USER 1000
RUN git clone https://github.com/Mrpac6689/AutoReg.git /home/kasm-user/.autoreg

# Cria virtualenv e instala dependências dentro dela
RUN python3 -m venv /home/kasm-user/.autoreg/venv \
    && /home/kasm-user/.autoreg/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# Define diretório de trabalho com venv ativada automaticamente
WORKDIR /home/kasm-user/.autoreg
CMD ["/bin/bash", "-c", "source /home/kasm-user/.autoreg/venv/bin/activate && exec bash"]
