import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
tienda = db["Tienda"]

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

def abrir_crud_tienda(username):
    def cargar_productos():
        for row in tree.get_children():
            tree.delete(row)
        for i, producto in enumerate(tienda.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                producto.get('producto_id', ''),
                producto.get('nombre', ''),
                producto.get('categoria', ''),
                producto.get('precio', ''),
                producto.get('stock', ''),
                producto.get('proveedor', ''),
                producto.get('descripcion', ''),
                "Sí" if producto.get('activo', True) else "No"
            ), tags=(tag,))

    def obtener_producto_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            producto_id = int(valores[0])
            return tienda.find_one({"producto_id": producto_id})
        return None

    def eliminar_producto():
        producto = obtener_producto_seleccionado()
        if producto:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el producto '{producto['nombre']}'?")
            if confirm:
                tienda.delete_one({"producto_id": producto['producto_id']})
                cargar_productos()
                messagebox.showinfo("Eliminado", "Producto eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un producto.")

    def abrir_formulario_producto(titulo_ventana, producto_existente=None):
        def guardar_producto():
            try:
                nuevo_producto = {
                    "producto_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "categoria": entry_categoria.get(),
                    "precio": float(entry_precio.get()),
                    "stock": int(entry_stock.get()),
                    "proveedor": entry_proveedor.get(),
                    "descripcion": entry_descripcion.get(),
                    "activo": var_activo.get() == 1
                }
                if producto_existente:
                    tienda.update_one({"producto_id": producto_existente["producto_id"]}, {"$set": nuevo_producto})
                    messagebox.showinfo("Actualizado", "Producto actualizado.")
                else:
                    if tienda.find_one({"producto_id": nuevo_producto["producto_id"]}):
                        messagebox.showerror("Error", "producto_id ya existe.")
                        return
                    tienda.insert_one(nuevo_producto)
                    messagebox.showinfo("Agregado", "Producto agregado.")
                ventana_form.destroy()
                cargar_productos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x500")
        crear_fondo_animado(ventana_form, "./fondos/fondo6.gif", (400, 500))
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="Categoría:").pack()
        entry_categoria = Entry(ventana_form)
        entry_categoria.pack()

        Label(ventana_form, text="Precio:").pack()
        entry_precio = Entry(ventana_form)
        entry_precio.pack()

        Label(ventana_form, text="Stock:").pack()
        entry_stock = Entry(ventana_form)
        entry_stock.pack()

        Label(ventana_form, text="Proveedor:").pack()
        entry_proveedor = Entry(ventana_form)
        entry_proveedor.pack()

        Label(ventana_form, text="Descripción:").pack()
        entry_descripcion = Entry(ventana_form)
        entry_descripcion.pack()

        var_activo = tk.IntVar(value=1)
        chk_activo = tk.Checkbutton(ventana_form, text="¿Activo?", variable=var_activo)
        chk_activo.pack()

        if producto_existente:
            entry_id.insert(0, producto_existente['producto_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, producto_existente['nombre'])
            entry_categoria.insert(0, producto_existente['categoria'])
            entry_precio.insert(0, producto_existente['precio'])
            entry_stock.insert(0, producto_existente['stock'])
            entry_proveedor.insert(0, producto_existente['proveedor'])
            entry_descripcion.insert(0, producto_existente['descripcion'])
            var_activo.set(1 if producto_existente['activo'] else 0)

        Button(ventana_form, text="Guardar", command=guardar_producto).pack(pady=10)

    def crear_producto():
        abrir_formulario_producto("Agregar Producto")

    def editar_producto():
        producto = obtener_producto_seleccionado()
        if producto:
            abrir_formulario_producto("Editar Producto", producto)
        else:
            messagebox.showwarning("Aviso", "Seleccione un producto.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Tienda - Sesión: {username}")
    ventana.geometry("1000x600")
    crear_fondo_animado(ventana, "./fondos/fondo.gif", (1000, 600))
    Label(ventana, text="Productos registrados en Tienda", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "Categoría", "Precio", "Stock", "Proveedor", "Descripción", "Activo")

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
        tree.column(col, width=120, anchor="center", stretch=True)

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

    Button(boton_frame, text="Agregar", width=15, command=crear_producto).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_producto).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_producto).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_productos).grid(row=0, column=3, padx=5)

    cargar_productos()
    ventana.mainloop()
