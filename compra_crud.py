import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
compras = db["Compra"]

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


def abrir_crud_compras(username):
    def cargar_compras():
        for row in tree.get_children():
            tree.delete(row)
        for i, compra in enumerate(compras.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                compra.get('compra_id', ''),
                compra.get('cliente_id', ''),
                compra.get('fecha_compra', ''),
                compra.get('total', ''),
                compra.get('metodo_pago', ''),
                compra.get('estado', ''),
                compra.get('tienda_id', ''),
                compra.get('detalle', '')
            ), tags=(tag,))

    def obtener_compra_seleccionada():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            compra_id = int(valores[0])
            return compras.find_one({"compra_id": compra_id})
        return None

    def eliminar_compra():
        compra = obtener_compra_seleccionada()
        if compra:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar la compra ID '{compra['compra_id']}'?")
            if confirm:
                compras.delete_one({"compra_id": compra['compra_id']})
                cargar_compras()
                messagebox.showinfo("Eliminado", "Compra eliminada correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione una compra.")

    def abrir_formulario_compra(titulo_ventana, compra_existente=None):
        def guardar_compra():
            try:
                nuevo_compra = {
                    "compra_id": int(entry_id.get()),
                    "cliente_id": int(entry_cliente_id.get()),
                    "fecha_compra": entry_fecha.get(),
                    "total": float(entry_total.get()),
                    "metodo_pago": entry_metodo_pago.get(),
                    "estado": entry_estado.get(),
                    "tienda_id": int(entry_tienda_id.get()),
                    "detalle": entry_detalle.get()
                }
                if compra_existente:
                    compras.update_one({"compra_id": compra_existente["compra_id"]}, {"$set": nuevo_compra})
                    messagebox.showinfo("Actualizado", "Compra actualizada.")
                else:
                    if compras.find_one({"compra_id": nuevo_compra["compra_id"]}):
                        messagebox.showerror("Error", "compra_id ya existe.")
                        return
                    compras.insert_one(nuevo_compra)
                    messagebox.showinfo("Agregado", "Compra agregada.")
                ventana_form.destroy()
                cargar_compras()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x550")
        crear_fondo_animado(ventana_form, "./fondos/fondo7.gif", (400, 550))
        Label(ventana_form, text="ID Compra:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="ID Cliente:").pack()
        entry_cliente_id = Entry(ventana_form)
        entry_cliente_id.pack()

        Label(ventana_form, text="Fecha Compra (YYYY-MM-DD):").pack()
        entry_fecha = Entry(ventana_form)
        entry_fecha.pack()

        Label(ventana_form, text="Total:").pack()
        entry_total = Entry(ventana_form)
        entry_total.pack()

        Label(ventana_form, text="Método de Pago:").pack()
        entry_metodo_pago = Entry(ventana_form)
        entry_metodo_pago.pack()

        Label(ventana_form, text="Estado:").pack()
        entry_estado = Entry(ventana_form)
        entry_estado.pack()

        Label(ventana_form, text="ID Tienda:").pack()
        entry_tienda_id = Entry(ventana_form)
        entry_tienda_id.pack()

        Label(ventana_form, text="Detalle:").pack()
        entry_detalle = Entry(ventana_form)
        entry_detalle.pack()

        if compra_existente:
            entry_id.insert(0, compra_existente['compra_id'])
            entry_id.config(state="disabled")
            entry_cliente_id.insert(0, compra_existente['cliente_id'])
            entry_fecha.insert(0, compra_existente['fecha_compra'])
            entry_total.insert(0, compra_existente['total'])
            entry_metodo_pago.insert(0, compra_existente['metodo_pago'])
            entry_estado.insert(0, compra_existente['estado'])
            entry_tienda_id.insert(0, compra_existente['tienda_id'])
            entry_detalle.insert(0, compra_existente['detalle'])

        Button(ventana_form, text="Guardar", command=guardar_compra).pack(pady=10)

    def crear_compra():
        abrir_formulario_compra("Agregar Compra")

    def editar_compra():
        compra = obtener_compra_seleccionada()
        if compra:
            abrir_formulario_compra("Editar Compra", compra)
        else:
            messagebox.showwarning("Aviso", "Seleccione una compra.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Compras - Sesión: {username}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo4.gif", (900, 600))
    Label(ventana, text="Compras registradas", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID Compra", "ID Cliente", "Fecha Compra", "Total", "Método Pago", "Estado", "ID Tienda", "Detalle")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_compra).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_compra).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_compra).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_compras).grid(row=0, column=3, padx=5)

    cargar_compras()
    ventana.mainloop()
