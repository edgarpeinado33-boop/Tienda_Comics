import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, ttk
from db_config import get_db
from PIL import Image, ImageTk, ImageSequence

db = get_db()
personajes = db["Personajes"]

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


def abrir_crud_personajes(username):
    def cargar_personajes():
        for row in tree.get_children():
            tree.delete(row)
        for i, p in enumerate(personajes.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            
            origen_id = p.get('comic_id') or p.get('manga_id') or ''
            tree.insert("", "end", values=(
                p.get('personaje_id', ''),
                p.get('nombre', ''),
                p.get('alias', ''),
                origen_id,
                p.get('poderes', ''),
                p.get('genero', ''),
                p.get('afiliacion', ''),
                p.get('primera_aparicion', ''),
                p.get('estado', '')
            ), tags=(tag,))

    def obtener_personaje_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            personaje_id = int(valores[0])
            return personajes.find_one({"personaje_id": personaje_id})
        return None

    def eliminar_personaje():
        p = obtener_personaje_seleccionado()
        if p:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar el personaje '{p['nombre']}'?")
            if confirm:
                personajes.delete_one({"personaje_id": p['personaje_id']})
                cargar_personajes()
                messagebox.showinfo("Eliminado", "Personaje eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un personaje.")

    def abrir_formulario_personaje(titulo_ventana, personaje_existente=None):
        def guardar_personaje():
            try:
                
                comic_id_val = entry_comic_id.get().strip()
                manga_id_val = entry_manga_id.get().strip()
                
                comic_id = int(comic_id_val) if comic_id_val else None
                manga_id = int(manga_id_val) if manga_id_val else None

                nuevo_personaje = {
                    "personaje_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "alias": entry_alias.get(),
                    "comic_id": comic_id,
                    "manga_id": manga_id,
                    "poderes": entry_poderes.get(),
                    "genero": entry_genero.get(),
                    "afiliacion": entry_afiliacion.get(),
                    "primera_aparicion": entry_primera_aparicion.get(),
                    "estado": entry_estado.get()
                }

                if personaje_existente:
                    personajes.update_one({"personaje_id": personaje_existente["personaje_id"]}, {"$set": nuevo_personaje})
                    messagebox.showinfo("Actualizado", "Personaje actualizado.")
                else:
                    if personajes.find_one({"personaje_id": nuevo_personaje["personaje_id"]}):
                        messagebox.showerror("Error", "personaje_id ya existe.")
                        return
                    personajes.insert_one(nuevo_personaje)
                    messagebox.showinfo("Agregado", "Personaje agregado.")
                ventana_form.destroy()
                cargar_personajes()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo_ventana)
        ventana_form.geometry("400x550")
        crear_fondo_animado(ventana_form, "./fondos/fondo.gif", (400, 550))

        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="Alias:").pack()
        entry_alias = Entry(ventana_form)
        entry_alias.pack()

        Label(ventana_form, text="Comic ID (opcional):").pack()
        entry_comic_id = Entry(ventana_form)
        entry_comic_id.pack()

        Label(ventana_form, text="Manga ID (opcional):").pack()
        entry_manga_id = Entry(ventana_form)
        entry_manga_id.pack()

        Label(ventana_form, text="Poderes:").pack()
        entry_poderes = Entry(ventana_form)
        entry_poderes.pack()

        Label(ventana_form, text="Género:").pack()
        entry_genero = Entry(ventana_form)
        entry_genero.pack()

        Label(ventana_form, text="Afiliación:").pack()
        entry_afiliacion = Entry(ventana_form)
        entry_afiliacion.pack()

        Label(ventana_form, text="Primera aparición (YYYY-MM-DD):").pack()
        entry_primera_aparicion = Entry(ventana_form)
        entry_primera_aparicion.pack()

        Label(ventana_form, text="Estado:").pack()
        entry_estado = Entry(ventana_form)
        entry_estado.pack()

        if personaje_existente:
            entry_id.insert(0, personaje_existente['personaje_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, personaje_existente['nombre'])
            entry_alias.insert(0, personaje_existente['alias'])
            entry_comic_id.insert(0, personaje_existente.get('comic_id', '') or '')
            entry_manga_id.insert(0, personaje_existente.get('manga_id', '') or '')
            entry_poderes.insert(0, personaje_existente['poderes'])
            entry_genero.insert(0, personaje_existente['genero'])
            entry_afiliacion.insert(0, personaje_existente['afiliacion'])
            entry_primera_aparicion.insert(0, personaje_existente['primera_aparicion'])
            entry_estado.insert(0, personaje_existente['estado'])

        Button(ventana_form, text="Guardar", command=guardar_personaje).pack(pady=10)

    def crear_personaje():
        abrir_formulario_personaje("Agregar Personaje")

    def editar_personaje():
        p = obtener_personaje_seleccionado()
        if p:
            abrir_formulario_personaje("Editar Personaje", p)
        else:
            messagebox.showwarning("Aviso", "Seleccione un personaje.")

   
    ventana = Toplevel() if tk._default_root else tk.Tk()
    ventana.title(f"CRUD Personajes - Sesión: {username}")
    ventana.geometry("950x600")
    crear_fondo_animado(ventana, "./fondos/fondo7.gif", (950, 600))

    Label(ventana, text="Personajes registrados", font=("Arial", 14, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "Alias", "Comic/Manga ID", "Poderes", "Género", "Afiliación", "Primera Aparición", "Estado")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_personaje).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_personaje).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_personaje).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_personajes).grid(row=0, column=3, padx=5)

    cargar_personajes()
    ventana.mainloop()
