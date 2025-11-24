import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, StringVar, OptionMenu, ttk
from db_config import get_db
from datetime import date
import subprocess
import sys
from PIL import Image, ImageTk, ImageSequence
import os
db = get_db()
clientes = db["Clientes"]
compras = db["Compras"]
tienda = db["Tienda"]

METODOS_PAGO = ["Tarjeta", "Efectivo", "Transferencia"]
ESTADOS_COMPRA = ["Completado", "Pendiente", "Cancelado"]

def crear_fondo_animado(ventana, gif_path, size):
    
    gif = Image.open(gif_path)
    frames = [ImageTk.PhotoImage(frame.resize(size, Image.LANCZOS)) for frame in ImageSequence.Iterator(gif)]

    fondo_label = tk.Label(ventana)
    fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

    def animar(ind=0):
        if fondo_label.winfo_exists():
            fondo_label.configure(image=frames[ind])
            ventana.after(100, animar, (ind + 1) % len(frames))

    animar()
    return fondo_label


def crear_fondo_estatico(ventana, img_path, size):
    
    img = Image.open(img_path).resize(size, Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    fondo_label = tk.Label(ventana, image=img_tk)
    fondo_label.image = img_tk 
    fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
    return fondo_label

def abrir_crud_clientes_1(username):
    ventana = tk.Tk()
    ventana.title(f"Gestión de Clientes - Sesión de {username}")
    ventana.geometry("1100x600")
    ventana.resizable(False, False)

    
    gif_path = os.path.join(os.path.dirname(__file__), "fondos", "fondo2.gif")
    crear_fondo_animado(ventana, gif_path, (1100, 600))



    label_titulo = Label(ventana, text="Listado de Clientes", font=("Arial", 16, "bold"))
    label_titulo.pack(pady=(10, 0))

    columnas = ("ID", "Nombre", "Email", "Teléfono", "Dirección", "Registro", "Activo", "Pago Preferido", "Nacimiento")
    tree = ttk.Treeview(ventana, columns=columnas, show="headings", height=20)
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    tree.pack(pady=10)

    tree.tag_configure('oddrow', background="white")
    tree.tag_configure('evenrow', background="lightblue")

   
    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)

    def cargar_clientes():
        for row in tree.get_children():
            tree.delete(row)
        for i, cliente in enumerate(clientes.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                cliente['cliente_id'],
                cliente['nombre'],
                cliente['email'],
                cliente['telefono'],
                cliente['direccion'],
                cliente['fecha_registro'],
                "Sí" if cliente['activo'] else "No",
                cliente['metodo_pago_preferido'],
                cliente['fecha_nacimiento']
            ), tags=(tag,))


    def abrir_formulario_cliente_1(titulo, cliente_existente=None):
        def guardar_cliente():
            try:
                nuevo_cliente = {
                    "cliente_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "email": entry_email.get(),
                    "telefono": entry_telefono.get(),
                    "direccion": entry_direccion.get(),
                    "fecha_registro": entry_fecha_registro.get(),
                    "activo": var_activo.get() == "1",
                    "metodo_pago_preferido": var_metodo_pago.get(),
                    "fecha_nacimiento": entry_fecha_nacimiento.get()
                }
                if cliente_existente:
                    clientes.update_one({"cliente_id": cliente_existente["cliente_id"]}, {"$set": nuevo_cliente})
                    messagebox.showinfo("Actualizado", "Cliente actualizado.")
                else:
                    if clientes.find_one({"cliente_id": nuevo_cliente["cliente_id"]}):
                        messagebox.showerror("Error", "cliente_id ya existe.")
                        return
                    clientes.insert_one(nuevo_cliente)
                    messagebox.showinfo("Agregado", "Cliente agregado.")
                ventana_form.destroy()
                cargar_clientes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo)
        ventana_form.geometry("400x550")
        
        crear_fondo_animado(ventana_form, "./fondos/fondo7.gif", (400, 550))
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="Email:").pack()
        entry_email = Entry(ventana_form)
        entry_email.pack()

        Label(ventana_form, text="Teléfono:").pack()
        entry_telefono = Entry(ventana_form)
        entry_telefono.pack()

        Label(ventana_form, text="Dirección:").pack()
        entry_direccion = Entry(ventana_form)
        entry_direccion.pack()

        Label(ventana_form, text="Fecha Registro (YYYY-MM-DD):").pack()
        entry_fecha_registro = Entry(ventana_form)
        entry_fecha_registro.pack()

        Label(ventana_form, text="Activo (1 = Sí, 0 = No):").pack()
        var_activo = StringVar()
        entry_activo = Entry(ventana_form, textvariable=var_activo)
        entry_activo.pack()

        Label(ventana_form, text="Método de pago preferido:").pack()
        var_metodo_pago = StringVar()
        var_metodo_pago.set(METODOS_PAGO[0])
        OptionMenu(ventana_form, var_metodo_pago, *METODOS_PAGO).pack()

        Label(ventana_form, text="Fecha de Nacimiento (YYYY-MM-DD):").pack()
        entry_fecha_nacimiento = Entry(ventana_form)
        entry_fecha_nacimiento.pack()

        if cliente_existente:
            entry_id.insert(0, cliente_existente['cliente_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, cliente_existente['nombre'])
            entry_email.insert(0, cliente_existente['email'])
            entry_telefono.insert(0, cliente_existente['telefono'])
            entry_direccion.insert(0, cliente_existente['direccion'])
            entry_fecha_registro.insert(0, cliente_existente['fecha_registro'])
            var_activo.set("1" if cliente_existente['activo'] else "0")
            var_metodo_pago.set(cliente_existente['metodo_pago_preferido'])
            entry_fecha_nacimiento.insert(0, cliente_existente['fecha_nacimiento'])

        Button(ventana_form, text="Guardar", command=guardar_cliente).pack(pady=10)

    def crear_cliente():
        abrir_formulario_cliente_1("Agregar Cliente")

    def registrar_compra():
        seleccion = tree.focus()
        if not seleccion:
            messagebox.showwarning("Selecciona un cliente", "Selecciona un cliente para registrar una compra.")
            return

        cliente = tree.item(seleccion)['values']
        cliente_id = cliente[0]

        ventana_compra = Toplevel(ventana)
        ventana_compra.title("Registrar Compra")
        ventana_compra.geometry("650x700")
        crear_fondo_animado(ventana_compra, "./fondos/fondo5.gif", (650, 700))
        Label(ventana_compra, text=f"Registrar compra para Cliente ID {cliente_id}", font=("Arial", 12, "bold")).pack(pady=10)

        Label(ventana_compra, text="ID Compra:").pack()
        entry_compra_id = Entry(ventana_compra)
        entry_compra_id.pack()

        Label(ventana_compra, text="Fecha de Compra (YYYY-MM-DD):").pack()
        entry_fecha = Entry(ventana_compra)
        entry_fecha.insert(0, str(date.today()))
        entry_fecha.pack()

        Label(ventana_compra, text="Método de Pago:").pack()
        var_pago = StringVar()
        var_pago.set(METODOS_PAGO[0])
        OptionMenu(ventana_compra, var_pago, *METODOS_PAGO).pack()

        Label(ventana_compra, text="Estado:").pack()
        var_estado = StringVar()
        var_estado.set(ESTADOS_COMPRA[0])
        OptionMenu(ventana_compra, var_estado, *ESTADOS_COMPRA).pack()

        Label(ventana_compra, text="Agregar productos al detalle de compra:", font=("Arial", 11, "bold")).pack(pady=10)
        frame_detalle = tk.Frame(ventana_compra)
        frame_detalle.pack()

        productos_lista = []
        for producto in tienda.find():
            nombre_producto = f"{producto.get('nombre', 'SinNombre')} ({producto.get('tipo', 'Producto')})"
            productos_lista.append((nombre_producto, producto['producto_id'], producto.get('precio', 0)))

        if not productos_lista:
            messagebox.showwarning("Sin productos", "No hay productos en la tienda.")
            ventana_compra.destroy()
            return

        var_producto_seleccionado = StringVar()
        var_producto_seleccionado.set(productos_lista[0][0])

        OptionMenu(frame_detalle, var_producto_seleccionado, *[p[0] for p in productos_lista]).grid(row=0, column=0, padx=5)
        Label(frame_detalle, text="Cantidad:").grid(row=0, column=1)
        entry_cantidad = Entry(frame_detalle, width=5)
        entry_cantidad.grid(row=0, column=2)
        entry_cantidad.insert(0, "1")

        detalle_compra = []

        def agregar_producto():
            nombre_sel = var_producto_seleccionado.get()
            cantidad_text = entry_cantidad.get()
            if not cantidad_text.isdigit() or int(cantidad_text) <= 0:
                messagebox.showerror("Error", "Cantidad inválida.")
                return
            cantidad = int(cantidad_text)

            for nombre, pid, precio in productos_lista:
                if nombre == nombre_sel:
                    for i, (p_id, _, cant, _) in enumerate(detalle_compra):
                        if p_id == pid:
                            detalle_compra[i] = (pid, nombre, cant + cantidad, precio)
                            break
                    else:
                        detalle_compra.append((pid, nombre, cantidad, precio))
                    break

            refrescar_tree_detalle()
            entry_cantidad.delete(0, tk.END)
            entry_cantidad.insert(0, "1")

        def refrescar_tree_detalle():
            for row in tree_detalle.get_children():
                tree_detalle.delete(row)
            total = 0
            for pid, nombre, cantidad, precio in detalle_compra:
                subtotal = cantidad * precio
                total += subtotal
                tree_detalle.insert("", "end", values=(nombre, cantidad, f"Bs {precio:.2f}", f"Bs {subtotal:.2f}"))
            label_total.config(text=f"Total: Bs {total:.2f}")

        tree_detalle = ttk.Treeview(ventana_compra, columns=("Producto", "Cantidad", "Precio (Bs)", "Subtotal (Bs)"), show="headings")
        for col in ("Producto", "Cantidad", "Precio (Bs)", "Subtotal (Bs)"):
            tree_detalle.heading(col, text=col)
            tree_detalle.column(col, width=150, anchor="center")
        tree_detalle.pack(pady=10)

        Button(frame_detalle, text="Agregar", command=agregar_producto).grid(row=0, column=3, padx=5)

        Button(ventana_compra, text="Eliminar Producto Seleccionado",
               command=lambda: eliminar_producto_seleccionado()).pack(pady=5)

        label_total = Label(ventana_compra, text="Total: Bs 0.00", font=("Arial", 12, "bold"))
        label_total.pack()

        def eliminar_producto_seleccionado():
            selected = tree_detalle.selection()
            if not selected:
                messagebox.showwarning("Seleccionar", "Seleccione un producto para eliminar.")
                return
            item = tree_detalle.item(selected[0])
            nombre_eliminar = item['values'][0]
            for i, (_, nombre, _, _) in enumerate(detalle_compra):
                if nombre == nombre_eliminar:
                    detalle_compra.pop(i)
                    break
            refrescar_tree_detalle()

        def guardar_compra():
            try:
                compra_id = int(entry_compra_id.get())
                if compras.find_one({"compra_id": compra_id}):
                    messagebox.showerror("Error", "ID de compra ya existe.")
                    return
                if not detalle_compra:
                    messagebox.showerror("Error", "Agregue al menos un producto.")
                    return
                compra = {
                    "compra_id": compra_id,
                    "cliente_id": cliente_id,
                    "fecha": entry_fecha.get(),
                    "metodo_pago": var_pago.get(),
                    "estado": var_estado.get(),
                    "detalle": [
                        {"producto_id": pid, "cantidad": cant, "precio": precio}
                        for pid, _, cant, precio in detalle_compra
                    ]
                }
                compras.insert_one(compra)
                messagebox.showinfo("Compra guardada", "Compra registrada exitosamente.")
                ventana_compra.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(ventana_compra, text="Guardar Compra", command=guardar_compra).pack(pady=10)
    def cerrar_sesion():
         ventana.destroy()
         subprocess.Popen([sys.executable, "main.py"])

    btn_agregar = Button(frame_botones, text="Agregar Cliente", command=crear_cliente)
    btn_compra = Button(frame_botones, text="Registrar Compra", command=registrar_compra)
    btn_cerrar_sesion = Button(frame_botones, text="Cerrar Sesión", command=cerrar_sesion)

    btn_agregar.pack(side="left", padx=15)
    btn_compra.pack(side="left", padx=15)
    btn_cerrar_sesion.pack(side="left", padx=15)

    cargar_clientes()
    ventana.mainloop()
