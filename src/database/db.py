import sqlite3
from pathlib import Path
import datetime

# Ruta ajustada para la nueva estructura - apunta a data/
DB_PATH = Path(__file__).parent.parent.parent / "data" / "data.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    
    # Migración: Añadir columna work_name si no existe
    try:
        cur.execute("SELECT work_name FROM quotes LIMIT 1")
    except sqlite3.OperationalError:
        # La columna no existe, añadirla
        cur.execute("ALTER TABLE quotes ADD COLUMN work_name TEXT")
        conn.commit()
    
    # Migración: Añadir columna supplier_price a materials si no existe
    try:
        cur.execute("SELECT supplier_price FROM materials LIMIT 1")
    except sqlite3.OperationalError:
        # La columna no existe, añadirla
        cur.execute("ALTER TABLE materials ADD COLUMN supplier_price REAL DEFAULT 0")
        conn.commit()
    
    # Migración: Añadir columna formatted_notes a quotes si no existe
    try:
        cur.execute("SELECT formatted_notes FROM quotes LIMIT 1")
    except sqlite3.OperationalError:
        # La columna no existe, añadirla
        cur.execute("ALTER TABLE quotes ADD COLUMN formatted_notes TEXT")
        conn.commit()
    
    # Migración: Añadir columna supplier_price a quote_items si no existe
    try:
        cur.execute("SELECT supplier_price FROM quote_items LIMIT 1")
    except sqlite3.OperationalError:
        # La columna no existe, añadirla
        cur.execute("ALTER TABLE quote_items ADD COLUMN supplier_price REAL DEFAULT 0")
        conn.commit()
    
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
    cur.execute('CREATE INDEX IF NOT EXISTS idx_clients_dni ON clients(dni)')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY,
        client_id INTEGER,
        client_name TEXT,
        client_address TEXT,
        client_dni TEXT,
        work_name TEXT,
        date TEXT,
        labor_cost REAL DEFAULT 0,
        notes TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
    ''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_quotes_date ON quotes(date)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_quotes_client ON quotes(client_name)')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS quote_items (
        id INTEGER PRIMARY KEY,
        quote_id INTEGER NOT NULL,
        material_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        image_path TEXT,
        unit_price REAL NOT NULL,
        supplier_price REAL DEFAULT 0,
        quantity REAL NOT NULL,
        FOREIGN KEY(quote_id) REFERENCES quotes(id),
        FOREIGN KEY(material_id) REFERENCES materials(id)
    )
    ''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_quote_items_quote ON quote_items(quote_id)')
    conn.commit()
    conn.close()

### Materials CRUD
def add_material(name, description, image_path, price, category="Sin categoría", supplier_price=0):
    # Normalizar categoría para evitar duplicados con diferente capitalización
    normalized_category = normalize_category(category)
    
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO materials (name,description,image_path,price,supplier_price,category) VALUES (?,?,?,?,?,?)',
                (name, description, image_path, price, supplier_price, normalized_category))
    conn.commit()
    mid = cur.lastrowid
    conn.close()
    return mid

def update_material(mid, name, description, image_path, price, category="Sin categoría", supplier_price=0):
    # Normalizar categoría para evitar duplicados con diferente capitalización
    normalized_category = normalize_category(category)
    
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('UPDATE materials SET name=?,description=?,image_path=?,price=?,supplier_price=?,category=? WHERE id=?',
                (name, description, image_path, price, supplier_price, normalized_category, mid))
    conn.commit()
    conn.close()

