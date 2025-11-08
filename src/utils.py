import os
import hashlib
import secrets
from typing import Tuple
from datetime import datetime

PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 16

def gerar_salt() -> str:
    return secrets.token_hex(SALT_BYTES)

def hash_senha(senha: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt, PBKDF2_ITERATIONS)
    return dk.hex()

def criar_hash_senha(senha: str) -> Tuple[str, str]:
    salt = gerar_salt()
    hashed = hash_senha(senha, salt)
    return salt, hashed

def verificar_senha(senha: str, salt_hex: str, hash_hex: str) -> bool:
    return hash_senha(senha, salt_hex) == hash_hex

def validar_data(data: str) -> bool:
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except Exception:
        return False

def validar_nome(nome: str) -> bool:
    return bool(nome.strip()) and len(nome.strip()) <= 50

def validar_curso(curso: str) -> bool:
    return bool(curso.strip()) and len(curso.strip()) <= 40

# PDF - optional dependency: fpdf2
try:
    from fpdf import FPDF
except Exception:
    FPDF = None

def gerar_boletim_pdf(aluno: dict, caminho_saida: str):
    """Gera um boletim em PDF com visual moderno."""
    if FPDF is None:
        raise RuntimeError("Módulo fpdf não instalado. Rode: pip install fpdf2")

    class PDF(FPDF):
        def header(self):
            # Cabeçalho azul
            self.set_fill_color(43, 107, 230)  # Azul institucional
            self.rect(0, 0, 210, 40, 'F')
            
            # Título em branco
            self.set_font('Arial', 'B', 24)
            self.set_text_color(255, 255, 255)
            self.cell(0, 25, 'Boletim Escolar', align='C', ln=True)
            
            # Subtítulo
            self.set_font('Arial', '', 12)
            self.cell(0, 8, 'Sistema Acadêmico - 2025', align='C', ln=True)

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Espaço após cabeçalho
    pdf.ln(20)
    
    # Dados do aluno em um quadro azul claro
    pdf.set_fill_color(240, 247, 255)  # Azul muito claro
    pdf.rect(10, 50, 190, 50, 'F')
    
    pdf.set_text_color(51, 51, 51)  # Texto escuro
    pdf.set_font('Arial', 'B', 12)
    pdf.set_xy(15, 55)
    pdf.cell(0, 8, 'Dados do Aluno:', ln=True)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_x(15)
    pdf.cell(0, 8, f'Matrícula: {aluno.get("matricula")}', ln=True)
    pdf.set_x(15)
    pdf.cell(0, 8, f'Nome: {aluno.get("nome")}', ln=True)
    pdf.set_x(15)
    pdf.cell(0, 8, f'Curso: {aluno.get("curso")}', ln=True)
    pdf.set_x(15)
    pdf.cell(0, 8, f'Data de Nascimento: {aluno.get("data_nascimento")}', ln=True)
    
    # Notas em cards separados
    pdf.ln(15)
    
    # Função helper para desenhar card de nota
    def desenhar_card_nota(x, y, titulo, nota):
        pdf.set_fill_color(255, 255, 255)  # Fundo branco
        pdf.set_draw_color(43, 107, 230)   # Borda azul
        pdf.rect(x, y, 60, 40, 'DF')
        
        # Título do card
        pdf.set_xy(x, y + 5)
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(43, 107, 230)  # Azul
        pdf.cell(60, 10, titulo, align='C', ln=True)
        
        # Nota
        pdf.set_xy(x, y + 20)
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(51, 51, 51)  # Cinza escuro
        pdf.cell(60, 10, str(nota), align='C')
    
    # Cards de notas lado a lado
    np1 = aluno.get('np1') if aluno.get('np1') is not None else '—'
    np2 = aluno.get('np2') if aluno.get('np2') is not None else '—'
    media = round((aluno.get('np1') + aluno.get('np2'))/2, 1) if aluno.get('np1') is not None and aluno.get('np2') is not None else '—'
    
    desenhar_card_nota(15, 120, 'NP1', np1)
    desenhar_card_nota(85, 120, 'NP2', np2)
    desenhar_card_nota(155, 120, 'Média', media)
    
    # Rodapé com data
    pdf.set_y(-30)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(128, 128, 128)
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 10, f'Gerado em {data_atual}', align='C')

    os.makedirs(os.path.dirname(caminho_saida) or '.', exist_ok=True)
    pdf.output(caminho_saida)