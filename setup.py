from setuptools import setup, find_packages

# Lendo as dependências do arquivo requirements.txt, garantindo UTF-8
with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.read().splitlines()
    requirements = [line.strip() for line in requirements if line.strip() and not line.startswith("#")]

# Lendo a descrição longa (README.md), garantindo UTF-8
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='AutoReg',
    version='4.2.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'autoreg=autoreg4_2_1:main',
        ],
    },
    author='Michel Ribeiro Paes',
    description='AUTOREG - Operação automatizada de Sistemas - SISREG & G-HOSP',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/seu_usuario/seu_repositorio',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
