"""
Módulo de acceso a base de datos - Funciones relacionadas con presupuestos
"""
import datetime
from .core import get_conn

### Clients CRUD
def add_client(name, address='', dni='', phone='', email=''):
    """Añade un cliente"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO clients (name, address, dni, phone, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, address, dni, phone, email))
    
    conn.commit()
    client_id = cur.lastrowid
    conn.close()
    return client_id

def list_clients():
    """Lista todos los clientes"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients ORDER BY name')
    clients = cur.fetchall()
    conn.close()
    return clients

def get_client(client_id):
    """Obtiene un cliente por ID"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients WHERE id=?', (client_id,))
    client = cur.fetchone()
    conn.close()
    return client

def update_client(client_id, name, address=None, dni=None, phone=None, email=None):
    """Actualiza un cliente"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Obtener datos actuales
    cur.execute('SELECT * FROM clients WHERE id=?', (client_id,))
    current = cur.fetchone()
    if not current:
        conn.close()
        return False
    
    # Actualizar solo los campos proporcionados
    update_data = {
        'name': name if name is not None else current['name'],
        'address': address if address is not None else current['address'],
        'dni': dni if dni is not None else current['dni'],
        'phone': phone if phone is not None else current['phone'],
        'email': email if email is not None else current['email']
    }
    
    cur.execute('''
        UPDATE clients
        SET name=:name, address=:address, dni=:dni, phone=:phone, email=:email
        WHERE id=:id
    ''', {**update_data, 'id': client_id})
    
    conn.commit()
    conn.close()
    return True

def delete_client(client_id):
    """Elimina un cliente"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM clients WHERE id=?', (client_id,))
    conn.commit()
    conn.close()

### Quotes CRUD
def add_quote(client_id, client_name, client_address, client_dni, work_name, labor_cost=0, notes=''):
    """Añade un presupuesto"""
    conn = get_conn()
    cur = conn.cursor()
    
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    cur.execute('''
        INSERT INTO quotes (
            client_id, client_name, client_address, client_dni,
            work_name, date, labor_cost, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (client_id, client_name, client_address, client_dni, work_name, date, labor_cost, notes))
    
    conn.commit()
    quote_id = cur.lastrowid
    conn.close()
    return quote_id

def list_quotes():
    """Lista todos los presupuestos"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM quotes ORDER BY date DESC')
    quotes = cur.fetchall()
    conn.close()
    return quotes

def get_quote(quote_id):
    """Obtiene un presupuesto y sus items por ID"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Obtener presupuesto
    cur.execute('SELECT * FROM quotes WHERE id=?', (quote_id,))
    quote = cur.fetchone()
    
    if not quote:
        conn.close()
        return None, []
    
    # Obtener items
    cur.execute('SELECT * FROM quote_items WHERE quote_id=?', (quote_id,))
    items = cur.fetchall()
    
    conn.close()
    return quote, items

def update_quote(quote_id, client_id=None, client_name=None, client_address=None, 
                client_dni=None, work_name=None, labor_cost=None, notes=None):
    """Actualiza un presupuesto"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Obtener datos actuales
    cur.execute('SELECT * FROM quotes WHERE id=?', (quote_id,))
    current = cur.fetchone()
    if not current:
        conn.close()
        return False
    
    # Actualizar solo los campos proporcionados
    update_data = {
        'client_id': client_id if client_id is not None else current['client_id'],
        'client_name': client_name if client_name is not None else current['client_name'],
        'client_address': client_address if client_address is not None else current['client_address'],
        'client_dni': client_dni if client_dni is not None else current['client_dni'],
        'work_name': work_name if work_name is not None else current['work_name'],
        'labor_cost': labor_cost if labor_cost is not None else current['labor_cost'],
        'notes': notes if notes is not None else current['notes']
    }
    
    cur.execute('''
        UPDATE quotes 
        SET client_id=:client_id, client_name=:client_name, 
            client_address=:client_address, client_dni=:client_dni,
            work_name=:work_name, labor_cost=:labor_cost, notes=:notes
        WHERE id=?
    ''', {**update_data, 'id': quote_id})
    
    conn.commit()
    conn.close()
    return True

def delete_quote(quote_id):
    """Elimina un presupuesto y sus items"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Eliminar items primero
    cur.execute('DELETE FROM quote_items WHERE quote_id=?', (quote_id,))
    # Eliminar presupuesto
    cur.execute('DELETE FROM quotes WHERE id=?', (quote_id,))
    
    conn.commit()
    conn.close()

### Quote Items CRUD
def add_quote_item(quote_id, material_id, name, description, unit_price, quantity, supplier_price=0):
    """Añade un item a un presupuesto"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO quote_items (
            quote_id, material_id, name, description,
            unit_price, quantity, supplier_price
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (quote_id, material_id, name, description, unit_price, quantity, supplier_price))
    
    conn.commit()
    item_id = cur.lastrowid
    conn.close()
    return item_id

def update_quote_item(item_id, quantity=None, unit_price=None):
    """Actualiza cantidad o precio de un item"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Obtener datos actuales
    cur.execute('SELECT * FROM quote_items WHERE id=?', (item_id,))
    current = cur.fetchone()
    if not current:
        conn.close()
        return False
    
    # Actualizar solo los campos proporcionados
    update_data = {
        'quantity': quantity if quantity is not None else current['quantity'],
        'unit_price': unit_price if unit_price is not None else current['unit_price']
    }
    
    cur.execute('''
        UPDATE quote_items 
        SET quantity=:quantity, unit_price=:unit_price 
        WHERE id=?
    ''', {**update_data, 'id': item_id})
    
    conn.commit()
    conn.close()
    return True

def delete_quote_item(item_id):
    """Elimina un item de un presupuesto"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM quote_items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()