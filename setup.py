from setuptools import setup, find_packages

# Lendo as dependências do arquivo requirements.txt, filtrando linhas vazias e caracteres não reconhecidos
with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.read().splitlines()
    # Filtra apenas linhas que não estão vazias e que não são comentários
    requirements = [line.strip() for line in requirements if line.strip() and not line.startswith("#")]

setup(
    name='AutoReg',
    version='4.2.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,  # Usa as dependências do requirements.txt limpas
    entry_points={
        'console_scripts': [
            'autoreg=autoreg4_2_1:main',  # Nome do comando para execução do seu programa
        ],
    },
    author='Michel Ribeiro Paes',
    description='AUTOREG - Operação automatizada de Sistemas - SISREG & G-HOSP',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/seu_usuario/seu_repositorio',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
