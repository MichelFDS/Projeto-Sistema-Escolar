import os
import sqlite3
import sys
from src.utils import criar_hash_senha, verificar_senha

# When frozen by PyInstaller, use the folder containing the executable as base.
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

DB_NAME = os.path.join(BASE_DIR, 'bancodados_alunos.db')

def conectar():
    # Aumentar timeout para reduzir falhas "database is locked" em cenários
    # com concorrência leve (vários clientes escrevendo em sequência).
    # Também ativamos WAL para melhorar concorrência entre leitores/escritores.
    conn = sqlite3.connect(DB_NAME, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        # pragma pode ser chamado a cada conexão sem problema
        conn.execute('PRAGMA journal_mode=WAL')
    except Exception:
        pass
    return conn

def inicializar_banco():
    conn = conectar()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS alunos (
        matricula INTEGER PRIMARY KEY,
       nome TEXT NOT NULL,
        curso TEXT NOT NULL,
        data_nascimento TEXT NOT NULL,
        np1 REAL CHECK (np1 >= 0 AND np1 <= 10),
        np2 REAL CHECK (np2 >= 0 AND np2 <= 10)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY,
        salt TEXT NOT NULL,
        senha_hash TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK(tipo IN ('aluno', 'professor', 'administrador')),
        matricula_assoc INTEGER,
        FOREIGN KEY(matricula_assoc) REFERENCES alunos(matricula)
    )
    ''')

    # Inserir usuários padrão se não existirem
    cur.execute('SELECT COUNT(*) FROM usuarios')
    if cur.fetchone()[0] == 0:
        defaults = [
            ('admin', 'admin', 'administrador', None),
            ('professor', 'prof123', 'professor', None),
            ('aluno', 'aluno123', 'aluno', None)
        ]
        for username, senha, tipo, assoc in defaults:
            salt, senha_hash = criar_hash_senha(senha)
            cur.execute('INSERT OR IGNORE INTO usuarios (username, salt, senha_hash, tipo, matricula_assoc) VALUES (?, ?, ?, ?, ?)',
                        (username, salt, senha_hash, tipo, assoc))

    conn.commit()

    # criar tabela de mensagens persistentes
    cur.execute('''
    CREATE TABLE IF NOT EXISTS mensagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        username TEXT NOT NULL,
        tipo TEXT NOT NULL,
        mensagem TEXT NOT NULL
    )
    ''')

    conn.commit()
    return conn

# CRUD functions
def cadastrar_aluno(conn, matricula: int, nome: str, curso: str, data_nasc: str, username: str = None, senha: str = None):
    cur = conn.cursor()
    try:
        cur.execute('BEGIN TRANSACTION')
        
        # Cadastra o aluno
        cur.execute('INSERT INTO alunos (matricula, nome, curso, data_nascimento) VALUES (?, ?, ?, ?)',
                    (matricula, nome, curso, data_nasc))
        
        # Se fornecido username e senha, cria conta de usuário
        if username and senha:
            salt, senha_hash = criar_hash_senha(senha)
            cur.execute('INSERT INTO usuarios (username, salt, senha_hash, tipo, matricula_assoc) VALUES (?, ?, ?, ?, ?)',
                        (username, salt, senha_hash, 'aluno', matricula))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def obter_aluno(conn, matricula: int):
    cur = conn.cursor()
    cur.execute('SELECT * FROM alunos WHERE matricula = ?', (matricula,))
    row = cur.fetchone()
    return dict(row) if row else None

def listar_alunos(conn):
    cur = conn.cursor()
    cur.execute('SELECT matricula, nome, curso, data_nascimento, np1, np2 FROM alunos ORDER BY matricula')
    return [dict(r) for r in cur.fetchall()]

def atualizar_aluno(conn, matricula: int, nome: str, curso: str, data_nasc: str):
    cur = conn.cursor()
    cur.execute('UPDATE alunos SET nome = ?, curso = ?, data_nascimento = ? WHERE matricula = ?',
                (nome, curso, data_nasc, matricula))
    conn.commit()

def excluir_aluno(conn, matricula: int):
    cur = conn.cursor()
    cur.execute('DELETE FROM alunos WHERE matricula = ?', (matricula,))
    conn.commit()

def atualizar_notas(conn, matricula: int, np1: float, np2: float):
    cur = conn.cursor()
    cur.execute('UPDATE alunos SET np1 = ?, np2 = ? WHERE matricula = ?', (np1, np2, matricula))
    conn.commit()

def autenticar_usuario(conn, username: str, senha: str):
    cur = conn.cursor()
    cur.execute('SELECT username, salt, senha_hash, tipo, matricula_assoc FROM usuarios WHERE username = ?', (username,))
    r = cur.fetchone()
    if not r:
        return None
    if verificar_senha(senha, r['salt'], r['senha_hash']):
        return {'username': r['username'], 'tipo': r['tipo'], 'matricula_assoc': r['matricula_assoc']}
    return None


def autenticar_aluno_por_matricula(conn, matricula: int):
    """Autentica um aluno apenas pela matrícula (RA). Retorna dicionário de usuário simulado se existir."""
    cur = conn.cursor()
    cur.execute('SELECT matricula, nome FROM alunos WHERE matricula = ?', (matricula,))
    r = cur.fetchone()
    if not r:
        return None
    # Retorna uma estrutura parecida com a de autenticar_usuario
    username = r['nome'] if r['nome'] else str(r['matricula'])
    return {'username': username, 'tipo': 'aluno', 'matricula_assoc': r['matricula']}


def autenticar_aluno_por_matricula_e_senha(conn, matricula: int, senha: str):
    """Autentica um aluno pela matrícula (RA) e senha.

    Procura na tabela `usuarios` um registro com `matricula_assoc = matricula` e tipo 'aluno'
    e valida a senha com o hash/salt. Retorna dicionário de usuário se válido.
    """
    cur = conn.cursor()
    cur.execute('SELECT username, salt, senha_hash, tipo, matricula_assoc FROM usuarios WHERE matricula_assoc = ? AND tipo = ?', (matricula, 'aluno'))
    r = cur.fetchone()
    if not r:
        return None
    if verificar_senha(senha, r['salt'], r['senha_hash']):
        return {'username': r['username'], 'tipo': r['tipo'], 'matricula_assoc': r['matricula_assoc']}
    return None

def associar_matricula_usuario(conn, username: str, matricula: int):
    cur = conn.cursor()
    cur.execute('UPDATE usuarios SET matricula_assoc = ? WHERE username = ?', (matricula, username))
    conn.commit()


def salvar_mensagem(conn, username: str, tipo: str, mensagem: str, timestamp: str = None):
    """Salva uma mensagem persistente no banco."""
    cur = conn.cursor()
    if not timestamp:
        import datetime
        timestamp = datetime.datetime.now().isoformat()
    cur.execute('INSERT INTO mensagens (timestamp, username, tipo, mensagem) VALUES (?, ?, ?, ?)',
                (timestamp, username, tipo, mensagem))
    conn.commit()
    return cur.lastrowid


def listar_mensagens(conn, since_id: int = None, limit: int = None):
    """Retorna lista de mensagens ordenadas por id asc. Se since_id for fornecido, retorna mensagens com id > since_id."""
    cur = conn.cursor()
    if since_id is not None:
        if limit:
            cur.execute('SELECT id, timestamp, username, tipo, mensagem FROM mensagens WHERE id > ? ORDER BY id ASC LIMIT ?', (since_id, limit))
        else:
            cur.execute('SELECT id, timestamp, username, tipo, mensagem FROM mensagens WHERE id > ? ORDER BY id ASC', (since_id,))
    else:
        if limit:
            cur.execute('SELECT id, timestamp, username, tipo, mensagem FROM mensagens ORDER BY id ASC LIMIT ?', (limit,))
        else:
            cur.execute('SELECT id, timestamp, username, tipo, mensagem FROM mensagens ORDER BY id ASC')
    rows = cur.fetchall()
    return [dict(r) for r in rows]
