import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk, BooleanVar, Checkbutton
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
guionistas = db["Guionistas"]

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

def abrir_crud_guionistas(username):
    def cargar_guionistas():
        for row in tree.get_children():
            tree.delete(row)
        for i, guionista in enumerate(guionistas.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                guionista.get('guionista_id', ''),
                guionista.get('nombre', ''),
                guionista.get('pais', ''),
                guionista.get('fecha_nacimiento', ''),
                guionista.get('especialidad', ''),
                "Sí" if guionista.get('activo', False) else "No",
                guionista.get('comics_escritos', ''),
                guionista.get('biografia', '')
            ), tags=(tag,))

    def obtener_guionista_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            guionista_id = int(valores[0])
            return guionistas.find_one({"guionista_id": guionista_id})
        return None

    def eliminar_guionista():
        guionista = obtener_guionista_seleccionado()
        if guionista:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el guionista '{guionista['nombre']}'?")
            if confirm:
                guionistas.delete_one({"guionista_id": guionista['guionista_id']})
                cargar_guionistas()
                messagebox.showinfo("Eliminado", "Guionista eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un guionista.")

    def abrir_formulario_guionista(titulo_ventana, guionista_existente=None):
        def guardar_guionista():
            try:
                nuevo_guionista = {
                    "guionista_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "pais": entry_pais.get(),
                    "fecha_nacimiento": entry_fecha_nacimiento.get(),
                    "especialidad": entry_especialidad.get(),
                    "activo": activo_var.get(),
                    "comics_escritos": int(entry_comics_escritos.get()),
                    "biografia": entry_biografia.get()
                }
                if guionista_existente:
                    guionistas.update_one({"guionista_id": guionista_existente["guionista_id"]}, {"$set": nuevo_guionista})
                    messagebox.showinfo("Actualizado", "Guionista actualizado.")
                else:
                    if guionistas.find_one({"guionista_id": nuevo_guionista["guionista_id"]}):
                        messagebox.showerror("Error", "guionista_id ya existe.")
                        return
                    guionistas.insert_one(nuevo_guionista)
                    messagebox.showinfo("Agregado", "Guionista agregado.")
                ventana_form.destroy()
                cargar_guionistas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x550")
        crear_fondo_animado(ventana_form, "./fondos/fondo2.gif", (400, 550))
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="País:").pack()
        entry_pais = Entry(ventana_form)
        entry_pais.pack()

        Label(ventana_form, text="Fecha de Nacimiento (YYYY-MM-DD):").pack()
        entry_fecha_nacimiento = Entry(ventana_form)
        entry_fecha_nacimiento.pack()

        Label(ventana_form, text="Especialidad:").pack()
        entry_especialidad = Entry(ventana_form)
        entry_especialidad.pack()

        activo_var = BooleanVar()
        chk_activo = Checkbutton(ventana_form, text="Activo", variable=activo_var)
        chk_activo.pack()

        Label(ventana_form, text="Comics escritos:").pack()
        entry_comics_escritos = Entry(ventana_form)
        entry_comics_escritos.pack()

        Label(ventana_form, text="Biografía:").pack()
        entry_biografia = Entry(ventana_form)
        entry_biografia.pack()

        if guionista_existente:
            entry_id.insert(0, guionista_existente['guionista_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, guionista_existente['nombre'])
            entry_pais.insert(0, guionista_existente['pais'])
            entry_fecha_nacimiento.insert(0, guionista_existente['fecha_nacimiento'])
            entry_especialidad.insert(0, guionista_existente['especialidad'])
            activo_var.set(guionista_existente.get('activo', False))
            entry_comics_escritos.insert(0, guionista_existente['comics_escritos'])
            entry_biografia.insert(0, guionista_existente['biografia'])

        Button(ventana_form, text="Guardar", command=guardar_guionista).pack(pady=10)

    def crear_guionista():
        abrir_formulario_guionista("Agregar Guionista")

    def editar_guionista():
        guionista = obtener_guionista_seleccionado()
        if guionista:
            abrir_formulario_guionista("Editar Guionista", guionista)
        else:
            messagebox.showwarning("Aviso", "Seleccione un guionista.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Guionistas - Sesión: {username}")
    ventana.geometry("1000x600")
    crear_fondo_animado(ventana, "./fondos/fondo7.gif", (1000, 600))
    Label(ventana, text="Guionistas registrados", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "País", "Fecha Nac.", "Especialidad", "Activo", "Cómics Escritos", "Biografía")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_guionista).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_guionista).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_guionista).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_guionistas).grid(row=0, column=3, padx=5)

    cargar_guionistas()
    ventana.mainloop()
