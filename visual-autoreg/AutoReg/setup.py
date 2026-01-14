from setuptools import setup, find_packages

setup(
    name="AutoReg",
    version="0.1.0",
    author="Seu Nome",
    author_email="seuemail@example.com",
    description="Aplicação para automação de registro com interface gráfica moderna.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt6",
        "PyQt6-WebEngine"
    ],
    entry_points={
        "console_scripts": [
            "autorege=main:main",
        ],
    },
)