"""
Processo Seletivo SEFAZ/ES - Solução Avançada
Autor: [Seu Nome]
Data: [Data]

Descrição:
Este script implementa uma solução completa para o processo seletivo da SEFAZ/ES, incluindo:
- Criação de banco de dados SQLite com constraints
- Geração de sequência Fibonacci
- Validação de qualidade dos dados
- Relatório PDF profissional com gráficos
- Análise matemática da sequência

Funcionalidades Implementadas:
✅ 1. Criação das tabelas com constraints
✅ 2. Inserção de candidato e números Fibonacci
✅ 3. Validação de dados com sistema de constraints
✅ 4. Consultas SQL para análise dos dados
✅ 5. Geração de relatório PDF com gráficos profissionais
✅ 6. Análise matemática da proporção áurea
✅ 7. Sistema de logging detalhado
✅ 8. Interface de linha de comando (CLI)

Diferenciais Técnicos:
• Gráficos profissionais com matplotlib
• Validação rigorosa de qualidade dos dados
• Análise matemática da sequência Fibonacci
• Relatório PDF com design institucional
• Tratamento de erros robusto
• Documentação completa do código
"""

import sqlite3
import argparse
import logging
from typing import List, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("selecao.log"),
        logging.StreamHandler()
    ]
)

class DatabaseManager:
    """Gerencia todas as operações de banco de dados"""
    
    def __init__(self, db_path: str = 'selecao.db'):
        """
        Inicializa a conexão com o banco de dados
        Args:
            db_path: Caminho para o arquivo do banco SQLite
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        logging.info("Banco de dados conectado")
    
    def create_tables(self) -> bool:
        """
        Cria as tabelas SELECAO_CANDIDATO e SELECAO_TESTE com constraints
        Returns:
            True se bem sucedido, False caso contrário
        """
        try:
            # Tabela de candidatos
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SELECAO_CANDIDATO (
                ID_CANDIDATO INTEGER PRIMARY KEY AUTOINCREMENT,
                NME_CANDIDATO TEXT NOT NULL,
                DAT_INSCRICAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Tabela de testes com constraints
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
            self.conn.commit()
            logging.info("Tabelas criadas com sucesso")
            return True
        except sqlite3.Error as e:
            logging.error(f"Erro na criação de tabelas: {e}")
            return False

    def insert_candidate(self, name: str) -> int:
        """
        Insere um novo candidato na tabela
        Args:
            name: Nome do candidato
        Returns:
            ID do candidato inserido ou -1 em caso de erro
        """
        try:
            self.cursor.execute(
                "INSERT INTO SELECAO_CANDIDATO (NME_CANDIDATO) VALUES (?)",
                (name,)
            )
            self.conn.commit()
            logging.info(f"Candidato '{name}' inserido")
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Erro ao inserir candidato: {e}")
            return -1

    def generate_fibonacci(self, n: int = 30) -> List[int]:
        """
        Gera a sequência Fibonacci de forma eficiente
        Args:
            n: Quantidade de números a gerar
        Returns:
            Lista com os n primeiros números da sequência
        """
        a, b = 0, 1
        sequence = []
        for _ in range(n):
            sequence.append(b)
            a, b = b, a + b
        return sequence

    def insert_tests(self, candidate_id: int, fib_sequence: List[int]):
        """
        Insere os números Fibonacci na tabela de testes
        Args:
            candidate_id: ID do candidato associado
            fib_sequence: Lista de números Fibonacci
        """
        try:
            for num in fib_sequence:
                is_even = 1 if num % 2 == 0 else 0
                is_odd = 1 - is_even
                self.cursor.execute(
                    """INSERT INTO SELECAO_TESTE 
                    (ID_CANDIDATO, NUM_FIBONACCI, NUM_PAR, NUM_IMPAR) 
                    VALUES (?, ?, ?, ?)""",
                    (candidate_id, num, is_even, is_odd)
                )
            self.conn.commit()
            logging.info(f"{len(fib_sequence)} testes inseridos")
        except sqlite3.Error as e:
            logging.error(f"Erro ao inserir testes: {e}")

    def execute_query(self, query: str) -> List[Tuple]:
        """
        Executa uma consulta SQL e retorna os resultados
        Args:
            query: Comando SQL a ser executado
        Returns:
            Lista de tuplas com os resultados
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Erro na consulta: {e}")
            return []

    def delete_large_numbers(self, threshold: int = 5000):
        """
        Remove números maiores que o limite especificado
        Args:
            threshold: Valor limite para remoção
        """
        try:
            self.cursor.execute(
                "DELETE FROM SELECAO_TESTE WHERE NUM_FIBONACCI > ?",
                (threshold,)
            )
            self.conn.commit()
            logging.info(f"Números acima de {threshold} removidos")
        except sqlite3.Error as e:
            logging.error(f"Erro ao deletar registros: {e}")
    
    def get_stats(self) -> dict:
        """
        Obtém estatísticas completas do banco de dados
        Returns:
            Dicionário com todas estatísticas relevantes
        """
        stats = {}
        
        # Total de números
        stats['total'] = self.execute_query("SELECT COUNT(*) FROM SELECAO_TESTE")[0][0]
        
        # Contagem par/ímpar
        count_result = self.execute_query(
            "SELECT SUM(NUM_PAR), SUM(NUM_IMPAR) FROM SELECAO_TESTE"
        )[0]
        stats['pares'] = count_result[0] or 0
        stats['impares'] = count_result[1] or 0
        
        # Sequência Fibonacci completa
        stats['sequencia'] = [row[0] for row in self.execute_query(
            "SELECT NUM_FIBONACCI FROM SELECAO_TESTE ORDER BY NUM_FIBONACCI"
        )]
        
        # Top 5 maiores números
        stats['top5'] = [row[0] for row in self.execute_query(
            "SELECT NUM_FIBONACCI FROM SELECAO_TESTE ORDER BY NUM_FIBONACCI DESC LIMIT 5"
        )]
        
        # Dados do candidato
        stats['candidato'] = self.execute_query(
            "SELECT NME_CANDIDATO, DAT_INSCRICAO FROM SELECAO_CANDIDATO LIMIT 1"
        )[0]
        
        return stats
    
    def validate_constraints(self) -> dict:
        """
        Valida as constraints do banco de dados
        Returns:
            Dicionário com resultados da validação
        """
        try:
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
            
            if any(results.values()):
                logging.warning(f"Problemas nas constraints: {results}")
            else:
                logging.info("Todas as constraints validadas com sucesso!")
            
            return results
            
        except Exception as e:
            logging.error(f"Erro durante validação: {e}")
            return {
                'invalid_par': -1,
                'invalid_impar': -1,
                'inconsistent_parity': -1,
                'null_values': -1
            }

