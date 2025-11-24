import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
ediciones = db["Ediciones_Especiales"]

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


def abrir_crud_ediciones_especiales(username):
    def cargar_ediciones():
        for row in tree.get_children():
            tree.delete(row)
        for i, edicion in enumerate(ediciones.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                edicion.get('edicion_id', ''),
                edicion.get('comic_id', ''),
                edicion.get('nombre_edicion', ''),
                edicion.get('fecha_lanzamiento', ''),
                edicion.get('cantidad_limitada', ''),
                edicion.get('precio', ''),
                edicion.get('caracteristicas', ''),
                "Sí" if edicion.get('disponible', False) else "No"
            ), tags=(tag,))

    def obtener_edicion_seleccionada():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            edicion_id = int(valores[0])
            return ediciones.find_one({"edicion_id": edicion_id})
        return None

    def eliminar_edicion():
        edicion = obtener_edicion_seleccionada()
        if edicion:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar la edición '{edicion['nombre_edicion']}'?")
            if confirm:
                ediciones.delete_one({"edicion_id": edicion['edicion_id']})
                cargar_ediciones()
                messagebox.showinfo("Eliminado", "Edición especial eliminada correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione una edición especial.")

    def abrir_formulario_edicion(titulo_ventana, edicion_existente=None):
        def guardar_edicion():
            try:
                nueva_edicion = {
                    "edicion_id": int(entry_id.get()),
                    "comic_id": int(entry_comic_id.get()),
                    "nombre_edicion": entry_nombre.get(),
                    "fecha_lanzamiento": entry_fecha.get(),
                    "cantidad_limitada": int(entry_cantidad.get()),
                    "precio": float(entry_precio.get()),
                    "caracteristicas": entry_caracteristicas.get(),
                    "disponible": var_disponible.get() == 1
                }
                if edicion_existente:
                    ediciones.update_one({"edicion_id": edicion_existente["edicion_id"]}, {"$set": nueva_edicion})
                    messagebox.showinfo("Actualizado", "Edición especial actualizada.")
                else:
                    if ediciones.find_one({"edicion_id": nueva_edicion["edicion_id"]}):
                        messagebox.showerror("Error", "edicion_id ya existe.")
                        return
                    ediciones.insert_one(nueva_edicion)
                    messagebox.showinfo("Agregado", "Edición especial agregada.")
                ventana_form.destroy()
                cargar_ediciones()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x500")
        crear_fondo_animado(ventana_form, "./fondos/fondo7.gif", (400, 500))
        Label(ventana_form, text="ID Edición:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="ID Cómic:").pack()
        entry_comic_id = Entry(ventana_form)
        entry_comic_id.pack()

        Label(ventana_form, text="Nombre Edición:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="Fecha Lanzamiento (YYYY-MM-DD):").pack()
        entry_fecha = Entry(ventana_form)
        entry_fecha.pack()

        Label(ventana_form, text="Cantidad Limitada:").pack()
        entry_cantidad = Entry(ventana_form)
        entry_cantidad.pack()

        Label(ventana_form, text="Precio:").pack()
        entry_precio = Entry(ventana_form)
        entry_precio.pack()

        Label(ventana_form, text="Características:").pack()
        entry_caracteristicas = Entry(ventana_form)
        entry_caracteristicas.pack()

        var_disponible = tk.IntVar()
        chk_disponible = tk.Checkbutton(ventana_form, text="Disponible", variable=var_disponible)
        chk_disponible.pack(pady=5)

        if edicion_existente:
            entry_id.insert(0, edicion_existente['edicion_id'])
            entry_id.config(state="disabled")
            entry_comic_id.insert(0, edicion_existente['comic_id'])
            entry_nombre.insert(0, edicion_existente['nombre_edicion'])
            entry_fecha.insert(0, edicion_existente['fecha_lanzamiento'])
            entry_cantidad.insert(0, edicion_existente['cantidad_limitada'])
            entry_precio.insert(0, edicion_existente['precio'])
            entry_caracteristicas.insert(0, edicion_existente['caracteristicas'])
            var_disponible.set(1 if edicion_existente['disponible'] else 0)

        Button(ventana_form, text="Guardar", command=guardar_edicion).pack(pady=10)

    def crear_edicion():
        abrir_formulario_edicion("Agregar Edición Especial")

    def editar_edicion():
        edicion = obtener_edicion_seleccionada()
        if edicion:
            abrir_formulario_edicion("Editar Edición Especial", edicion)
        else:
            messagebox.showwarning("Aviso", "Seleccione una edición especial.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Ediciones Especiales - Sesión: {username}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo4.gif", (900, 600))
    Label(ventana, text="Ediciones Especiales registradas", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID Edición", "ID Cómic", "Nombre Edición", "Fecha Lanzamiento", "Cantidad Limitada", "Precio", "Características", "Disponible")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_edicion).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_edicion).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_edicion).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_ediciones).grid(row=0, column=3, padx=5)

    cargar_ediciones()
    ventana.mainloop()
