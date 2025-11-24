import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
detalle_venta = db["DetalleVenta"]

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


def abrir_crud_detalle_ventas(username):
    def cargar_detalles():
        for row in tree.get_children():
            tree.delete(row)
        for i, detalle in enumerate(detalle_venta.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                detalle.get('detalle_id', ''),
                detalle.get('venta_id', ''),
                detalle.get('producto_id', ''),
                detalle.get('cantidad', ''),
                detalle.get('precio_unitario', ''),
                detalle.get('total', ''),
                detalle.get('descuento', ''),
                detalle.get('comentarios', '')
            ), tags=(tag,))

    def obtener_detalle_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            detalle_id = int(valores[0])
            return detalle_venta.find_one({"detalle_id": detalle_id})
        return None

    def eliminar_detalle():
        detalle = obtener_detalle_seleccionado()
        if detalle:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el detalle con ID '{detalle['detalle_id']}'?")
            if confirm:
                detalle_venta.delete_one({"detalle_id": detalle['detalle_id']})
                cargar_detalles()
                messagebox.showinfo("Eliminado", "Detalle de venta eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un detalle.")

    def abrir_formulario_detalle(titulo_ventana, detalle_existente=None):
        def guardar_detalle():
            try:
                nuevo_detalle = {
                    "detalle_id": int(entry_detalle_id.get()),
                    "venta_id": int(entry_venta_id.get()),
                    "producto_id": int(entry_producto_id.get()),
                    "cantidad": int(entry_cantidad.get()),
                    "precio_unitario": float(entry_precio_unitario.get()),
                    "total": float(entry_total.get()),
                    "descuento": float(entry_descuento.get()),
                    "comentarios": entry_comentarios.get()
                }
                if detalle_existente:
                    detalle_venta.update_one({"detalle_id": detalle_existente["detalle_id"]}, {"$set": nuevo_detalle})
                    messagebox.showinfo("Actualizado", "Detalle de venta actualizado.")
                else:
                    if detalle_venta.find_one({"detalle_id": nuevo_detalle["detalle_id"]}):
                        messagebox.showerror("Error", "detalle_id ya existe.")
                        return
                    detalle_venta.insert_one(nuevo_detalle)
                    messagebox.showinfo("Agregado", "Detalle de venta agregado.")
                ventana_form.destroy()
                cargar_detalles()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x500")
        crear_fondo_animado(ventana_form, "./fondos/fondo5.gif", (400, 500))
        Label(ventana_form, text="Detalle ID:").pack()
        entry_detalle_id = Entry(ventana_form)
        entry_detalle_id.pack()

        Label(ventana_form, text="Venta ID:").pack()
        entry_venta_id = Entry(ventana_form)
        entry_venta_id.pack()

        Label(ventana_form, text="Producto ID:").pack()
        entry_producto_id = Entry(ventana_form)
        entry_producto_id.pack()

        Label(ventana_form, text="Cantidad:").pack()
        entry_cantidad = Entry(ventana_form)
        entry_cantidad.pack()

        Label(ventana_form, text="Precio Unitario:").pack()
        entry_precio_unitario = Entry(ventana_form)
        entry_precio_unitario.pack()

        Label(ventana_form, text="Total:").pack()
        entry_total = Entry(ventana_form)
        entry_total.pack()

        Label(ventana_form, text="Descuento:").pack()
        entry_descuento = Entry(ventana_form)
        entry_descuento.pack()

        Label(ventana_form, text="Comentarios:").pack()
        entry_comentarios = Entry(ventana_form)
        entry_comentarios.pack()

        if detalle_existente:
            entry_detalle_id.insert(0, detalle_existente['detalle_id'])
            entry_detalle_id.config(state="disabled")
            entry_venta_id.insert(0, detalle_existente['venta_id'])
            entry_producto_id.insert(0, detalle_existente['producto_id'])
            entry_cantidad.insert(0, detalle_existente['cantidad'])
            entry_precio_unitario.insert(0, detalle_existente['precio_unitario'])
            entry_total.insert(0, detalle_existente['total'])
            entry_descuento.insert(0, detalle_existente['descuento'])
            entry_comentarios.insert(0, detalle_existente['comentarios'])

        Button(ventana_form, text="Guardar", command=guardar_detalle).pack(pady=10)

    def crear_detalle():
        abrir_formulario_detalle("Agregar Detalle de Venta")

    def editar_detalle():
        detalle = obtener_detalle_seleccionado()
        if detalle:
            abrir_formulario_detalle("Editar Detalle de Venta", detalle)
        else:
            messagebox.showwarning("Aviso", "Seleccione un detalle.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Detalle Venta - Sesión: {username}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo6.gif", (400, 500))
    Label(ventana, text="Detalles de Venta registrados", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("Detalle ID", "Venta ID", "Producto ID", "Cantidad", "Precio Unitario", "Total", "Descuento", "Comentarios")

    tree = ttk.Treeview(frame_interno, columns=columnas, show="headings", selectmode="browse")

    style = ttk.Style()
    style.theme_use('default')
    style.configure("Treeview",
                    background="white",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="white",
                    font=("Arial", 10),
                    bordercolor="black",
                    borderwidth=1)
    style.configure("Treeview.Heading",
                    font=("Arial", 11, "bold"),
                    background="#d9d9d9",
                    foreground="black",
                    relief="raised",
                    bordercolor="black",
                    borderwidth=1)
    style.map("Treeview",
              background=[('selected', '#3399FF')],
              foreground=[('selected', 'white')])

    tree.tag_configure('oddrow', background='white')
    tree.tag_configure('evenrow', background='#f0f0f0')

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=110, anchor="center", stretch=True)

    scrollbar_v = ttk.Scrollbar(frame_interno, orient="vertical", command=tree.yview)
    scrollbar_h = ttk.Scrollbar(frame_interno, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

    tree.grid(row=0, column=0, sticky='nsew')
    scrollbar_v.grid(row=0, column=1, sticky='ns')
    scrollbar_h.grid(row=1, column=0, sticky='ew')

    frame_interno.grid_rowconfigure(0, weight=1)
    frame_interno.grid_columnconfigure(0, weight=1)

    boton_frame = tk.Frame(ventana)
    boton_frame.pack(pady=10)

    Button(boton_frame, text="Agregar", width=15, command=crear_detalle).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_detalle).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_detalle).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_detalles).grid(row=0, column=3, padx=5)

    cargar_detalles()
    ventana.mainloop()
