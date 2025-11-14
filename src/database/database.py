"""
Capa de acceso a datos y gestión de la base de datos SQLite.
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from sqlalchemy.engine import Engine
from src.models.models import Base, Cliente, Trabajador, Material, Presupuesto, LineaPresupuesto, ParteTrabajo, DetalleManoObra, MaterialUsado


# Habilitar claves foráneas en SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Database:
    """Clase para gestionar la base de datos"""

    def __init__(self, db_path='constructora.db'):
        """
        Inicializa la conexión a la base de datos.

        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def create_tables(self):
        """Crea todas las tablas en la base de datos"""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Retorna una nueva sesión de base de datos"""
        return self.Session()

    def close_session(self, session):
        """Cierra una sesión"""
        if session:
            session.close()


class ClienteDAO:
    """Data Access Object para Cliente"""

    def __init__(self, db: Database):
        self.db = db

    def crear(self, **kwargs):
        """Crea un nuevo cliente"""
        session = self.db.get_session()
        try:
            cliente = Cliente(**kwargs)
            session.add(cliente)
            session.commit()
            session.refresh(cliente)
            return cliente
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def obtener_por_id(self, id):
        """Obtiene un cliente por ID"""
        session = self.db.get_session()
        try:
            return session.query(Cliente).filter(Cliente.id == id).first()
        finally:
            self.db.close_session(session)

    def obtener_todos(self):
        """Obtiene todos los clientes"""
        session = self.db.get_session()
        try:
            return session.query(Cliente).all()
        finally:
            self.db.close_session(session)

    def actualizar(self, id, **kwargs):
        """Actualiza un cliente"""
        session = self.db.get_session()
        try:
            cliente = session.query(Cliente).filter(Cliente.id == id).first()
            if cliente:
                for key, value in kwargs.items():
                    if hasattr(cliente, key):
                        setattr(cliente, key, value)
                cliente.fecha_actualizacion = datetime.now()
                session.commit()
                session.refresh(cliente)
                return cliente
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def eliminar(self, id):
        """Elimina un cliente"""
        session = self.db.get_session()
        try:
            cliente = session.query(Cliente).filter(Cliente.id == id).first()
            if cliente:
                session.delete(cliente)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def buscar(self, criterio):
        """Busca clientes por nombre, empresa o NIF"""
        session = self.db.get_session()
        try:
            criterio_lower = f"%{criterio.lower()}%"
            return session.query(Cliente).filter(
                (Cliente.nombre.ilike(criterio_lower)) |
                (Cliente.apellidos.ilike(criterio_lower)) |
                (Cliente.empresa.ilike(criterio_lower)) |
                (Cliente.nif_cif.ilike(criterio_lower))
            ).all()
        finally:
            self.db.close_session(session)


class TrabajadorDAO:
    """Data Access Object para Trabajador"""

    def __init__(self, db: Database):
        self.db = db

    def crear(self, **kwargs):
        """Crea un nuevo trabajador"""
        session = self.db.get_session()
        try:
            # Validar DNI único solo si tiene valor
            dni = kwargs.get('dni', '').strip()
            if dni:
                existe = session.query(Trabajador).filter(Trabajador.dni == dni).first()
                if existe:
                    raise ValueError(f"Ya existe un trabajador con el DNI {dni}")

            trabajador = Trabajador(**kwargs)
            session.add(trabajador)
            session.commit()
            session.refresh(trabajador)
            return trabajador
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def obtener_por_id(self, id):
        """Obtiene un trabajador por ID"""
        session = self.db.get_session()
        try:
            return session.query(Trabajador).filter(Trabajador.id == id).first()
        finally:
            self.db.close_session(session)

    def obtener_todos(self, solo_activos=True):
        """Obtiene todos los trabajadores"""
        session = self.db.get_session()
        try:
            query = session.query(Trabajador)
            if solo_activos:
                query = query.filter(Trabajador.activo == 1)
            return query.all()
        finally:
            self.db.close_session(session)

    def actualizar(self, id, **kwargs):
        """Actualiza un trabajador"""
        session = self.db.get_session()
        try:
            trabajador = session.query(Trabajador).filter(Trabajador.id == id).first()
            if trabajador:
                # Validar DNI único solo si tiene valor y cambió
                dni = kwargs.get('dni', '').strip()
                if dni and dni != trabajador.dni:
                    existe = session.query(Trabajador).filter(
                        Trabajador.dni == dni,
                        Trabajador.id != id
                    ).first()
                    if existe:
                        raise ValueError(f"Ya existe un trabajador con el DNI {dni}")

                for key, value in kwargs.items():
                    if hasattr(trabajador, key):
                        setattr(trabajador, key, value)
                trabajador.fecha_actualizacion = datetime.now()
                session.commit()
                session.refresh(trabajador)
                return trabajador
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def eliminar(self, id):
        """Elimina (marca como inactivo) un trabajador"""
        session = self.db.get_session()
        try:
            trabajador = session.query(Trabajador).filter(Trabajador.id == id).first()
            if trabajador:
                trabajador.activo = 0
                trabajador.fecha_actualizacion = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def buscar(self, criterio):
        """Busca trabajadores por nombre o DNI"""
        session = self.db.get_session()
        try:
            criterio_lower = f"%{criterio.lower()}%"
            return session.query(Trabajador).filter(
                (Trabajador.nombre.ilike(criterio_lower)) |
                (Trabajador.apellidos.ilike(criterio_lower)) |
                (Trabajador.dni.ilike(criterio_lower))
            ).all()
        finally:
            self.db.close_session(session)


class MaterialDAO:
    """Data Access Object para Material"""

    def __init__(self, db: Database):
        self.db = db

    def crear(self, **kwargs):
        """Crea un nuevo material"""
        session = self.db.get_session()
        try:
            material = Material(**kwargs)
            session.add(material)
            session.commit()
            session.refresh(material)
            return material
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def obtener_por_id(self, id):
        """Obtiene un material por ID"""
        session = self.db.get_session()
        try:
            return session.query(Material).filter(Material.id == id).first()
        finally:
            self.db.close_session(session)

    def obtener_todos(self, solo_activos=True):
        """Obtiene todos los materiales"""
        session = self.db.get_session()
        try:
            query = session.query(Material)
            if solo_activos:
                query = query.filter(Material.activo == 1)
            return query.all()
        finally:
            self.db.close_session(session)

    def actualizar(self, id, **kwargs):
        """Actualiza un material"""
        session = self.db.get_session()
        try:
            material = session.query(Material).filter(Material.id == id).first()
            if material:
                for key, value in kwargs.items():
                    if hasattr(material, key):
                        setattr(material, key, value)
                material.fecha_actualizacion = datetime.now()
                session.commit()
                session.refresh(material)
                return material
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def eliminar(self, id):
        """Elimina (marca como inactivo) un material"""
        session = self.db.get_session()
        try:
            material = session.query(Material).filter(Material.id == id).first()
            if material:
                material.activo = 0
                material.fecha_actualizacion = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def buscar(self, criterio):
        """Busca materiales por nombre, descripción o referencia"""
        session = self.db.get_session()
        try:
            criterio_lower = f"%{criterio.lower()}%"
            return session.query(Material).filter(
                (Material.nombre.ilike(criterio_lower)) |
                (Material.descripcion.ilike(criterio_lower)) |
                (Material.referencia.ilike(criterio_lower))
            ).all()
        finally:
            self.db.close_session(session)


class PresupuestoDAO:
    """Data Access Object para Presupuesto"""

    def __init__(self, db: Database):
        self.db = db

    def crear(self, **kwargs):
        """Crea un nuevo presupuesto"""
        session = self.db.get_session()
        try:
            presupuesto = Presupuesto(**kwargs)
            session.add(presupuesto)
            session.commit()
            session.refresh(presupuesto)
            return presupuesto
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def obtener_por_id(self, id):
        """Obtiene un presupuesto por ID con eager loading"""
        session = self.db.get_session()
        try:
            presupuesto = session.query(Presupuesto).options(
                joinedload(Presupuesto.cliente),
                joinedload(Presupuesto.lineas).joinedload(LineaPresupuesto.material)
            ).filter(Presupuesto.id == id).first()

            # Expunge para desvincularlo de la sesión
            if presupuesto:
                session.expunge_all()
            return presupuesto
        finally:
            self.db.close_session(session)

    def obtener_todos(self):
        """Obtiene todos los presupuestos con eager loading"""
        session = self.db.get_session()
        try:
            presupuestos = session.query(Presupuesto).options(
                joinedload(Presupuesto.cliente),
                joinedload(Presupuesto.lineas)
            ).order_by(Presupuesto.fecha_creacion.desc()).all()

            # Expunge para desvincularlos de la sesión
            session.expunge_all()
            return presupuestos
        finally:
            self.db.close_session(session)

    def actualizar(self, id, **kwargs):
        """Actualiza un presupuesto"""
        session = self.db.get_session()
        try:
            presupuesto = session.query(Presupuesto).filter(Presupuesto.id == id).first()
            if presupuesto:
                for key, value in kwargs.items():
                    if hasattr(presupuesto, key):
                        setattr(presupuesto, key, value)
                presupuesto.fecha_actualizacion = datetime.now()
                session.commit()
                session.refresh(presupuesto)
                return presupuesto
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def eliminar(self, id):
        """Elimina un presupuesto"""
        session = self.db.get_session()
        try:
            presupuesto = session.query(Presupuesto).filter(Presupuesto.id == id).first()
            if presupuesto:
                session.delete(presupuesto)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def generar_numero_presupuesto(self):
        """Genera un nuevo número de presupuesto"""
        session = self.db.get_session()
        try:
            year = datetime.now().year
            # Buscar el último presupuesto del año
            ultimo = session.query(Presupuesto).filter(
                Presupuesto.numero.like(f'{year}%')
            ).order_by(Presupuesto.numero.desc()).first()

            if ultimo:
                # Extraer el número secuencial
                try:
                    num = int(ultimo.numero.split('-')[1]) + 1
                except:
                    num = 1
            else:
                num = 1

            return f"{year}-{num:04d}"
        finally:
            self.db.close_session(session)


class ParteTrabajoDAO:
    """Data Access Object para ParteTrabajo"""

    def __init__(self, db: Database):
        self.db = db

    def crear(self, **kwargs):
        """Crea un nuevo parte de trabajo"""
        session = self.db.get_session()
        try:
            parte = ParteTrabajo(**kwargs)
            session.add(parte)
            session.commit()
            session.refresh(parte)
            return parte
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def obtener_por_id(self, id):
        """Obtiene un parte de trabajo por ID con eager loading"""
        session = self.db.get_session()
        try:
            parte = session.query(ParteTrabajo).options(
                joinedload(ParteTrabajo.detalles_mano_obra).joinedload(DetalleManoObra.trabajador),
                joinedload(ParteTrabajo.materiales_usados).joinedload(MaterialUsado.material),
                joinedload(ParteTrabajo.presupuesto)
            ).filter(ParteTrabajo.id == id).first()

            # Expunge para desvincularlo de la sesión
            if parte:
                session.expunge_all()
            return parte
        finally:
            self.db.close_session(session)

    def obtener_todos(self):
        """Obtiene todos los partes de trabajo con eager loading"""
        session = self.db.get_session()
        try:
            partes = session.query(ParteTrabajo).options(
                joinedload(ParteTrabajo.detalles_mano_obra),
                joinedload(ParteTrabajo.materiales_usados)
            ).order_by(ParteTrabajo.fecha_creacion.desc()).all()

            # Expunge para desvincularlos de la sesión
            session.expunge_all()
            return partes
        finally:
            self.db.close_session(session)

    def actualizar(self, id, **kwargs):
        """Actualiza un parte de trabajo"""
        session = self.db.get_session()
        try:
            parte = session.query(ParteTrabajo).filter(ParteTrabajo.id == id).first()
            if parte:
                for key, value in kwargs.items():
                    if hasattr(parte, key):
                        setattr(parte, key, value)
                parte.fecha_actualizacion = datetime.now()
                session.commit()
                session.refresh(parte)
                return parte
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def eliminar(self, id):
        """Elimina un parte de trabajo"""
        session = self.db.get_session()
        try:
            parte = session.query(ParteTrabajo).filter(ParteTrabajo.id == id).first()
            if parte:
                session.delete(parte)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close_session(session)

    def generar_numero_parte(self):
        """Genera un nuevo número de parte de trabajo"""
        session = self.db.get_session()
        try:
            year = datetime.now().year
            # Buscar el último parte del año
            ultimo = session.query(ParteTrabajo).filter(
                ParteTrabajo.numero.like(f'PT-{year}%')
            ).order_by(ParteTrabajo.numero.desc()).first()

            if ultimo:
                # Extraer el número secuencial
                try:
                    num = int(ultimo.numero.split('-')[2]) + 1
                except:
                    num = 1
            else:
                num = 1

            return f"PT-{year}-{num:04d}"
        finally:
            self.db.close_session(session)
