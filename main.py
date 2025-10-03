import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import db
from pdf_generator import export_quote_to_pdf

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False

APP_DIR = Path(__file__).parent
COMPANY_NAME = "Barajar Peña"
BRAND_COLOR = "#2196F3"

def ensure_db():
    db.init_db()

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{COMPANY_NAME} - Gestor de Presupuestos")
        self.root.geometry('1000x700')
        
        # Configure style
        if HAS_TTKBOOTSTRAP:
            style = ttkb.Style('flatly')
        else:
            style = ttk.Style()
            style.theme_use('clam')
        
        # Header with company name
        header = ttk.Frame(root)
        header.pack(fill='x', padx=20, pady=15)
        
        title = ttk.Label(header, text=COMPANY_NAME, font=('Helvetica', 24, 'bold'))
        title.pack(side='left')
        
        subtitle = ttk.Label(header, text="Gestión de Presupuestos", font=('Helvetica', 12))
        subtitle.pack(side='left', padx=20)
        
        # Quick actions bar
        actions = ttk.Frame(root)
        actions.pack(fill='x', padx=20, pady=10)
        
        btn_style = {'padding': 10, 'width': 20}
        if HAS_TTKBOOTSTRAP:
            ttk.Button(actions, text="➕ Nuevo Presupuesto", command=self.quick_new_quote, bootstyle="success", **btn_style).pack(side='left', padx=5)
            ttk.Button(actions, text="📦 Nuevo Material", command=self.quick_new_material, bootstyle="primary", **btn_style).pack(side='left', padx=5)
            ttk.Button(actions, text="👤 Nuevo Cliente", command=self.quick_new_client, bootstyle="info", **btn_style).pack(side='left', padx=5)
        else:
            ttk.Button(actions, text="➕ Nuevo Presupuesto", command=self.quick_new_quote, **btn_style).pack(side='left', padx=5)
            ttk.Button(actions, text="📦 Nuevo Material", command=self.quick_new_material, **btn_style).pack(side='left', padx=5)
            ttk.Button(actions, text="👤 Nuevo Cliente", command=self.quick_new_client, **btn_style).pack(side='left', padx=5)
        
        # Main content with tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Quotes tab (main view)
        self.quotes_frame = QuotesFrame(self.notebook, self)
        self.notebook.add(self.quotes_frame, text='📋 Presupuestos')
        
        # Materials tab
        self.materials_frame = MaterialsFrame(self.notebook, self)
        self.notebook.add(self.materials_frame, text='📦 Materiales')
        
        # Clients tab
        self.clients_frame = ClientsFrame(self.notebook, self)
        self.notebook.add(self.clients_frame, text='👥 Clientes')
        
        # Status bar
        status = ttk.Frame(root)
        status.pack(fill='x', side='bottom')
        self.status_label = ttk.Label(status, text="Listo", font=('Helvetica', 9))
        self.status_label.pack(side='left', padx=20, pady=5)
        
        # Keyboard shortcuts
        root.bind('<Control-n>', lambda e: self.quick_new_quote())
        root.bind('<Control-m>', lambda e: self.quick_new_material())
        root.bind('<Control-u>', lambda e: self.quick_new_client())
        root.bind('<F5>', lambda e: self.refresh_all())
        
        self.refresh_all()
    
    def quick_new_quote(self):
        self.notebook.select(0)
        self.quotes_frame.new_quote()
    
    def quick_new_material(self):
        MaterialEditor(self.root, None, on_save=self.materials_frame.refresh)
    
    def quick_new_client(self):
        ClientEditor(self.root, None, on_save=self.clients_frame.refresh)
    
    def refresh_all(self):
        self.quotes_frame.refresh()
        self.materials_frame.refresh()
        self.clients_frame.refresh()
        self.status_label.config(text=f"Actualizado - {db.list_quotes().__len__()} presupuestos")

class MaterialsFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        
        # Search bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side='left', padx=5)
        
        # Tree
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        cols = ('name', 'category', 'desc', 'price')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)
        self.tree.heading('name', text='Nombre')
        self.tree.heading('category', text='Categoría')
        self.tree.heading('desc', text='Descripción')
        self.tree.heading('price', text='Precio (€)')
        self.tree.column('name', width=180)
        self.tree.column('category', width=120)
        self.tree.column('desc', width=250)
        self.tree.column('price', width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Double-click to edit
        self.tree.bind('<Double-Button-1>', lambda e: self.edit())
        
        # Buttons
        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=10, pady=15)
        
        btn_config = {'padding': 8, 'width': 15}
        if HAS_TTKBOOTSTRAP:
            ttk.Button(btns, text='➕ Añadir', command=self.add, bootstyle="success", **btn_config).pack(side='left', padx=5)
            ttk.Button(btns, text='✏️ Editar', command=self.edit, bootstyle="info", **btn_config).pack(side='left', padx=5)
            ttk.Button(btns, text='🗑️ Borrar', command=self.delete, bootstyle="danger", **btn_config).pack(side='left', padx=5)
        else:
            ttk.Button(btns, text='➕ Añadir', command=self.add, **btn_config).pack(side='left', padx=5)
            ttk.Button(btns, text='✏️ Editar', command=self.edit, **btn_config).pack(side='left', padx=5)
            ttk.Button(btns, text='🗑️ Borrar', command=self.delete, **btn_config).pack(side='left', padx=5)
        
        self.refresh()
    
    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        search = self.search_var.get().lower()
        for m in db.list_materials():
            category = m['category'] if m['category'] else 'Sin categoría'
            if search and search not in m['name'].lower() and search not in (m['description'] or '').lower() and search not in (category or '').lower():
                continue
            desc = (m['description'] or '')[:50]
            self.tree.insert('', 'end', iid=str(m['id']), 
                           values=(m['name'], category, desc, f"{m['price']:.2f}"))
    
    def add(self):
        MaterialEditor(self, None, on_save=self.refresh)
    
    def edit(self):
        sel = self.tree.selection()
        if not sel:
            return
        mid = int(sel[0])
        MaterialEditor(self, mid, on_save=self.refresh)
    
    def delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        mid = int(sel[0])
        if messagebox.askyesno('Confirmar', '¿Borrar este material?'):
            db.delete_material(mid)
            self.refresh()

