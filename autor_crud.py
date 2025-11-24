import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk, BooleanVar, Checkbutton
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
autores = db["Autores"]

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

def abrir_crud_autores(username):
    def cargar_autores():
        for row in tree.get_children():
            tree.delete(row)
        for i, autor in enumerate(autores.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                autor.get('autor_id', ''),
                autor.get('nombre', ''),
                autor.get('pais', ''),
                autor.get('fecha_nacimiento', ''),
                autor.get('genero_especialidad', ''),
                autor.get('numero_comics', ''),
                "Sí" if autor.get('activo', False) else "No",
                autor.get('biografia', '')
            ), tags=(tag,))

    def obtener_autor_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            autor_id = int(valores[0])
            return autores.find_one({"autor_id": autor_id})
        return None

    def eliminar_autor():
        autor = obtener_autor_seleccionado()
        if autor:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el autor '{autor['nombre']}'?")
            if confirm:
                autores.delete_one({"autor_id": autor['autor_id']})
                cargar_autores()
                messagebox.showinfo("Eliminado", "Autor eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un autor.")

    def abrir_formulario_autor(titulo_ventana, autor_existente=None):
        def guardar_autor():
            try:
                nuevo_autor = {
                    "autor_id": int(entry_autor_id.get()),
                    "nombre": entry_nombre.get(),
                    "pais": entry_pais.get(),
                    "fecha_nacimiento": entry_fecha_nacimiento.get(),
                    "genero_especialidad": entry_genero_especialidad.get(),
                    "numero_comics": int(entry_numero_comics.get()),
                    "activo": var_activo.get(),
                    "biografia": entry_biografia.get()
                }
                if autor_existente:
                    autores.update_one({"autor_id": autor_existente["autor_id"]}, {"$set": nuevo_autor})
                    messagebox.showinfo("Actualizado", "Autor actualizado.")
                else:
                    if autores.find_one({"autor_id": nuevo_autor["autor_id"]}):
                        messagebox.showerror("Error", "autor_id ya existe.")
                        return
                    autores.insert_one(nuevo_autor)
                    messagebox.showinfo("Agregado", "Autor agregado.")
                ventana_form.destroy()
                cargar_autores()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x550")
        
        crear_fondo_animado(ventana_form, "./fondos/fondo7.gif", (400, 550))

        Label(ventana_form, text="ID Autor:").pack()
        entry_autor_id = Entry(ventana_form)
        entry_autor_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="País:").pack()
        entry_pais = Entry(ventana_form)
        entry_pais.pack()

        Label(ventana_form, text="Fecha de nacimiento (YYYY-MM-DD):").pack()
        entry_fecha_nacimiento = Entry(ventana_form)
        entry_fecha_nacimiento.pack()

        Label(ventana_form, text="Género/Especialidad:").pack()
        entry_genero_especialidad = Entry(ventana_form)
        entry_genero_especialidad.pack()

        Label(ventana_form, text="Número de cómics:").pack()
        entry_numero_comics = Entry(ventana_form)
        entry_numero_comics.pack()

        var_activo = BooleanVar()
        check_activo = Checkbutton(ventana_form, text="Activo", variable=var_activo)
        check_activo.pack()

        Label(ventana_form, text="Biografía:").pack()
        entry_biografia = Entry(ventana_form)
        entry_biografia.pack()

        if autor_existente:
            entry_autor_id.insert(0, autor_existente['autor_id'])
            entry_autor_id.config(state="disabled")
            entry_nombre.insert(0, autor_existente['nombre'])
            entry_pais.insert(0, autor_existente['pais'])
            entry_fecha_nacimiento.insert(0, autor_existente['fecha_nacimiento'])
            entry_genero_especialidad.insert(0, autor_existente['genero_especialidad'])
            entry_numero_comics.insert(0, autor_existente['numero_comics'])
            var_activo.set(autor_existente.get('activo', False))
            entry_biografia.insert(0, autor_existente['biografia'])

        Button(ventana_form, text="Guardar", command=guardar_autor).pack(pady=10)

    def crear_autor():
        abrir_formulario_autor("Agregar Autor")

    def editar_autor():
        autor = obtener_autor_seleccionado()
        if autor:
            abrir_formulario_autor("Editar Autor", autor)
        else:
            messagebox.showwarning("Aviso", "Seleccione un autor.")

    
    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Autores - Sesión: {username}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo6.gif", (900, 600))
    Label(ventana, text="Autores registrados", font=("Arial", 14, "bold")).pack(pady=5)
    
    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "País", "Fecha Nac.", "Género/Especialidad", "Número Cómics", "Activo", "Biografía")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_autor).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_autor).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_autor).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_autores).grid(row=0, column=3, padx=5)

    cargar_autores()
    ventana.mainloop()
