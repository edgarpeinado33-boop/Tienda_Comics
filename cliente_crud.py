import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button, StringVar, OptionMenu, ttk
from db_config import get_db

db = get_db()
clientes = db["Clientes"]

METODOS_PAGO = ["Tarjeta", "Efectivo", "Transferencia"]

def abrir_crud_clientes(username):
    def cargar_clientes():
        for row in tree.get_children():
            tree.delete(row)
        for i, cliente in enumerate(clientes.find()):
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(
                cliente['cliente_id'],
                cliente['nombre'],
                cliente['email'],
                cliente['telefono'],
                cliente['direccion'],
                cliente['fecha_registro'],
                "Sí" if cliente['activo'] else "No",
                cliente['metodo_pago_preferido'],
                cliente['fecha_nacimiento']
            ), tags=(tag,))

    def obtener_cliente_seleccionado():
        seleccionado = tree.focus()
        if seleccionado:
            valores = tree.item(seleccionado, 'values')
            cliente_id = int(valores[0])
            return clientes.find_one({"cliente_id": cliente_id})
        return None

    def eliminar_cliente():
        cliente = obtener_cliente_seleccionado()
        if cliente:
            confirm = messagebox.askyesno("Confirmar", f"¿Eliminar a {cliente['nombre']}?")
            if confirm:
                clientes.delete_one({"cliente_id": cliente['cliente_id']})
                cargar_clientes()
                messagebox.showinfo("Eliminado", "Cliente eliminado correctamente.")
        else:
            messagebox.showwarning("Aviso", "Seleccione un cliente.")

    def abrir_formulario_cliente(titulo, cliente_existente=None):
        def guardar_cliente():
            try:
                nuevo_cliente = {
                    "cliente_id": int(entry_id.get()),
                    "nombre": entry_nombre.get(),
                    "email": entry_email.get(),
                    "telefono": entry_telefono.get(),
                    "direccion": entry_direccion.get(),
                    "fecha_registro": entry_fecha_registro.get(),
                    "activo": var_activo.get() == "1",
                    "metodo_pago_preferido": var_metodo_pago.get(),
                    "fecha_nacimiento": entry_fecha_nacimiento.get()
                }
                if cliente_existente:
                    clientes.update_one({"cliente_id": cliente_existente["cliente_id"]}, {"$set": nuevo_cliente})
                    messagebox.showinfo("Actualizado", "Cliente actualizado.")
                else:
                    if clientes.find_one({"cliente_id": nuevo_cliente["cliente_id"]}):
                        messagebox.showerror("Error", "cliente_id ya existe.")
                        return
                    clientes.insert_one(nuevo_cliente)
                    messagebox.showinfo("Agregado", "Cliente agregado.")

                ventana_form.destroy()
                cargar_clientes()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ventana_form = Toplevel(ventana)
        ventana_form.title(titulo)
        ventana_form.geometry("400x550")

   
        Label(ventana_form, text="ID:").pack()
        entry_id = Entry(ventana_form)
        entry_id.pack()

        Label(ventana_form, text="Nombre:").pack()
        entry_nombre = Entry(ventana_form)
        entry_nombre.pack()

        Label(ventana_form, text="Email:").pack()
        entry_email = Entry(ventana_form)
        entry_email.pack()

        Label(ventana_form, text="Teléfono:").pack()
        entry_telefono = Entry(ventana_form)
        entry_telefono.pack()

        Label(ventana_form, text="Dirección:").pack()
        entry_direccion = Entry(ventana_form)
        entry_direccion.pack()

        Label(ventana_form, text="Fecha Registro (YYYY-MM-DD):").pack()
        entry_fecha_registro = Entry(ventana_form)
        entry_fecha_registro.pack()

        Label(ventana_form, text="Activo (1 = Sí, 0 = No):").pack()
        var_activo = StringVar()
        entry_activo = Entry(ventana_form, textvariable=var_activo)
        entry_activo.pack()

        Label(ventana_form, text="Método de pago preferido:").pack()
        var_metodo_pago = StringVar()
        var_metodo_pago.set(METODOS_PAGO[0])
        option_metodo_pago = OptionMenu(ventana_form, var_metodo_pago, *METODOS_PAGO)
        option_metodo_pago.pack()

        Label(ventana_form, text="Fecha de Nacimiento (YYYY-MM-DD):").pack()
        entry_fecha_nacimiento = Entry(ventana_form)
        entry_fecha_nacimiento.pack()

        if cliente_existente:
            entry_id.insert(0, cliente_existente['cliente_id'])
            entry_id.config(state="disabled")
            entry_nombre.insert(0, cliente_existente['nombre'])
            entry_email.insert(0, cliente_existente['email'])
            entry_telefono.insert(0, cliente_existente['telefono'])
            entry_direccion.insert(0, cliente_existente['direccion'])
            entry_fecha_registro.insert(0, cliente_existente['fecha_registro'])
            var_activo.set("1" if cliente_existente['activo'] else "0")
            var_metodo_pago.set(cliente_existente['metodo_pago_preferido'])
            entry_fecha_nacimiento.insert(0, cliente_existente['fecha_nacimiento'])

        Button(ventana_form, text="Guardar", command=guardar_cliente).pack(pady=10)

    def crear_cliente():
        abrir_formulario_cliente("Agregar Cliente")

    def editar_cliente():
        cliente = obtener_cliente_seleccionado()
        if cliente:
            abrir_formulario_cliente("Editar Cliente", cliente)
        else:
            messagebox.showwarning("Aviso", "Seleccione un cliente.")


    ventana = tk.Tk()
    ventana.title(f"CRUD Clientes - Sesión: {username}")
    ventana.geometry("900x600")

    Label(ventana, text="Clientes registrados", font=("Arial", 14, "bold")).pack(pady=5)


    frame_tabla = tk.Frame(ventana, relief="solid", borderwidth=2, bg="black")
    frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)


    frame_interno = tk.Frame(frame_tabla, bg="white")
    frame_interno.pack(padx=1, pady=1, fill="both", expand=True)

    columnas = ("ID", "Nombre", "Email", "Teléfono", "Dirección", "Fecha Registro", "Activo", "Método Pago", "Fecha Nacimiento")

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

    Button(boton_frame, text="Agregar", width=15, command=crear_cliente).grid(row=0, column=0, padx=5)
    Button(boton_frame, text="Editar seleccionado", width=15, command=editar_cliente).grid(row=0, column=1, padx=5)
    Button(boton_frame, text="Eliminar seleccionado", width=15, command=eliminar_cliente).grid(row=0, column=2, padx=5)
    Button(boton_frame, text="Recargar", width=15, command=cargar_clientes).grid(row=0, column=3, padx=5)

    cargar_clientes()
    ventana.mainloop()


