import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
ventas = db["Ventas"]
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

def abrir_crud_ventas(username):
    def cargar_ventas():
        for row in tree.get_children():
            tree.delete(row)
        for i, venta in enumerate(ventas.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                venta.get('venta_id', ''),
                venta.get('producto', ''),
                venta.get('cliente_id', ''),
                venta.get('fecha_venta', ''),
                venta.get('cantidad', ''),
                venta.get('precio_unitario', ''),
                venta.get('total', ''),
                venta.get('metodo_pago', '')
            ), tags=(tag,))

    def obtener_venta_seleccionada():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            venta_id = int(valores[0])
            return ventas.find_one({"venta_id": venta_id})
        return None

    def eliminar_venta():
        venta = obtener_venta_seleccionada()
        if venta:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar la venta del producto '{venta['producto']}'?")
            if confirm:
                ventas.delete_one({"venta_id": venta['venta_id']})
                cargar_ventas()
                messagebox.showinfo("Eliminado", "Venta eliminada correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione una venta.")

    def abrir_formulario_venta(titulo_ventana, venta_existente=None):
        def guardar_venta():
            try:
                nueva_venta = {
                    "venta_id": int(entry_id.get()),
                    "producto": entry_producto.get(),
                    "cliente_id": int(entry_cliente_id.get()),
                    "fecha_venta": entry_fecha.get(),
                    "cantidad": int(entry_cantidad.get()),
                    "precio_unitario": float(entry_precio.get()),
                    "total": float(entry_total.get()),
                    "metodo_pago": entry_metodo_pago.get()
                }
                if venta_existente:
                    ventas.update_one({"venta_id": venta_existente["venta_id"]}, {"$set": nueva_venta})
                    messagebox.showinfo("Actualizado", "Venta actualizada.")
                else:
                    if ventas.find_one({"venta_id": nueva_venta["venta_id"]}):
                        messagebox.showerror("Error", "venta_id ya existe.")
                        return
                    ventas.insert_one(nueva_venta)
                    messagebox.showinfo("Agregado", "Venta agregada.")
                ventana_form.destroy()
                cargar_ventas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x500")
        crear_fondo_animado(ventana_form, "./fondos/fondo2.gif", (400, 500))
        Label(ventana_form, text="ID Venta:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Producto:").pack()
        entry_producto = Entry(ventana_form)
        entry_producto.pack()

        Label(ventana_form, text="Cliente ID:").pack()
        entry_cliente_id = Entry(ventana_form)
        entry_cliente_id.pack()

        Label(ventana_form, text="Fecha Venta (YYYY-MM-DD):").pack()
        entry_fecha = Entry(ventana_form)
        entry_fecha.pack()

        Label(ventana_form, text="Cantidad:").pack()
        entry_cantidad = Entry(ventana_form)
        entry_cantidad.pack()

        Label(ventana_form, text="Precio Unitario:").pack()
        entry_precio = Entry(ventana_form)
        entry_precio.pack()

        Label(ventana_form, text="Total:").pack()
        entry_total = Entry(ventana_form)
        entry_total.pack()

        Label(ventana_form, text="Método de Pago:").pack()
        entry_metodo_pago = Entry(ventana_form)
        entry_metodo_pago.pack()

        if venta_existente:
            entry_id.insert(0, venta_existente['venta_id'])
            entry_id.config(state="disabled")
            entry_producto.insert(0, venta_existente['producto'])
            entry_cliente_id.insert(0, venta_existente['cliente_id'])
            entry_fecha.insert(0, venta_existente['fecha_venta'])
            entry_cantidad.insert(0, venta_existente['cantidad'])
            entry_precio.insert(0, venta_existente['precio_unitario'])
            entry_total.insert(0, venta_existente['total'])
            entry_metodo_pago.insert(0, venta_existente['metodo_pago'])

        Button(ventana_form, text="Guardar", command=guardar_venta).pack(pady=10)

    def crear_venta():
        abrir_formulario_venta("Agregar Venta")

    def editar_venta():
        venta = obtener_venta_seleccionada()
        if venta:
            abrir_formulario_venta("Editar Venta", venta)
        else:
            messagebox.showwarning("Aviso", "Seleccione una venta.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Ventas - Sesión: {username}")
    ventana.geometry("950x600")
    crear_fondo_animado(ventana, "./fondos/fondo3.gif", (950, 600))
    Label(ventana, text="Ventas registradas", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID Venta", "Producto", "Cliente ID", "Fecha Venta", "Cantidad", "Precio Unitario", "Total", "Método de Pago")

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
        tree.column(col, width=100, anchor="center", stretch=True)

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

    Button(boton_frame, text="Agregar", width=15, command=crear_venta).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=18, command=editar_venta).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=20, command=eliminar_venta).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_ventas).grid(row=0, column=3, padx=5)

    cargar_ventas()
    ventana.mainloop()
