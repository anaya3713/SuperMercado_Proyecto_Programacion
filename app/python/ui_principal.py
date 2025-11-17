import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# funciones que abrirán otras ventanas; import local al hacer clic para evitar cargas innecesarias

def run_app():
    root = tk.Tk()
    root.title('SuperMercado - Principal')
    root.geometry('360x220')

    frame = ttk.Frame(root, padding=16)
    frame.pack(fill='both', expand=True)

    label = ttk.Label(frame, text='Panel Principal', font=('Segoe UI', 14))
    label.pack(pady=(0, 12))

    btn_contabilidad = ttk.Button(frame, text='Contabilidad', width=24, command=lambda: open_contabilidad(root))
    btn_contabilidad.pack(pady=6)

    btn_inventario = ttk.Button(frame, text='Inventario', width=24, command=lambda: open_inventario(root))
    btn_inventario.pack(pady=6)

    btn_caja = ttk.Button(frame, text='Caja', width=24, command=lambda: open_caja(root))
    btn_caja.pack(pady=6)

    root.mainloop()


def open_contabilidad(parent):
    try:
        import ui_contabilidad
        ui_contabilidad.open_contabilidad(parent)
    except Exception as e:
        messagebox.showerror('Error', f'No se pudo abrir contabilidad:\n{e}')


def open_inventario(parent):
    try:
        import ui_inventario
        ui_inventario.open_inventario(parent)
    except Exception as e:
        messagebox.showerror('Error', f'No se pudo abrir inventario:\n{e}')


def open_caja(parent):
    try:
        import ui_caja
        ui_caja.open_caja(parent)
    except Exception as e:
        messagebox.showerror('Error', f'No se pudo abrir caja:\n{e}')


if __name__ == '__main__':
    run_app()
