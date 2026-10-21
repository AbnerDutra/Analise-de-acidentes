from collections.abc import Callable
from tkinter import ttk


class TelaLocais(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Notebook,
        *,
        on_create: Callable[[], None],
        on_edit: Callable[[], None],
        on_delete: Callable[[], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__(parent, padding=14)
        parent.add(self, text="Locais")

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Button(
            toolbar,
            text="Novo",
            style="Action.TButton",
            command=on_create,
        ).pack(side="left")
        ttk.Button(
            toolbar,
            text="Editar selecionado",
            style="Action.TButton",
            command=on_edit,
        ).pack(side="left", padx=7)
        ttk.Button(
            toolbar,
            text="Excluir selecionado",
            style="Action.TButton",
            command=on_delete,
        ).pack(side="left")
        ttk.Button(
            toolbar,
            text="Atualizar lista",
            style="Action.TButton",
            command=on_refresh,
        ).pack(side="right")

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True)
        columns = (
            ("idlocal", "ID", 65),
            ("estado", "Estado", 100),
            ("cidade", "Cidade", 170),
            ("bairro", "Bairro", 150),
            ("rua", "Endereço", 280),
        )
        self.tree = ttk.Treeview(
            table_frame,
            columns=tuple(column[0] for column in columns),
            show="headings",
            selectmode="browse",
        )
        for key, label, width in columns:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, minwidth=55, anchor="w")

        vertical = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        horizontal = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
        )
        self.tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.bind(
            "<Double-1>",
            lambda event: on_edit() if event.widget is self.tree else None,
        )