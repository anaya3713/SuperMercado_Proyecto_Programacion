import tkinter as tk
from tkinter import ttk, messagebox

import Conexion

# try importing matplotlib for plotting; if missing, we'll show an error when user tries to plot
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    _HAS_MATPLOTLIB = True
except Exception:
    _HAS_MATPLOTLIB = False


def open_contabilidad(parent):
    win = tk.Toplevel(parent)
    win.title('Contabilidad')
    win.geometry('900x560')

    frame = ttk.Frame(win, padding=10)
    frame.pack(fill='both', expand=True)

    top = ttk.Frame(frame)
    top.pack(fill='x', pady=(0,8))

    ttk.Label(top, text='Año (opcional):').pack(side='left')
    year_var = tk.StringVar()
    ttk.Entry(top, width=8, textvariable=year_var).pack(side='left', padx=6)

    btn = ttk.Button(top, text='Cargar', command=lambda: cargar())
    btn.pack(side='left', padx=6)

    # area de texto para detalle
    text = tk.Text(frame, wrap='none', height=12)
    text.pack(fill='x', expand=False)

    # marco para la gráfica
    plot_frame = ttk.Frame(frame)
    plot_frame.pack(fill='both', expand=True, pady=(8,0))

    # referencia al canvas actual para poder borrarlo
    canvas_holder = {'canvas': None}

    def cargar():
        try:
            año = year_var.get().strip()
            año_val = int(año) if año else None
            datos = Conexion.contabilidad(año_val)
            text.delete('1.0', tk.END)
            # limpiar plot frame
            for w in plot_frame.winfo_children():
                w.destroy()
            if not datos:
                text.insert(tk.END, 'No hay datos o ocurrió un error.')
                return

            # mostrar texto resumen por mes
            for row in datos:
                text.insert(tk.END, f"Mes: {row['mes']}\n")
                text.insert(tk.END, f"  Ingresos: {row['total_ingresos']:.2f}\n")
                text.insert(tk.END, f"  Costos: {row['total_costos']:.2f}\n")
                text.insert(tk.END, f"  Subtotales: {row['total_subtotales']:.2f}\n")
                text.insert(tk.END, f"  Unidades vendidas: {row['total_unidades']}\n\n")

            # intentar graficar si matplotlib está disponible
            if not _HAS_MATPLOTLIB:
                messagebox.showwarning('Matplotlib no disponible', 'La librería matplotlib no está instalada. Instálala con: pip install matplotlib')
                return

            meses = [r['mes'] for r in datos]
            ingresos = [r['total_ingresos'] for r in datos]
            costos = [r['total_costos'] for r in datos]

            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(meses, ingresos, marker='o', label='Ingresos')
            ax.plot(meses, costos, marker='o', label='Costos')
            ax.set_title('Ingresos y Costos por mes')
            ax.set_xlabel('Mes')
            ax.set_ylabel('Valor')
            ax.grid(True, linestyle='--', alpha=0.4)
            ax.legend()
            for label in ax.get_xticklabels():
                label.set_rotation(45)

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            widget = canvas.get_tk_widget()
            widget.pack(fill='both', expand=True)
            canvas_holder['canvas'] = canvas

        except Exception as e:
            messagebox.showerror('Error', f'Error consultando contabilidad:\n{e}')

    win.transient(parent)
    win.grab_set()
    win.focus_force()
