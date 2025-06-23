"""
SISTEMA DE PROCESSO SELETIVO SEFAZ/ES
Desenvolvedor: Gabriel Cordeiro de Carvalho
Data: 2025
Versão: 1.0

========================================================================
FEATURES PRINCIPAIS:
1. Gerenciamento completo de banco de dados SQLite
2. Geração automática de sequência Fibonacci
3. Análise estatística de paridade (pares/ímpares)
4. Validação de constraints e qualidade dos dados
5. Geração de relatórios em PDF com gráficos
6. Exportação de dados para JSON
7. Sistema de logs detalhado
8. Testes unitários integrados
9. Métrica para o tempo de execução

========================================================================
COMO USAR:
1. Modo normal (processo completo):
   python selecao.py --nome "Nome do Candidato" [--expected_ratio 1.618] [--tolerancia 0.5] [--export_json]

2. Modo teste (validações):
   python selecao.py --testar

3. Ajuda (mostra opções):
   python selecao.py

Exemplo completo:
   python selecao.py --nome "João Silva" --expected_ratio 1.6 --tolerancia 0.3 --export_json

========================================================================
OBSERVAÇÕES:
- Arquivos gerados: selecao.db (banco de dados), relatorio.pdf, dados.json (opcional)
- Logs são salvos em selecao.log
- Proporção áurea padrão: 1.618 (com tolerância de 0.5)
"""

import sqlite3
import argparse
import logging
from typing import List, Tuple, Dict, Any
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import json
import time

logging.basicConfig(
    # Define o nível mínimo de logs que será registrado (INFO inclui INFO, WARNING, ERROR, CRITICAL)
    level=logging.INFO,
    
    # Formato das mensagens de log:
    # %(asctime)s - Data/hora do log
    # %(levelname)s - Nível do log (INFO, ERROR, etc)
    # %(message)s - Mensagem do log
    format='%(asctime)s - %(levelname)s - %(message)s',
    
    # Handlers (saídas) para os logs:
    handlers=[
        # 1. Arquivo de log (cria/grava no arquivo 'selecao.log')
        logging.FileHandler("selecao.log"),
        
        # 2. Saída no console (mostra os logs no terminal durante a execução)
        logging.StreamHandler()
    ]
)

