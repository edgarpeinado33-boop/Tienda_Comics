import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
series = db["Series"]

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

def abrir_crud_series(username):
    def cargar_series():
        for row in tree.get_children():
            tree.delete(row)
        for i, serie in enumerate(series.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                serie.get('serie_id', ''),
                serie.get('nombre', ''),
                serie.get('descripcion', ''),
                serie.get('editorial_id', ''),
                serie.get('numero_volumenes', ''),
                serie.get('genero', ''),
                serie.get('fecha_inicio', ''),
                "Sí" if serie.get('activo') else "No"
            ), tags=(tag,))

    def obtener_serie_seleccionada():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            serie_id = int(valores[0])
            return series.find_one({"serie_id": serie_id})
        return None

    def eliminar_serie():
        serie = obtener_serie_seleccionada()
        if serie:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar la serie '{serie['nombre']}'?")
            if confirm:
                series.delete_one({"serie_id": serie['serie_id']})
                cargar_series()
                messagebox.showinfo("Eliminado", "Serie eliminada correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione una serie.")

    def abrir_formulario_serie(titulo_ventana, serie_existente=None):
        def guardar_serie():
            try:
                nueva_serie = {
                    "serie_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "descripcion": entry_descripcion.get(),
                    "editorial_id": int(entry_editorial_id.get()),
                    "numero_volumenes": int(entry_volumenes.get()),
                    "genero": entry_genero.get(),
                    "fecha_inicio": entry_fecha_inicio.get(),
                    "activo": var_activo.get() == 1
                }
                if serie_existente:
                    series.update_one({"serie_id": serie_existente["serie_id"]}, {"$set": nueva_serie})
                    messagebox.showinfo("Actualizado", "Serie actualizada.")
                else:
                    if series.find_one({"serie_id": nueva_serie["serie_id"]}):
                        messagebox.showerror("Error", "serie_id ya existe.")
                        return
                    series.insert_one(nueva_serie)
                    messagebox.showinfo("Agregado", "Serie agregada.")
                ventana_form.destroy()
                cargar_series()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x500")
        crear_fondo_animado(ventana_form, "./fondos/fondo5.gif", (400, 500))
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="Descripción:").pack()
        entry_descripcion = Entry(ventana_form)
        entry_descripcion.pack()

        Label(ventana_form, text="Editorial ID:").pack()
        entry_editorial_id = Entry(ventana_form)
        entry_editorial_id.pack()

        Label(ventana_form, text="Volúmenes:").pack()
        entry_volumenes = Entry(ventana_form)
        entry_volumenes.pack()

        Label(ventana_form, text="Género:").pack()
        entry_genero = Entry(ventana_form)
        entry_genero.pack()

        Label(ventana_form, text="Fecha Inicio (YYYY-MM-DD):").pack()
        entry_fecha_inicio = Entry(ventana_form)
        entry_fecha_inicio.pack()

        var_activo = tk.IntVar()
        tk.Checkbutton(ventana_form, text="¿Activo?", variable=var_activo).pack()

        if serie_existente:
            entry_id.insert(0, serie_existente['serie_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, serie_existente['nombre'])
            entry_descripcion.insert(0, serie_existente['descripcion'])
            entry_editorial_id.insert(0, serie_existente['editorial_id'])
            entry_volumenes.insert(0, serie_existente['numero_volumenes'])
            entry_genero.insert(0, serie_existente['genero'])
            entry_fecha_inicio.insert(0, serie_existente['fecha_inicio'])
            var_activo.set(1 if serie_existente['activo'] else 0)

        Button(ventana_form, text="Guardar", command=guardar_serie).pack(pady=10)

    def crear_serie():
        abrir_formulario_serie("Agregar Serie")

    def editar_serie():
        serie = obtener_serie_seleccionada()
        if serie:
            abrir_formulario_serie("Editar Serie", serie)
        else:
            messagebox.showwarning("Aviso", "Seleccione una serie.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Series - Sesión: {username}")
    ventana.geometry("950x600")
    crear_fondo_animado(ventana, "./fondos/fondo2.gif", (950, 600))
    Label(ventana, text="Series registradas", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "Descripción", "Editorial ID", "Volúmenes", "Género", "Fecha Inicio", "Activo")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_serie).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=20, command=editar_serie).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=20, command=eliminar_serie).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_series).grid(row=0, column=3, padx=5)

    cargar_series()
    ventana.mainloop()
