from collections.abc import Callable
import tkinter as tk
from tkinter import ttk


class TelaAnalise(ttk.Frame):
    analysis_options = {
        "Resumo geral": ("analises/resumo", "summary"),
        "Acidentes por região": ("analises/acidentes-por-regiao", "city"),
        "Horários com mais acidentes": (
            "analises/horarios-com-mais-acidentes",
            "list",
        ),
        "Acidentes por condição climática": (
            "analises/acidentes-por-clima",
            "list",
        ),
        "Acidentes por gravidade": (
            "analises/acidentes-por-gravidade",
            "list",
        ),
        "Acidentes por período do dia": (
            "analises/acidentes-por-periodo",
            "list",
        ),
        "Veículos mais envolvidos": (
            "analises/veiculos-mais-envolvidos",
            "list",
        ),
        "Locais com mais ocorrências": (
            "analises/locais-com-mais-ocorrencias",
            "list",
        ),
    }

    def __init__(
        self,
        parent: ttk.Notebook,
        *,
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__(parent, padding=14)
        parent.add(self, text="Análises")
        self.records: dict[str, dict] = {}

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Label(toolbar, text="Relatório:").pack(side="left")
        self.analysis_name = tk.StringVar(self, value="Resumo geral")
        self.analysis_picker = ttk.Combobox(
            toolbar,
            textvariable=self.analysis_name,
            values=tuple(self.analysis_options),
            state="readonly",
            width=33,
        )
        self.analysis_picker.pack(side="left", padx=(8, 14))
        self.analysis_picker.bind(
            "<<ComboboxSelected>>",
            self._toggle_city_filter,
        )

        self.city_filter = ttk.Frame(toolbar)
        ttk.Label(self.city_filter, text="Cidade:").pack(side="left")
        self.city_var = tk.StringVar(self)
        ttk.Entry(
            self.city_filter,
            textvariable=self.city_var,
            width=18,
        ).pack(side="left", padx=(5, 10))
        ttk.Button(
            toolbar,
            text="Executar análise",
            style="Action.TButton",
            command=on_refresh,
        ).pack(side="left")

        self.message = ttk.Label(self, text="")
        self.message.pack(anchor="w", pady=(0, 8))
        result_frame = ttk.Frame(self)
        result_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(result_frame, columns=(), show="headings")
        vertical = ttk.Scrollbar(
            result_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        horizontal = ttk.Scrollbar(
            result_frame,
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
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        self._toggle_city_filter()

    def _toggle_city_filter(self, _event: tk.Event | None = None) -> None:
        if _event is not None and _event.widget is not self.analysis_picker:
            return
        kind = self.analysis_options[self.analysis_name.get()][1]
        if kind == "city":
            self.city_filter.pack(side="left")
        else:
            self.city_filter.pack_forget()