class DatabaseManager:
    """Gerencia todas as operações de banco de dados"""
    
    def __init__(self, db_path: str = 'selecao.db'):
        """Inicializa a conexão com o banco de dados SQLite.
        
        Args:
            db_path (str): Caminho para o arquivo do banco de dados. 
                Padrão: 'selecao.db' (banco criado no diretório atual)
        """
        # Estabelece conexão com o banco de dados SQLite
        self.conn = sqlite3.connect(db_path)
        
        # Cria um cursor para executar comandos SQL
        self.cursor = self.conn.cursor()
        
        # Registra no log que a conexão foi estabelecida
        logging.info("Banco de dados conectado")

    def create_tables(self) -> bool:
        """Cria as tabelas necessárias no banco de dados.
        
        Returns:
            bool: True se as tabelas foram criadas com sucesso, False caso contrário
        """
        try:
            # 1. LIMPEZA - Remove tabelas existentes para evitar conflitos
            self.cursor.execute("DROP TABLE IF EXISTS SELECAO_TESTE")
            self.cursor.execute("DROP TABLE IF EXISTS SELECAO_CANDIDATO")
            
            # 2. CRIAÇÃO DA TABELA DE CANDIDATOS
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SELECAO_CANDIDATO (
                ID_CANDIDATO INTEGER PRIMARY KEY AUTOINCREMENT,
                NME_CANDIDATO TEXT NOT NULL,
                DAT_INSCRICAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
            )
            """)
            
            # 3. CRIAÇÃO DA TABELA DE TESTES (relacionada aos candidatos)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SELECAO_TESTE (
                ID_TESTE INTEGER PRIMARY KEY AUTOINCREMENT,      
                ID_CANDIDATO INTEGER,                            
                NUM_FIBONACCI INTEGER NOT NULL,                  
                NUM_PAR INTEGER CHECK (NUM_PAR IN (0, 1)) NOT NULL,  
                NUM_IMPAR INTEGER CHECK (NUM_IMPAR IN (0, 1)) NOT NULL, 
                FOREIGN KEY (ID_CANDIDATO) REFERENCES SELECAO_CANDIDATO(ID_CANDIDATO) 
            )
            """)
            
            # 4. CONFIRMA as alterações no banco
            self.conn.commit()
            logging.info("Tabelas criadas com sucesso")
            return True
            
        except sqlite3.Error as e:
            # 5. TRATAMENTO DE ERRO - Registra falhas
            logging.error(f"Erro na criação de tabelas: {e}")
            return False
        
    def insert_candidate(self, name: str) -> int:
        """Insere um novo candidato na tabela SELECAO_CANDIDATO.
        
        # 1. INICIALIZAÇÃO
        # MÉTODO IMPORTANTE PARA CADASTRO DE NOVOS CANDIDATOS NO SISTEMA
        
        Args:
            name (str): Nome do candidato a ser inserido no banco de dados
            
        Returns:
            int: ID gerado para o novo candidato (lastrowid) ou -1 em caso de erro
        """
        try:
            # 2. EXECUÇÃO DA QUERY SQL
            # UTILIZA PARAMETRIZAÇÃO PARA EVITAR SQL INJECTION
            self.cursor.execute(
                "INSERT INTO SELECAO_CANDIDATO (NME_CANDIDATO) VALUES (?)",
                (name,)
            )
            
            # 3. CONFIRMAÇÃO DA TRANSAÇÃO
            self.conn.commit()
            
            # 4. REGISTRO DO LOG E RETORNO DO ID
            logging.info(f"Candidato '{name}' inserido")
            return self.cursor.lastrowid
            
        except sqlite3.Error as e:
            # 5. TRATAMENTO DE ERROS
            # REGISTRA ERRO NO LOG E RETORNA CÓDIGO DE FALHA
            logging.error(f"Erro ao inserir candidato: {e}")
            return -1
    
    def generate_fibonacci(self, n: int = 30) -> List[int]:
        """Gera e retorna a sequência de Fibonacci até o n-ésimo termo.
        
        Args:
            n (int): Quantidade de números da sequência a gerar (padrão: 30)
        
        Returns:
            List[int]: Sequência de Fibonacci
        """
        a, b = 0, 1
        sequence = []
        
        # Gera cada número da sequência
        for i in range(n):
            sequence.append(b)
            a, b = b, a + b
        
        # Formata e imprime a sequência conforme especificação
        print("\n[SEQUÊNCIA FIBONACCI GERADA]")
        for i, num in enumerate(sequence):
            # Quebra de linha a cada 10 números para melhor visualização
            end_char = "\n" if (i + 1) % 10 == 0 else ", "
            # Último número não tem vírgula
            if i == len(sequence) - 1:
                print(num)
            else:
                print(num, end=end_char)
        
        return sequence
    
    def insert_tests(self, candidate_id: int, fib_sequence: List[int]):
        """Insere uma sequência de testes Fibonacci na tabela SELECAO_TESTE.
        
        # 1. INICIALIZAÇÃO
        # MÉTODO CRÍTICO PARA REGISTRO DE TESTES DE PERFORMANCE DOS CANDIDATOS
        
        Args:
            candidate_id (int): ID do candidato associado aos testes
            fib_sequence (List[int]): Lista de números da sequência Fibonacci a serem analisados
            
        Processo:
            - Para cada número Fibonacci, calcula se é par ou ímpar
            - Insere registro com metadados de análise
            - Inclui extensos logs para debugging
        """
        try:
            # 2. DEBUG INICIAL
            # LOGS DETALHADOS PARA MONITORAMENTO DO PROCESSO
            print(f"\n[DEBUG] Iniciando inserção de testes para candidato ID: {candidate_id}")
            logging.debug(f" Tamanho da sequência: {len(fib_sequence)} números")
            
            # 3. PROCESSAMENTO DA SEQUÊNCIA
            for i, num in enumerate(fib_sequence):
                # 3.1. ANÁLISE MATEMÁTICA
                # CLASSIFICAÇÃO PAR/ÍMPAR COM OPERAÇÃO BITWISE (OTIMIZADO)
                is_even = 1 if num % 2 == 0 else 0
                is_odd = 1 - is_even
                
                # 3.2. DEBUG DOS VALORES (OPCIONAL)
                logging.debug(f" Inserindo #{i+1}: Fib={num} | Par={is_even} | Ímpar={is_odd}")
                
                # 4. EXECUÇÃO DA QUERY
                self.cursor.execute(
                    """INSERT INTO SELECAO_TESTE 
                    (ID_CANDIDATO, NUM_FIBONACCI, NUM_PAR, NUM_IMPAR) 
                    VALUES (?, ?, ?, ?)""",
                    (candidate_id, num, is_even, is_odd)
                )
                
                # 5. DEBUG COMPLEMENTAR
                # MOSTRA PRIMEIROS E ÚLTIMOS 5 REGISTROS PARA VERIFICAÇÃO
                if i < 5 or i >= len(fib_sequence) - 5:
                    print(f"  [SQL] INSERT INTO SELECAO_TESTE VALUES({candidate_id}, {num}, {is_even}, {is_odd})")
            
            # 6. FINALIZAÇÃO
            self.conn.commit()
            logging.debug(f" Commit realizado! {len(fib_sequence)} registros inseridos.")
            logging.info(f"{len(fib_sequence)} testes inseridos")
        
        except sqlite3.Error as e:
            # 7. TRATAMENTO DE ERROS AVANÇADO
            # CAPTURA INFORMÇÕES ESPECÍFICAS DO SQLITE
            print(f"[ERRO CRÍTICO] Falha na inserção: {e}")
            logging.error(f"Erro ao inserir testes: {e}")
            
            # 7.1. DIAGNÓSTICO APRIMORADO
            if hasattr(e, 'sqlite_errorname'):
                print(f"  Código do erro SQLite: {e.sqlite_errorname}")
            if hasattr(e, 'sqlite_errorcode'):
                print(f"  Número do erro: {e.sqlite_errorcode}")

    def execute_query(self, query: str, params: tuple = ()) -> List[Tuple]:
        """Executa uma consulta SQL com parâmetros opcionais.
        
        Args:
            query (str): Comando SQL a ser executado
            params (tuple, optional): Parâmetros para a query. Defaults to ().
        
        Returns:
            List[Tuple]: Resultados da consulta ou lista vazia em caso de erro
        """
        try:
            self.cursor.execute(query, params)  # Agora aceita parâmetros
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Erro na consulta '{query}': {e}")
            return []

    def delete_large_numbers(self, threshold: int = 5000):
        """Remove números Fibonacci acima de um limite da tabela SELECAO_TESTE.
        
        # MÉTODO IMPORTANTE PARA MANUTENÇÃO DO BANCO DE DADOS
        
        Args:
            threshold (int): Valor limite para exclusão (padrão: 5000)
                            Todos os números maiores que este serão removidos
        """
        try:
            # 1.EXECUTA A EXCLUSÃO DOS REGISTROS
            self.cursor.execute(
                "DELETE FROM SELECAO_TESTE WHERE NUM_FIBONACCI > ?",
                (threshold,)
            )
            
            # 2.CONFIRMA A TRANSAÇÃO
            self.conn.commit()
            
            # 3.REGISTRA O LOG DE OPERAÇÃO
            logging.info(f"Números acima de {threshold} removidos")
            
        except sqlite3.Error as e:
            # TRATAMENTO DE ERROS
            logging.error(f"Erro ao deletar registros: {e}")

    def get_stats(self, candidate_id: int) -> dict:
        """Obtém estatísticas completas do candidato e sua sequência Fibonacci.
             
        Args:
            candidate_id (int): ID do candidato para filtrar os dados
            
        Returns:
            dict: Dicionário contendo todas estatísticas calculadas
        """
        stats = {}
        
        # 1. CONTAGEM TOTAL DE NÚMEROS
        stats['total'] = self.execute_query(
            "SELECT COUNT(*) FROM SELECAO_TESTE WHERE ID_CANDIDATO = ?",
            (candidate_id,)
        )[0][0]
        
        # 2. SEPARAÇÃO PARES/ÍMPARES
        count_result = self.execute_query(
            "SELECT SUM(NUM_PAR), SUM(NUM_IMPAR) FROM SELECAO_TESTE WHERE ID_CANDIDATO = ?",
            (candidate_id,)
        )[0]
        stats['pares'] = count_result[0] or 0  # Evita None com fallback para 0
        stats['impares'] = count_result[1] or 0
        
        # 3. SEQUÊNCIA COMPLETA ORDENADA
        stats['sequencia'] = [row[0] for row in self.execute_query(
            "SELECT NUM_FIBONACCI FROM SELECAO_TESTE WHERE ID_CANDIDATO = ? ORDER BY NUM_FIBONACCI",
            (candidate_id,)
        )]
        
        # 4. TOP 5 MAIORES NÚMEROS
        stats['top5'] = [row[0] for row in self.execute_query(
            "SELECT NUM_FIBONACCI FROM SELECAO_TESTE WHERE ID_CANDIDATO = ? ORDER BY NUM_FIBONACCI DESC LIMIT 5",
            (candidate_id,)
        )]
        
        # 5. DADOS CADASTRAIS DO CANDIDATO
        stats['candidato'] = self.execute_query(
            "SELECT NME_CANDIDATO, DAT_INSCRICAO FROM SELECAO_CANDIDATO WHERE ID_CANDIDATO = ?",
            (candidate_id,)
        )[0]
        
        return stats

    def validate_constraints(self) -> dict:
        """Valida as restrições de integridade dos dados na tabela SELECAO_TESTE.
        
        Realiza verificações críticas para garantir a consistência dos dados:
        - Valores válidos para campos de paridade (0 ou 1)
        - Consistência entre campos de par e ímpar
        - Ausência de valores nulos em campos obrigatórios
        
        Returns:
            dict: Relatório de validação contendo:
                - invalid_par (int): Qtd de valores inválidos em NUM_PAR
                - invalid_impar (int): Qtd de valores inválidos em NUM_IMPAR
                - inconsistent_parity (int): Qtd de registros com paridade inconsistente
                - null_values (int): Qtd de valores nulos em NUM_FIBONACCI
                Retorna -1 para cada chave em caso de erro na validação
        """
        try:
            # 1. CONSULTA DE VALIDAÇÃO
            # Verifica conformidade dos dados com as regras de negócio
            results = {
                'invalid_par': self.execute_query(
                    "SELECT COUNT(*) FROM SELECAO_TESTE WHERE NUM_PAR NOT IN (0, 1)"
                )[0][0],
                
                'invalid_impar': self.execute_query(
                    "SELECT COUNT(*) FROM SELECAO_TESTE WHERE NUM_IMPAR NOT IN (0, 1)"
                )[0][0],
                
                'inconsistent_parity': self.execute_query(
                    "SELECT COUNT(*) FROM SELECAO_TESTE WHERE NUM_PAR = NUM_IMPAR"
                )[0][0],
                
                'null_values': self.execute_query(
                    "SELECT COUNT(*) FROM SELECAO_TESTE WHERE NUM_FIBONACCI IS NULL"
                )[0][0]
            }

            # 2. ANÁLISE DOS RESULTADOS
            # Avalia se foram encontradas inconsistências
            if any(results.values()):
                logging.warning(f"Inconsistências detectadas: {results}")
            else:
                logging.info("Dados validados com sucesso - nenhuma inconsistência encontrada")
                
            return results
            
        except Exception as e:
            # 3. TRATAMENTO DE FALHAS
            # Captura e registra erros durante o processo de validação
            logging.error(f"Falha na validação: {str(e)}")
            return {
                'invalid_par': -1,
                'invalid_impar': -1,
                'inconsistent_parity': -1,
                'null_values': -1
            }