def generate_report(stats: dict, filename: str = "relatorio.pdf"):
    """
    Gera relatório PDF profissional com gráficos e análise
    Args:
        stats: Dicionário com estatísticas dos dados
        filename: Nome do arquivo de saída
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("helvetica", size=10)
        
        # ---- CABEÇALHO INSTITUCIONAL ----
        pdf.set_font_size(14)
        pdf.set_font(style='B')
        pdf.set_fill_color(40, 60, 80)  # Azul institucional
        pdf.set_text_color(255, 255, 255)  # Texto branco
        pdf.cell(0, 15, "SEFAZ/ES - Relatório de Processo Seletivo", 
                new_x="LMARGIN", new_y="NEXT", align='C', fill=True)
        pdf.ln(10)
        
        # Resetar cor do texto
        pdf.set_text_color(0, 0, 0)
        
        # ---- INFORMAÇÕES DO CANDIDATO ----
        pdf.set_font_size(12)
        pdf.set_font(style='B')
        pdf.cell(0, 10, "Dados do Candidato", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(style='')
        pdf.cell(0, 6, f"Nome: {stats['candidato'][0]}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Data de Inscrição: {stats['candidato'][1]}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)
        
        # ---- SEQUÊNCIA FIBONACCI ----
        pdf.set_font(style='B')
        pdf.cell(0, 10, f"Sequência Fibonacci ({len(stats['sequencia'])} números)", 
                new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(style='')
        
        # Formatação da sequência com truncagem se necessário
        fib_str = ', '.join(map(str, stats['sequencia']))
        if len(fib_str) > 150:
            fib_str = fib_str[:150] + '... [truncado]'
        
        pdf.set_draw_color(200, 200, 200)
        pdf.set_fill_color(245, 245, 245)
        pdf.multi_cell(0, 6, fib_str, border=1, fill=True)
        pdf.ln(10)
        
        # ---- TOP 5 MAIORES NÚMEROS ----
        pdf.set_font(style='B')
        pdf.cell(0, 10, "Top 5 Maiores Números", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(style='')
        
        # Tabela formatada
        pdf.set_draw_color(150, 150, 150)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(40, 8, "Posição", border=1, fill=True, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(40, 8, "Valor", border=1, fill=True, align='C', new_x="LMARGIN", new_y="NEXT")
        
        for i, num in enumerate(stats['top5'], 1):
            pdf.cell(40, 8, str(i), border=1, align='C', new_x="RIGHT", new_y="TOP")
            pdf.cell(40, 8, f"{num:,}", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(10)
        
        # ---- ESTATÍSTICAS E GRÁFICOS ----
        pdf.set_font(style='B')
        pdf.cell(0, 10, "Análise Estatística", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(style='')
        
        # Dados para o gráfico de barras
        labels = ['Pares', 'Ímpares']
        values = [stats['pares'], stats['impares']]
        colors = ['#4e79a7', '#f28e2b']  # Azul e laranja profissional
        
        # Criação do gráfico de barras
        plt.figure(figsize=(8, 4))
        bars = plt.bar(labels, values, color=colors)
        plt.title('Distribuição Par/Ímpar na Sequência Fibonacci', pad=15)
        plt.ylabel('Quantidade')
        
        # Adiciona valores nas barras
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.5,
                f'{height} ({height/stats["total"]*100:.1f}%)',
                ha='center',
                va='bottom',
                fontsize=9
            )
        
        plt.tight_layout()
        
        # Salva o gráfico em buffer
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150)
        img_buffer.seek(0)
        
        # Insere o gráfico no PDF
        pdf.image(img_buffer, x=10, w=190)
        plt.close()
        
        # Análise matemática da proporção
        pdf.ln(10)
        pdf.set_font(style='B')
        pdf.cell(0, 10, "Análise Matemática", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(style='')
        
        ratio = stats['impares'] / stats['pares'] if stats['pares'] > 0 else 0
        pdf.cell(0, 6, f"Proporção Ímpares/Pares: {ratio:.3f}", new_x="LMARGIN", new_y="NEXT")
        
        expected_ratio = 1.618  # Proporção áurea aproximada
        pdf.cell(0, 6, f"Proporção Áurea Esperada: *{expected_ratio:.3f}", 
                new_x="LMARGIN", new_y="NEXT")
        
        if abs(ratio - expected_ratio) < 0.5:
            pdf.set_text_color(0, 128, 0)  # Verde para sucesso
            pdf.cell(0, 6, "✓ Proporção dentro do esperado para sequência Fibonacci", 
                    new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_text_color(255, 0, 0)  # Vermelho para alerta
            pdf.cell(0, 6, "& Proporção fora do padrão Fibonacci esperado", 
                    new_x="LMARGIN", new_y="NEXT")
        
        # Reseta cor do texto
        pdf.set_text_color(0, 0, 0)
        
        # ---- RODAPÉ PROFISSIONAL ----
        pdf.ln(15)
        pdf.set_font_size(8)
        pdf.set_font(style='I')
        pdf.cell(0, 5, f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.cell(0, 5, "Secretaria da Fazenda do Espírito Santo - Processo Seletivo", 
                new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.cell(0, 5, "Todos os direitos reservados © 2025", 
                new_x="LMARGIN", new_y="NEXT", align='C')
        
        # Salva o PDF
        pdf.output(filename)
        logging.info(f"Relatório gerado: {filename}")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao gerar relatório: {e}")
        return False

def run_full_process(candidate_name: str):
    """Executa o fluxo completo do processo seletivo"""
    try:
        logging.info("Iniciando processo seletivo")
        db = DatabaseManager()
        
        # Etapa 1: Criação do banco de dados
        if not db.create_tables():
            logging.error("Falha na criação das tabelas. Abortando.")
            return
        
        # Etapa 2: Inserção do candidato
        candidate_id = db.insert_candidate(candidate_name)
        if candidate_id == -1:
            logging.error("Falha ao inserir candidato. Abortando.")
            return
        
        # Etapa 3: Geração e inserção da sequência Fibonacci
        fib_sequence = db.generate_fibonacci(30)
        db.insert_tests(candidate_id, fib_sequence)
        
        # Etapa 4: Validação das constraints
        constraints = db.validate_constraints()
        if any(constraints.values()):
            logging.error("Problemas encontrados nas constraints dos dados")
        else:
            logging.info("Dados validados com sucesso")
        
        # Etapa 5: Coleta de estatísticas para relatório
        stats_before = db.get_stats()
        
        # Etapa 6: Execução das consultas obrigatórias
        print("\n[CONSULTAS OBRIGATÓRIAS]")
        print("Sequência Fibonacci completa:")
        for num in stats_before['sequencia']:
            print(num, end=', ')
        
        print("\n\nTop 5 maiores números:")
        for i, num in enumerate(stats_before['top5'], 1):
            print(f"{i}. {num}")
        
        print("\nContagem Par/Ímpar:")
        print(f"Pares: {stats_before['pares']}")
        print(f"Ímpares: {stats_before['impares']}")
        
        # Etapa 7: Remoção de números grandes
        db.delete_large_numbers(5000)
        
        # Etapa 8: Geração do relatório PDF
        generate_report(stats_before)
        
        logging.info("Processo concluído com sucesso!")
        print(f"\nRelatório gerado: relatorio.pdf")
        
    except Exception as e:
        logging.error(f"Erro fatal no processo: {e}")

def test_fibonacci_generation():
    """Teste unitário para a geração de Fibonacci"""
    try:
        db = DatabaseManager()
        sequence = db.generate_fibonacci(10)
        expected = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        assert sequence == expected, f"Esperado {expected}, obtido {sequence}"
        print("✅ Teste de Fibonacci aprovado!")
    except AssertionError as e:
        print(f"❌ Falha no teste: {e}")

if __name__ == "__main__":
    # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(
        description="Sistema de Processo Seletivo SEFAZ/ES",
        epilog="Desenvolvido para a vaga de programador Python"
    )
    parser.add_argument('--nome', help="Nome do candidato fictício")
    parser.add_argument('--testar', action='store_true', help="Executar testes unitários")
    
    args = parser.parse_args()
    
    # Controle de execução
    if args.testar:
        print("\nExecutando testes unitários...")
        test_fibonacci_generation()
    elif args.nome:
        run_full_process(args.nome)
    else:
        print("Modo de uso:")
        print("  --nome 'Nome Candidato' : Executa o processo completo")
        print("  --testar : Executa testes unitários")
        print("\nExemplo: python selecao.py --nome \"João Silva\"")