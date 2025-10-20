"""
Módulo de acceso a base de datos - Funciones relacionadas con trabajadores
"""
import datetime
from .core import get_conn

def add_worker(name, phone='', role='Oficial', hourly_rate=0):
    """Añade un trabajador"""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO workers (name, phone, role, hourly_rate)
        VALUES (?, ?, ?, ?)
    ''', (name, phone, role, hourly_rate))

    conn.commit()
    worker_id = cur.lastrowid
    conn.close()
    return worker_id

def list_workers(active_only=True):
    """Lista todos los trabajadores"""
    conn = get_conn()
    cur = conn.cursor()
    
    if active_only:
        cur.execute('SELECT * FROM workers WHERE active=1 ORDER BY name')
    else:
        cur.execute('SELECT * FROM workers ORDER BY name')
        
    workers = cur.fetchall()
    conn.close()
    return workers

def get_worker(worker_id):
    """Obtiene un trabajador por ID"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM workers WHERE id=?', (worker_id,))
    worker = cur.fetchone()
    conn.close()
    return worker

def update_worker(worker_id, name=None, phone=None, role=None, hourly_rate=None, active=None):
    """Actualiza un trabajador"""
    conn = get_conn()
    cur = conn.cursor()

    # Obtener datos actuales
    cur.execute('SELECT * FROM workers WHERE id=?', (worker_id,))
    current = cur.fetchone()
    if not current:
        conn.close()
        return False

    # Actualizar solo los campos proporcionados
    update_data = {
        'name': name if name is not None else current['name'],
        'phone': phone if phone is not None else current['phone'],
        'role': role if role is not None else current.get('role', 'Oficial'),
        'hourly_rate': hourly_rate if hourly_rate is not None else current['hourly_rate'],
        'active': active if active is not None else current['active']
    }

    cur.execute('''
        UPDATE workers
        SET name=:name, phone=:phone, role=:role,
            hourly_rate=:hourly_rate, active=:active
        WHERE id=:id
    ''', {**update_data, 'id': worker_id})

    conn.commit()
    conn.close()
    return True

def delete_worker(worker_id):
    """Elimina un trabajador"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM workers WHERE id=?', (worker_id,))
    conn.commit()
    conn.close()