def add_section(pdf: FPDF, titulo: str, conteudo: str, font_style: str = '') -> None:
    """Adiciona uma seção formatada ao documento PDF.

    Args:
        pdf (FPDF): Instância do objeto FPDF
        titulo (str): Texto do título da seção (opcional)
        conteudo (str): Texto do conteúdo principal
        font_style (str, optional): Estilo da fonte ('B' para negrito). Default: ''

    Processo:
        - Formata título em negrito (se especificado)
        - Adiciona conteúdo com estilo normal
        - Mantém consistência de espaçamento
    """
    # 1. IMPRESSÃO DO TÍTULO (SE EXISTIR)
    if titulo.strip():
        # Configura fonte para título (negrito e maior se especificado)
        pdf.set_font(
            family="helvetica",
            style='B' if font_style == 'B' else '',
            size=12 if font_style == 'B' else 10
        )
        pdf.cell(0, 10, titulo, new_x="LMARGIN", new_y="NEXT")
    
    # 2. IMPRESSÃO DO CONTEÚDO
    # Configura fonte padrão para o conteúdo
    pdf.set_font(
        family="helvetica",
        style=font_style if font_style != 'B' else '',
        size=10
    )
    pdf.multi_cell(0, 6, conteudo)
    
    # 3. FORMATAÇÃO FINAL
    # Adiciona pequeno espaçamento pós-seção
    pdf.ln(1)