class MaterialEditor(tk.Toplevel):
    def __init__(self, master, mid=None, on_save=None):
        super().__init__(master)
        self.mid = mid
        self.on_save = on_save
        self.title('Nuevo Material' if not mid else 'Editar Material')
        self.geometry('650x550')  # Más grande para que todo sea visible
        self.transient(master)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f'650x550+{x}+{y}')
        
        # Form
        form = ttk.Frame(self, padding=20)
        form.pack(fill='both', expand=True)
        
        ttk.Label(form, text='Nombre *', font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.name = ttk.Entry(form, width=40, font=('Helvetica', 11))
        self.name.grid(row=0, column=1, pady=5, sticky='ew')
        self.name.focus()
        
        ttk.Label(form, text='Descripción', font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky='nw', pady=5)
        self.desc = tk.Text(form, height=5, width=40, font=('Helvetica', 10))
        self.desc.grid(row=1, column=1, pady=5, sticky='ew')
        
        ttk.Label(form, text='Precio (€) *', font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        self.price = ttk.Entry(form, width=20, font=('Helvetica', 11))
        self.price.grid(row=2, column=1, pady=5, sticky='w')
        
        ttk.Label(form, text='Categoría', font=('Helvetica', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        
        # Editable combobox - allows typing new categories
        cat_frame = ttk.Frame(form)
        cat_frame.grid(row=3, column=1, pady=5, sticky='ew')
        
        categories = db.get_categories() if db.get_categories() else ['Sin categoría']
        self.category = ttk.Combobox(cat_frame, values=categories, width=37, font=('Helvetica', 11))
        self.category.pack(side='left', fill='x', expand=True)
        self.category.set('Sin categoría')
        
        # Allow typing new categories
        self.category['state'] = 'normal'  # Makes it editable
        
        # Info label
        ttk.Label(cat_frame, text='💡', font=('Helvetica', 8)).pack(side='right', padx=2)
        
        # Add tooltip behavior
        cat_info = ttk.Label(form, text='Escribe una nueva categoría o selecciona una existente', 
                            font=('Helvetica', 8), foreground='gray')
        cat_info.grid(row=4, column=1, sticky='w')
        
        ttk.Label(form, text='Imagen', font=('Helvetica', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=5)
        img_frame = ttk.Frame(form)
        img_frame.grid(row=5, column=1, pady=5, sticky='ew')
        self.img_path = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.img_path, state='readonly').pack(side='left', fill='x', expand=True)
        ttk.Button(img_frame, text='📁', command=self.choose_image, width=3).pack(side='right', padx=5)
        
        form.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill='x', side='bottom')
        ttk.Button(btn_frame, text='💾 Guardar', command=self.save).pack(side='right', padx=5)
        ttk.Button(btn_frame, text='❌ Cancelar', command=self.destroy).pack(side='right', padx=5)
        
        # Load data if editing
        if mid:
            m = db.get_material(mid)
            if m:
                self.name.insert(0, m['name'])
                if m['description']:
                    self.desc.insert('1.0', m['description'])
                self.price.insert(0, str(m['price']))
                if m['category']:
                    self.category.set(m['category'])
                if m['image_path']:
                    self.img_path.set(m['image_path'])
        
        # Keyboard shortcuts
        self.bind('<Return>', lambda e: self.save())
        self.bind('<Escape>', lambda e: self.destroy())
    
    def choose_image(self):
        p = filedialog.askopenfilename(filetypes=[('Imágenes','*.png *.jpg *.jpeg *.bmp')])
        if p:
            self.img_path.set(p)
    
    def save(self):
        name = self.name.get().strip()
        if not name:
            messagebox.showerror('Error', 'El nombre es obligatorio')
            self.name.focus()
            return
        desc = self.desc.get('1.0', 'end').strip()
        try:
            price = float(self.price.get())
            if price < 0:
                raise ValueError()
        except:
            messagebox.showerror('Error', 'Precio inválido (debe ser ≥ 0)')
            self.price.focus()
            return
        img = self.img_path.get() or None
        category = self.category.get().strip() or 'Sin categoría'
        if self.mid:
            db.update_material(self.mid, name, desc, img, price, category)
        else:
            db.add_material(name, desc, img, price, category)
        if self.on_save:
            self.on_save()
        self.destroy()

class ClientsFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        
        # Search bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side='left', padx=5)
        
        # Tree
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        cols = ('name', 'address', 'dni', 'phone')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)
        self.tree.heading('name', text='Nombre')
        self.tree.heading('address', text='Dirección')
        self.tree.heading('dni', text='DNI')
        self.tree.heading('phone', text='Teléfono')
        self.tree.column('name', width=200)
        self.tree.column('address', width=250)
        self.tree.column('dni', width=120)
        self.tree.column('phone', width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<Double-Button-1>', lambda e: self.edit())
        
        # Buttons
        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=10, pady=10)
        ttk.Button(btns, text='➕ Añadir', command=self.add).pack(side='left', padx=5)
        ttk.Button(btns, text='✏️ Editar', command=self.edit).pack(side='left', padx=5)
        ttk.Button(btns, text='🗑️ Borrar', command=self.delete).pack(side='left', padx=5)
        
        self.refresh()
    
    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        search = self.search_var.get().lower()
        for c in db.list_clients():
            if search and search not in c['name'].lower() and search not in (c['dni'] or '').lower():
                continue
            self.tree.insert('', 'end', iid=str(c['id']), 
                           values=(c['name'], c['address'] or '', c['dni'] or '', c['phone'] or ''))
    
    def add(self):
        ClientEditor(self, None, on_save=self.refresh)
    
    def edit(self):
        sel = self.tree.selection()
        if not sel:
            return
        cid = int(sel[0])
        ClientEditor(self, cid, on_save=self.refresh)
    
    def delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        cid = int(sel[0])
        if messagebox.askyesno('Confirmar', '¿Borrar este cliente?'):
            db.delete_client(cid)
            self.refresh()

class ClientEditor(tk.Toplevel):
    def __init__(self, master, cid=None, on_save=None):
        super().__init__(master)
        self.cid = cid
        self.on_save = on_save
        self.title('Nuevo Cliente' if not cid else 'Editar Cliente')
        self.geometry('600x450')  # Más grande
        self.transient(master)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (450 // 2)
        self.geometry(f'600x450+{x}+{y}')
        
        form = ttk.Frame(self, padding=20)
        form.pack(fill='both', expand=True)
        
        fields = [
            ('Nombre *', 'name'),
            ('Dirección', 'address'),
            ('DNI', 'dni'),
            ('Teléfono', 'phone'),
            ('Email', 'email')
        ]
        
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form, text=label, font=('Helvetica', 10, 'bold')).grid(row=i, column=0, sticky='w', pady=5)
            entry = ttk.Entry(form, width=40, font=('Helvetica', 11))
            entry.grid(row=i, column=1, pady=5, sticky='ew')
            self.entries[key] = entry
        
        self.entries['name'].focus()
        form.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill='x', side='bottom')
        ttk.Button(btn_frame, text='💾 Guardar', command=self.save).pack(side='right', padx=5)
        ttk.Button(btn_frame, text='❌ Cancelar', command=self.destroy).pack(side='right', padx=5)
        
        # Load data
        if cid:
            c = db.get_client(cid)
            if c:
                for key, entry in self.entries.items():
                    val = c[key]
                    if val:
                        entry.insert(0, val)
        
        self.bind('<Return>', lambda e: self.save())
        self.bind('<Escape>', lambda e: self.destroy())
    
    def save(self):
        name = self.entries['name'].get().strip()
        if not name:
            messagebox.showerror('Error', 'El nombre es obligatorio')
            self.entries['name'].focus()
            return
        address = self.entries['address'].get().strip()
        dni = self.entries['dni'].get().strip()
        phone = self.entries['phone'].get().strip()
        email = self.entries['email'].get().strip()
        if self.cid:
            db.update_client(self.cid, name, address, dni, phone, email)
        else:
            db.add_client(name, address, dni, phone, email)
        if self.on_save:
            self.on_save()
        self.destroy()

class QuotesFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        
        # Search bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side='left', padx=5)
        
        # Tree
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        cols = ('id', 'date', 'client', 'total')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)
        self.tree.heading('id', text='#')
        self.tree.heading('date', text='Fecha')
        self.tree.heading('client', text='Cliente')
        self.tree.heading('total', text='Total (€)')
        self.tree.column('id', width=60)
        self.tree.column('date', width=120)
        self.tree.column('client', width=250)
        self.tree.column('total', width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<Double-Button-1>', lambda e: self.export_pdf())
        
        # Buttons
        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=10, pady=10)
        ttk.Button(btns, text='➕ Nuevo Presupuesto', command=self.new_quote).pack(side='left', padx=5)
        ttk.Button(btns, text='✏️ Editar', command=self.edit_quote).pack(side='left', padx=5)
        ttk.Button(btns, text='🗑️ Eliminar', command=self.delete_quote).pack(side='left', padx=5)
        ttk.Button(btns, text='📄 Exportar PDF', command=self.export_pdf).pack(side='left', padx=5)
        ttk.Button(btns, text='👁️ Ver Detalles', command=self.view_details).pack(side='left', padx=5)
        
        self.refresh()
    
    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        search = self.search_var.get().lower()
        for q in db.list_quotes():
            if search and search not in (q['client_name'] or '').lower():
                continue
            # Calculate total
            _, items = db.get_quote(q['id'])
            total = sum(item['unit_price'] * item['quantity'] for item in items)
            total += q['labor_cost'] or 0
            self.tree.insert('', 'end', iid=str(q['id']), 
                           values=(q['id'], q['date'], q['client_name'] or '', f"{total:.2f}"))
    
    def new_quote(self):
        QuoteEditor(self, on_save=self.refresh)
    
    def edit_quote(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Atención', 'Selecciona un presupuesto para editar')
            return
        qid = int(sel[0])
        QuoteEditor(self, quote_id=qid, on_save=self.refresh)
    
    def delete_quote(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Atención', 'Selecciona un presupuesto para eliminar')
            return
        qid = int(sel[0])
        if messagebox.askyesno('Confirmar', f'¿Eliminar el presupuesto #{qid}?\n\nEsta acción no se puede deshacer.'):
            try:
                db.delete_quote(qid)
                self.refresh()
                messagebox.showinfo('Éxito', 'Presupuesto eliminado correctamente')
            except Exception as e:
                messagebox.showerror('Error', f'Error al eliminar: {str(e)}')
    
    def export_pdf(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Atención', 'Selecciona un presupuesto')
            return
        qid = int(sel[0])
        default_name = f"presupuesto_{qid}.pdf"
        p = filedialog.asksaveasfilename(defaultextension='.pdf', 
                                        initialfile=default_name,
                                        filetypes=[('PDF','*.pdf')])
        if not p:
            return
        try:
            export_quote_to_pdf(qid, p)
            messagebox.showinfo('Éxito', f'PDF exportado:\n{p}')
        except Exception as e:
            messagebox.showerror('Error', f'Error al exportar: {str(e)}')
    
    def view_details(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Atención', 'Selecciona un presupuesto')
            return
        qid = int(sel[0])
        QuoteViewer(self, qid)

class QuoteViewer(tk.Toplevel):
    def __init__(self, master, qid):
        super().__init__(master)
        self.qid = qid
        self.title(f'Presupuesto #{qid}')
        self.geometry('900x650')  # Más grande
        self.transient(master)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f'900x650+{x}+{y}')
        
        quote, items = db.get_quote(qid)
        
        # Header
        header = ttk.Frame(self, padding=20)
        header.pack(fill='x')
        ttk.Label(header, text=f"Presupuesto #{quote['id']}", font=('Helvetica', 16, 'bold')).pack(anchor='w')
        ttk.Label(header, text=f"Fecha: {quote['date']}").pack(anchor='w')
        ttk.Label(header, text=f"Cliente: {quote['client_name'] or 'N/A'}").pack(anchor='w')
        if quote['client_address']:
            ttk.Label(header, text=f"Dirección: {quote['client_address']}").pack(anchor='w')
        
        # Items
        items_frame = ttk.LabelFrame(self, text='Items', padding=10)
        items_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        cols = ('name', 'qty', 'price', 'total')
        tree = ttk.Treeview(items_frame, columns=cols, show='headings', height=10)
        tree.heading('name', text='Material')
        tree.heading('qty', text='Cantidad')
        tree.heading('price', text='Precio Unit.')
        tree.heading('total', text='Total')
        tree.pack(fill='both', expand=True)
        
        subtotal = 0
        for item in items:
            line_total = item['unit_price'] * item['quantity']
            subtotal += line_total
            tree.insert('', 'end', values=(item['name'], item['quantity'], 
                                          f"{item['unit_price']:.2f} €", 
                                          f"{line_total:.2f} €"))
        
        # Totals
        totals = ttk.Frame(self, padding=20)
        totals.pack(fill='x')
        ttk.Label(totals, text=f"Subtotal materiales: {subtotal:.2f} €", font=('Helvetica', 11)).pack(anchor='e')
        ttk.Label(totals, text=f"Mano de obra: {quote['labor_cost']:.2f} €", font=('Helvetica', 11)).pack(anchor='e')
        total = subtotal + (quote['labor_cost'] or 0)
        ttk.Label(totals, text=f"TOTAL: {total:.2f} €", font=('Helvetica', 14, 'bold')).pack(anchor='e')
        
        ttk.Button(self, text='Cerrar', command=self.destroy).pack(pady=10)

class QuoteEditor(tk.Toplevel):
    def __init__(self, master, quote_id=None, on_save=None):
        super().__init__(master)
        self.quote_id = quote_id
        self.on_save = on_save
        self.title('Editar Presupuesto' if quote_id else 'Nuevo Presupuesto')
        self.geometry('1200x750')  # Mucho más grande para ver todo
        self.transient(master)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.winfo_screenheight() // 2) - (750 // 2)
        self.geometry(f'1200x750+{x}+{y}')
        
        # Left panel - client & labor
        left = ttk.Frame(self, padding=15)
        left.pack(side='left', fill='y')
        
        ttk.Label(left, text='Cliente', font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0,5))
        
        # Client selection with quick add
        client_frame = ttk.Frame(left)
        client_frame.pack(fill='x', pady=5)
        self.clients_list = db.list_clients()
        client_names = [c['name'] for c in self.clients_list]
        self.client_cb = ttk.Combobox(client_frame, values=client_names, width=25)
        self.client_cb.pack(side='top', fill='x')
        ttk.Button(client_frame, text='➕ Nuevo cliente', 
                  command=self.quick_add_client).pack(fill='x', pady=5)
        
        ttk.Separator(left, orient='horizontal').pack(fill='x', pady=15)
        
        ttk.Label(left, text='Mano de obra (€)', font=('Helvetica', 11, 'bold')).pack(anchor='w')
        self.labor = ttk.Entry(left, width=15, font=('Helvetica', 12))
        self.labor.insert(0, '0')
        self.labor.pack(anchor='w', pady=5)
        
        ttk.Separator(left, orient='horizontal').pack(fill='x', pady=15)
        
        # Smart material search
        ttk.Label(left, text='Buscar y añadir material', font=('Helvetica', 11, 'bold')).pack(anchor='w', pady=(0,5))
        
        search_frame = ttk.Frame(left)
        search_frame.pack(fill='x', pady=5)
        self.mat_search_var = tk.StringVar()
        self.mat_search_var.trace('w', lambda *args: self.filter_materials())
        search_entry = ttk.Entry(search_frame, textvariable=self.mat_search_var, font=('Helvetica', 10))
        search_entry.pack(fill='x')
        ttk.Label(search_frame, text='🔍 Escribe para buscar...', font=('Helvetica', 8)).pack(anchor='w')
        
        # Results listbox
        results_frame = ttk.Frame(left)
        results_frame.pack(fill='both', expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.mat_listbox = tk.Listbox(results_frame, height=12, yscrollcommand=scrollbar.set, font=('Helvetica', 9))
        self.mat_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.mat_listbox.yview)
        
        self.mat_listbox.bind('<Double-Button-1>', lambda e: self.add_selected_material())
        
        self.materials_list = db.list_materials()
        self.filtered_materials = []
        self.filter_materials()
        
        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text='➕ Añadir', 
                  command=self.add_selected_material).pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(btn_frame, text='📦 Nuevo', 
                  command=self.quick_add_material).pack(side='right', fill='x', expand=True, padx=2)
        
        # Right panel - items list
        right = ttk.Frame(self, padding=15)
        right.pack(side='right', fill='both', expand=True)
        
        ttk.Label(right, text='Items del presupuesto', font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0,10))
        
        # Items treeview
        cols = ('name', 'price', 'qty', 'total')
        self.items_tree = ttk.Treeview(right, columns=cols, show='headings', height=15)
        self.items_tree.heading('name', text='Material')
        self.items_tree.heading('price', text='Precio')
        self.items_tree.heading('qty', text='Cantidad')
        self.items_tree.heading('total', text='Total')
        self.items_tree.column('name', width=250)
        self.items_tree.column('price', width=80)
        self.items_tree.column('qty', width=80)
        self.items_tree.column('total', width=100)
        self.items_tree.pack(fill='both', expand=True, pady=(0,10))
        
        self.items_tree.bind('<Double-Button-1>', lambda e: self.edit_item())
        
        item_btns = ttk.Frame(right)
        item_btns.pack(fill='x', pady=(0, 10))
        ttk.Button(item_btns, text='✏️ Editar', command=self.edit_item).pack(side='left', padx=5)
        ttk.Button(item_btns, text='🗑️ Quitar', command=self.remove_item).pack(side='left', padx=5)
        
        # Totals display
        totals_frame = ttk.LabelFrame(right, text='Resumen', padding=10)
        totals_frame.pack(fill='x', pady=10)
        self.total_label = ttk.Label(totals_frame, text='Total: 0.00 €', font=('Helvetica', 14, 'bold'))
        self.total_label.pack()
        
        # Bottom buttons - More prominent
        bottom = ttk.Frame(self, padding=15)
        bottom.pack(side='bottom', fill='x')
        
        # Cancelar button (left)
        ttk.Button(bottom, text='❌ Cancelar', command=self.destroy, 
                  style='secondary.TButton').pack(side='left', padx=5)
        
        # Guardar button (right, larger and more prominent)
        save_btn = ttk.Button(bottom, text='💾 GUARDAR PRESUPUESTO', command=self.save,
                             style='success.TButton')
        save_btn.pack(side='right', padx=5, ipadx=20, ipady=10)
        
        # Keyboard shortcut hint
        ttk.Label(bottom, text='(Ctrl+S para guardar | Esc para cancelar)', 
                 font=('Helvetica', 8), foreground='gray').pack(side='right', padx=10)
        
        self.items_data = []  # List of dicts with material info
        
        # Load existing quote if editing
        if quote_id:
            self.load_quote_data()
        
        # Keyboard shortcuts
        self.bind('<Escape>', lambda e: self.destroy())
        self.bind('<Control-s>', lambda e: self.save())
        self.bind('<Control-S>', lambda e: self.save())
        
        # Update totals on labor change
        self.labor.bind('<KeyRelease>', lambda e: self.update_totals())
    
    def quick_add_client(self):
        ClientEditor(self, None, on_save=self.reload_clients)
    
    def reload_clients(self):
        self.clients_list = db.list_clients()
        self.client_cb['values'] = [c['name'] for c in self.clients_list]
    
    def quick_add_material(self):
        MaterialEditor(self, None, on_save=self.reload_materials)
    
    def reload_materials(self):
        self.materials_list = db.list_materials()
        self.filter_materials()
    
    def filter_materials(self):
        """Filter materials based on search query"""
        query = self.mat_search_var.get().strip().lower()
        
        self.mat_listbox.delete(0, tk.END)
        self.filtered_materials = []
        
        if not query:
            # Show all materials grouped by category
            materials_by_cat = {}
            for m in self.materials_list:
                cat = m['category'] if m['category'] else 'Sin categoría'
                if cat not in materials_by_cat:
                    materials_by_cat[cat] = []
                materials_by_cat[cat].append(m)
            
            for cat in sorted(materials_by_cat.keys()):
                self.mat_listbox.insert(tk.END, f"━━ {cat} ━━")
                self.filtered_materials.append(None)  # Category separator
                for m in sorted(materials_by_cat[cat], key=lambda x: x['name']):
                    display = f"  {m['name']} - {m['price']:.2f}€"
                    self.mat_listbox.insert(tk.END, display)
                    self.filtered_materials.append(m)
        else:
            # Search and show matching materials
            matches = []
            for m in self.materials_list:
                score = 0
                name_lower = m['name'].lower()
                desc_lower = (m['description'] or '').lower()
                cat_lower = (m['category'] or '').lower()
                
                # Exact match in name gets highest priority
                if query == name_lower:
                    score = 100
                elif name_lower.startswith(query):
                    score = 90
                elif query in name_lower:
                    score = 80
                elif query in desc_lower:
                    score = 50
                elif query in cat_lower:
                    score = 40
                
                if score > 0:
                    matches.append((score, m))
            
            # Sort by score (highest first) then by name
            matches.sort(key=lambda x: (-x[0], x[1]['name']))
            
            if matches:
                for score, m in matches[:20]:  # Limit to top 20 results
                    cat = m['category'] if m['category'] else 'Sin categoría'
                    display = f"{m['name']} [{cat}] - {m['price']:.2f}€"
                    self.mat_listbox.insert(tk.END, display)
                    self.filtered_materials.append(m)
            else:
                self.mat_listbox.insert(tk.END, "❌ No se encontraron materiales")
                self.filtered_materials.append(None)
    
    def add_selected_material(self):
        selection = self.mat_listbox.curselection()
        if not selection:
            if self.filtered_materials and self.filtered_materials[0]:
                # Auto-select first if nothing selected
                selection = (0,)
            else:
                return
        
        idx = selection[0]
        if idx >= len(self.filtered_materials):
            return
            
        mat = self.filtered_materials[idx]
        if mat is None:  # Category separator
            return
        
        # Quick quantity dialog
        qty = simpledialog.askfloat('Cantidad', f'Cantidad de {mat["name"]}:', 
                                    initialvalue=1.0, minvalue=0.01)
        if qty is None:
            return
        
        self.items_data.append({
            'material_id': mat['id'],
            'name': mat['name'],
            'description': mat['description'],
            'image_path': mat['image_path'],
            'price': mat['price'],
            'quantity': qty
        })
        self.refresh_items()
        self.mat_search_var.set('')  # Clear search after adding
    
    def refresh_items(self):
        for r in self.items_tree.get_children():
            self.items_tree.delete(r)
        for i, item in enumerate(self.items_data):
            total = item['price'] * item['quantity']
            self.items_tree.insert('', 'end', iid=str(i),
                                  values=(item['name'], f"{item['price']:.2f}", 
                                         item['quantity'], f"{total:.2f}"))
        self.update_totals()
    
    def update_totals(self):
        """Update the total display"""
        subtotal = sum(item['price'] * item['quantity'] for item in self.items_data)
        try:
            labor_cost = float(self.labor.get() or 0)
        except ValueError:
            labor_cost = 0
        total = subtotal + labor_cost
        
        self.total_label.config(
            text=f'Subtotal: {subtotal:.2f} € | Mano de obra: {labor_cost:.2f} € | TOTAL: {total:.2f} €'
        )
    
    def edit_item(self):
        sel = self.items_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        item = self.items_data[idx]
        
        # Quick edit dialog
        new_qty = simpledialog.askfloat('Editar cantidad', 
                                       f'Nueva cantidad para {item["name"]}:', 
                                       initialvalue=item['quantity'],
                                       minvalue=0.01)
        if new_qty is not None:
            self.items_data[idx]['quantity'] = new_qty
            self.refresh_items()
    
    def remove_item(self):
        sel = self.items_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.items_data[idx]
        self.refresh_items()
    
    def load_quote_data(self):
        """Load existing quote data for editing"""
        quote, items = db.get_quote(self.quote_id)
        if not quote:
            messagebox.showerror('Error', 'Presupuesto no encontrado')
            self.destroy()
            return
        
        # Load quote info
        if quote['client_name']:
            self.client_cb.set(quote['client_name'])
        if quote['labor_cost']:
            self.labor.delete(0, tk.END)
            self.labor.insert(0, str(quote['labor_cost']))
        
        # Load items
        for item in items:
            self.items_data.append({
                'material_id': item['material_id'],
                'name': item['name'],
                'description': item['description'],
                'image_path': item['image_path'],
                'price': item['unit_price'],
                'quantity': item['quantity']
            })
        
        self.refresh_items()
    
    def save(self):
        client_name = self.client_cb.get().strip()
        if not client_name:
            messagebox.showerror('Error', 'Selecciona un cliente')
            self.client_cb.focus()
            return
        
        if not self.items_data:
            messagebox.showerror('Error', 'Añade al menos un item')
            return
        
        # Find client
        client = None
        for c in self.clients_list:
            if c['name'] == client_name:
                client = c
                break
        
        if client:
            client_id = client['id']
            client_address = client['address']
            client_dni = client['dni']
        else:
            client_id = None
            client_address = ''
            client_dni = ''
        
        try:
            labor = float(self.labor.get())
            if labor < 0:
                raise ValueError()
        except:
            messagebox.showerror('Error', 'Mano de obra inválida')
            self.labor.focus()
            return
        
        # Create or update quote
        if self.quote_id:
            # Update existing quote
            db.update_quote(self.quote_id, client_id, client_name, client_address, client_dni, labor_cost=labor)
            # Delete old items and add new ones
            quote, old_items = db.get_quote(self.quote_id)
            for old_item in old_items:
                db.delete_quote_item(old_item['id'])
            qid = self.quote_id
        else:
            # Create new quote
            qid = db.create_quote(client_id, client_name, client_address, client_dni, labor_cost=labor)
        
        # Add items
        for item in self.items_data:
            db.add_quote_item(qid, item['material_id'], item['name'], 
                            item['description'], item['image_path'],
                            item['price'], item['quantity'])
        
        action = 'actualizado' if self.quote_id else 'creado'
        messagebox.showinfo('Éxito', f'Presupuesto #{qid} {action}')
        
        if self.on_save:
            self.on_save()
        self.destroy()

def main():
    ensure_db()
    if HAS_TTKBOOTSTRAP:
        root = ttkb.Window(themename="flatly")
    else:
        root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
