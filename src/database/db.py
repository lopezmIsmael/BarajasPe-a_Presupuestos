"""
Módulo de acceso a base de datos - Punto de entrada principal
"""
import datetime
from .core import get_conn, init_db
from . import quotes, materials, workers

# Re-exportar funciones comunes
from .quotes import (
    add_quote, get_quote, list_quotes, update_quote, delete_quote,
    add_quote_item, update_quote_item, delete_quote_item,
    add_client, get_client, list_clients, update_client, delete_client
)
from .materials import (
    add_material, get_material, list_materials, update_material, delete_material,
    list_material_categories
)
from .workers import (
    add_worker, get_worker, list_workers, update_worker, delete_worker
)

# Compatibilidad: algunas partes del código usan `db.create_quote` en vez de
# `db.add_quote` o `db_quotes.add_quote`. Proporcionamos un envoltorio
# `create_quote` que delega a `quotes.add_quote` y mantiene la firma esperada.
def create_quote(client_id, client_name, client_address, client_dni, work_name, labor_cost=0, notes='', formatted_notes=None):
    return quotes.add_quote(client_id, client_name, client_address, client_dni, work_name, labor_cost=labor_cost, notes=notes, formatted_notes=formatted_notes)

### CRUD Partes de Trabajo

def add_work_report(work_name, date_start, date_end, client_name=None, quote_id=None, 
                   tools_used='', notes=''):
    """
    Crea un nuevo parte de trabajo.
    
    Args:
        work_name (str): Nombre del trabajo
        date_start (str): Fecha de inicio (YYYY-MM-DD)
        date_end (str): Fecha de fin (YYYY-MM-DD)
        client_name (str, opcional): Nombre del cliente
        quote_id (int, opcional): ID del presupuesto asociado
        tools_used (str, opcional): Herramientas usadas
        notes (str, opcional): Notas adicionales
        
    Returns:
        int: ID del parte creado
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Obtener datos del presupuesto si se proporciona
    if quote_id:
        quote, items = quotes.get_quote(quote_id)
        if quote:
            client_name = client_name or quote['client_name']
    
    # Crear el parte
    cur.execute('''
        INSERT INTO work_reports (
            work_name, client_name, start_date, end_date, quote_id,
            tools_used, notes, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        work_name, client_name, date_start, date_end, quote_id,
        tools_used, notes, 'En progreso'
    ))
    
    report_id = cur.lastrowid
    
    # Si hay presupuesto, importar materiales del presupuesto
    if quote_id and quote:
        for item in items:
            # Crear una entrada por cada material del presupuesto
            cur.execute('''
                INSERT INTO work_report_materials (
                    report_id, date, material_id, material_name, quantity
                ) VALUES (?, ?, ?, ?, 0)
            ''', (
                report_id, date_start, item['material_id'], item['name']
            ))
    
    conn.commit()
    conn.close()
    return report_id

def list_work_reports(quote_id=None, include_details=False):
    """
    Lista partes de obra, opcionalmente filtrados por presupuesto.
    
    Args:
        quote_id (int, opcional): ID del presupuesto para filtrar
        include_details (bool, opcional): Si True, incluye trabajadores y materiales
        
    Returns:
        list: Lista de partes encontrados
    """
    conn = get_conn()
    cur = conn.cursor()
    
    if quote_id:
        cur.execute('''
            SELECT * FROM work_reports 
            WHERE quote_id=?
            ORDER BY start_date DESC
        ''', (quote_id,))
    else:
        cur.execute('SELECT * FROM work_reports ORDER BY start_date DESC')
    
    reports = []
    for row in cur.fetchall():
        report = dict(row)
        
        if include_details:
            # Obtener lista de trabajadores únicos
            cur.execute('''
                SELECT DISTINCT w.name
                FROM work_report_assignments a
                JOIN workers w ON w.id = a.worker_id
                WHERE a.report_id=?
                ORDER BY w.name
            ''', (report['id'],))
            report['workers'] = [r['name'] for r in cur.fetchall()]
            
            # Obtener lista de materiales únicos
            cur.execute('''
                SELECT DISTINCT material_name
                FROM work_report_materials
                WHERE report_id=?
                ORDER BY material_name
            ''', (report['id'],))
            report['materials'] = [r['material_name'] for r in cur.fetchall()]
        
        reports.append(report)
    
    conn.close()
    return reports

def get_work_report(report_id, include_details=True):
    """
    Obtiene un parte de trabajo por ID
    
    Args:
        report_id (int): ID del parte a obtener
        include_details (bool, opcional): Si True, incluye asignaciones y materiales
        
    Returns:
        dict: Datos del parte o None si no existe
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Obtener datos básicos
    cur.execute('SELECT * FROM work_reports WHERE id=?', (report_id,))
    report = cur.fetchone()
    if not report:
        conn.close()
        return None
    
    # Convertir a diccionario
    report_dict = dict(report)
    
    if include_details:
        # Obtener asignaciones de trabajo agrupadas por trabajador y fecha
        assignments_by_worker = {}
        cur.execute('''
            SELECT a.*, w.name as worker_name
            FROM work_report_assignments a
            JOIN workers w ON w.id = a.worker_id
            WHERE a.report_id=?
            ORDER BY a.date, w.name
        ''', (report_id,))
        
        for row in cur.fetchall():
            worker_id = row['worker_id']
            if worker_id not in assignments_by_worker:
                assignments_by_worker[worker_id] = {
                    'name': row['worker_name'],
                    'assignments': []
                }
            assignments_by_worker[worker_id]['assignments'].append({
                'date': row['date'],
                'hours': row['hours'],
                'task': row['task']
            })
        
        report_dict['workers'] = assignments_by_worker
        
        # Obtener materiales agrupados por fecha
        materials_by_date = {}
        cur.execute('''
            SELECT * FROM work_report_materials
            WHERE report_id=?
            ORDER BY date, material_name
        ''', (report_id,))
        
        for row in cur.fetchall():
            date = row['date']
            if date not in materials_by_date:
                materials_by_date[date] = []
            materials_by_date[date].append({
                'id': row['material_id'],
                'name': row['material_name'],
                'quantity': row['quantity'],
                'notes': row['notes']
            })
        
        report_dict['materials'] = materials_by_date
    
    conn.close()
    return report_dict

