from setuptools import setup


with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.read().splitlines()
    requirements = [line.strip() for line in requirements if line.strip() and not line.startswith("#")]


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='AutoReg-Mrpac6689',
    version='5.0.0',
    py_modules=['autoreg'],  
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'autoreg=autoreg:criar_janela_principal' 
        ]
    },
    author='Michel Ribeiro Paes',
    author_email='michelrpaes@gmail.com',
    description='AUTOREG - Operação automatizada de Sistemas - SISREG & G-HOSP',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Mrpac6689/AutoReg',
    license='GPL-3.0-or-later',  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3',
)
