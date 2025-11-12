import customtkinter as ctk
from tkinter import messagebox, ttk, Tk
import tkinter as tk
import sqlite3
import os
import datetime
from src.database import listar_alunos, obter_aluno, cadastrar_aluno, atualizar_aluno, excluir_aluno, atualizar_notas, autenticar_usuario, associar_matricula_usuario, autenticar_aluno_por_matricula, autenticar_aluno_por_matricula_e_senha, listar_turmas, criar_turma
from src.utils import validar_data, validar_nome, validar_curso, gerar_boletim_pdf
from src.chat import ChatApp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SistemaGUI:
    def __init__(self, root, conn, theme):
        self.conn = conn
        self.root = root
        self.theme = theme
        self.colors = theme["colors"]
        self.fonts = theme["fonts"]
        self.root.withdraw()
        self.usuario_logado = None
        self.janela_atual = None
        self.abrir_tela_inicial()

    def _center_window(self, janela, largura, altura):
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        pos_x = (largura_tela - largura) // 2
        pos_y = (altura_tela - altura) // 2
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    def sair_app(self):
        """Fecha todas as janelas e encerra o processo do aplicativo."""
        try:
            if self.janela_atual:
                try:
                    self.janela_atual.destroy()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            # Tentativa gentil de destruir a raiz
            try:
                self.root.destroy()
            except Exception:
                pass
        finally:
            # Garante término do processo
            import os
            os._exit(0)

    def abrir_tela_inicial(self):
        # Limpa a janela anterior se existir
        if self.janela_atual is not None:
            try:
                self.janela_atual.destroy()
            except Exception:
                pass
        
        # Cria nova janela
        self.tela_inicial = ctk.CTk()
        self.janela_atual = self.tela_inicial
        self.tela_inicial.title("Sistema Acadêmico")
        largura, altura = 1000, 600
        self._center_window(self.tela_inicial, largura, altura)
        self.tela_inicial.resizable(False, False)
        self.tela_inicial.configure(fg_color=self.colors.BG)
        # Protocolo para fechar a janela corretamente (fecha todo o app)
        self.tela_inicial.protocol("WM_DELETE_WINDOW", self.sair_app)

        # Menu lateral (azul)
        menu_frame = ctk.CTkFrame(self.tela_inicial, fg_color=self.colors.PRIMARY, width=280, corner_radius=0)
        menu_frame.pack(side="left", fill="y")
        menu_frame.pack_propagate(False)
        
        # Logo/Título no menu
        titulo = ctk.CTkLabel(menu_frame, text="Sistema\nAcadêmico", 
                            font=self.fonts.TITLE,
                            text_color=self.colors.TEXT_LIGHT)
        titulo.pack(pady=(50, 30))

        # Área principal (branca)
        main_frame = ctk.CTkFrame(self.tela_inicial, fg_color=self.colors.BG, corner_radius=0)
        main_frame.pack(side="right", fill="both", expand=True)

        # Frame central para botões
        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.pack(expand=True)
        
        welcome = ctk.CTkLabel(center_frame, 
                             text="Bem-vindo!\nSelecione seu tipo de acesso", 
                             font=self.fonts.SUBTITLE,
                             text_color=self.colors.TEXT)
        welcome.pack(pady=(0, 30))

        # Botões de perfil em rosa/roxo
        for tipo in ("aluno", "professor", "administrador"):
            btn = ctk.CTkButton(center_frame, 
                              text=tipo.capitalize(),
                              width=300, 
                              height=60,
                              font=self.fonts.SUBTITLE,
                              fg_color=self.colors.PRIMARY,
                              hover_color=self.colors.HOVER,
                              corner_radius=10,
                              command=lambda t=tipo: self.abrir_tela_login(t))
            btn.pack(pady=12)

        # Copyright no menu lateral
        rodape = ctk.CTkLabel(menu_frame, 
                             text="© 2025 Sistema Acadêmico\nTodos os direitos reservados",
                             font=self.fonts.SMALL,
                             text_color=self.colors.TEXT_LIGHT)
        rodape.pack(side="bottom", pady=20)

        self.tela_inicial.mainloop()

    def abrir_tela_login(self, tipo_usuario):
        # Limpa a janela anterior
        if self.janela_atual is not None:
            try:
                self.janela_atual.destroy()
            except Exception:
                pass

        # Cria nova janela de login
        self.login_janela = ctk.CTk()
        self.janela_atual = self.login_janela
        self.login_janela.title(f"Login - {tipo_usuario.capitalize()}")
        largura, altura = 1000, 600
        self._center_window(self.login_janela, largura, altura)
        self.login_janela.resizable(False, False)
        self.login_janela.configure(fg_color=self.colors.BG)
        # Protocolo para fechar a janela corretamente (volta para inicial)
        self.login_janela.protocol("WM_DELETE_WINDOW", self.voltar_para_inicial)

        # Menu lateral azul
        menu_frame = ctk.CTkFrame(self.login_janela, fg_color=self.colors.PRIMARY, width=280, corner_radius=0)
        menu_frame.pack(side="left", fill="y")
        menu_frame.pack_propagate(False)
        
        # Logo/título no menu
        titulo_menu = ctk.CTkLabel(menu_frame, 
                                 text=f"Login\n{tipo_usuario.capitalize()}", 
                                 font=self.fonts.TITLE,
                                 text_color=self.colors.TEXT_LIGHT)
        titulo_menu.pack(pady=(50, 30))

        # Área principal (branca)
        main_frame = ctk.CTkFrame(self.login_janela, fg_color=self.colors.BG, corner_radius=0)
        main_frame.pack(side="right", fill="both", expand=True)

        # Card de login centralizado
        card = ctk.CTkFrame(main_frame, fg_color=self.colors.BG_SECONDARY, corner_radius=15)
        card.pack(expand=True, padx=50)

        # Título do card
        titulo = ctk.CTkLabel(card, 
                            text=f"Entrar como {tipo_usuario.capitalize()}", 
                            font=self.fonts.SUBTITLE,
                            text_color=self.colors.TEXT)
        titulo.pack(pady=(30, 20))

        # Campos de entrada estilizados
        # Para alunos permitimos login apenas por RA (matrícula). A senha fica opcional/oculta.
        if tipo_usuario == "aluno":
            self.entrada_usuario = ctk.CTkEntry(card,
                                              placeholder_text="Matrícula (RA)",
                                              width=400,
                                              height=45,
                                              font=self.fonts.TEXT,
                                              fg_color=self.colors.BG,
                                              border_color=self.colors.PRIMARY,
                                              corner_radius=8)
            self.entrada_usuario.pack(pady=12)
            # Campo de senha para aluno (agora obrigatório junto com RA)
            self.entrada_senha = ctk.CTkEntry(card,
                                            placeholder_text="Senha",
                                            width=400,
                                            height=45,
                                            font=self.fonts.TEXT,
                                            show="•",
                                            fg_color=self.colors.BG,
                                            border_color=self.colors.PRIMARY,
                                            corner_radius=8)
            self.entrada_senha.pack(pady=12)
            self.entrada_matricula_aluno = None
        else:
            self.entrada_usuario = ctk.CTkEntry(card,
                                              placeholder_text="Usuário",
                                              width=400,
                                              height=45,
                                              font=self.fonts.TEXT,
                                              fg_color=self.colors.BG,
                                              border_color=self.colors.PRIMARY,
                                              corner_radius=8)
            self.entrada_usuario.pack(pady=12)

            self.entrada_senha = ctk.CTkEntry(card,
                                            placeholder_text="Senha",
                                            width=400,
                                            height=45,
                                            font=self.fonts.TEXT,
                                            show="•",
                                            fg_color=self.colors.BG,
                                            border_color=self.colors.PRIMARY,
                                            corner_radius=8)
            self.entrada_senha.pack(pady=12)
            self.entrada_matricula_aluno = None

        # Botões estilizados
        btn_entrar = ctk.CTkButton(card,
                                 text="Entrar",
                                 width=400,
                                 height=45,
                                 font=self.fonts.BUTTON,
                                 fg_color=self.colors.PRIMARY,
                                 hover_color=self.colors.HOVER,
                                 corner_radius=10,
                                 command=lambda: self.fazer_login(tipo_usuario))
        btn_entrar.pack(pady=(20, 10))

        btn_voltar = ctk.CTkButton(card,
                                 text="Voltar",
                                 width=400,
                                 height=45,
                                 font=self.fonts.BUTTON,
                                 fg_color=self.colors.PRIMARY,
                                 hover_color=self.colors.HOVER,
                                 corner_radius=10,
                                 command=self.voltar_para_inicial)
        btn_voltar.pack(pady=(0, 30))

        # Copyright no menu lateral
        rodape = ctk.CTkLabel(menu_frame, 
                             text="© 2025 Sistema Acadêmico\nTodos os direitos reservados",
                             font=self.fonts.SMALL,
                             text_color=self.colors.TEXT_LIGHT)
        rodape.pack(side="bottom", pady=20)

        self.login_janela.mainloop()

    def voltar_para_inicial(self):
        self.login_janela.destroy()
        self.abrir_tela_inicial()

    def fazer_login(self, tipo_usuario):
        usuario = self.entrada_usuario.get().strip()
        senha = self.entrada_senha.get().strip() if self.entrada_senha else None

        # Fluxo para aluno: exigir matrícula (RA) e senha
        if tipo_usuario == 'aluno':
            if not usuario or not usuario.isdigit():
                messagebox.showerror('Erro', 'Informe uma matrícula válida (somente números).')
                return
            if not senha:
                messagebox.showerror('Erro', 'Informe a senha.')
                return
            matricula = int(usuario)
            aluno_auth = autenticar_aluno_por_matricula_e_senha(self.conn, matricula, senha)
            if not aluno_auth:
                messagebox.showerror('Erro', 'Matrícula ou senha incorretos.')
                return
            # Associar usuário logado com a matrícula
            self.usuario_logado = aluno_auth
            messagebox.showinfo('Login', f"Bem-vindo(a), Aluno ({aluno_auth['matricula_assoc']})!")
            self.abrir_menu_principal()
            return

        # Fluxo padrão para professor/administrador usando usuário+senha
        if not usuario or not senha:
            messagebox.showerror('Erro', 'Preencha usuário e senha.')
            return

        auth = autenticar_usuario(self.conn, usuario, senha)
        if auth and auth['tipo'] == tipo_usuario:
            self.usuario_logado = auth
            messagebox.showinfo('Login', f"Bem-vindo(a), {tipo_usuario.capitalize()} ({usuario})!")
            self.abrir_menu_principal()

    def voltar_para_inicial(self):
        # Simplesmente chama abrir_tela_inicial que já cuida da limpeza
        self.abrir_tela_inicial()

    def abrir_menu_principal(self):
        # Limpa a janela anterior
        if self.janela_atual is not None:
            try:
                self.janela_atual.destroy()
            except Exception:
                pass

        # Cria nova janela do menu principal
        self.menu_janela = ctk.CTk()
        self.janela_atual = self.menu_janela
        tipo = self.usuario_logado['tipo']
        self.menu_janela.title(f"Menu Principal - {tipo.capitalize()}")
        largura, altura = 900, 650
        self._center_window(self.menu_janela, largura, altura)
        self.menu_janela.resizable(False, False)
        # Protocolo para fechar a janela corretamente (fecha o app)
        self.menu_janela.protocol("WM_DELETE_WINDOW", self.sair_app)

        titulo = ctk.CTkLabel(self.menu_janela, text=f"Bem-vindo(a), {self.usuario_logado['username']} ({tipo})", font=("Arial", 20, "bold"))
        titulo.pack(pady=20)

        frame = ctk.CTkFrame(self.menu_janela)
        frame.pack(pady=10, padx=20, fill="both", expand=True)

        if tipo == "administrador":
            ctk.CTkButton(frame, text="Cadastrar Aluno", width=220, height=50, command=self.tela_cadastrar_aluno).pack(pady=10)
            ctk.CTkButton(frame, text="Consultar Aluno", width=220, height=50, command=self.tela_consultar_aluno).pack(pady=10)
            ctk.CTkButton(frame, text="Atualizar Aluno", width=220, height=50, command=self.tela_atualizar_aluno).pack(pady=10)
            ctk.CTkButton(frame, text="Excluir Aluno", width=220, height=50, command=self.tela_excluir_aluno).pack(pady=10)
            ctk.CTkButton(frame, text="Listar Todos Alunos", width=220, height=50, command=self.tela_listar_alunos).pack(pady=10)
            ctk.CTkButton(frame, text="Gerenciar Notas", width=220, height=50, command=self.tela_menu_notas).pack(pady=10)
            ctk.CTkButton(frame, text="Chat", width=220, height=50, command=self.abrir_chat).pack(pady=10)
            ctk.CTkButton(frame, text="Gerenciar Turmas", width=220, height=50, command=self.tela_gerenciar_turmas).pack(pady=10)

        elif tipo == "professor":
            ctk.CTkButton(frame, text="Consultar Aluno", width=220, height=50, command=self.tela_consultar_aluno).pack(pady=10)
            ctk.CTkButton(frame, text="Listar Todos Alunos", width=220, height=50, command=self.tela_listar_alunos).pack(pady=10)
            ctk.CTkButton(frame, text="Atualizar Notas", width=220, height=50, command=self.tela_menu_notas).pack(pady=10)
            ctk.CTkButton(frame, text="Chat", width=220, height=50, command=self.abrir_chat).pack(pady=10)

        elif tipo == "aluno":
            ctk.CTkButton(frame, text="Ver meus dados e notas", width=260, height=50, command=self.tela_consultar_proprio).pack(pady=10)
            ctk.CTkButton(frame, text="Chat", width=260, height=50, command=self.abrir_chat).pack(pady=10)

        ctk.CTkButton(self.menu_janela, text="Sair", width=120, height=40, fg_color="#E74C3C", command=self.sair_para_login).pack(side="bottom", pady=12)

        self.menu_janela.mainloop()

    def sair_para_login(self):
        self.voltar_para_inicial()

    def tela_cadastrar_aluno(self):
        win = ctk.CTkToplevel(self.menu_janela)
        win.title("Cadastrar Aluno")
        self._center_window(win, 650, 700)
        win.resizable(False, False)
        win.transient(self.menu_janela)  # Define janela pai
        win.grab_set()  # Torna a janela modal
        win.focus_set()  # Foca a janela

        frame = ctk.CTkFrame(win)
        frame.pack(pady=8, padx=12, fill="both", expand=True)

        # Dados do aluno
        lbl_dados = ctk.CTkLabel(frame, text="Dados do Aluno", font=("Arial", 16, "bold"))
        lbl_dados.pack(pady=10)
        
        ent_matricula = ctk.CTkEntry(frame, placeholder_text="Matrícula (número inteiro)", width=420)
        ent_matricula.pack(pady=8)
        ent_nome = ctk.CTkEntry(frame, placeholder_text="Nome", width=420)
        ent_nome.pack(pady=8)
        ent_curso = ctk.CTkEntry(frame, placeholder_text="Curso", width=420)
        ent_curso.pack(pady=8)
        # Turma (dropdown) - carregar turmas atuais
        turmas_list = listar_turmas(self.conn)
        turma_options = ['Nenhuma'] + [t['nome'] for t in turmas_list] + ['Criar nova...']
        turma_menu = ctk.CTkOptionMenu(frame, values=turma_options)
        turma_menu.set(turma_options[0])
        turma_menu.pack(pady=8)
        ent_nova_turma = ctk.CTkEntry(frame, placeholder_text="Nome da nova turma (se selecionar criar)", width=420)
        # inicialmente escondido (não empacotado até selecionar criar)
        ent_data = ctk.CTkEntry(frame, placeholder_text="Data de Nascimento (DD/MM/YYYY)", width=420)
        ent_data.pack(pady=8)

        # Dados de login
        lbl_login = ctk.CTkLabel(frame, text="Dados de Acesso", font=("Arial", 16, "bold"))
        lbl_login.pack(pady=10)
        
        ent_username = ctk.CTkEntry(frame, placeholder_text="Nome de usuário para login", width=420)
        ent_username.pack(pady=8)
        ent_senha = ctk.CTkEntry(frame, placeholder_text="Senha", width=420, show="*")
        ent_senha.pack(pady=8)
        ent_confirma_senha = ctk.CTkEntry(frame, placeholder_text="Confirme a senha", width=420, show="*")
        ent_confirma_senha.pack(pady=8)

        def cadastrar_aluno_interno():
            try:
                # Obter os dados dos campos
                matricula = ent_matricula.get().strip()
                nome = ent_nome.get().strip()
                curso = ent_curso.get().strip()
                turma_selec = turma_menu.get() if hasattr(turma_menu, 'get') else None
                nova_turma_nome = ent_nova_turma.get().strip() if ent_nova_turma.winfo_ismapped() else None
                data_nasc = ent_data.get().strip()
                username = ent_username.get().strip()
                senha = ent_senha.get()
                confirma_senha = ent_confirma_senha.get()

                # Validação dos dados do aluno
                if not matricula.isdigit():
                    raise ValueError("Matrícula deve ser número inteiro.")
                matricula_int = int(matricula)
                if obter_aluno(self.conn, matricula_int):
                    raise ValueError("Matrícula já cadastrada.")
                if not validar_nome(nome):
                    raise ValueError("Nome inválido (vazio ou >50 chars).")
                if not validar_curso(curso):
                    raise ValueError("Curso inválido (vazio ou >40 chars).")
                if not validar_data(data_nasc):
                    raise ValueError("Data inválida. Use DD/MM/YYYY.")

                # Validação dos dados de login
                if not username:
                    raise ValueError("Nome de usuário é obrigatório.")
                if len(username) < 4:
                    raise ValueError("Nome de usuário deve ter pelo menos 4 caracteres.")
                if not senha:
                    raise ValueError("Senha é obrigatória.")
                if len(senha) < 6:
                    raise ValueError("Senha deve ter pelo menos 6 caracteres.")
                if senha != confirma_senha:
                    raise ValueError("As senhas não coincidem.")

                # Determinar turma_id a salvar
                turma_id = None
                if turma_selec and turma_selec not in ('Nenhuma', None):
                    if turma_selec == 'Criar nova...':
                        if not nova_turma_nome:
                            raise ValueError('Informe o nome da nova turma.')
                        turma_id = criar_turma(self.conn, nova_turma_nome)
                    else:
                        # procurar id pela lista carregada
                        for t in turmas_list:
                            if t['nome'] == turma_selec:
                                turma_id = t['id']
                                break

                # chamar cadastrar com turma_id explicitamente: usamos kwargs to keep signature compatible
                cadastrar_aluno(self.conn, matricula_int, nome, curso, data_nasc, username, senha)
                # se turma_id fornecido, atualizar agora (compatível com versões anteriores)
                if turma_id is not None:
                    atualizar_aluno(self.conn, matricula_int, nome, curso, data_nasc, turma_id)
                messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso com dados de acesso!")
                win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Nome de usuário já existe!")
            except Exception as e:
                messagebox.showerror("Erro ao cadastrar", str(e))

        ctk.CTkButton(frame, text="Salvar", width=180, command=cadastrar_aluno_interno).pack(pady=12)

        # Mostrar/ocultar campo de nova turma quando necessário
        def on_turma_change(value):
            try:
                if value == 'Criar nova...':
                    ent_nova_turma.pack(pady=8)
                else:
                    try:
                        ent_nova_turma.pack_forget()
                    except Exception:
                        pass
            except Exception:
                pass

        try:
            turma_menu.configure(command=on_turma_change)
        except Exception:
            # CTkOptionMenu may not accept command in some versions; fallback using trace if variable available
            try:
                var = turma_menu._variable
                var.trace_add('write', lambda *a: on_turma_change(var.get()))
            except Exception:
                pass

    def tela_gerenciar_turmas(self):
        win = ctk.CTkToplevel(self.menu_janela)
        win.title('Gerenciar Turmas')
        self._center_window(win, 500, 420)
        win.resizable(False, False)
        win.transient(self.menu_janela)
        try:
            win.grab_set()
        except Exception:
            pass

        frame = ctk.CTkFrame(win)
        frame.pack(fill='both', expand=True, padx=12, pady=12)

        lbl = ctk.CTkLabel(frame, text='Turmas Cadastradas', font=self.fonts.SUBTITLE)
        lbl.pack(pady=(6, 8))

        list_container = tk.Frame(frame)
        list_container.pack(fill='both', expand=True)
        cols = ('id', 'nome')
        tree = ttk.Treeview(list_container, columns=cols, show='headings', height=8)
        tree.heading('id', text='ID')
        tree.heading('nome', text='Nome da Turma')
        tree.column('id', width=50, anchor='w')
        tree.column('nome', anchor='w')
        tree.pack(side='left', fill='both', expand=True)
        vsb = ttk.Scrollbar(list_container, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')

        def refresh_tree():
            for i in tree.get_children():
                tree.delete(i)
            for t in listar_turmas(self.conn):
                tree.insert('', 'end', values=(t.get('id'), t.get('nome')))

        refresh_tree()

        # Add new turma
        ent_nova = ctk.CTkEntry(frame, placeholder_text='Nome da nova turma', width=320)
        ent_nova.pack(pady=8)

        def criar_nova():
            nome = ent_nova.get().strip()
            if not nome:
                messagebox.showerror('Erro', 'Informe o nome da turma.')
                return
            try:
                criar_turma(self.conn, nome)
                messagebox.showinfo('Sucesso', 'Turma criada.')
                ent_nova.delete(0, 'end')
                refresh_tree()
            except Exception as e:
                messagebox.showerror('Erro', str(e))

        ctk.CTkButton(frame, text='Criar Turma', width=160, command=criar_nova).pack(pady=6)

    def tela_consultar_aluno(self):
        win = ctk.CTkToplevel(self.menu_janela)
        win.title("Consultar Aluno")
        self._center_window(win, 650, 520)
        win.resizable(False, False)
        win.transient(self.menu_janela)  # Define janela pai
        win.grab_set()  # Torna a janela modal
        win.focus_set()  # Foca a janela

        ent_mat = ctk.CTkEntry(win, placeholder_text="Matrícula", width=420)
        ent_mat.pack(pady=10)

        txt_result = ctk.CTkLabel(win, text="", wraplength=580, justify="left")
        txt_result.pack(pady=12)

        def consultar():
            matricula = ent_mat.get().strip()
            if not matricula.isdigit():
                messagebox.showerror("Erro", "Informe uma matrícula válida (número).")
                return
            aluno = obter_aluno(self.conn, int(matricula))
            if aluno:
                np1 = aluno.get('np1') if aluno.get('np1') is not None else "-"
                np2 = aluno.get('np2') if aluno.get('np2') is not None else "-"
                media = (aluno.get('np1') + aluno.get('np2')) / 2 if aluno.get('np1') is not None and aluno.get('np2') is not None else "-"
                texto = (
                    "- Dados Pessoais -\n"
                    f"Matrícula: {aluno.get('matricula')}\n"
                    f"Nome: {aluno.get('nome')}\n"
                    f"Curso: {aluno.get('curso')}\n"
                    f"Turma: {aluno.get('turma') or '-'}\n"
                    f"Data de Nascimento: {aluno.get('data_nascimento')}\n\n"
                    "- Notas -\n"
                    f"NP1: {np1}\n"
                    f"NP2: {np2}\n"
                    f"Média Final: {media}"
                )
                txt_result.configure(text=texto)
            else:
                txt_result.configure(text="Aluno não encontrado.")

        ctk.CTkButton(win, text="Consultar", width=160, command=consultar).pack(pady=8)

    def tela_consultar_proprio(self):
        matricula_assoc = self.usuario_logado.get('matricula_assoc')
        if not matricula_assoc:
            res = ctk.CTkInputDialog(text="Insira sua matrícula:", title="Informar Matrícula")
            matricula_text = res.get_input() if res else None
            if not matricula_text or not matricula_text.isdigit():
                messagebox.showerror("Erro", "Matrícula inválida.")
                return
            matricula_assoc = int(matricula_text)

        aluno = obter_aluno(self.conn, matricula_assoc)
        if not aluno:
            messagebox.showerror("Erro", "Aluno não encontrado com essa matrícula.")
            return

        win = ctk.CTkToplevel(self.menu_janela)
        win.title("Meus Dados")
        self._center_window(win, 600, 420)
        win.resizable(False, False)
        win.transient(self.menu_janela)
        try:
            win.grab_set()
        except Exception:
            pass
        try:
            win.focus_force()
        except Exception:
            pass

        np1 = aluno.get('np1') if aluno.get('np1') is not None else "-"
        np2 = aluno.get('np2') if aluno.get('np2') is not None else "-"
        media = (aluno.get('np1') + aluno.get('np2')) / 2 if aluno.get('np1') is not None and aluno.get('np2') is not None else "-"

        texto = (
            "- Dados Pessoais -\n"
            f"Matrícula: {aluno.get('matricula')}\n"
            f"Nome: {aluno.get('nome')}\n"
            f"Curso: {aluno.get('curso')}\n"
            f"Turma: {aluno.get('turma') or '-'}\n"
            f"Data de Nascimento: {aluno.get('data_nascimento')}\n\n"
            "- Notas -\n"
            f"NP1: {np1}\n"
            f"NP2: {np2}\n"
            f"Média Final: {media}"
        )
        # Frame principal
        main_frame = ctk.CTkFrame(win, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Card com os dados
        card = ctk.CTkFrame(main_frame, fg_color=self.colors.BG_SECONDARY, corner_radius=10)
        card.pack(expand=True, fill="both")
        
        # Título do card
        titulo = ctk.CTkLabel(card, 
                            text="Meus Dados e Notas",
                            font=self.fonts.SUBTITLE,
                            text_color=self.colors.TEXT)
        titulo.pack(pady=(20, 15))
        
        # Dados em texto
        lbl = ctk.CTkLabel(card, 
                          text=texto, 
                          font=self.fonts.TEXT,
                          justify="left",
                          text_color=self.colors.TEXT)
        lbl.pack(pady=(0, 20))
        
        # Botão para gerar PDF
        btn_pdf = ctk.CTkButton(
            card,
            text="Gerar Boletim PDF",
            font=self.fonts.BUTTON,
            fg_color=self.colors.PRIMARY,
            hover_color=self.colors.HOVER,
            corner_radius=8,
            command=lambda: self.gerar_boletim_aluno(aluno.get('matricula'))
        )
        btn_pdf.pack(pady=(0, 20))

    def tela_atualizar_aluno(self):
        win = ctk.CTkToplevel(self.menu_janela)
        win.title("Atualizar Aluno")
        self._center_window(win, 650, 560)
        win.resizable(False, False)
        win.transient(self.menu_janela)  # Define janela pai
        win.grab_set()  # Torna a janela modal
        win.focus_set()  # Foca a janela

        ent_mat = ctk.CTkEntry(win, placeholder_text="Matrícula do aluno a atualizar", width=420)
        ent_mat.pack(pady=10)
        ent_nome = ctk.CTkEntry(win, placeholder_text="Novo nome (deixe em branco para manter)", width=420)
        ent_nome.pack(pady=6)
        ent_curso = ctk.CTkEntry(win, placeholder_text="Novo curso (deixe em branco para manter)", width=420)
        ent_curso.pack(pady=6)
        ent_data = ctk.CTkEntry(win, placeholder_text="Nova data (DD/MM/YYYY) (deixe em branco para manter)", width=420)
        ent_data.pack(pady=6)

        def buscar_e_atualizar():
            matricula = ent_mat.get().strip()
            if not matricula.isdigit():
                messagebox.showerror("Erro", "Informe uma matrícula válida.")
                return
            matricula = int(matricula)
            aluno = obter_aluno(self.conn, matricula)
            if not aluno:
                messagebox.showerror("Erro", "Aluno não encontrado.")
                return

            novo_nome = ent_nome.get().strip() or aluno.get('nome')
            novo_curso = ent_curso.get().strip() or aluno.get('curso')
            nova_data = ent_data.get().strip() or aluno.get('data_nascimento')

            if not validar_nome(novo_nome) or not validar_curso(novo_curso) or not validar_data(nova_data):
                messagebox.showerror("Erro", "Validação falhou nos campos. Cheque valores e tamanhos.")
                return

            try:
                atualizar_aluno(self.conn, matricula, novo_nome, novo_curso, nova_data)
                messagebox.showinfo("Sucesso", "Dados atualizados com sucesso.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ctk.CTkButton(win, text="Atualizar", command=buscar_e_atualizar, width=180).pack(pady=12)

    def tela_excluir_aluno(self):
        win = ctk.CTkToplevel(self.menu_janela)
        win.title("Excluir Aluno")
        self._center_window(win, 600, 420)
        win.resizable(False, False)
        win.transient(self.menu_janela)  # Define janela pai
        win.grab_set()  # Torna a janela modal
        win.focus_set()  # Foca a janela

        ent_mat = ctk.CTkEntry(win, placeholder_text="Matrícula", width=420)
        ent_mat.pack(pady=8)

        def excluir():
            matricula = ent_mat.get().strip()
            if not matricula.isdigit():
                messagebox.showerror("Erro", "Matrícula inválida.")
                return
            matricula = int(matricula)
            aluno = obter_aluno(self.conn, matricula)
            if not aluno:
                messagebox.showerror("Erro", "Aluno não encontrado.")
                return
            confirma = messagebox.askyesno("Confirmar", f"Confirma exclusão do aluno {aluno.get('nome')} (matrícula {matricula})?")
            if confirma:
                try:
                    excluir_aluno(self.conn, matricula)
                    messagebox.showinfo("Sucesso", "Aluno excluído.")
                    win.destroy()
                except Exception as e:
                    messagebox.showerror("Erro", str(e))

        ctk.CTkButton(win, text="Excluir", width=160, command=excluir).pack(pady=10)

    def tela_listar_alunos(self):
        win = ctk.CTkToplevel(self.menu_janela)
        win.title("Listar Todos Alunos")
        self._center_window(win, 900, 600)
        win.resizable(True, True)
        win.transient(self.menu_janela)  # Define janela pai
        win.grab_set()  # Torna a janela modal
        win.focus_set()  # Foca a janela

        lbl = ctk.CTkLabel(win, text="Lista de Alunos Cadastrados", font=("Arial", 18, "bold"))
        lbl.pack(pady=10)

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=10, pady=8)

        container = tk.Frame(frame)
        container.pack(fill='both', expand=True)
        cols = ("matricula", "nome", "curso", "turma", "nasc", "np1", "np2")
        tree = ttk.Treeview(container, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c.capitalize())
            tree.column(c, anchor='w')
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        for a in listar_alunos(self.conn):
            np1 = a.get('np1') if a.get('np1') is not None else '—'
            np2 = a.get('np2') if a.get('np2') is not None else '—'
            tree.insert('', 'end', values=(a.get('matricula'), a.get('nome'), a.get('curso'), a.get('turma') or '-', a.get('data_nascimento'), np1, np2))

    def tela_menu_notas(self):
        win = ctk.CTkToplevel(self.menu_janela)
        win.title("Menu de Notas")
        self._center_window(win, 600, 420)
        win.resizable(False, False)
        win.transient(self.menu_janela)  # Define janela pai
        win.grab_set()  # Torna a janela modal
        win.focus_set()  # Foca a janela

        ctk.CTkButton(win, text="Adicionar/Atualizar notas do aluno", width=300, height=45, command=self.tela_atualizar_notas).pack(pady=12)
        ctk.CTkButton(win, text="Ver notas de um aluno", width=300, height=45, command=self.tela_ver_notas).pack(pady=6)

    def tela_atualizar_notas(self):
        win = ctk.CTkToplevel(self.menu_janela)
        win.title("Atualizar Notas")
        self._center_window(win, 600, 460)
        win.resizable(False, False)
        win.transient(self.menu_janela)  # Define janela pai
        win.grab_set()  # Torna a janela modal
        win.focus_set()  # Foca a janela

        ent_mat = ctk.CTkEntry(win, placeholder_text="Matrícula do aluno", width=420)
        ent_mat.pack(pady=8)
        ent_np1 = ctk.CTkEntry(win, placeholder_text="Nota NP1 (0 a 10)", width=420)
        ent_np1.pack(pady=8)
        ent_np2 = ctk.CTkEntry(win, placeholder_text="Nota NP2 (0 a 10)", width=420)
        ent_np2.pack(pady=8)

        def salvar_notas():
            matricula = ent_mat.get().strip()
            np1_text = ent_np1.get().strip()
            np2_text = ent_np2.get().strip()
            if not matricula.isdigit():
                messagebox.showerror("Erro", "Matrícula inválida.")
                return
            try:
                np1 = float(np1_text); np2 = float(np2_text)
            except Exception:
                messagebox.showerror("Erro", "Notas devem ser números (0 a 10).")
                return
            if not (0 <= np1 <= 10 and 0 <= np2 <= 10):
                messagebox.showerror("Erro", "Notas devem estar entre 0 e 10.")
                return
            matricula_int = int(matricula)
            if not obter_aluno(self.conn, matricula_int):
                messagebox.showerror("Erro", "Matrícula não encontrada.")
                return
            try:
                atualizar_notas(self.conn, matricula_int, np1, np2)
                messagebox.showinfo("Sucesso", "Notas atualizadas com sucesso.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ctk.CTkButton(win, text="Salvar Notas", width=180, command=salvar_notas).pack(pady=12)

    def tela_ver_notas(self):
        win = ctk.CTkToplevel(self.menu_janela)
        win.title("Ver Notas")
        self._center_window(win, 600, 420)
        win.resizable(False, False)
        win.transient(self.menu_janela)  # Define janela pai
        win.grab_set()  # Torna a janela modal
        win.focus_set()  # Foca a janela

        ent_mat = ctk.CTkEntry(win, placeholder_text="Matrícula", width=420)
        ent_mat.pack(pady=8)

        lbl_res = ctk.CTkLabel(win, text="", wraplength=560, justify="left")
        lbl_res.pack(pady=8)

        def ver():
            matricula = ent_mat.get().strip()
            if not matricula.isdigit():
                messagebox.showerror("Erro", "Matrícula inválida.")
                return
            aluno = obter_aluno(self.conn, int(matricula))
            if not aluno:
                lbl_res.configure(text="Aluno não encontrado.")
                return
            np1 = aluno.get('np1') if aluno.get('np1') is not None else '-'
            np2 = aluno.get('np2') if aluno.get('np2') is not None else '-'
            media = (aluno.get('np1') + aluno.get('np2')) / 2 if aluno.get('np1') is not None and aluno.get('np2') is not None else '-'
            texto = (
                "- Dados do Aluno -\n"
                f"Nome: {aluno.get('nome')}\n"
                f"Curso: {aluno.get('curso')}\n"
                f"Turma: {aluno.get('turma') or '-'}\n\n"
                "- Notas -\n"
                f"NP1: {np1}\n"
                f"NP2: {np2}\n"
                f"Média Final: {media}"
            )
            lbl_res.configure(text=texto)

        ctk.CTkButton(win, text="Ver", width=160, command=ver).pack(pady=6)

    def gerar_boletim_aluno(self, matricula: int):
        """Gera o boletim PDF do aluno na pasta Downloads."""
        aluno = obter_aluno(self.conn, matricula)
        if not aluno:
            messagebox.showerror("Erro", "Aluno não encontrado.")
            return
            
        # Define o nome do arquivo com matrícula e timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"boletim_{matricula}_{timestamp}.pdf"
        
        # Salva na pasta Downloads do usuário
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        caminho_completo = os.path.join(downloads_path, nome_arquivo)
        
        try:
            gerar_boletim_pdf(aluno, caminho_completo)
            messagebox.showinfo(
                "Sucesso", 
                f"Boletim gerado com sucesso!\nSalvo em: Downloads/{nome_arquivo}"
            )
            
            # Tenta abrir o PDF automaticamente
            try:
                os.startfile(caminho_completo)
            except Exception:
                pass  # Se não conseguir abrir, apenas ignora
                
        except Exception as e:
            if "fpdf não instalado" in str(e):
                messagebox.showerror(
                    "Erro",
                    "Para gerar PDFs, instale o pacote fpdf2:\n\npip install fpdf2"
                )
            else:
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")
                
    def gerar_boletim(self, matricula: int, caminho_saida: str):
        """Mantida para compatibilidade."""
        self.gerar_boletim_aluno(matricula)
            
    def abrir_chat(self):
        tipo_usuario = self.usuario_logado['tipo']
        # Chat opera sempre sobre o banco local; parâmetro api_url foi removido
        chat = ChatApp(self.menu_janela, self.conn, self.usuario_logado)
        # Chat agora usa o usuário autenticado (persistente) — não há seletor de papel local

    def _is_float(self, v):
        try:
            float(v)
            return True
        except:
            return False