def update_work_report(report_id, work_name=None, client_name=None, 
                      date_start=None, date_end=None, tools_used=None, 
                      notes=None, status=None):
    """
    Actualiza los datos básicos de un parte de trabajo
    
    Args:
        report_id (int): ID del parte a actualizar
        work_name (str, opcional): Nuevo nombre del trabajo
        client_name (str, opcional): Nuevo nombre del cliente
        date_start (str, opcional): Nueva fecha inicial (YYYY-MM-DD)
        date_end (str, opcional): Nueva fecha final (YYYY-MM-DD)
        tools_used (str, opcional): Nuevas herramientas usadas
        notes (str, opcional): Nuevas notas adicionales
        status (str, opcional): Nuevo estado del parte
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Obtener datos actuales
    cur.execute('SELECT * FROM work_reports WHERE id=?', (report_id,))
    current = cur.fetchone()
    if not current:
        conn.close()
        return False
    
    # Actualizar solo los campos proporcionados
    update_data = {
        'work_name': work_name if work_name is not None else current['work_name'],
        'client_name': client_name if client_name is not None else current['client_name'],
        'start_date': date_start if date_start is not None else current['start_date'],
        'end_date': date_end if date_end is not None else current['end_date'],
        'tools_used': tools_used if tools_used is not None else current['tools_used'],
        'notes': notes if notes is not None else current['notes'],
        'status': status if status is not None else current['status']
    }
    
    # Ejecutar actualización
    cur.execute('''
        UPDATE work_reports
        SET work_name=:work_name,
            client_name=:client_name,
            start_date=:start_date,
            end_date=:end_date,
            tools_used=:tools_used,
            notes=:notes,
            status=:status,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=:id
    ''', {**update_data, 'id': report_id})
    
    conn.commit()
    conn.close()
    return True

def add_work_assignment(report_id, worker_id, date, task=None, hours=0):
    """
    Añade o actualiza una asignación de trabajo
    
    Args:
        report_id (int): ID del parte
        worker_id (int): ID del trabajador
        date (str): Fecha (YYYY-MM-DD)
        task (str, opcional): Descripción de la tarea
        hours (float, opcional): Horas trabajadas
    
    Returns:
        int: ID de la asignación creada
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Comprobar si ya existe una asignación para ese día
    cur.execute('''
        SELECT id FROM work_report_assignments
        WHERE report_id=? AND worker_id=? AND date=?
    ''', (report_id, worker_id, date))
    
    existing = cur.fetchone()
    if existing:
        # Actualizar existente
        cur.execute('''
            UPDATE work_report_assignments
            SET task=?, hours=?
            WHERE id=?
        ''', (task, hours, existing['id']))
        assignment_id = existing['id']
    else:
        # Crear nueva
        cur.execute('''
            INSERT INTO work_report_assignments (
                report_id, worker_id, date, task, hours
            ) VALUES (?, ?, ?, ?, ?)
        ''', (report_id, worker_id, date, task, hours))
        assignment_id = cur.lastrowid
    
    # Actualizar timestamp del parte
    cur.execute('''
        UPDATE work_reports
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (report_id,))
    
    conn.commit()
    conn.close()
    return assignment_id

def add_work_material(report_id, date, material_id=None, material_name=None, quantity=0, notes=None):
    """
    Añade o actualiza un material usado en el parte
    
    Args:
        report_id (int): ID del parte
        date (str): Fecha de uso (YYYY-MM-DD)
        material_id (int, opcional): ID del material
        material_name (str, opcional): Nombre del material
        quantity (float, opcional): Cantidad usada
        notes (str, opcional): Notas adicionales
    
    Returns:
        int: ID del uso de material creado
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Si se proporciona material_id, obtener el nombre
    if material_id and not material_name:
        cur.execute('SELECT name FROM materials WHERE id=?', (material_id,))
        result = cur.fetchone()
        if result:
            material_name = result['name']
    
    # Si solo hay nombre, buscar el id
    elif material_name and not material_id:
        cur.execute('SELECT id FROM materials WHERE name=?', (material_name,))
        result = cur.fetchone()
        if result:
            material_id = result['id']
    
    if not material_name:
        raise ValueError('Se requiere al menos el nombre del material')
    
    # Comprobar si ya existe para esa fecha
    cur.execute('''
        SELECT id FROM work_report_materials
        WHERE report_id=? AND date=? AND material_id=?
    ''', (report_id, date, material_id))
    
    existing = cur.fetchone()
    if existing:
        # Actualizar existente
        cur.execute('''
            UPDATE work_report_materials
            SET quantity=?, notes=?
            WHERE id=?
        ''', (quantity, notes, existing['id']))
        material_usage_id = existing['id']
    else:
        # Crear nuevo
        cur.execute('''
            INSERT INTO work_report_materials (
                report_id, date, material_id, material_name, quantity, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (report_id, date, material_id, material_name, quantity, notes))
        material_usage_id = cur.lastrowid
    
    # Actualizar timestamp del parte
    cur.execute('''
        UPDATE work_reports
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (report_id,))
    
    conn.commit()
    conn.close()
    return material_usage_id

def delete_work_report(report_id):
    """Elimina un parte de trabajo y sus datos relacionados"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Eliminar relaciones
    cur.execute('DELETE FROM work_report_assignments WHERE report_id=?', (report_id,))
    cur.execute('DELETE FROM work_report_materials WHERE report_id=?', (report_id,))
    
    # Eliminar parte principal
    cur.execute('DELETE FROM work_reports WHERE id=?', (report_id,))
    
    conn.commit()
    conn.close()