def create_bar_chart(labels: List[str], values: List[int], colors: List[str], total: int) -> BytesIO:
    """Gera um gráfico de barras com a distribuição de números pares/ímpares.

    Args:
        labels (List[str]): Rótulos das barras (ex: ['Pares', 'Ímpares'])
        values (List[int]): Valores correspondentes a cada categoria
        colors (List[str]): Cores específicas para cada barra
        total (int): Valor total para cálculo de porcentagens

    Returns:
        BytesIO: Buffer contendo a imagem do gráfico em formato PNG

    Processo:
        - Configura tamanho e estilo do gráfico
        - Adiciona rótulos e valores percentuais
        - Exporta para buffer de memória
    """
    # 1. CONFIGURAÇÃO INICIAL
    plt.figure(figsize=(6, 2))
    
    # 2. CRIAÇÃO DAS BARRAS
    bars = plt.bar(labels, values, color=colors)
    plt.title('Distribuição Par/Ímpar na Sequência Fibonacci', pad=15)
    plt.ylabel('Quantidade')
    
    # 3. ADIÇÃO DE RÓTULOS
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # Posição X centralizada
            height + 0.5,                       # Posição Y acima da barra
            f'{height} ({height / total * 100:.1f}%)',  # Texto com valor e %
            ha='center',                        # Alinhamento horizontal
            va='bottom',                        # Alinhamento vertical
            fontsize=9
        )
    
    # 4. EXPORTAÇÃO PARA MEMÓRIA
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_pie_chart(labels: List[str], sizes: List[int], colors: List[str]) -> BytesIO:
    """Gera um gráfico de pizza (setores) com distribuição de par/ímpar.

    Args:
        labels (List[str]): Nomes das categorias (ex: ['Pares', 'Ímpares'])
        sizes (List[int]): Valores proporcionais para cada categoria
        colors (List[str]): Cores específicas para cada fatia

    Returns:
        BytesIO: Buffer contendo a imagem do gráfico em formato PNG

    Processo:
        - Configura layout circular perfeito
        - Adiciona porcentagens automáticas
        - Aplica efeito de sombra para melhor visualização
        - Exporta para buffer de memória
    """
    # 1. CONFIGURAÇÃO DO GRÁFICO
    plt.figure(figsize=(3, 3))  # Tamanho quadrado para gráfico circular
    
    # 2. CRIAÇÃO DAS FATIAS
    plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',  # Formatação automática de porcentagens
        shadow=True,        # Efeito de profundidade
        startangle=90       # Rotação inicial (12h)
    )
    
    # 3. FORMATAÇÃO FINAL
    plt.axis('equal')  # Garante proporção circular perfeita
    plt.title('Distribuição Par/Ímpar em Gráfico de setores', pad=15)
    
    # 4. EXPORTAÇÃO PARA MEMÓRIA
    img_buffer = BytesIO()
    plt.savefig(
        img_buffer,
        format='png',
        dpi=150,            # Resolução balanceada
        bbox_inches='tight'  # Evita cortes
    )
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def generate_report(stats: dict, execution_time: float, filename: str = "relatorio.pdf", expected_ratio: float = 1.618, tolerancia: float = 0.5):
    """Gera um relatório PDF com os resultados da análise da sequência Fibonacci.
    
    Args:
        stats (dict): Dicionário contendo os dados estatísticos para o relatório. Deve conter:
            - 'sequencia': Lista com a sequência Fibonacci gerada
            - 'top5': Lista com os 5 maiores números da sequência
            - 'pares': Quantidade de números pares
            - 'impares': Quantidade de números ímpares
            - 'total': Total de números analisados
            - 'candidato': Tupla com (nome, data_inscricao) do candidato
            
        filename (str, optional): Nome do arquivo PDF de saída. Padrão: "relatorio.pdf"
        expected_ratio (float, optional): Valor esperado da proporção áurea (ímpares/pares). Padrão: 1.618
        tolerancia (float, optional): Margem de aceitação para a proporção. Padrão: 0.5
    
    Returns:
        bool: True se o relatório foi gerado com sucesso, False caso contrário
    
    Exemplo de uso:
        >>> dados = {
        ...     'sequencia': [1, 1, 2, 3, 5],
        ...     'top5': [5, 3, 2, 1, 1],
        ...     'pares': 1,
        ...     'impares': 4,
        ...     'total': 5,
        ...     'candidato': ("Fulano", "2023-01-01")
        ... }
        >>> generate_report(dados, "meu_relatorio.pdf", 1.6, 0.1)
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("helvetica", size=10)

        # Cabeçalho
        pdf.set_font_size(14)
        pdf.set_font(style='B')
        pdf.set_fill_color(40, 60, 80)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 15, "SEFAZ/ES - Relatório de Processo Seletivo",
                new_x="LMARGIN", new_y="NEXT", align='C', fill=True)
        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)

        # Dados do candidato
        add_section(pdf, "Dados do Candidato",
                    f"Nome: {stats['candidato'][0]}\nData de Inscrição: {stats['candidato'][1]}", 'B')              
        pdf.ln(4)
        
        # Sequência Fibonacci
        fib_str = ', '.join(map(str, stats['sequencia']) ) 
        pdf.set_font("helvetica", style='B', size=12)
        pdf.cell(0, 10, f"Sequência Fibonacci ({len(stats['sequencia'])} números)", fib_str, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font_size(14)
        pdf.set_font(style='B')
        if len(fib_str) > 300:
            fib_str = fib_str[:300] + '... [truncado]'
        add_section(pdf, " ", f"{fib_str}", 'B')
        pdf.ln(6)

        # Top 5 maiores números - formatação tabela simples
        add_section(pdf, "Top 5 Maiores Números", "", 'B')
        pdf.set_draw_color(150, 150, 150)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(40, 8, "Posição", border=1, fill=True, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(40, 8, "Valor", border=1, fill=True, align='C', new_x="LMARGIN", new_y="NEXT")
        for i, num in enumerate(stats['top5'], 1):
            pdf.cell(40, 8, str(i), border=1, align='C', new_x="RIGHT", new_y="TOP")
            pdf.cell(40, 8, f"{num:,}", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # Análise Estatística + Gráficos
        add_section(pdf, "Análise Estatística e Gráficos", "", 'B')
    
        labels = ['Pares', 'Ímpares']
        values = [stats['pares'], stats['impares']]
        colors_bar = ['#4e79a7', '#f28e2b']
        img_bar = create_bar_chart(labels, values, colors_bar, stats['total'])
        pdf.image(img_bar, x=10, w=190)
        pdf.ln(10)

        colors_pie = ['#66c2a5', '#fc8d62']
        img_pie = create_pie_chart(labels, values, colors_pie)
        pdf.image(img_pie, x=50, w=100)
        pdf.ln(10)

        # Análise Matemática da proporção
        add_section(pdf, "Análise Matemática", "", 'B')
        ratio = stats['impares'] / stats['pares'] if stats['pares'] > 0 else 0
        pdf.cell(0, 6, f"Proporção Ímpares/Pares: {ratio:.3f}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Proporção Áurea Esperada: ~ {expected_ratio:.3f}", new_x="LMARGIN", new_y="NEXT")

        # Verifica se a proporção Ímpares/Pares se aproxima da Proporção Áurea
        # e destaca o resultado em verde (ok) ou vermelho (fora do padrão)
        if abs(ratio - expected_ratio) < tolerancia:
            pdf.set_text_color(0, 128, 0)
            pdf.cell(0, 6, " Proporção dentro do esperado para sequência Fibonacci", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 6, "Proporção fora do padrão Fibonacci esperado", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)

         # Rodapé
        pdf.ln(15)
        pdf.set_font_size(8)
        pdf.set_font(style='I')
        pdf.cell(0, 5, f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                 new_x="LMARGIN", new_y="NEXT", align='C')
        
        # --- Medição do tempo ---
        pdf.cell(0, 5, f"Tempo de execução do processo: {execution_time:.4f} segundos",
                 new_x="LMARGIN", new_y="NEXT", align='C')

        pdf.cell(0, 5, "Secretaria da Fazenda do Espírito Santo - Processo Seletivo",
                 new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.cell(0, 5, "Todos os direitos reservados © 2025",
                 new_x="LMARGIN", new_y="NEXT", align='C')

        pdf.output(filename)
        logging.info(f"Relatório gerado: {filename}")
        return True

        pdf.output(filename)
        logging.info(f"Relatório gerado: {filename}")
        return True
    # Captura e registra qualquer erro durante a geração do relatório
    except Exception as e:
        logging.error(f"Erro ao gerar relatório: {e}")
        return False

def export_stats_to_json(stats: Dict[str, Any], filename: str = "dados.json"):
    """Exporta estatísticas para arquivo JSON.
    
    Args:
        stats (Dict[str, Any]): Dicionário com dados a serem salvos
        filename (str, optional): Nome do arquivo de saída. Default: "dados.json"
    
    Returns:
        bool: True se exportado com sucesso, False se falhar
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4, default=str)
        logging.info(f"Dados exportados para JSON: {filename}")
        return True
    except Exception as e:
        logging.error(f"Erro ao exportar JSON: {e}") 
        return False