def delete_material(mid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM materials WHERE id=?', (mid,))
    conn.commit()
    conn.close()

def list_materials():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM materials ORDER BY name')
    rows = cur.fetchall()
    conn.close()
    return rows

def get_material(mid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM materials WHERE id=?', (mid,))
    row = cur.fetchone()
    conn.close()
    return row

def search_materials(query):
    """Search materials by name, description or category"""
    conn = get_conn()
    cur = conn.cursor()
    search_term = f'%{query}%'
    cur.execute('''SELECT * FROM materials 
                   WHERE name LIKE ? OR description LIKE ? OR category LIKE ?
                   ORDER BY name''',
                (search_term, search_term, search_term))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_categories():
    """Get all unique categories"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT category FROM materials ORDER BY category')
    rows = cur.fetchall()
    conn.close()
    return [r['category'] for r in rows]

def normalize_category(category):
    """Normaliza la categoría para que coincida con una existente (case-insensitive)"""
    if not category or category.strip() == '':
        return 'Sin categoría'
    
    category_input = category.strip()
    
    # Obtener todas las categorías existentes
    existing_categories = get_categories()
    
    # Crear un mapeo de lowercase a la versión original
    category_map = {cat.lower(): cat for cat in existing_categories if cat}
    
    # Buscar coincidencia case-insensitive
    category_lower = category_input.lower()
    if category_lower in category_map:
        return category_map[category_lower]
    
    # Si no existe, devolver la versión con capitalización del usuario
    return category_input

### Clients CRUD
def add_client(name, address, dni, phone, email):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO clients (name,address,dni,phone,email) VALUES (?,?,?,?,?)',
                (name, address, dni, phone, email))
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid

def update_client(cid, name, address, dni, phone, email):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('UPDATE clients SET name=?,address=?,dni=?,phone=?,email=? WHERE id=?',
                (name, address, dni, phone, email, cid))
    conn.commit()
    conn.close()

def delete_client(cid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM clients WHERE id=?', (cid,))
    conn.commit()
    conn.close()

def list_clients():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients ORDER BY name')
    rows = cur.fetchall()
    conn.close()
    return rows

def get_client(cid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients WHERE id=?', (cid,))
    row = cur.fetchone()
    conn.close()
    return row

### Quotes
def create_quote(client_id, client_name, client_address, client_dni, work_name=None, labor_cost=0, notes=None, formatted_notes=None):
    conn = get_conn()
    cur = conn.cursor()
    date = datetime.date.today().isoformat()
    cur.execute('''INSERT INTO quotes (client_id,client_name,client_address,client_dni,work_name,date,labor_cost,notes,formatted_notes)
                   VALUES (?,?,?,?,?,?,?,?,?)''',
                (client_id, client_name, client_address, client_dni, work_name, date, labor_cost, notes, formatted_notes))
    conn.commit()
    qid = cur.lastrowid
    conn.close()
    return qid

def add_quote_item(quote_id, material_id, name, description, image_path, unit_price, quantity, supplier_price=0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''INSERT INTO quote_items (quote_id,material_id,name,description,image_path,unit_price,supplier_price,quantity)
                   VALUES (?,?,?,?,?,?,?,?)''',
                (quote_id, material_id, name, description, image_path, unit_price, supplier_price, quantity))
    conn.commit()
    iid = cur.lastrowid
    conn.close()
    return iid

def list_quotes():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM quotes ORDER BY date DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

def get_quote(qid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM quotes WHERE id=?', (qid,))
    quote = cur.fetchone()
    cur.execute('SELECT * FROM quote_items WHERE quote_id=?', (qid,))
    items = cur.fetchall()
    conn.close()
    return quote, items

def delete_quote(qid):
    """Delete a quote and all its items"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM quote_items WHERE quote_id=?', (qid,))
    cur.execute('DELETE FROM quotes WHERE id=?', (qid,))
    conn.commit()
    conn.close()

def update_quote(qid, client_id, client_name, client_address, client_dni, work_name=None, labor_cost=0, notes=None, formatted_notes=None):
    """Update quote header info"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''UPDATE quotes SET client_id=?,client_name=?,client_address=?,client_dni=?,work_name=?,labor_cost=?,notes=?,formatted_notes=?
                   WHERE id=?''',
                (client_id, client_name, client_address, client_dni, work_name, labor_cost, notes, formatted_notes, qid))
    conn.commit()
    conn.close()

def delete_quote_item(item_id):
    """Delete a single item from a quote"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM quote_items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()

def update_quote_item(item_id, quantity, unit_price):
    """Update quantity or price of a quote item"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('UPDATE quote_items SET quantity=?, unit_price=? WHERE id=?',
                (quantity, unit_price, item_id))
    conn.commit()
    conn.close()
