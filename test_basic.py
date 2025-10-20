#!/usr/bin/env python3
"""
Script de prueba básico para verificar que todas las operaciones CRUD funcionan
"""
import sys
from src.database import db

def test_database():
    """Prueba operaciones básicas de base de datos"""
    print("🔍 Probando operaciones de base de datos...\n")

    # Inicializar DB
    print("✓ Inicializando base de datos...")
    db.init_db()

    # Test 1: Trabajadores
    print("\n📋 TEST 1: Trabajadores")
    try:
        # Crear
        worker_id = db.add_worker("Test Worker", "123456789", "Oficial")
        print(f"  ✓ Creado trabajador ID: {worker_id}")

        # Leer
        worker = db.get_worker(worker_id)
        print(f"  ✓ Leído trabajador: {worker['name']}")

        # Actualizar
        db.update_worker(worker_id, "Test Worker Updated", "987654321", "Encargado")
        worker = db.get_worker(worker_id)
        print(f"  ✓ Actualizado trabajador: {worker['name']} - {worker['role']}")

        # Listar
        workers = db.list_workers()
        print(f"  ✓ Total trabajadores: {len(workers)}")

        # Eliminar
        db.delete_worker(worker_id)
        print(f"  ✓ Eliminado trabajador ID: {worker_id}")

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

    # Test 2: Clientes
    print("\n📋 TEST 2: Clientes")
    try:
        # Crear
        client_id = db.add_client("Test Client", "Calle Test 123", "12345678A", "555-1234", "test@test.com")
        print(f"  ✓ Creado cliente ID: {client_id}")

        # Leer
        client = db.get_client(client_id)
        print(f"  ✓ Leído cliente: {client['name']}")

        # Actualizar
        db.update_client(client_id, "Test Client Updated", "Calle Test 456", "87654321B", "555-4321", "updated@test.com")
        client = db.get_client(client_id)
        print(f"  ✓ Actualizado cliente: {client['name']}")

        # Listar
        clients = db.list_clients()
        print(f"  ✓ Total clientes: {len(clients)}")

        # Eliminar
        db.delete_client(client_id)
        print(f"  ✓ Eliminado cliente ID: {client_id}")

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

    # Test 3: Materiales
    print("\n📋 TEST 3: Materiales")
    try:
        # Crear
        material_id = db.add_material("Test Material", "Descripción test", None, 100.50, "Categoría Test", 80.00)
        print(f"  ✓ Creado material ID: {material_id}")

        # Leer
        material = db.get_material(material_id)
        print(f"  ✓ Leído material: {material['name']} - {material['price']}€")

        # Actualizar
        db.update_material(material_id, "Test Material Updated", "Nueva descripción", None, 120.75, "Nueva Categoría", 95.00)
        material = db.get_material(material_id)
        print(f"  ✓ Actualizado material: {material['name']} - {material['price']}€")

        # Listar
        materials = db.list_materials()
        print(f"  ✓ Total materiales: {len(materials)}")

        # Categorías
        categories = db.list_material_categories()
        print(f"  ✓ Categorías encontradas: {len(categories)}")

        # Eliminar
        db.delete_material(material_id)
        print(f"  ✓ Eliminado material ID: {material_id}")

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

    # Test 4: Partes de Obra
    print("\n📋 TEST 4: Partes de Obra")
    try:
        from datetime import datetime
        today = datetime.today().strftime('%Y-%m-%d')

        # Crear trabajador y material para el parte
        worker_id = db.add_worker("Worker Para Parte", "111111111", "Oficial")
        material_id = db.add_material("Material Para Parte", "Test", None, 50.0, "Test", 40.0)

        # Crear parte de obra
        report_id = db.add_work_report(
            work_name="Test Obra",
            date_start=today,
            date_end=today,
            client_name="Test Cliente",
            quote_id=None
        )
        print(f"  ✓ Creado parte de obra ID: {report_id}")

        # Añadir asignación de trabajo
        assignment_id = db.add_work_assignment(report_id, worker_id, today, "Tarea test", 8.0)
        print(f"  ✓ Añadida asignación ID: {assignment_id}")

        # Añadir material usado
        material_usage_id = db.add_work_material(report_id, today, material_id, "Material Para Parte", 5)
        print(f"  ✓ Añadido material usado ID: {material_usage_id}")

        # Leer parte con detalles
        report = db.get_work_report(report_id, include_details=True)
        print(f"  ✓ Leído parte: {report['work_name']}")
        print(f"  ✓ Trabajadores en parte: {len(report.get('workers', {}))}")
        print(f"  ✓ Materiales en parte: {len(report.get('materials', {}))}")

        # Listar partes
        reports = db.list_work_reports()
        print(f"  ✓ Total partes: {len(reports)}")

        # Eliminar
        db.delete_work_report(report_id)
        print(f"  ✓ Eliminado parte ID: {report_id}")

        # Limpiar
        db.delete_worker(worker_id)
        db.delete_material(material_id)

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n✅ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
    return True

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
