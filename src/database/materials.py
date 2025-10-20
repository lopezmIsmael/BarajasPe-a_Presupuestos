"""
Módulo de acceso a base de datos - Funciones relacionadas con materiales
"""
import datetime
from .core import get_conn

def add_material(name, description='', image_path='', price=0, supplier_price=0, category='Sin categoría'):
    """Añade un material"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO materials (
            name, description, image_path, price, supplier_price, category
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, description, image_path, price, supplier_price, category))
    
    conn.commit()
    material_id = cur.lastrowid
    conn.close()
    return material_id

def list_materials():
    """Lista todos los materiales"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM materials ORDER BY name')
    rows = cur.fetchall()
    # Convertir sqlite3.Row a dict para consumo más sencillo en la UI
    materials = [dict(r) for r in rows]
    conn.close()
    return materials

def get_material(material_id):
    """Obtiene un material por ID"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM materials WHERE id=?', (material_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_material(material_id, name=None, description=None, image_path=None, price=None, supplier_price=None, category=None):
    """Actualiza un material"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Obtener datos actuales
    cur.execute('SELECT * FROM materials WHERE id=?', (material_id,))
    current = cur.fetchone()
    if not current:
        conn.close()
        return False
    
    # Actualizar solo los campos proporcionados
    update_data = {
        'name': name if name is not None else current['name'],
        'description': description if description is not None else current['description'],
        'image_path': image_path if image_path is not None else current['image_path'],
        'price': price if price is not None else current['price'],
        'supplier_price': supplier_price if supplier_price is not None else current['supplier_price'],
        'category': category if category is not None else current['category']
    }
    
    cur.execute('''
        UPDATE materials
        SET name=:name, description=:description, image_path=:image_path,
            price=:price, supplier_price=:supplier_price, category=:category
        WHERE id=:id
    ''', {**update_data, 'id': material_id})
    
    conn.commit()
    conn.close()
    return True

def delete_material(material_id):
    """Elimina un material"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM materials WHERE id=?', (material_id,))
    conn.commit()
    conn.close()

def list_material_categories():
    """Lista todas las categorías de materiales"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT category FROM materials ORDER BY category')
    categories = [row['category'] for row in cur.fetchall()]
    conn.close()
    return categories