def run_full_process(candidate_name: str,
                     expected_ratio: float = 1.618,
                     tolerancia: float = 0.5,
                     export_json: bool = False):
    """
    Executa o fluxo completo do processo seletivo: cria o banco, insere dados,
    executa consultas, deleta registros e gera relatórios, medindo o tempo total.
    
    Args:
        candidate_name (str): Nome do candidato a ser registrado.
        expected_ratio (float): Valor esperado da proporção áurea (padrão: 1.618).
        tolerancia (float): Margem aceitável para validação (padrão: 0.5).
        export_json (bool): Se True, exporta os dados para JSON (padrão: False).
    """
    # 1. INICIALIZAÇÃO E MEDIÇÃO DE TEMPO
    start_time = time.perf_counter()
    logging.info("=" * 50)
    logging.info(f"INICIANDO PROCESSO SELETIVO PARA: {candidate_name}")
    logging.info("=" * 50)

    try:
        db = DatabaseManager()

        # 2. PREPARAÇÃO DO BANCO DE DADOS E INSERÇÃO
        if not db.create_tables():
            logging.error("Processo abortado devido a falha na criação das tabelas.")
            return

        candidate_id = db.insert_candidate(candidate_name)
        if candidate_id == -1:
            logging.error("Processo abortado devido a falha ao inserir candidato.")
            return

        fib_sequence = db.generate_fibonacci(30) # Gera os 30 números pedidos
        db.insert_tests(candidate_id, fib_sequence)

        # Validação de consistência (boa prática do seu código original)
        db.validate_constraints()

        # 3. CONSULTAS SQL (ANTES DA EXCLUSÃO)
        logging.info("Executando consultas SQL obrigatórias (antes da exclusão)...")
        stats_before = db.get_stats(candidate_id)
        
        print("\n" + "-"*20 + " RESULTADOS ANTES DA EXCLUSÃO " + "-"*20)
        # a) Listar a sequência Fibonacci
        print("\n[CONSULTA 1] Sequência Fibonacci completa:")
        print(', '.join(map(str, stats_before['sequencia'])))
        
        # b) Listar os 5 maiores números
        print("\n[CONSULTA 2] 5 maiores números da sequência:")
        print(', '.join(map(str, stats_before['top5'])))

        # c) Contar pares e ímpares
        print("\n[CONSULTA 3] Contagem de números pares e ímpares:")
        print(f"   - Pares: {stats_before['pares']}")
        print(f"   - Ímpares: {stats_before['impares']}")
        print("-" * 64 + "\n")

        # 4. OPERAÇÃO DE EXCLUSÃO
        delete_threshold = 5000
        logging.info(f"[OPERAÇÃO] Deletando todos os números maiores que {delete_threshold}...")
        db.delete_large_numbers(threshold=delete_threshold)
        logging.info("Deleção concluída com sucesso.")

        # 5. CONSULTA SQL (APÓS A EXCLUSÃO)
        logging.info("Executando consultas SQL obrigatórias (após a exclusão)...")
        stats_after = db.get_stats(candidate_id)
        
        print("\n" + "-"*20 + " RESULTADOS APÓS A EXCLUSÃO " + "-"*21)
        # d) Listar a sequência Fibonacci novamente
        print(f"\n[CONSULTA 4] Sequência Fibonacci remanescente (números <= {delete_threshold}):")
        print(', '.join(map(str, stats_after['sequencia'])))
        print("-" * 64 + "\n")


    except Exception as e:
        logging.critical(f"Ocorreu um erro fatal durante a execução: {e}")

    finally:
        # 6. FINALIZAÇÃO E RELATÓRIOS
        end_time = time.perf_counter()
        duration = end_time - start_time

        logging.info("=" * 50)
        logging.info("PROCESSO FINALIZADO")
        logging.info(f"Tempo de execução total: {duration:.4f} segundos.")
        logging.info("=" * 50)

        # Gera os relatórios com base nos dados de antes da exclusão, que são mais completos,
        # mas adiciona o tempo total de execução de todo o processo.
        if 'stats_before' in locals():
            logging.info("Gerando relatório em PDF...")
            generate_report(stats_before, 
                            duration, 
                            filename="relatorio.pdf",
                            expected_ratio=expected_ratio, 
                            tolerancia=tolerancia)

            if export_json:
                logging.info("Exportando dados para JSON...")
                export_stats_to_json(stats_before, filename="dados_finais.json")
        else:
            logging.warning("Não foi possível gerar relatórios pois os dados iniciais não foram coletados.")

