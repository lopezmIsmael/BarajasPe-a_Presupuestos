"""
Módulo core de acceso a base de datos - Funciones básicas compartidas
"""
import sqlite3
from pathlib import Path

# Ruta ajustada para la nueva estructura - apunta a data/
DB_PATH = Path(__file__).parent.parent.parent / "data" / "data.db"

def get_conn():
    """Obtiene una conexión a la base de datos"""
    # Crear el directorio data si no existe
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos y realiza migraciones necesarias"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Crear tablas principales
    cur.execute('''
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        image_path TEXT,
        price REAL NOT NULL DEFAULT 0,
        supplier_price REAL DEFAULT 0,
        category TEXT DEFAULT "Sin categoría"
    )
    ''')
    
    cur.execute('CREATE INDEX IF NOT EXISTS idx_materials_name ON materials(name)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_materials_category ON materials(category)')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        address TEXT,
        dni TEXT,
        phone TEXT,
        email TEXT
    )
    ''')
    
    cur.execute('CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name)')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY,
        client_id INTEGER,
        client_name TEXT NOT NULL,
        client_address TEXT,
        client_dni TEXT,
        work_name TEXT NOT NULL,
        date TEXT NOT NULL,
        labor_cost REAL DEFAULT 0,
        notes TEXT,
        formatted_notes TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    )
    ''')
    
    cur.execute('CREATE INDEX IF NOT EXISTS idx_quotes_client ON quotes(client_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_quotes_date ON quotes(date)')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS quote_items (
        id INTEGER PRIMARY KEY,
        quote_id INTEGER NOT NULL,
        material_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        image_path TEXT,
        unit_price REAL NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        supplier_price REAL DEFAULT 0,
        FOREIGN KEY (quote_id) REFERENCES quotes(id),
        FOREIGN KEY (material_id) REFERENCES materials(id)
    )
    ''')
    
    cur.execute('CREATE INDEX IF NOT EXISTS idx_quote_items_quote ON quote_items(quote_id)')
    # Migración: añadir columna image_path a quote_items si no existe
    try:
        cur.execute("ALTER TABLE quote_items ADD COLUMN image_path TEXT")
    except sqlite3.OperationalError:
        pass  # ya existe
    
    # Crear tabla de trabajadores
    cur.execute('''
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        dni TEXT,
        phone TEXT,
        role TEXT DEFAULT 'Oficial',
        hourly_rate REAL DEFAULT 0,
        active INTEGER DEFAULT 1
    )
    ''')

    # Migración: Añadir columna 'role' si no existe
    try:
        cur.execute("ALTER TABLE workers ADD COLUMN role TEXT DEFAULT 'Oficial'")
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    cur.execute('CREATE INDEX IF NOT EXISTS idx_workers_name ON workers(name)')
    
    # Crear tabla de partes de obra
    cur.execute('''
    CREATE TABLE IF NOT EXISTS work_reports (
        id INTEGER PRIMARY KEY,
        client_name TEXT NOT NULL,
        work_name TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        tools_used TEXT,
        notes TEXT,
        status TEXT DEFAULT "En progreso",
        quote_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (quote_id) REFERENCES quotes(id)
    )
    ''')
    
    cur.execute('CREATE INDEX IF NOT EXISTS idx_work_reports_start_date ON work_reports(start_date)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_work_reports_quote ON work_reports(quote_id)')
    
    # Tabla para registrar las asignaciones de trabajadores a partes de obra
    cur.execute('''
    CREATE TABLE IF NOT EXISTS worker_assignments (
        id INTEGER PRIMARY KEY,
        work_report_id INTEGER NOT NULL,
        worker_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        hours REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (work_report_id) REFERENCES work_reports(id),
        FOREIGN KEY (worker_id) REFERENCES workers(id)
    )
    ''')
    
    cur.execute('CREATE INDEX IF NOT EXISTS idx_worker_assignments_report ON worker_assignments(work_report_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_worker_assignments_worker ON worker_assignments(worker_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_worker_assignments_date ON worker_assignments(date)')

    # Tabla de asignaciones de trabajo (NUEVA estructura)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS work_report_assignments (
        id INTEGER PRIMARY KEY,
        report_id INTEGER NOT NULL,
        worker_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        task TEXT,
        hours REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (report_id) REFERENCES work_reports(id),
        FOREIGN KEY (worker_id) REFERENCES workers(id)
    )
    ''')

    cur.execute('CREATE INDEX IF NOT EXISTS idx_work_report_assignments_report ON work_report_assignments(report_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_work_report_assignments_worker ON work_report_assignments(worker_id)')

    # Tabla de materiales usados en partes de obra
    cur.execute('''
    CREATE TABLE IF NOT EXISTS work_report_materials (
        id INTEGER PRIMARY KEY,
        report_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        material_id INTEGER,
        material_name TEXT NOT NULL,
        quantity REAL NOT NULL DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (report_id) REFERENCES work_reports(id),
        FOREIGN KEY (material_id) REFERENCES materials(id)
    )
    ''')

    cur.execute('CREATE INDEX IF NOT EXISTS idx_work_report_materials_report ON work_report_materials(report_id)')

    conn.commit()
    conn.close()