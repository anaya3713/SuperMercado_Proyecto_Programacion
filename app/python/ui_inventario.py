try:
    from .InventarioWindow import VentanaInventario  # type: ignore
except ImportError:
    from InventarioWindow import VentanaInventario


def open_inventario(parent=None):
    VentanaInventario(parent).mostrar()
