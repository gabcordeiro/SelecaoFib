Sistema de Análise de Candidatos 

📝 Descrição do Projeto
O script automatiza o cadastro, a avaliação baseada na sequência de Fibonacci e a análise de dados de candidatos fictícios, utilizando Python e SQLite.

✨ Features Principais
Gerenciamento de Banco de Dados: Criação e manipulação de um banco de dados SQLite com duas tabelas (SELECAO_CANDIDATO e SELECAO_TESTE) e relacionamento via chave estrangeira.
Geração de Dados: Geração automática dos 30 primeiros números da sequência de Fibonacci e classificação de paridade.
Análise com SQL: Execução de consultas SQL para listar, filtrar, agregar (COUNT) e deletar dados.
Interface de Linha de Comando (CLI): Uso do módulo argparse para criar uma ferramenta flexível e fácil de usar via terminal.
Relatórios Profissionais: Geração automática de um relatório em PDF contendo as análises, estatísticas e gráficos de pizza/barra para visualização dos resultados.
Exportação de Dados: Funcionalidade opcional para exportar os dados analisados para um arquivo JSON.
Logging Detalhado: Sistema de logs que registra todas as etapas, avisos e erros da execução em um arquivo (selecao.log) e no console.
Monitoramento de Performance: Cálculo e exibição do tempo total de execução do script.
Validação de Dados: Checagem de integridade (constraints) para garantir a qualidade dos dados inseridos no banco.
💻 Tecnologias Utilizadas
Linguagem: Python 3
Banco de Dados: SQLite3
Bibliotecas Principais:
matplotlib: Para a geração dos gráficos.
fpdf2: Para a criação dos relatórios em PDF.
argparse: Para a interface de linha de comando.
logging: Para o sistema de logs.
🚀 Como Usar
Pré-requisitos
Python 3.8 ou superior
Pip (gerenciador de pacotes do Python)
Instalação
Clone este repositório:
Bash

git clone [URL_DO_SEU_REPOSITORIO]
Navegue até o diretório do projeto:
Bash

cd [NOME_DO_DIRETORIO]
Instale as dependências necessárias:
Bash

pip install -r requirements.txt
Execução
O script é executado via linha de comando.

Para ver todas as opções disponíveis:

Bash

python selecao.py --help
Execução padrão (modo principal):
Este comando realiza todo o processo para um candidato fictício e gera o relatório em PDF.

Bash

python selecao.py --nome "Gabriel Cordeiro de Carvalho"
Execução com exportação para JSON:

Bash

python selecao.py --nome "João Silva" --export_json
📂 Arquivos Gerados
Após a execução bem-sucedida, os seguintes arquivos serão criados no diretório raiz:

selecao.db: O banco de dados SQLite contendo todas as tabelas e dados.
relatorio_final.pdf: O relatório completo com análises, estatísticas e gráficos.
dados_finais.json: (Opcional) Arquivo com os dados exportados, gerado se a flag --export_json for utilizada.
selecao.log: Arquivo de log com o registro detalhado de toda a execução do script.
👨‍💻 Autor
Gabriel Cordeiro de Carvalho

GitHub: [Link para seu GitHub]
LinkedIn: [Link para seu LinkedIn]
📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.