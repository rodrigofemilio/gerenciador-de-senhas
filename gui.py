"""Interface gráfica desktop construída somente com Tkinter."""

import secrets
import string
import tkinter as tk
from tkinter import messagebox, ttk

from cryptography.fernet import InvalidToken

from crypto_utils import descriptografar, gerar_chave_from_senha, gerar_salt, criptografar
from db_manager import (
    adicionar_senha,
    atualizar_senha,
    buscar_senha,
    deletar_senha,
    inicializar_db,
    listar_servicos,
    obter_salt,
    obter_verificador,
    salvar_salt,
    salvar_verificador,
)

COLORS = {
    "bg": "#F5F7FB", "surface": "#FFFFFF", "nav": "#172033",
    "nav_hover": "#26324A", "primary": "#625BF6", "primary_dark": "#5048E5",
    "text": "#172033", "muted": "#6B7280", "border": "#E5E7EB",
    "success": "#159B73", "danger": "#DC4C64", "soft": "#EEF0FF",
}


class CredentialDialog(tk.Toplevel):
    def __init__(self, parent, title, item=None):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.configure(bg=COLORS["surface"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        body = tk.Frame(self, bg=COLORS["surface"], padx=30, pady=24)
        body.pack(fill="both", expand=True)
        tk.Label(body, text=title, font=("Arial", 18, "bold"), bg=COLORS["surface"],
                 fg=COLORS["text"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 18))

        self.vars = {name: tk.StringVar() for name in ("servico", "usuario", "senha")}
        if item:
            self.vars["servico"].set(item.get("servico", ""))
            self.vars["usuario"].set(item.get("usuario", ""))
            self.vars["senha"].set(item.get("senha", ""))

        for row, (name, label) in enumerate((("servico", "Serviço"), ("usuario", "Usuário ou e-mail"),
                                              ("senha", "Senha")), 1):
            tk.Label(body, text=label, font=("Arial", 10, "bold"), bg=COLORS["surface"],
                     fg=COLORS["text"]).grid(row=row * 2 - 1, column=0, columnspan=2, sticky="w")
            entry = ttk.Entry(body, textvariable=self.vars[name], width=44,
                              show="•" if name == "senha" else "")
            entry.grid(row=row * 2, column=0, columnspan=2, sticky="ew", pady=(5, 14), ipady=7)
            if row == 1:
                entry.focus_set()

        ttk.Button(body, text="Gerar senha forte", command=self._generate).grid(row=7, column=0, sticky="w")
        actions = tk.Frame(body, bg=COLORS["surface"])
        actions.grid(row=8, column=0, columnspan=2, sticky="e", pady=(24, 0))
        ttk.Button(actions, text="Cancelar", command=self.destroy).pack(side="left", padx=6)
        ttk.Button(actions, text="Salvar credencial", style="Primary.TButton",
                   command=self._save).pack(side="left")
        self.bind("<Return>", lambda _event: self._save())
        self.bind("<Escape>", lambda _event: self.destroy())
        self.update_idletasks()
        self.geometry(f"+{parent.winfo_rootx() + 220}+{parent.winfo_rooty() + 100}")

    def _generate(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%&*+-_"
        self.vars["senha"].set("".join(secrets.choice(alphabet) for _ in range(20)))

    def _save(self):
        data = {name: var.get().strip() for name, var in self.vars.items()}
        if not all(data.values()):
            messagebox.showwarning("Campos incompletos", "Preencha serviço, usuário e senha.", parent=self)
            return
        self.result = data
        self.destroy()


class PasswordManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cofre — Gerenciador de Senhas")
        self.geometry("1080x680")
        self.minsize(900, 580)
        self.configure(bg=COLORS["bg"])
        self.key = None
        self.selected_service = None
        self.password_visible = False
        self._styles()
        inicializar_db()
        self.withdraw()
        self.after(50, self._authenticate)

    def _styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TEntry", fieldbackground=COLORS["surface"], bordercolor=COLORS["border"],
                        lightcolor=COLORS["border"], darkcolor=COLORS["border"], padding=5)
        style.configure("TButton", font=("Arial", 10, "bold"), padding=(14, 9),
                        background=COLORS["surface"], foreground=COLORS["text"], borderwidth=1)
        style.map("TButton", background=[("active", COLORS["bg"])])
        style.configure("Primary.TButton", background=COLORS["primary"], foreground="white", borderwidth=0)
        style.map("Primary.TButton", background=[("active", COLORS["primary_dark"])])

    def _authenticate(self):
        salt = obter_salt()
        first_run = salt is None
        dialog = tk.Toplevel(self)
        dialog.title("Acessar o cofre")
        dialog.configure(bg=COLORS["surface"])
        dialog.resizable(False, False)
        dialog.protocol("WM_DELETE_WINDOW", self.destroy)
        dialog.grab_set()
        box = tk.Frame(dialog, bg=COLORS["surface"], padx=42, pady=34)
        box.pack()
        tk.Label(box, text="◆", font=("Arial", 28, "bold"), fg=COLORS["primary"],
                 bg=COLORS["surface"]).pack()
        tk.Label(box, text="Crie sua senha mestra" if first_run else "Bem-vindo de volta",
                 font=("Arial", 20, "bold"), fg=COLORS["text"], bg=COLORS["surface"]).pack(pady=(8, 5))
        tk.Label(box, text=("Ela protege todas as suas credenciais." if first_run else
                            "Digite sua senha mestra para abrir o cofre."),
                 font=("Arial", 10), fg=COLORS["muted"], bg=COLORS["surface"]).pack(pady=(0, 18))
        password = tk.StringVar()
        confirm = tk.StringVar()
        entry = ttk.Entry(box, textvariable=password, show="•", width=36)
        entry.pack(ipady=7, pady=5)
        confirm_entry = None
        if first_run:
            confirm_entry = ttk.Entry(box, textvariable=confirm, show="•", width=36)
            confirm_entry.pack(ipady=7, pady=5)
        feedback = tk.Label(box, text="", font=("Arial", 9), fg=COLORS["danger"], bg=COLORS["surface"])
        feedback.pack(pady=4)

        def unlock():
            value = password.get()
            if not value:
                feedback.config(text="Digite uma senha mestra.")
                return
            if first_run:
                if value != confirm.get():
                    feedback.config(text="As senhas não coincidem.")
                    return
                new_salt = gerar_salt()
                salvar_salt(new_salt)
                self.key = gerar_chave_from_senha(value, new_salt)
                salvar_verificador(criptografar("cofre-valido", self.key))
            else:
                self.key = gerar_chave_from_senha(value, salt)
                services = listar_servicos()
                try:
                    verifier = obter_verificador()
                    if verifier:
                        descriptografar(verifier, self.key)
                    elif services:
                        descriptografar(buscar_senha(services[0])["senha"], self.key)
                        salvar_verificador(criptografar("cofre-valido", self.key))
                except InvalidToken:
                    feedback.config(text="Senha mestra incorreta.")
                    password.set("")
                    entry.focus_set()
                    return
            dialog.destroy()
            self.deiconify()
            self._build_ui()

        ttk.Button(box, text="Criar meu cofre" if first_run else "Abrir cofre",
                   style="Primary.TButton", command=unlock).pack(fill="x", pady=(10, 0))
        dialog.bind("<Return>", lambda _event: unlock())
        dialog.update_idletasks()
        dialog.geometry(f"+{(dialog.winfo_screenwidth()-dialog.winfo_width())//2}+"
                        f"{(dialog.winfo_screenheight()-dialog.winfo_height())//2}")
        entry.focus_set()

    def _build_ui(self):
        nav = tk.Frame(self, bg=COLORS["nav"], width=220)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)
        tk.Label(nav, text="◆  COFRE", font=("Arial", 16, "bold"), fg="white",
                 bg=COLORS["nav"]).pack(anchor="w", padx=25, pady=(28, 42))
        for icon, text in (("▣", "Todos os itens"), ("☆", "Favoritos"), ("◷", "Recentes")):
            row = tk.Frame(nav, bg=COLORS["nav_hover"] if text == "Todos os itens" else COLORS["nav"])
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=f"{icon}   {text}", font=("Arial", 10, "bold"), fg="white",
                     bg=row["bg"], anchor="w", padx=14, pady=12).pack(fill="x")
        tk.Label(nav, text="ARMAZENAMENTO LOCAL\nSuas senhas não saem deste computador.",
                 justify="left", wraplength=170, font=("Arial", 8), fg="#AEB7CA",
                 bg=COLORS["nav"]).pack(side="bottom", anchor="w", padx=25, pady=25)

        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(side="left", fill="both", expand=True)
        header = tk.Frame(content, bg=COLORS["bg"], padx=28, pady=22)
        header.pack(fill="x")
        title = tk.Frame(header, bg=COLORS["bg"])
        title.pack(side="left")
        tk.Label(title, text="Minhas senhas", font=("Arial", 23, "bold"), fg=COLORS["text"],
                 bg=COLORS["bg"]).pack(anchor="w")
        self.count_label = tk.Label(title, text="", font=("Arial", 9), fg=COLORS["muted"], bg=COLORS["bg"])
        self.count_label.pack(anchor="w", pady=(3, 0))
        ttk.Button(header, text="＋ Nova credencial", style="Primary.TButton",
                   command=self._add).pack(side="right")

        tools = tk.Frame(content, bg=COLORS["bg"], padx=28)
        tools.pack(fill="x", pady=(0, 14))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh())
        ttk.Entry(tools, textvariable=self.search_var, width=42).pack(side="left", ipady=6)
        tk.Label(tools, text="  ⌕  Busque por serviço ou usuário", fg=COLORS["muted"],
                 bg=COLORS["bg"], font=("Arial", 9)).pack(side="left")

        area = tk.Frame(content, bg=COLORS["bg"], padx=28, pady=4)
        area.pack(fill="both", expand=True)
        self.list_frame = tk.Frame(area, bg=COLORS["surface"], width=350,
                                   highlightbackground=COLORS["border"], highlightthickness=1)
        self.list_frame.pack(side="left", fill="both", expand=True, padx=(0, 14))
        self.detail = tk.Frame(area, bg=COLORS["surface"], width=360,
                               highlightbackground=COLORS["border"], highlightthickness=1)
        self.detail.pack(side="left", fill="both")
        self.detail.pack_propagate(False)
        self._refresh()

    def _refresh(self):
        for child in self.list_frame.winfo_children():
            child.destroy()
        query = self.search_var.get().lower().strip()
        services = []
        for name in listar_servicos():
            item = buscar_senha(name)
            if not query or query in name.lower() or query in item["usuario"].lower():
                services.append(item)
        label = "credencial protegida" if len(services) == 1 else "credenciais protegidas"
        self.count_label.config(text=f"{len(services)} {label}")
        if not services:
            tk.Label(self.list_frame, text="🔐", font=("Arial", 30), bg=COLORS["surface"]).pack(pady=(90, 10))
            tk.Label(self.list_frame, text="Seu cofre está vazio" if not query else "Nenhum resultado",
                     font=("Arial", 14, "bold"), fg=COLORS["text"], bg=COLORS["surface"]).pack()
            tk.Label(self.list_frame, text="Adicione sua primeira credencial com segurança." if not query else
                     "Tente buscar por outro termo.", font=("Arial", 9), fg=COLORS["muted"],
                     bg=COLORS["surface"]).pack(pady=7)
            self._show_detail(None)
            return
        for item in services:
            row = tk.Frame(self.list_frame, bg=COLORS["surface"], cursor="hand2")
            row.pack(fill="x", padx=12, pady=(10, 0))
            avatar = tk.Label(row, text=item["servico"][:1].upper(), font=("Arial", 13, "bold"),
                              fg=COLORS["primary"], bg=COLORS["soft"], width=3, pady=9)
            avatar.pack(side="left", padx=(0, 12))
            labels = tk.Frame(row, bg=COLORS["surface"])
            labels.pack(side="left", fill="x", expand=True)
            tk.Label(labels, text=item["servico"], font=("Arial", 11, "bold"), fg=COLORS["text"],
                     bg=COLORS["surface"]).pack(anchor="w")
            tk.Label(labels, text=item["usuario"], font=("Arial", 9), fg=COLORS["muted"],
                     bg=COLORS["surface"]).pack(anchor="w", pady=(3, 0))
            tk.Frame(self.list_frame, height=1, bg=COLORS["border"]).pack(fill="x", padx=12, pady=(10, 0))
            for widget in (row, avatar, labels, *labels.winfo_children()):
                widget.bind("<Button-1>", lambda _e, value=item["servico"]: self._select(value))
        if self.selected_service and buscar_senha(self.selected_service):
            self._show_detail(buscar_senha(self.selected_service))
        else:
            self._select(services[0]["servico"])

    def _select(self, service):
        self.selected_service = service
        self.password_visible = False
        self._show_detail(buscar_senha(service))

    def _show_detail(self, item):
        for child in self.detail.winfo_children():
            child.destroy()
        if not item:
            tk.Label(self.detail, text="Selecione uma credencial", font=("Arial", 11),
                     fg=COLORS["muted"], bg=COLORS["surface"]).pack(expand=True)
            return
        box = tk.Frame(self.detail, bg=COLORS["surface"], padx=26, pady=28)
        box.pack(fill="both", expand=True)
        tk.Label(box, text=item["servico"][:1].upper(), font=("Arial", 22, "bold"), width=3,
                 pady=10, fg=COLORS["primary"], bg=COLORS["soft"]).pack(anchor="w")
        tk.Label(box, text=item["servico"], font=("Arial", 20, "bold"), fg=COLORS["text"],
                 bg=COLORS["surface"]).pack(anchor="w", pady=(14, 3))
        tk.Label(box, text="Credencial protegida", font=("Arial", 9), fg=COLORS["success"],
                 bg=COLORS["surface"]).pack(anchor="w", pady=(0, 24))
        self._field(box, "USUÁRIO OU E-MAIL", item["usuario"])
        password = descriptografar(item["senha"], self.key)
        shown = password if self.password_visible else "•" * min(max(len(password), 8), 18)
        self._field(box, "SENHA", shown)
        ttk.Button(box, text="Ocultar senha" if self.password_visible else "Mostrar senha",
                   command=lambda: self._toggle(item)).pack(anchor="w", pady=(0, 24))
        ttk.Button(box, text="Editar credencial", command=lambda: self._edit(item)).pack(fill="x", pady=4)
        ttk.Button(box, text="Excluir", command=lambda: self._delete(item)).pack(fill="x", pady=4)

    def _field(self, parent, label, value):
        tk.Label(parent, text=label, font=("Arial", 8, "bold"), fg=COLORS["muted"],
                 bg=COLORS["surface"]).pack(anchor="w")
        tk.Label(parent, text=value, font=("Arial", 11), fg=COLORS["text"],
                 bg=COLORS["bg"], anchor="w", padx=12, pady=10).pack(fill="x", pady=(5, 17))

    def _toggle(self, item):
        self.password_visible = not self.password_visible
        self._show_detail(item)

    def _add(self):
        dialog = CredentialDialog(self, "Nova credencial")
        self.wait_window(dialog)
        if dialog.result:
            data = dialog.result
            success, message = adicionar_senha(data["servico"], data["usuario"],
                                                criptografar(data["senha"], self.key))
            if success:
                self.selected_service = data["servico"]
                self._refresh()
            else:
                messagebox.showerror("Não foi possível salvar", message, parent=self)

    def _edit(self, item):
        plain = descriptografar(item["senha"], self.key)
        dialog = CredentialDialog(self, "Editar credencial", {**item, "senha": plain})
        self.wait_window(dialog)
        if dialog.result:
            data = dialog.result
            if data["servico"].lower() != item["servico"].lower():
                if buscar_senha(data["servico"]):
                    messagebox.showerror("Não foi possível salvar", "Serviço já cadastrado!", parent=self)
                    return
                deletar_senha(item["servico"])
                adicionar_senha(data["servico"], data["usuario"], criptografar(data["senha"], self.key))
            else:
                atualizar_senha(item["servico"], criptografar(data["senha"], self.key), data["usuario"])
            self.selected_service = data["servico"]
            self._refresh()

    def _delete(self, item):
        if messagebox.askyesno("Excluir credencial", f"Excluir a credencial de {item['servico']}?",
                               icon="warning", parent=self):
            deletar_senha(item["servico"])
            self.selected_service = None
            self._refresh()


def main():
    app = PasswordManagerApp()
    app.mainloop()
