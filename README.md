# 📊 Sistema de Análise de Candidatos - Desafio SEFAZ/ES

### 🚀 Solução completa para o desafio técnico do processo seletivo da SEFAZ-ES

---

## 📝 Descrição do Projeto

Este projeto é uma solução completa para o desafio de programação proposto no processo seletivo da **Secretaria da Fazenda do Espírito Santo (SEFAZ-ES)**.  
O script automatiza o cadastro, a avaliação baseada na **sequência de Fibonacci** e a análise de dados de candidatos fictícios, utilizando **Python** e **SQLite**.

A solução não apenas cumpre todos os requisitos obrigatórios, como também implementa **funcionalidades extras**, demonstrando boas práticas de desenvolvimento, robustez e apresentação de dados profissional.

---

## ✨ Features Principais

✅ **Gerenciamento de Banco de Dados**  
- Criação e manipulação de banco SQLite com tabelas `SELECAO_CANDIDATO` e `SELECAO_TESTE`  
- Relacionamento via chave estrangeira

✅ **Geração de Dados**  
- Geração dos 30 primeiros números da sequência de Fibonacci  
- Classificação de paridade (par/ímpar)

✅ **Análise com SQL**  
- Consultas SQL para listar, filtrar, agregar (`COUNT`) e deletar dados

✅ **Interface de Linha de Comando (CLI)**  
- Uso de `argparse` para criar uma ferramenta flexível e intuitiva

✅ **Relatórios Profissionais**  
- Geração de PDF com análises, estatísticas e gráficos (pizza e barra)

✅ **Exportação de Dados**  
- Exportação opcional dos dados para arquivo JSON

✅ **Logging Detalhado**  
- Registro completo em arquivo `selecao.log` e no console

✅ **Monitoramento de Performance**  
- Cálculo e exibição do tempo total de execução do script

✅ **Validação de Dados**  
- Checagem de integridade para garantir a qualidade dos dados

---

## 💻 Tecnologias Utilizadas

- **Linguagem**: Python 3  
- **Banco de Dados**: SQLite3  
- **Bibliotecas**:
  - `matplotlib`: geração de gráficos
  - `fpdf2`: criação de relatórios em PDF
  - `argparse`: CLI
  - `logging`: sistema de logs

---

## 🚀 Como Usar

### ✅ Pré-requisitos

- Python 3.8 ou superior  
- Pip (gerenciador de pacotes)

### 🔧 Instalação

```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd [NOME_DO_DIRETORIO]
pip install -r requirements.txt
