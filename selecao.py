import sqlite3
import argparse
import logging
from typing import List, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
import numpy as np
from io import BytesIO

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


    #Função para validação das constraints     
    def validate_constraints(self):
        """Valida as constraints do banco de dados e retorna dicionário padronizado"""
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
            
    def get_stats(self):
        """Obtém estatísticas completas do banco de dados"""
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
        
        # Top 5 maiores
        stats['top5'] = [row[0] for row in self.execute_query(
            "SELECT NUM_FIBONACCI FROM SELECAO_TESTE ORDER BY NUM_FIBONACCI DESC LIMIT 5"
        )]
        
        # Dados do candidato
        stats['candidato'] = self.execute_query(
            "SELECT NME_CANDIDATO, DAT_INSCRICAO FROM SELECAO_CANDIDATO LIMIT 1"
        )[0]
        
        return stats

def generate_report(stats: dict, filename: str = "relatorio.pdf"):
    """Gera relatório PDF com gráficos profissionais"""
 

    try:
                # Validação inicial (modificada)
        db = DatabaseManager()
        constraints = db.validate_constraints()
        
        if constraints['inconsistent_parity'] > 0:  # Note a chave atualizada
            logging.warning(f"Dados inconsistentes encontrados: {constraints['inconsistent_parity']} registros")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("helvetica", size=12)
        
        # ---- CABEÇALHO ----
        pdf.set_font_size(14)
        pdf.set_font(style='B')
        pdf.set_fill_color(53, 85, 107)  # Azul profissional
        pdf.set_text_color(255, 255, 255)  # Texto branco
        pdf.cell(0, 15, "Relatório do Processo Seletivo - SEFAZ/ES", 
                new_x="LMARGIN", new_y="NEXT", align='C', fill=True)
        pdf.ln(10)
        
        # Resetar cor do texto
        pdf.set_text_color(0, 0, 0)
        
        # ---- INFORMAÇÕES BÁSICAS ----
        pdf.set_font_size(10)
        pdf.set_font(style='B')
        pdf.cell(0, 10, f"Nome do Candidato: {stats['candidato'][0]}", new_x="LMARGIN", new_y="NEXT")

        
        # ---- SEQUÊNCIA FIBONACCI ----
        pdf.set_font_size(10)
        pdf.set_font(style='B')
        # CORREÇÃO: Removido o parêntese extra
        pdf.cell(0, 10, f"Sequência Fibonacci ({len(stats['sequencia'])} números):", 
                new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(style='')
        pdf.set_font_size(10)
        
        # Formatando a sequência para caber no PDF
        fib_str = ', '.join(map(str, stats['sequencia']))
        if len(fib_str) > 150:  # Se for muito longo, truncar
            fib_str = fib_str[:150] + '...'
        
        pdf.set_draw_color(200, 200, 200)
        pdf.set_fill_color(245, 245, 245)
        pdf.multi_cell(0, 7, fib_str, border=1, fill=True)
        pdf.ln(10)
        
        # ---- TOP 5 MAIORES NÚMEROS ----
        pdf.set_font_size(10)
        pdf.set_font(style='B')
        pdf.cell(0, 10, "Top 5 Maiores Números:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(style='')
        pdf.set_font_size(8)
        
        # Tabela estilizada
        pdf.set_draw_color(150, 150, 150)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(40, 8, "Posição", border=1, fill=True, align='C', new_x="RIGHT", new_y="TOP")
        pdf.cell(40, 8, "Valor", border=1, fill=True, align='C', new_x="LMARGIN", new_y="NEXT")
        
        for i, num in enumerate(stats['top5'], 1):
            pdf.cell(40, 8, str(i), border=1, align='C', new_x="RIGHT", new_y="TOP")
            pdf.cell(40, 8, str(num), border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(10)
        
        # ---- ESTATÍSTICAS E GRÁFICOS ----
        pdf.set_font_size(10)
        pdf.set_font(style='B')
        pdf.cell(0, 10, "Estatísticas:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(style='')
        pdf.set_font_size(10)
        
        # Dados para gráfico
        labels = ['Pares', 'Ímpares']
        sizes = [stats['pares'], stats['impares']]
        colors = ['#66c2a5', '#fc8d62']
        
        # Substitua o código do gráfico por:
        plt.figure(figsize=(8,4))
        bars = plt.bar(['Pares', 'Ímpares'], 
                    [stats['pares'], stats['impares']], 
                    color=['#4e79a7', '#f28e2b'])

        plt.title('Distribuição Par/Ímpar na Sequência Fibonacci', pad=20)
        plt.ylabel('Quantidade')

        # Adiciona valores nas barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)} ({height/stats["total"]*100:.1f}%)',
                    ha='center', va='bottom')

        plt.tight_layout()

        # Criar gráfico de pizza
        plt.figure(figsize=(6, 4))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
               shadow=True, startangle=90)
        plt.axis('equal')  # Gráfico circular
        plt.title('Distribuição Par/Ímpar')
        
        # Salvar gráfico em buffer
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150)
        img_buffer.seek(0)
        
        # Inserir gráfico no PDF
        pdf.ln(5)
        pdf.cell(0, 10, "Distribuição de Números:", new_x="LMARGIN", new_y="NEXT")
        pdf.image(img_buffer, x=50, w=100)
        pdf.ln(5)
        
        # Fechar figura para liberar memória
        plt.close()
        
        # Estatísticas textuais
        pdf.set_font_size(8)
        pdf.cell(0, 4, f"Total de Números: {stats['total']}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 4, f"Pares: {stats['pares']} ({stats['pares']/stats['total']*100:.1f}%)", 
               new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 4, f"Ímpares: {stats['impares']} ({stats['impares']/stats['total']*100:.1f}%)", 
               new_x="LMARGIN", new_y="NEXT")
        
        # análise matemática
        pdf.ln(10)
        pdf.set_font(style='B')
        pdf.cell(0, 10, "Análise Matemática:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(style='')

        ratio = stats['impares']/stats['pares']
        pdf.cell(0, 6, f"Proporção Ímpares/Pares: {ratio:.2f} (esperado ~2.618 para Fibonacci)", new_x="LMARGIN", new_y="NEXT")

        if abs(ratio - 2.618) < 0.1:
            pdf.cell(0, 6, "✓ Proporção dentro do esperado", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.cell(0, 6, "* Proporção fora do padrão Fibonacci", new_x="LMARGIN", new_y="NEXT")

        # ---- RODAPÉ ----
        pdf.ln(15)
        pdf.set_font_size(8)
        pdf.set_font(style='I')
        pdf.cell(0, 5, f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.cell(0, 5, "Processo Seletivo SEFAZ/ES - Todos os direitos reservados", 
                new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.output(filename)
        logging.info(f"Relatório gerado: {filename}")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao gerar relatório: {e}")
        return False
    


#Função que executa todo o processo    
def run_full_process(candidate_name: str):
    """Executa fluxo completo do processo seletivo"""
    db = DatabaseManager()
    
      # Validação após inserção (atualizada)
    constraints = db.validate_constraints()
    if constraints['inconsistent_parity'] > 0:  # Chave atualizada aqui
        logging.error(f"Problema de consistência encontrado: {constraints}")
    else:
        logging.info("Dados consistentes!")

    if not db.create_tables():
        return
    
    candidate_id = db.insert_candidate(candidate_name)
    if candidate_id == -1:
        return
    
    fib_sequence = db.generate_fibonacci()
    db.insert_tests(candidate_id, fib_sequence)
    
    # Obter estatísticas ANTES da deleção
    stats_before = db.get_stats()

    # VALIDAÇÃO CRÍTICA (novo código)
    constraints = db.validate_constraints()
    if any(constraints.values()):
        logging.error(f"Problemas nas constraints: {constraints}")
    else:
        logging.info("Todas as constraints validadas com sucesso!")
    
    # 


    # Executar consultas obrigatórias
    print("\nSequência Fibonacci:")
    for row in stats_before['sequencia']:
        print(row)
    
    print("\nTop 5 Maiores:")
    for num in stats_before['top5']:
        print(num)
    
    print("\nContagem Par/Ímpar:")
    print(f"Pares: {stats_before['pares']}, Ímpares: {stats_before['impares']}")
    
    # Deletar números grandes
    db.delete_large_numbers(5000)
    
    # Obter estatísticas APÓS deleção
    stats_after = db.get_stats()
    
    # Gerar relatório com estatísticas ANTES da deleção
    generate_report(stats_before)
    
    logging.info("Processo concluído com sucesso!")
    print(f"\nRelatório gerado: relatorio.pdf")

def test_fibonacci_generation():
    """Teste unitário para geração de Fibonacci"""
    db = DatabaseManager()
    sequence = db.generate_fibonacci(10)
    assert sequence == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55], "Sequência Fibonacci incorreta"
    print("✅ Teste de Fibonacci aprovado!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processo Seletivo SEFAZ/ES")
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



