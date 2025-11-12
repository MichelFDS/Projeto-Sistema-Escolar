Estrutura recomendada e instruções rápidas.

1) Criar e ativar um virtualenv (recomendado):
=== Sistema Acadêmico — instruções rápidas (modo local) ===

Setup e execução (modo desenvolvedor)

1) Criar e ativar um virtualenv (recomendado):

```powershell
python -m venv venv
# Sistema Acadêmico — Instruções (modo local)

Este repositório foi revertido para executar em modo local, sem servidor HTTP/API.
Todas as funcionalidades (cadastro, consulta, notas e chat) operam diretamente no arquivo SQLite local (`bancodados_alunos.db`).

Requisitos mínimos
- Windows 10/11
- Python 3.8+
- Dependências listadas em `requirements.txt`

Instruções rápidas (desenvolvedor)
1) Criar e ativar um virtualenv (recomendado):

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

2) Instalar dependências:

```powershell
python -m pip install -r .\requirements.txt
```

3) Rodar a aplicação (GUI):

```powershell
python -m src.main
```

Boas práticas antes de empacotar
- Pare todas as instâncias do aplicativo antes de gerar o executável com PyInstaller.
- Pause o OneDrive na pasta do projeto durante o empacotamento para evitar arquivos bloqueados.
- Se aparecer "database is locked", reinicie o app e garanta que apenas uma instância esteja escrevendo no DB.

Observações
- O chat e demais funções gravam diretamente no arquivo SQLite local. Se precisar de sincronização em rede será necessário um servidor/API (opção removida a pedido).
- Para gerar boletins em PDF instale `fpdf2` se não estiver incluído: `pip install fpdf2`.

Suporte
Se quiser que eu reative a opção de API no futuro (por exemplo para demonstrar em 2 notebooks), eu posso reverter e orientar passo-a-passo. Por enquanto o código foi revertido para execução local conforme solicitado.

---
