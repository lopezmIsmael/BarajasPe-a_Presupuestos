"""
Editor WYSIWYG (What You See Is What You Get) para documentos de presupuesto
Muestra el documento con apariencia de PDF mientras permite edición directa
"""
import tkinter as tk
from tkinter import ttk, font as tkfont
import json


class PDFStyleEditor(ttk.Frame):
    """
    Editor de texto con apariencia de PDF que permite edición directa
    Combina visualización estilo documento con capacidad de edición
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        
        # Configuración del frame principal
        self.grid_rowconfigure(0, weight=0)  # Toolbar
        self.grid_rowconfigure(1, weight=1)  # Editor
        self.grid_columnconfigure(0, weight=1)
        
        # Barra de herramientas
        self._create_toolbar()
        
        # Frame que simula una hoja de papel
        self._create_paper_view()
        
        # Callback para actualización
        self.on_change_callback = None
    
    def _create_toolbar(self):
        """Crea la barra de herramientas con botones de formato"""
        toolbar = ttk.Frame(self, style='Toolbar.TFrame')
        toolbar.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # Contenedor interno con padding
        toolbar_inner = ttk.Frame(toolbar)
        toolbar_inner.pack(fill='x', padx=10, pady=5)
        
        # Tamaño de fuente
        ttk.Label(toolbar_inner, text="Tamaño:", font=('Helvetica', 9)).pack(side='left', padx=(0, 5))
        self.font_size_var = tk.StringVar(value="10")
        font_combo = ttk.Combobox(toolbar_inner, textvariable=self.font_size_var, 
                                  values=["8", "9", "10", "11", "12", "14", "16", "18", "20"],
                                  width=5, state='readonly')
        font_combo.pack(side='left', padx=(0, 10))
        font_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_font_size())
        
        # Separador
        ttk.Separator(toolbar_inner, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # Botón Negrita
        bold_btn = ttk.Button(toolbar_inner, text="N", width=3, 
                             command=lambda: self._toggle_format('bold'))
        bold_btn.pack(side='left', padx=2)
        
        # Botón Subrayado
        underline_btn = ttk.Button(toolbar_inner, text="S", width=3,
                                   command=lambda: self._toggle_format('underline'))
        underline_btn.pack(side='left', padx=2)
        
        # Botón Tachado
        strike_btn = ttk.Button(toolbar_inner, text="T", width=3,
                               command=lambda: self._toggle_format('strikethrough'))
        strike_btn.pack(side='left', padx=2)
        
        
        # Botón Viñeta
        bullet_btn = ttk.Button(toolbar_inner, text="•", width=3,
                               command=self._insert_bullet)
        bullet_btn.pack(side='left', padx=2)
    
    def _create_paper_view(self):
        """Crea el área de edición con apariencia de hoja de papel"""
        # Contenedor exterior (fondo gris como escritorio)
        outer_frame = tk.Frame(self, bg='#E0E0E0')
        outer_frame.grid(row=1, column=0, sticky='nsew')
        outer_frame.grid_rowconfigure(0, weight=1)
        outer_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas para scroll y centrado
        canvas = tk.Canvas(outer_frame, bg='#E0E0E0', highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(outer_frame, orient='vertical', command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno que contiene la "hoja de papel"
        inner_frame = tk.Frame(canvas, bg='#E0E0E0')
        canvas_frame = canvas.create_window((0, 0), window=inner_frame, anchor='n')
        
        # Centrar el contenido horizontalmente
        def center_content(event):
            canvas_width = event.width
            inner_width = inner_frame.winfo_reqwidth()
            x_position = max(0, (canvas_width - inner_width) // 2)
            canvas.coords(canvas_frame, x_position, 0)
        
        canvas.bind('<Configure>', center_content)
        
        # "Hoja de papel" - Frame con fondo blanco y sombra
        paper_container = tk.Frame(inner_frame, bg='#E0E0E0', padx=20, pady=20)
        paper_container.pack()
        
        # Sombra (Frame oscuro detrás)
        shadow = tk.Frame(paper_container, bg='#888888')
        shadow.place(x=5, y=5, relwidth=1, relheight=1)
        
        # Papel blanco (A4 proporciones: 210mm x 297mm ≈ 1:1.41)
        paper = tk.Frame(paper_container, bg='white', relief='flat', bd=0)
        paper.pack()
        
        # Área de texto dentro del papel
        text_container = tk.Frame(paper, bg='white')
        text_container.pack(fill='both', expand=True, padx=60, pady=80)  # Márgenes del papel
        
        # Widget de texto con estilo documento
        self.text = tk.Text(text_container, wrap='word',
                           font=('Times New Roman', 10),
                           width=70, height=35,
                           bg='white',
                           relief='flat',
                           borderwidth=0,
                           padx=10, pady=10)
        self.text.pack(fill='both', expand=True)
        
        # Configurar tags de formato
        self._setup_format_tags()
        
        # Bindings
        self.text.bind('<KeyRelease>', self._on_text_change)
        self.text.bind('<<Selection>>', self._on_selection_change)
        self.text.bind('<ButtonRelease-1>', self._on_selection_change)
        
        # Actualizar scrollregion cuando cambie el tamaño
        def update_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        inner_frame.bind('<Configure>', update_scroll)
        self.text.bind('<Configure>', update_scroll)
    
    def _setup_format_tags(self):
        """Configura los tags de formato del Text widget"""
        # Diferentes tamaños de fuente (configurar PRIMERO para que tengan menor prioridad)
        for size in [8, 9, 10, 11, 12, 14, 16, 18, 20]:
            tag_name = f'size_{size}'
            tag_font = tkfont.Font(family='Times New Roman', size=size)
            self.text.tag_configure(tag_name, font=tag_font)
            self.text.tag_raise(tag_name)  # Dar prioridad
            
            # Variantes con negrita
            tag_name_bold = f'size_{size}_bold'
            tag_font_bold = tkfont.Font(family='Times New Roman', size=size, weight='bold')
            self.text.tag_configure(tag_name_bold, font=tag_font_bold)
            self.text.tag_raise(tag_name_bold)
        
        # Negrita (configurar después para que tenga prioridad)
        bold_font = tkfont.Font(family='Times New Roman', size=10, weight='bold')
        self.text.tag_configure('bold', font=bold_font)
        self.text.tag_raise('bold')
        
        # Subrayado
        self.text.tag_configure('underline', underline=True)
        self.text.tag_raise('underline')
        
        # Tachado
        self.text.tag_configure('strikethrough', overstrike=True)
        self.text.tag_raise('strikethrough')
    
    def _toggle_format(self, format_type):
        """Aplica o quita formato al texto seleccionado"""
        try:
            sel_start = self.text.index(tk.SEL_FIRST)
            sel_end = self.text.index(tk.SEL_LAST)
            
            current_tags = self.text.tag_names(sel_start)
            
            if format_type in current_tags:
                self.text.tag_remove(format_type, sel_start, sel_end)
            else:
                self.text.tag_add(format_type, sel_start, sel_end)
            
            self._trigger_change_callback()
        except tk.TclError:
            pass
    
    def _apply_font_size(self):
        """Aplica el tamaño de fuente al texto seleccionado"""
        try:
            sel_start = self.text.index(tk.SEL_FIRST)
            sel_end = self.text.index(tk.SEL_LAST)
            
            size = self.font_size_var.get()
            
            # Quitar tags de tamaño anteriores
            for s in [8, 9, 10, 11, 12, 14, 16, 18, 20]:
                self.text.tag_remove(f'size_{s}', sel_start, sel_end)
                self.text.tag_remove(f'size_{s}_bold', sel_start, sel_end)
            
            current_tags = self.text.tag_names(sel_start)
            if 'bold' in current_tags:
                tag_name = f'size_{size}_bold'
            else:
                tag_name = f'size_{size}'
            
            self.text.tag_add(tag_name, sel_start, sel_end)
            self._trigger_change_callback()
        except tk.TclError:
            pass
    
    def _insert_bullet(self):
        """Inserta un punto de viñeta"""
        cursor_pos = self.text.index(tk.INSERT)
        line_start = self.text.index(f"{cursor_pos} linestart")
        line_content = self.text.get(line_start, f"{line_start} lineend")
        
        if not line_content.strip().startswith('•'):
            self.text.insert(line_start, '• ')
        else:
            line_end = self.text.index(f"{cursor_pos} lineend")
            self.text.insert(line_end, '\n• ')
            self.text.mark_set(tk.INSERT, f"{line_end} + 1 lines + 2 chars")
        
        self._trigger_change_callback()
    
    def _on_selection_change(self, event=None):
        """Actualiza el estado de los botones según la selección"""
        pass
    
    def _on_text_change(self, event=None):
        """Se llama cuando el contenido del texto cambia"""
        self._trigger_change_callback()
    
    def _trigger_change_callback(self):
        """Ejecuta el callback de cambio si está definido"""
        if self.on_change_callback:
            self.on_change_callback()
    
    def set_change_callback(self, callback):
        """Define la función callback para cambios en el contenido"""
        self.on_change_callback = callback
    
    def get_content_json(self):
        """Exporta el contenido con formato a JSON"""
        content = []
        text_content = self.text.get('1.0', 'end-1c')
        
        if not text_content:
            return json.dumps([])
        
        dump = self.text.dump('1.0', tk.END, tag=True, text=True)
        
        segments = []
        current_text = ""
        current_tags = set()
        
        for item in dump:
            item_type, value, index = item
            
            if item_type == 'text':
                current_text += value
            elif item_type == 'tagon':
                if current_text:
                    segments.append({'text': current_text, 'formats': list(current_tags)})
                    current_text = ""
                current_tags.add(value)
            elif item_type == 'tagoff':
                if current_text:
                    segments.append({'text': current_text, 'formats': list(current_tags)})
                    current_text = ""
                current_tags.discard(value)
        
        if current_text:
            segments.append({'text': current_text, 'formats': list(current_tags)})
        
        return json.dumps(segments, ensure_ascii=False)
    
    def set_content_json(self, json_string):
        """Carga contenido con formato desde JSON"""
        self.text.delete('1.0', tk.END)
        
        if not json_string:
            return
        
        try:
            segments = json.loads(json_string)
            
            for segment in segments:
                text = segment.get('text', '')
                formats = segment.get('formats', [])
                
                start_pos = self.text.index(tk.INSERT)
                self.text.insert(tk.INSERT, text)
                end_pos = self.text.index(tk.INSERT)
                
                for fmt in formats:
                    if fmt and not fmt.startswith('sel'):
                        self.text.tag_add(fmt, start_pos, end_pos)
        except json.JSONDecodeError:
            self.text.insert('1.0', json_string)
    
    def get_plain_text(self):
        """Obtiene el texto sin formato"""
        return self.text.get('1.0', 'end-1c')
    
    def set_plain_text(self, text):
        """Establece texto plano sin formato"""
        self.text.delete('1.0', tk.END)
        if text:
            self.text.insert('1.0', text)
    
    def clear(self):
        """Limpia todo el contenido"""
        self.text.delete('1.0', tk.END)
