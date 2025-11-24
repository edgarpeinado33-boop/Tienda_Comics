import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk, StringVar, IntVar, BooleanVar, Checkbutton
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
ilustradores = db["Ilustradores"]

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


def abrir_crud_ilustradores(username):
    def cargar_ilustradores():
        for row in tree.get_children():
            tree.delete(row)
        for i, ilustra in enumerate(ilustradores.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                ilustra.get('ilustrador_id', ''),
                ilustra.get('nombre', ''),
                ilustra.get('pais', ''),
                ilustra.get('fecha_nacimiento', ''),
                ilustra.get('especialidad', ''),
                "Sí" if ilustra.get('activo', False) else "No",
                ilustra.get('comics_asociados', ''),
                ilustra.get('biografia', '')
            ), tags=(tag,))

    def obtener_ilustrador_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            ilustra_id = int(valores[0])
            return ilustradores.find_one({"ilustrador_id": ilustra_id})
        return None

    def eliminar_ilustrador():
        ilustra = obtener_ilustrador_seleccionado()
        if ilustra:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar al ilustrador '{ilustra['nombre']}'?")
            if confirm:
                ilustradores.delete_one({"ilustrador_id": ilustra['ilustrador_id']})
                cargar_ilustradores()
                messagebox.showinfo("Eliminado", "Ilustrador eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un ilustrador.")

    def abrir_formulario_ilustrador(titulo_ventana, ilustra_existente=None):
        def guardar_ilustrador():
            try:
                nuevo_ilustra = {
                    "ilustrador_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "pais": entry_pais.get(),
                    "fecha_nacimiento": entry_fecha.get(),
                    "especialidad": entry_especialidad.get(),
                    "activo": var_activo.get(),
                    "comics_asociados": int(entry_comics.get()),
                    "biografia": entry_biografia.get()
                }
                if ilustra_existente:
                    ilustradores.update_one({"ilustrador_id": ilustra_existente["ilustrador_id"]}, {"$set": nuevo_ilustra})
                    messagebox.showinfo("Actualizado", "Ilustrador actualizado.")
                else:
                    if ilustradores.find_one({"ilustrador_id": nuevo_ilustra["ilustrador_id"]}):
                        messagebox.showerror("Error", "ilustrador_id ya existe.")
                        return
                    ilustradores.insert_one(nuevo_ilustra)
                    messagebox.showinfo("Agregado", "Ilustrador agregado.")
                ventana_form.destroy()
                cargar_ilustradores()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x550")
        crear_fondo_animado(ventana_form, "./fondos/fondo6.gif", (400, 550))
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
        entry_fecha = Entry(ventana_form)
        entry_fecha.pack()

        Label(ventana_form, text="Especialidad:").pack()
        entry_especialidad = Entry(ventana_form)
        entry_especialidad.pack()

        var_activo = BooleanVar()
        cb_activo = Checkbutton(ventana_form, text="Activo", variable=var_activo)
        cb_activo.pack()

        Label(ventana_form, text="Comics Asociados:").pack()
        entry_comics = Entry(ventana_form)
        entry_comics.pack()

        Label(ventana_form, text="Biografía:").pack()
        entry_biografia = Entry(ventana_form)
        entry_biografia.pack()

        if ilustra_existente:
            entry_id.insert(0, ilustra_existente['ilustrador_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, ilustra_existente['nombre'])
            entry_pais.insert(0, ilustra_existente['pais'])
            entry_fecha.insert(0, ilustra_existente['fecha_nacimiento'])
            entry_especialidad.insert(0, ilustra_existente['especialidad'])
            var_activo.set(ilustra_existente.get('activo', False))
            entry_comics.insert(0, ilustra_existente['comics_asociados'])
            entry_biografia.insert(0, ilustra_existente['biografia'])

        Button(ventana_form, text="Guardar", command=guardar_ilustrador).pack(pady=10)

    def crear_ilustrador():
        abrir_formulario_ilustrador("Agregar Ilustrador")

    def editar_ilustrador():
        ilustra = obtener_ilustrador_seleccionado()
        if ilustra:
            abrir_formulario_ilustrador("Editar Ilustrador", ilustra)
        else:
            messagebox.showwarning("Aviso", "Seleccione un ilustrador.")

    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Ilustradores - Sesión: {username}")
    ventana.geometry("900x600")
    crear_fondo_animado(ventana, "./fondos/fondo7.gif", (900, 600))
    Label(ventana, text="Ilustradores registrados", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "País", "Fecha Nacimiento", "Especialidad", "Activo", "Comics Asociados", "Biografía")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_ilustrador).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_ilustrador).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_ilustrador).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_ilustradores).grid(row=0, column=3, padx=5)

    cargar_ilustradores()
    ventana.mainloop()
