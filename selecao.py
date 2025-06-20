"""
Processo Seletivo SEFAZ-ES - Solução Avançada
Autor: Seu Nome
"""
import sqlite3
import argparse
import logging
from typing import List, Tuple
from datetime import datetime
from fpdf import FPDF  # Requer instalação: pip install fpdf

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    """Gerencia operações de banco de dados"""
    def __init__(self, db_path: str = 'selecao.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        logging.info("Banco de dados conectado")

    def create_tables(self):
        """Cria estrutura do banco de dados"""
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SELECAO_CANDIDATO (
                ID_CANDIDATO INTEGER PRIMARY KEY AUTOINCREMENT,
                NME_CANDIDATO TEXT NOT NULL,
                DAT_INSCRICAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SELECAO_TESTE (
                ID_TESTE INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_CANDIDATO INTEGER,
                NUM_FIBONACCI INTEGER NOT NULL,
                NUM_PAR INTEGER CHECK (NUM_PAR IN (0, 1)),
                NUM_IMPAR INTEGER CHECK (NUM_IMPAR IN (0, 1)),
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
        """Insere novo candidato e retorna ID"""
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
        """Gera sequência Fibonacci de forma eficiente"""
        a, b = 0, 1
        sequence = []
        for _ in range(n):
            sequence.append(b)
            a, b = b, a + b
        return sequence

    def insert_tests(self, candidate_id: int, fib_sequence: List[int]):
        """Insere registros de teste com validação de par/ímpar"""
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
        """Executa consulta SQL e retorna resultados"""
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Erro na consulta: {e}")
            return []

    def delete_large_numbers(self, threshold: int = 5000):
        """Remove números maiores que o limite especificado"""
        try:
            self.cursor.execute(
                "DELETE FROM SELECAO_TESTE WHERE NUM_FIBONACCI > ?",
                (threshold,)
            )
            self.conn.commit()
            logging.info(f"Números acima de {threshold} removidos")
        except sqlite3.Error as e:
            logging.error(f"Erro ao deletar registros: {e}")

    def generate_report(self, filename: str = "relatorio.pdf"):
        """Gera relatório PDF com resultados das consultas"""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("helvetica", size=12)
            
            # ---- CABEÇALHO ----
            pdf.set_font_size(16)
            pdf.set_font(style='B')
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 10, "Relatório do Processo Seletivo - SEFAZ/ES", 
                    new_x="LMARGIN", new_y="NEXT", align='C', fill=True)
            pdf.ln(10)
            
            # ---- INFORMAÇÕES BÁSICAS ----
            candidate = self.execute_query("SELECT NME_CANDIDATO, DAT_INSCRICAO FROM SELECAO_CANDIDATO LIMIT 1")[0]
            
            # ---- SEQUÊNCIA FIBONACCI (DISTINCT) ----
            pdf.set_font_size(12)
            pdf.set_font(style='B')
            pdf.cell(0, 10, "Sequência Fibonacci Única Gerada:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style='')
            pdf.set_font_size(10)
            
            # MODIFICAÇÃO CRÍTICA AQUI - Adicionado DISTINCT e ORDER BY
            fib_data = self.execute_query("SELECT DISTINCT NUM_FIBONACCI FROM SELECAO_TESTE ORDER BY NUM_FIBONACCI")
            fib_str = ', '.join(str(row[0]) for row in fib_data)
            
            pdf.set_draw_color(200, 200, 200)
            pdf.set_fill_color(245, 245, 245)
            pdf.multi_cell(0, 7, fib_str, border=1, fill=True)
            pdf.ln(10)
            
            # ---- TOP 5 NÚMEROS (DISTINCT) ----
            pdf.set_font_size(12)
            pdf.set_font(style='B')
            pdf.cell(0, 10, "Top 5 Maiores Números Únicos:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style='')
            pdf.set_font_size(10)
            
            # MODIFICAÇÃO CRÍTICA AQUI - Adicionado DISTINCT
            top5 = self.execute_query("SELECT DISTINCT NUM_FIBONACCI FROM SELECAO_TESTE ORDER BY NUM_FIBONACCI DESC LIMIT 5")
            
            # Tabela estilizada
            pdf.set_draw_color(150, 150, 150)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(40, 8, "Posição", border=1, fill=True, align='C', new_x="RIGHT", new_y="TOP")
            pdf.cell(40, 8, "Valor", border=1, fill=True, align='C', new_x="LMARGIN", new_y="NEXT")
            
            for i, row in enumerate(top5, 1):
                pdf.cell(40, 8, str(i), border=1, align='C', new_x="RIGHT", new_y="TOP")
                pdf.cell(40, 8, str(row[0]), border=1, align='C', new_x="LMARGIN", new_y="NEXT")
            
            pdf.ln(10)
            
            # ---- [Restante do código permanece igual] ----
            
            pdf.output(filename)
            logging.info(f"Relatório gerado: {filename}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório: {e}")
            return False

# Faz o processo completo, chama métodos de criação das tabelas e criação do fibonacci
def run_full_process(candidate_name: str):
    """Executa fluxo completo do processo seletivo"""
    db = DatabaseManager()
    
    if not db.create_tables():
        return
    
    candidate_id = db.insert_candidate(candidate_name)
    if candidate_id == -1:
        return
    
    fib_sequence = db.generate_fibonacci()
    db.insert_tests(candidate_id, fib_sequence)
    
    # Executa consultas obrigatórias
    queries = [
        ("Sequência Fibonacci", "SELECT NUM_FIBONACCI FROM SELECAO_TESTE"),
        ("Top 5 Maiores", "SELECT NUM_FIBONACCI FROM SELECAO_TESTE ORDER BY NUM_FIBONACCI DESC LIMIT 5"),
        ("Contagem Par/Ímpar", """
        SELECT 
            SUM(NUM_PAR) AS Pares,
            SUM(NUM_IMPAR) AS Impares 
        FROM SELECAO_TESTE""")
    ]
    
    for title, query in queries:
        print(f"\n{title}:")
        results = db.execute_query(query)
        for row in results:
            print(row)
    
    db.delete_large_numbers(5000)
    db.generate_report()
    logging.info("Processo concluído com sucesso!")

def test_fibonacci_generation():
    """Teste unitário para geração de Fibonacci"""
    db = DatabaseManager()
    sequence = db.generate_fibonacci(10)
    assert sequence == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55], "Sequência Fibonacci incorreta"
    print("✅ Teste de Fibonacci aprovado!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processo Seletivo SEFAZ-ES")
    parser.add_argument('--nome', help="Nome do candidato fictício")
    parser.add_argument('--testar', action='store_true', help="Executar testes unitários")
    
    args = parser.parse_args()
    
    if args.testar:
        test_fibonacci_generation()
    elif args.nome:
        run_full_process(args.nome)
    else:
        print("Modo de uso:")
        print("  --nome 'Nome Candidato' : Executa o processo completo")
        print("  --testar : Executa testes unitários")