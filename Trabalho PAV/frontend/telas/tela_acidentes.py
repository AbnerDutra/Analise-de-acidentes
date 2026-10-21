from datetime import date, time
import re
import tkinter as tk
from tkinter import messagebox, ttk

from ..api_client import APIClient, APIError
from .tela_analise import TelaAnalise
from .tela_locais import TelaLocais
from .tela_veiculos import TelaVeiculos


class MainWindow:
    def __init__(self, root: tk.Tk, client: APIClient) -> None:
        self.root = root
        self.client = client
        self.records: dict[str, dict[str, dict]] = {
            "acidentes": {},
            "locais": {},
            "veiculos": {},
        }
        self.analysis_records: dict[str, dict] = {}

        self._configure_style()
        self._build_header()
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.accident_tree = self._build_accident_tab()
        self.local_screen = TelaLocais(
            self.notebook,
            on_create=lambda: self._create_record("locais"),
            on_edit=lambda: self._edit_record("locais"),
            on_delete=lambda: self._delete_record("locais"),
            on_refresh=lambda: self._refresh_resource("locais"),
        )
        self.local_tree = self.local_screen.tree
        self.vehicle_screen = TelaVeiculos(
            self.notebook,
            on_create=lambda: self._create_record("veiculos"),
            on_edit=lambda: self._edit_record("veiculos"),
            on_delete=lambda: self._delete_record("veiculos"),
            on_refresh=lambda: self._refresh_resource("veiculos"),
        )
        self.vehicle_tree = self.vehicle_screen.tree
        self.analysis_screen = TelaAnalise(
            self.notebook,
            on_refresh=self._refresh_analysis,
        )
        self.analysis_options = self.analysis_screen.analysis_options
        self.analysis_name = self.analysis_screen.analysis_name
        self.city_var = self.analysis_screen.city_var
        self.analysis_tree = self.analysis_screen.tree
        self.analysis_message = self.analysis_screen.message
        self.analysis_records = self.analysis_screen.records
        self.refresh_all()

    def _configure_style(self) -> None:
        self.root.configure(bg="#f3f6fb")
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("TNotebook", background="#f3f6fb")
        style.configure("TNotebook.Tab", padding=(16, 9), font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Action.TButton", padding=(10, 6))

    def _build_header(self) -> None:
        header = ttk.Frame(self.root, padding=(20, 18, 20, 12))
        header.pack(fill="x")
        title_group = ttk.Frame(header)
        title_group.pack(side="left")
        ttk.Label(
            title_group,
            text="PAV | Gestão de Acidentes",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            title_group,
            text="Cadastros e análises de ocorrências de trânsito",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        ttk.Button(
            header,
            text="Conectar à API",
            style="Action.TButton",
            command=self._change_api_url,
        ).pack(side="right", anchor="center")

    def _change_api_url(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Conectar à API")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        body = ttk.Frame(dialog, padding=18)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Endereço base da API").pack(anchor="w")
        url_var = tk.StringVar(value=self.client.base_url)
        entry = ttk.Entry(body, textvariable=url_var, width=48)
        entry.pack(fill="x", pady=(6, 14))

        def connect() -> None:
            url = url_var.get().strip().rstrip("/")
            if not url.startswith(("http://", "https://")):
                messagebox.showerror(
                    "Endereço inválido",
                    "Informe um endereço começando com http:// ou https://.",
                    parent=dialog,
                )
                return
            client = APIClient(url)
            try:
                client.get("openapi.json")
            except APIError as error:
                messagebox.showerror("Falha de conexão", str(error), parent=dialog)
                return
            self.client = client
            dialog.destroy()
            self.refresh_all()

        ttk.Button(body, text="Conectar", command=connect).pack(anchor="e")
        entry.focus_set()
        dialog.bind("<Return>", lambda _event: connect())

    def _build_accident_tab(self) -> ttk.Treeview:
        frame = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(frame, text="Acidentes")

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Button(
            toolbar,
            text="Novo",
            style="Action.TButton",
            command=lambda: self._create_record("acidentes"),
        ).pack(side="left")
        ttk.Button(
            toolbar,
            text="Editar selecionado",
            style="Action.TButton",
            command=lambda: self._edit_record("acidentes"),
        ).pack(side="left", padx=7)
        ttk.Button(
            toolbar,
            text="Excluir selecionado",
            style="Action.TButton",
            command=lambda: self._delete_record("acidentes"),
        ).pack(side="left")
        ttk.Button(
            toolbar,
            text="Atualizar lista",
            style="Action.TButton",
            command=lambda: self._refresh_resource("acidentes"),
        ).pack(side="right")
        ttk.Button(
            toolbar,
            text="Excluir todos",
            style="Action.TButton",
            command=self._delete_all_accidents,
        ).pack(side="right", padx=7)

        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", expand=True)
        columns = (
            ("idacidente", "ID", 65),
            ("data", "Data", 100),
            ("hora", "Hora", 75),
            ("vitimas", "Vítimas", 75),
            ("clima", "Clima", 120),
            ("gravidade", "Gravidade", 110),
            ("local", "Local", 260),
            ("qtd_veiculos", "Qtd. veículos", 110),
        )
        column_ids = tuple(column[0] for column in columns)
        tree = ttk.Treeview(
            table_frame,
            columns=column_ids,
            show="headings",
            selectmode="browse",
        )
        for key, label, width in columns:
            tree.heading(key, text=label)
            tree.column(key, width=width, minwidth=55, anchor="w")

        vertical = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=tree.xview,
        )
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        tree.bind("<Double-1>", lambda _event: self._edit_record("acidentes"))
        return tree

    def refresh_all(self) -> None:
        for resource in ("acidentes", "locais", "veiculos"):
            self._refresh_resource(resource)
        self._refresh_analysis()

    def _refresh_resource(self, resource: str, *, show_error: bool = True) -> None:
        try:
            rows = self.client.get(resource)
        except APIError as error:
            if show_error:
                self._show_error(error)
            return

        tree, storage = self._tree_and_storage(resource)
        tree.delete(*tree.get_children())
        storage.clear()
        for row in rows:
            record_id = str(row[self._id_field(resource)])
            storage[str(record_id)] = row
            tree.insert(
                "",
                "end",
                iid=str(record_id),
                values=self._row_values(resource, row),
            )

    def _tree_and_storage(self, resource: str):
        if resource == "acidentes":
            return self.accident_tree, self.records["acidentes"]
        if resource == "locais":
            return self.local_tree, self.records["locais"]
        return self.vehicle_tree, self.records["veiculos"]

    @staticmethod
    def _id_field(resource: str) -> str:
        return {
            "acidentes": "idacidente",
            "locais": "idlocal",
            "veiculos": "idveiculo",
        }[resource]

    @staticmethod
    def _row_values(resource: str, row: dict) -> tuple:
        if resource == "acidentes":
            local = row.get("local") or {}
            location = ", ".join(
                value
                for value in (
                    local.get("rua"),
                    local.get("bairro"),
                    local.get("cidade"),
                    local.get("estado"),
                )
                if value
            )
            return (
                row["idacidente"],
                row["data_acidente"],
                row["hora_acidente"][:5],
                row["qtd_vitimas"],
                row["nome_clima"],
                row["tipo_gravidade"],
                location,
                row["qtd_veiculos"],
            )
        if resource == "locais":
            return (
                row["idlocal"],
                row["estado"],
                row["cidade"],
                row.get("bairro") or "",
                row.get("rua") or "",
            )
        return (row["idveiculo"], row["idacidente"], row["nome_veiculo"])

    def _selected_record(self, resource: str) -> dict | None:
        tree, storage = self._tree_and_storage(resource)
        selection = tree.selection()
        if not selection:
            messagebox.showinfo(
                "Seleção necessária",
                "Selecione um registro na tabela.",
                parent=self.root,
            )
            return None
        return storage.get(selection[0])

    def _create_record(self, resource: str) -> None:
        self._open_record_form(resource)

    def _edit_record(self, resource: str) -> None:
        row = self._selected_record(resource)
        if row is not None:
            self._open_record_form(resource, row)

    def _open_record_form(self, resource: str, row: dict | None = None) -> None:
        editing = row is not None
        labels = {"acidentes": "acidente", "locais": "local", "veiculos": "veículo"}
        window = tk.Toplevel(self.root)
        window.title(f"{'Editar' if editing else 'Novo'} {labels[resource]}")
        window.transient(self.root)
        window.grab_set()
        window.resizable(False, False)
        body = ttk.Frame(window, padding=18)
        body.pack(fill="both", expand=True)
        fields: dict[str, ttk.Entry] = {}

        def add_field(key: str, label: str, value: str = "") -> None:
            ttk.Label(body, text=label).pack(anchor="w", pady=(8, 2))
            entry = ttk.Entry(body, width=48)
            entry.insert(0, value)
            entry.pack(fill="x")
            fields[key] = entry

        if resource == "acidentes":
            local = (row or {}).get("local") or {}
            values = {
                "estado": local.get("estado", ""),
                "cidade": local.get("cidade", ""),
                "bairro": local.get("bairro", ""),
                "rua": local.get("rua", ""),
                "data_acidente": (row or {}).get(
                    "data_acidente",
                    date.today().isoformat(),
                ),
                "hora_acidente": (row or {}).get("hora_acidente", "12:00")[:5],
                "qtd_vitimas": str((row or {}).get("qtd_vitimas", 0)),
                "qtd_veiculos": str(
                    (row or {}).get(
                        "qtd_veiculos",
                        len((row or {}).get("veiculos", [])),
                    )
                ),
                "nome_clima": (row or {}).get("nome_clima", ""),
                "tipo_gravidade": (row or {}).get("tipo_gravidade", ""),
            }
            for key, label in (
                ("estado", "Estado"),
                ("cidade", "Cidade"),
                ("bairro", "Bairro"),
                ("rua", "Endereço / rua"),
                ("data_acidente", "Data (AAAA-MM-DD)"),
                ("hora_acidente", "Hora (HH:MM)"),
                ("qtd_vitimas", "Quantidade de vítimas"),
                ("qtd_veiculos", "Quantidade de veículos envolvidos"),
                ("nome_clima", "Clima"),
                ("tipo_gravidade", "Gravidade"),
            ):
                add_field(key, label, values[key])
            ttk.Label(
                body,
                text="Clima: ensolarado, chuvoso, neblina ou nublado. "
                "Gravidade: leve, moderada, grave ou fatal.",
                wraplength=360,
            ).pack(anchor="w", pady=(8, 0))
        elif resource == "locais":
            add_field("estado", "Estado", (row or {}).get("estado", ""))
            add_field("cidade", "Cidade", (row or {}).get("cidade", ""))
            add_field("bairro", "Bairro", (row or {}).get("bairro", ""))
            add_field("rua", "Endereço / rua", (row or {}).get("rua", ""))
        else:
            add_field("idacidente", "ID do acidente", str((row or {}).get("idacidente", "")))
            add_field(
                "nome_veiculo",
                "Tipo / nome do veículo",
                (row or {}).get("nome_veiculo", ""),
            )

        def save() -> None:
            try:
                payload = self._form_payload(resource, fields)
                if editing:
                    record_id = row[self._id_field(resource)]
                    self.client.put(APIClient.resource_path(resource, record_id), payload)
                else:
                    self.client.post(resource, payload)
            except (ValueError, APIError) as error:
                self._show_error(error, parent=window)
                return
            window.destroy()
            self._refresh_resource(resource)
            if resource == "acidentes":
                self._refresh_resource("veiculos", show_error=False)

        buttons = ttk.Frame(body)
        buttons.pack(fill="x", pady=(16, 0))
        ttk.Button(buttons, text="Cancelar", command=window.destroy).pack(side="right")
        ttk.Button(buttons, text="Salvar", command=save).pack(side="right", padx=(0, 8))
        window.bind("<Return>", lambda _event: save())
        if fields:
            fields[next(iter(fields))].focus_set()

    @staticmethod
    def _form_payload(resource: str, fields: dict[str, ttk.Entry]) -> dict:
        values = {key: entry.get().strip() for key, entry in fields.items()}
        if resource == "locais":
            return {key: values[key] for key in ("estado", "cidade", "bairro", "rua")}
        if resource == "veiculos":
            try:
                accident_id = int(values["idacidente"])
            except ValueError as error:
                raise ValueError("O ID do acidente deve ser um número inteiro.") from error
            if accident_id <= 0:
                raise ValueError("O ID do acidente deve ser maior que zero.")
            return {
                "idacidente": accident_id,
                "nome_veiculo": values["nome_veiculo"],
            }

        try:
            accident_date = date.fromisoformat(values["data_acidente"])
            victims = int(values["qtd_vitimas"])
        except ValueError as error:
            raise ValueError(
                "Informe a data AAAA-MM-DD e a quantidade de vítimas como "
                "número inteiro."
            ) from error
        try:
            vehicle_count = int(values["qtd_veiculos"])
        except ValueError as error:
            raise ValueError(
                "Informe a quantidade de veículos como número inteiro maior que zero."
            ) from error
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", values["hora_acidente"]):
            raise ValueError("A hora deve estar no formato HH:MM, entre 00:00 e 23:59.")
        accident_time = time.fromisoformat(values["hora_acidente"])
        if accident_time.second or accident_time.microsecond:
            raise ValueError("A hora deve estar no formato HH:MM, sem segundos.")
        if victims < 0:
            raise ValueError("A quantidade de vítimas não pode ser negativa.")
        if vehicle_count <= 0:
            raise ValueError(
                "Informe pelo menos um veículo envolvido no acidente."
            )
        return {
            "local": {
                "estado": values["estado"],
                "cidade": values["cidade"],
                "bairro": values["bairro"],
                "rua": values["rua"],
            },
            "data_acidente": accident_date.isoformat(),
            "hora_acidente": accident_time.strftime("%H:%M"),
            "qtd_vitimas": victims,
            "qtd_veiculos": vehicle_count,
            "nome_clima": values["nome_clima"],
            "tipo_gravidade": values["tipo_gravidade"],
        }

    def _delete_record(self, resource: str) -> None:
        row = self._selected_record(resource)
        if row is None:
            return
        record_id = row[self._id_field(resource)]
        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja excluir o registro {record_id}?",
            parent=self.root,
        ):
            return
        try:
            self.client.delete(APIClient.resource_path(resource, record_id))
        except APIError as error:
            self._show_error(error)
            return
        self._refresh_resource(resource)
        if resource == "acidentes":
            self._refresh_resource("veiculos", show_error=False)

    def _delete_all_accidents(self) -> None:
        if not messagebox.askyesno(
            "Excluir todos os acidentes",
            "Esta ação excluirá todos os acidentes, veículos e locais. Continuar?",
            icon="warning",
            parent=self.root,
        ):
            return
        try:
            result = self.client.delete("acidentes")
        except APIError as error:
            self._show_error(error)
            return
        self.refresh_all()
        messagebox.showinfo(
            "Exclusão concluída",
            "Registros excluídos: "
            f"{result.get('acidentes', 0)} acidentes, "
            f"{result.get('veiculos', 0)} veículos e "
            f"{result.get('locais', 0)} locais.",
            parent=self.root,
        )

    def _refresh_analysis(self, *, show_error: bool = True) -> None:
        report, kind = self.analysis_options[self.analysis_name.get()]
        params = None
        if kind == "city" and self.city_var.get().strip():
            params = {"cidade": self.city_var.get().strip()}
        try:
            result = self.client.get(report, params=params)
        except APIError as error:
            if show_error:
                self._show_error(error)
            return

        self.analysis_tree.delete(*self.analysis_tree.get_children())
        self.analysis_records.clear()
        rows = [result] if isinstance(result, dict) else result
        if not rows:
            self.analysis_tree.configure(columns=())
            self.analysis_message.configure(text="Nenhum registro encontrado.")
            return

        columns = tuple(rows[0].keys())
        self.analysis_tree.configure(columns=columns, show="headings")
        for column in columns:
            self.analysis_tree.heading(column, text=column.replace("_", " ").title())
            self.analysis_tree.column(column, width=160, minwidth=80, anchor="w")
        for index, record in enumerate(rows):
            record_id = str(index)
            self.analysis_records[record_id] = record
            self.analysis_tree.insert(
                "",
                "end",
                iid=record_id,
                values=tuple(self._display_value(value) for value in record.values()),
            )
        self.analysis_message.configure(
            text=f"{len(rows)} resultado(s) — {self.analysis_name.get()}."
        )

    @staticmethod
    def _display_value(value) -> str:
        if isinstance(value, dict):
            return ", ".join(str(part) for part in value.values())
        if isinstance(value, list):
            return ", ".join(str(part) for part in value)
        return "" if value is None else str(value)

    @staticmethod
    def _show_error(error: Exception, parent: tk.Misc | None = None) -> None:
        messagebox.showerror("Erro", str(error), parent=parent)