def test_fibonacci_generation():
    """Testa a geração da sequência Fibonacci
    
    Verifica se os primeiros 10 números gerados correspondem à sequência esperada:
    [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    
    Exibe:
    - ✅ Teste aprovado (se correto)
    - ❌ Falha no teste (com diferenças) se houver erro
    """
    try:
        # 1. Prepara teste
        db = DatabaseManager()      
        # 2. Gera sequência (10 primeiros números)
        sequence = db.generate_fibonacci(10)       
        # 3. Define resultado esperado
        expected = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]       
        # 4. Compara resultados
        assert sequence == expected, f"Esperado {expected}, obtido {sequence}"        
        print("✅ Teste de Fibonacci aprovado!")
        
    except AssertionError as e:
        # 6. Trata falha do teste
        print(f"❌ Falha no teste: {e}")

if __name__ == "__main__":
    """Ponto de entrada principal do sistema de processo seletivo.

    Processamento:
        - Define e interpreta argumentos de linha de comando
        - Roteia para diferentes modos de operação:
            * Execução normal com nome do candidato
            * Modo de testes unitários
            * Exibição de ajuda
    """
    # 1. DEFINIÇÃO DOS ARGUMENTOS
    parser = argparse.ArgumentParser(
        description="Sistema de Processo Seletivo SEFAZ/ES",
        epilog="Desenvolvido para a vaga de programador Python"
    )
    
    # Argumentos principais
    parser.add_argument('--nome', 
                      help="Nome do candidato fictício para simulação completa")
    parser.add_argument('--testar', 
                      action='store_true',
                      help="Executa bateria de testes unitários")
    
    # Argumentos de configuração técnica
    parser.add_argument('--expected_ratio', 
                      type=float, 
                      default=1.618,
                      help="Valor esperado da proporção áurea (default: 1.618)")
    parser.add_argument('--tolerancia',
                      type=float,
                      default=0.5,
                      help="Margem de aceitação para a proporção (default: 0.5)")
    
    # Argumentos de saída
    parser.add_argument('--export_json',
                      action='store_true',
                      help="Gera arquivo JSON com os resultados da análise")
    
    # 2. PROCESSAMENTO DOS ARGUMENTOS
    args = parser.parse_args()
    
    # 3. ROTEAMENTO DA EXECUÇÃO
    if args.testar:
        # Modo teste - validação do sistema
        print("\n[STATUS] Executando testes unitários...")
        test_fibonacci_generation()
        
    elif args.nome:
        # Modo normal - processamento completo
        run_full_process(
            args.nome,
            args.expected_ratio,
            args.tolerancia,
            args.export_json
        )
        
    else:
        # Modo ajuda - exibe instruções
        print("\nModos de operação disponíveis:")
        print("  --nome 'Nome Completo'  : Inicia processo seletivo simulado")
        print("  --testar               : Executa validações internas")
        print("  --expected_ratio FLOAT : Ajusta proporção áurea esperada")
        print("  --tolerancia FLOAT     : Define margem de aceitação")
        print("  --export_json          : Exporta dados para arquivo JSON")
        print("\nExemplo completo:")
        print("  python selecao.py --nome \"Maria Silva\" --tolerancia 0.3 --export_json")