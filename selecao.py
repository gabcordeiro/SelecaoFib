import sqlite3
import argparse
import logging
from typing import List, Tuple, Dict, Any
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import json

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
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        logging.info("Banco de dados conectado")
    
    def create_tables(self) -> bool:
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
        a, b = 0, 1
        sequence = []
        for _ in range(n):
            sequence.append(b)
            a, b = b, a + b
        return sequence

    def insert_tests(self, candidate_id: int, fib_sequence: List[int]):
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
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Erro na consulta: {e}")
            return []

    def delete_large_numbers(self, threshold: int = 5000):
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
        stats = {}
        stats['total'] = self.execute_query("SELECT COUNT(*) FROM SELECAO_TESTE")[0][0]
        count_result = self.execute_query(
            "SELECT SUM(NUM_PAR), SUM(NUM_IMPAR) FROM SELECAO_TESTE"
        )[0]
        stats['pares'] = count_result[0] or 0
        stats['impares'] = count_result[1] or 0
        stats['sequencia'] = [row[0] for row in self.execute_query(
            "SELECT NUM_FIBONACCI FROM SELECAO_TESTE ORDER BY NUM_FIBONACCI"
        )]
        stats['top5'] = [row[0] for row in self.execute_query(
            "SELECT NUM_FIBONACCI FROM SELECAO_TESTE ORDER BY NUM_FIBONACCI DESC LIMIT 5"
        )]
        stats['candidato'] = self.execute_query(
            "SELECT NME_CANDIDATO, DAT_INSCRICAO FROM SELECAO_CANDIDATO LIMIT 1"
        )[0]
        return stats
    
    def validate_constraints(self) -> dict:
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

def add_section(pdf: FPDF, titulo: str, conteudo: str, font_style=''):
    if titulo.strip():  # Só imprime se o título não estiver vazio ou só com espaços
        pdf.set_font("helvetica", style='B' if font_style == 'B' else '', size=12 if font_style == 'B' else 10)
        pdf.cell(0, 10, titulo, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", style=font_style if font_style != 'B' else '', size=10)
    pdf.multi_cell(0, 6, conteudo)
    pdf.ln(1)


def create_bar_chart(labels: List[str], values: List[int], colors: List[str], total: int) -> BytesIO:
    plt.figure(figsize=(8, 4))
    bars = plt.bar(labels, values, color=colors)
    plt.title('Distribuição Par/Ímpar na Sequência Fibonacci', pad=15)
    plt.ylabel('Quantidade')
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.5,
            f'{height} ({height / total * 100:.1f}%)',
            ha='center',
            va='bottom',
            fontsize=9
        )
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150)
    img_buffer.seek(0)
    plt.close()
    return img_buffer

def create_pie_chart(labels: List[str], sizes: List[int], colors: List[str]) -> BytesIO:
    plt.figure(figsize=(4, 4))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    plt.axis('equal')
    plt.title('Distribuição Par/Ímpar em Gráfico de setores', pad=15)
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150)
    img_buffer.seek(0)
    plt.close()
    return img_buffer

def generate_report(stats: dict, filename: str = "relatorio.pdf", expected_ratio: float = 1.618, tolerancia: float = 0.5):
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
        if len(fib_str) > 150:
            fib_str = fib_str[:150] + '... [truncado]'
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
            pdf.cell(0, 6, "✓ Proporção dentro do esperado para sequência Fibonacci", new_x="LMARGIN", new_y="NEXT")
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
        pdf.cell(0, 5, "Secretaria da Fazenda do Espírito Santo - Processo Seletivo",
                new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.cell(0, 5, "Todos os direitos reservados © 2025",
                new_x="LMARGIN", new_y="NEXT", align='C')

        pdf.output(filename)
        logging.info(f"Relatório gerado: {filename}")
        return True
    # Captura e registra qualquer erro durante a geração do relatório
    except Exception as e:
        logging.error(f"Erro ao gerar relatório: {e}")
        return False

def export_stats_to_json(stats: Dict[str, Any], filename: str = "dados.json"):
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
    try:
        logging.info("Iniciando processo seletivo")
        db = DatabaseManager()

        if not db.create_tables():
            logging.error("Falha na criação das tabelas. Abortando.")
            return

        candidate_id = db.insert_candidate(candidate_name)
        if candidate_id == -1:
            logging.error("Falha ao inserir candidato. Abortando.")
            return

        fib_sequence = db.generate_fibonacci(30)
        db.insert_tests(candidate_id, fib_sequence)

        constraints = db.validate_constraints()
        if any(constraints.values()):
            logging.error("Problemas encontrados nas constraints dos dados")
        else:
            logging.info("Dados validados com sucesso")

        stats_before = db.get_stats()

        # Exibir consultas no console
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

        db.delete_large_numbers(5000)

        generate_report(stats_before, expected_ratio=expected_ratio, tolerancia=tolerancia)

        if export_json:
            export_stats_to_json(stats_before)

        logging.info("Processo concluído com sucesso!")
        print(f"\nRelatório gerado: relatorio.pdf")
        if export_json:
            print(f"Dados exportados para: dados.json")

    except Exception as e:
        logging.error(f"Erro fatal no processo: {e}")

def test_fibonacci_generation():
    try:
        db = DatabaseManager()
        sequence = db.generate_fibonacci(10)
        expected = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        assert sequence == expected, f"Esperado {expected}, obtido {sequence}"
        print("✅ Teste de Fibonacci aprovado!")
    except AssertionError as e:
        print(f"❌ Falha no teste: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sistema de Processo Seletivo SEFAZ/ES",
        epilog="Desenvolvido para a vaga de programador Python"
    )
    parser.add_argument('--nome', help="Nome do candidato fictício")
    parser.add_argument('--testar', action='store_true', help="Executar testes unitários")
    parser.add_argument('--expected_ratio', type=float, default=1.618, help="Proporção áurea esperada")
    parser.add_argument('--tolerancia', type=float, default=0.5, help="Tolerância para aceitação da proporção")
    parser.add_argument('--export_json', action='store_true', help="Exportar dados para JSON")

    args = parser.parse_args()

    if args.testar:
        print("\nExecutando testes unitários...")
        test_fibonacci_generation()
    elif args.nome:
        run_full_process(args.nome, args.expected_ratio, args.tolerancia, args.export_json)
    else:
        print("Modo de uso:")
        print("  --nome 'Nome Candidato' : Executa o processo completo")
        print("  --testar : Executa testes unitários")
        print("  --export_json : Exporta dados para JSON (opcional)")
        print("\nExemplo: python selecao.py --nome \"João Silva\" --export_json")
