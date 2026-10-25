import tkinter as tk
from tkinter import simpledialog

from .api_client import APIClient, APIError
from .telas.tela_acidentes import MainWindow


def main() -> None:
    root = tk.Tk()
    root.title("PAV - Sistema de Acidentes de Trânsito")
    root.geometry("1180x760")
    root.minsize(900, 600)

    client = APIClient()
    try:
        client.get("openapi.json")
    except APIError:
        api_url = simpledialog.askstring(
            "Endereço da API",
            "Não foi possível conectar à API em http://127.0.0.1:8000.\n"
            "Informe o endereço base da API:",
            initialvalue="http://127.0.0.1:8000",
            parent=root,
        )
        if not api_url:
            root.destroy()
            return
        client = APIClient(api_url)
        try:
            client.get("openapi.json")
        except APIError as error:
            from tkinter import messagebox

            messagebox.showerror("Falha de conexão", str(error), parent=root)
            root.destroy()
            return

    MainWindow(root, client)
    root.mainloop()


if __name__ == "__main__":
    main()