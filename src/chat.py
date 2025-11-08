import customtkinter as ctk
import datetime
import tkinter as tk
from tkinter import scrolledtext

from src.database import salvar_mensagem, listar_mensagens
import os
import json
try:
    import requests
except Exception:
    requests = None


class ChatApp:
    """Chat persistente e com interface moderna.

    Uso: ChatApp(parent, conn, usuario)
    - conn: conexão SQLite
    - usuario: dict retornado por autenticar_usuario (username, tipo, matricula_assoc)
    """

    POLL_MS = 2000

    def __init__(self, parent, conn, usuario, api_url: str = None):
        """Se api_url for fornecida (ex: http://192.168.0.10:5000), o chat usará a API
        em vez do acesso direto ao banco (modo LAN/demo)."""
        self.conn = conn
        self.usuario = usuario or {'username': 'anon', 'tipo': 'aluno'}
        self.api_url = api_url or os.environ.get('SISTEMA_API_URL')
        self.api_mode = bool(self.api_url) and requests is not None

        # janela
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Quadro de Mensagens (persistente)")
        self.window.geometry("820x560")
        self.window.minsize(560, 380)
        self.window.transient(parent)
        try:
            self.window.lift()
            self.window.focus_force()
        except Exception:
            pass

        # header
        header = ctk.CTkFrame(self.window)
        header.pack(fill='x', padx=12, pady=(12, 6))
        title = ctk.CTkLabel(header, text="Comunicação - Mural da Turma", font=("Arial", 18, "bold"))
        title.pack(side='left')
        info = ctk.CTkLabel(header, text=f"Usuário: {self.usuario.get('username')}  •  Perfil: {self.usuario.get('tipo')}", font=("Arial", 11))
        info.pack(side='right')

        # main area: messages with scrollbar
        main = ctk.CTkFrame(self.window, fg_color="transparent")
        main.pack(fill='both', expand=True, padx=12, pady=6)

        # Canvas com fundo branco para as mensagens
        self.canvas = tk.Canvas(main, bg='#FFFFFF', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(main, orient='vertical', command=self.canvas.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame para mensagens com fundo branco
        self.messages_frame = ctk.CTkFrame(self.canvas, fg_color="#FFFFFF")
        self.messages_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.messages_frame, anchor='nw')

        # input area com borda
        input_frame = ctk.CTkFrame(self.window, fg_color="#F5F5F5", corner_radius=8)
        input_frame.pack(fill='x', padx=12, pady=(6, 12))
        
        # Campo de mensagem moderno
        self.msg_entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Escreva uma mensagem... (professores: use /atividade para postar atividades)",
            height=40,
            fg_color="transparent",
            border_width=0,
            font=("Segoe UI", 12)
        )
        self.msg_entry.pack(side='left', fill='x', expand=True, padx=(12, 8), pady=6)
        
        # Botão de enviar azul
        self.send_btn = ctk.CTkButton(
            input_frame, 
            text="Enviar", 
            width=100,
            height=32, 
            command=self.send_message, 
            fg_color="#2B6BE6",
            hover_color="#2258C7",
            corner_radius=6,
            font=("Segoe UI", 12)
        )
        self.send_btn.pack(side='right', padx=8, pady=6)
        self.msg_entry.bind('<Return>', lambda e: self.send_message())

        # state
        self.last_id = 0
        self.rendered_ids = set()

        # carregar mensagens (via DB ou HTTP)
        if self.api_mode:
            self.load_messages_http()
        else:
            self.load_messages()

        # polling
        try:
            self.window.after(self.POLL_MS, self.poll_new_messages)
        except Exception:
            pass

    def _scroll_to_bottom(self):
        try:
            self.canvas.yview_moveto(1.0)
        except Exception:
            pass

    def load_messages(self):
        msgs = listar_mensagens(self.conn)
        for m in msgs:
            if m['id'] not in self.rendered_ids:
                self._add_message_widget(m)
                self.last_id = m['id']
        self._scroll_to_bottom()

    def poll_new_messages(self):
        try:
            if self.api_mode:
                new = self._fetch_messages_http()
            else:
                new = listar_mensagens(self.conn, since_id=self.last_id)
        except Exception as e:
            print('Chat: erro ao obter mensagens:', e)
            new = []

        if new:
            for m in new:
                if m['id'] not in self.rendered_ids:
                    self._add_message_widget(m)
                    self.last_id = m['id']
            self._scroll_to_bottom()
        try:
            self.window.after(self.POLL_MS, self.poll_new_messages)
        except Exception:
            pass

    def _add_message_widget(self, m: dict):
        """Cria um widget visual para a mensagem (bolha)."""
        # m: {id, timestamp, username, tipo, mensagem}
        msg_id = m.get('id')
        ts = m.get('timestamp')
        try:
            dt = datetime.datetime.fromisoformat(ts)
            ts_str = dt.strftime('%d/%m %H:%M')
        except Exception:
            ts_str = ts or ''

        username = m.get('username')
        tipo = m.get('tipo')
        text = m.get('mensagem')

        # detect activity posted by professor
        is_activity = False
        display_text = text
        low = (text or '').lower()
        if tipo == 'professor' and (low.startswith('/atividade') or low.startswith('atividade:') or low.startswith('atv:')):
            is_activity = True
            parts = text.split(' ', 1)
            display_text = parts[1].strip() if len(parts) > 1 else text

        # container frame per message
        mframe = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        mframe.pack(fill='x', pady=6, padx=6)

        # Estilos modernos para as mensagens por tipo de usuário
        if is_activity:
            # Atividades em destaque
            bubble_color = '#0055FF'  # Azul vibrante
            text_color = '#FFFFFF'    # Texto branco
            border_color = '#0055FF'
            username_color = '#0055FF'
        elif tipo == 'professor':
            # Professor: Azul
            bubble_color = '#E6F3FF'  # Azul claro
            text_color = '#0066CC'    # Azul médio
            border_color = '#0066CC'
            username_color = '#0066CC'
        elif tipo == 'administrador':
            # Admin: Vermelho
            bubble_color = '#FFF0F0'  # Vermelho bem claro
            text_color = '#CC0000'    # Vermelho
            border_color = '#CC0000'
            username_color = '#CC0000'
        else:
            # Aluno: Verde
            bubble_color = '#F0FFF0'  # Verde bem claro
            text_color = '#008800'    # Verde
            border_color = '#008800'
            username_color = '#008800'

        # Nome do usuário e hora
        hdr = ctk.CTkLabel(
            mframe, 
            text=f"{username}  •  {ts_str}", 
            font=("Segoe UI", 11, "bold"),
            text_color=username_color
        )
        hdr.pack(anchor='w', padx=12, pady=(2, 0))

        # Mensagem em um card moderno
        msg_frame = ctk.CTkFrame(
            mframe,
            fg_color=bubble_color,
            corner_radius=8,
            border_width=1,
            border_color=border_color
        )
        msg_frame.pack(anchor='w', padx=12, pady=(4, 2), fill='x')
        
        bubble = ctk.CTkLabel(
            msg_frame, 
            text=display_text, 
            wraplength=620,
            font=("Segoe UI", 12),
            text_color=text_color,
            justify='left'
        )
        bubble.pack(anchor='w', padx=12, pady=8)

        # Marcador especial para atividades
        if is_activity:
            note = ctk.CTkLabel(
                mframe, 
                text="📝 Nova Atividade Postada", 
                font=("Segoe UI", 11),
                text_color="#2B6BE6"
            )
            note.pack(anchor='w', padx=12, pady=(0, 4))

        self.rendered_ids.add(msg_id)

    def send_message(self):
        message = (self.msg_entry.get() or '').strip()
        if not message:
            return
        username = self.usuario.get('username')
        tipo = self.usuario.get('tipo')
        new_id = None
        try:
            if self.api_mode:
                # enviar via HTTP POST
                payload = {'usuario': username, 'texto': message, 'tipo': tipo}
                try:
                    resp = requests.post(f"{self.api_url.rstrip('/')}/api/mensagens", json=payload, timeout=3)
                    if resp.status_code in (200, 201):
                        # não temos o id retornado; será atualizado pelo polling
                        new_id = None
                    else:
                        print('Chat: envio HTTP retornou:', resp.status_code, resp.text)
                except Exception as e:
                    print('Chat: erro ao enviar via API:', e)
                    # fallback local se possível
                    new_id = salvar_mensagem(self.conn, username, tipo, message)
            else:
                # write to DB; salvar_mensagem should commit and return lastrowid
                new_id = salvar_mensagem(self.conn, username, tipo, message)
        except Exception as e:
            # surface minor DB errors to console for debugging
            print("Chat: erro ao salvar mensagem:", e)
        now = datetime.datetime.now().isoformat()
        m = {'id': new_id if new_id is not None else self.last_id + 1, 'timestamp': now, 'username': username, 'tipo': tipo, 'mensagem': message}
        # append visually
        if m['id'] not in self.rendered_ids:
            self._add_message_widget(m)
            self.last_id = m['id']
        try:
            self.msg_entry.delete(0, tk.END)
        except Exception:
            # CTkEntry also supports delete but be defensive
            try:
                self.msg_entry.delete(0, 'end')
            except Exception:
                pass
        self._scroll_to_bottom()

    # ---- HTTP helper methods (quando api_mode == True) ----
    def _fetch_messages_http(self):
        """Busca todas mensagens na API e retorna apenas as novas (com id > last_id)."""
        if not self.api_mode:
            return []
        try:
            resp = requests.get(f"{self.api_url.rstrip('/')}/api/mensagens", timeout=3)
            if resp.status_code != 200:
                print('Chat: erro HTTP ao listar mensagens:', resp.status_code)
                return []
            msgs = resp.json() or []
            # Filtrar por last_id
            new = [m for m in msgs if (m.get('id') or 0) > (self.last_id or 0)]
            # Ordenar por id asc
            new.sort(key=lambda x: x.get('id') or 0)
            return new
        except Exception as e:
            print('Chat: exceção _fetch_messages_http:', e)
            return []

    def load_messages_http(self):
        msgs = self._fetch_messages_http()
        for m in msgs:
            if m['id'] not in self.rendered_ids:
                self._add_message_widget(m)
                self.last_id = m['id']
        self._scroll_to_bottom()

