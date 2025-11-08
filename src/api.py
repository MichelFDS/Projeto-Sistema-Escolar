from flask import Flask, jsonify, request
from flask_cors import CORS
from src.database import conectar, listar_alunos, obter_aluno, listar_mensagens, salvar_mensagem

app = Flask(__name__)
# Limitar CORS a localhost; ajuste conforme necessário
CORS(app, origins=["http://localhost", "http://127.0.0.1"], supports_credentials=True)

@app.route('/api/alunos', methods=['GET'])
def api_listar_alunos():
    conn = conectar()
    try:
        rows = listar_alunos(conn)
        return jsonify(rows)
    finally:
        try: conn.close()
        except: pass

@app.route('/api/alunos/<int:matricula>', methods=['GET'])
def api_get_aluno(matricula):
    conn = conectar()
    try:
        aluno = obter_aluno(conn, matricula)
        if not aluno:
            return jsonify({'error': 'Aluno não encontrado'}), 404
        return jsonify(aluno)
    finally:
        try: conn.close()
        except: pass

@app.route('/api/mensagens', methods=['GET'])
def api_listar_mensagens():
    conn = conectar()
    try:
        msgs = listar_mensagens(conn)
        return jsonify(msgs)
    finally:
        try: conn.close()
        except: pass

@app.route('/api/mensagens', methods=['POST'])
def api_enviar_mensagem():
    data = request.get_json() or {}
    usuario = data.get('usuario') or data.get('username')
    texto = data.get('texto') or data.get('mensagem') or data.get('message')
    tipo = data.get('tipo') or data.get('role') or data.get('tipo_usuario') or 'mensagem'
    if not usuario or not texto:
        return jsonify({'error': 'usuario (username) e texto (mensagem) são obrigatórios'}), 400
    conn = conectar()
    try:
        # salvar com o tipo fornecido quando possível (professor/aluno/admin)
        new_id = salvar_mensagem(conn, usuario, tipo, texto)
        return jsonify({'status': 'ok', 'id': new_id}), 201
    finally:
        try: conn.close()
        except: pass

if __name__ == '__main__':
    # Roda por padrão na rede local na porta 5000.
    # Para uso em feira/local LAN recomendamos executar via waitress (mais robusto que o servidor dev).
    import os
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '5000'))
    try:
        from waitress import serve
        print(f"Iniciando API com waitress em {host}:{port}")
        serve(app, host=host, port=port)
    except Exception:
        # fallback para servidor Flask de desenvolvimento
        print(f"waitress não disponível — usando servidor Flask padrão em {host}:{port}")
        app.run(host=host, port=port, debug=False)
