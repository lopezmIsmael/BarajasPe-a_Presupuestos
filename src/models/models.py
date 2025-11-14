"""
Modelos de datos para la aplicación de gestión de constructora.
Define todas las entidades y relaciones del sistema.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Cliente(Base):
    """Modelo de Cliente"""
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100))
    empresa = Column(String(100))
    nif_cif = Column(String(20))
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(String(200))
    ciudad = Column(String(100))
    codigo_postal = Column(String(10))
    provincia = Column(String(100))
    notas = Column(Text)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    presupuestos = relationship("Presupuesto", back_populates="cliente", cascade="all, delete-orphan")

    def __repr__(self):
        if self.empresa:
            return f"{self.empresa} ({self.nombre} {self.apellidos or ''})"
        return f"{self.nombre} {self.apellidos or ''}"


class Trabajador(Base):
    """Modelo de Trabajador"""
    __tablename__ = 'trabajadores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    dni = Column(String(20), unique=False, nullable=True)  # Cambiado: permitir múltiples vacíos
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(String(200))
    coste_hora = Column(Float, nullable=False, default=0.0)  # Coste por hora de trabajo
    puesto = Column(String(100))
    fecha_alta = Column(Date)
    activo = Column(Integer, default=1)  # 1 = activo, 0 = inactivo
    notas = Column(Text)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    detalles_mano_obra = relationship("DetalleManoObra", back_populates="trabajador")

    def __repr__(self):
        return f"{self.nombre} {self.apellidos} - {self.coste_hora}€/h"


class Material(Base):
    """Modelo de Material"""
    __tablename__ = 'materiales'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), nullable=False)
    familia = Column(String(100), default='General')  # Categoría/familia del material
    descripcion = Column(Text)
    unidad = Column(String(20), nullable=False, default='ud')  # ud, m, m2, m3, kg, l, etc.
    precio_compra = Column(Float, nullable=False, default=0.0)
    precio_venta = Column(Float, nullable=False, default=0.0)
    margen_ganancia_defecto = Column(Float, default=20.0)  # Porcentaje de ganancia por defecto
    referencia = Column(String(50))
    proveedor = Column(String(100))
    stock_actual = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=0.0)
    activo = Column(Integer, default=1)  # 1 = activo, 0 = inactivo
    notas = Column(Text)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    lineas_presupuesto = relationship("LineaPresupuesto", back_populates="material")
    materiales_usados = relationship("MaterialUsado", back_populates="material")

    def __repr__(self):
        return f"[{self.familia}] {self.nombre} ({self.unidad}) - C:{self.precio_compra}€ V:{self.precio_venta}€"


class Presupuesto(Base):
    """Modelo de Presupuesto"""
    __tablename__ = 'presupuestos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(50), unique=True, nullable=False)  # Número de presupuesto
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    fecha_validez = Column(Date)  # Hasta cuando es válido el presupuesto
    titulo = Column(String(200))
    descripcion = Column(Text)
    coste_mano_obra = Column(Float, default=0.0)  # Coste total estimado de mano de obra
    estado = Column(String(20), default='borrador')  # borrador, enviado, aceptado, rechazado, facturado
    contenido_html = Column(Text)  # HTML editado del presupuesto
    notas_internas = Column(Text)  # Notas que no aparecen en el PDF
    descuento_global = Column(Float, default=0.0)  # Descuento porcentual global

    # Relaciones
    cliente = relationship("Cliente", back_populates="presupuestos")
    lineas = relationship("LineaPresupuesto", back_populates="presupuesto", cascade="all, delete-orphan")
    partes_trabajo = relationship("ParteTrabajo", back_populates="presupuesto")

    @property
    def total_materiales_coste(self):
        """Calcula el coste total de materiales (precio de compra)"""
        return sum(linea.coste_total for linea in self.lineas)

    @property
    def total_materiales_venta(self):
        """Calcula el precio de venta total de materiales"""
        return sum(linea.precio_venta_total for linea in self.lineas)

    @property
    def ganancia_materiales(self):
        """Calcula la ganancia en materiales"""
        return self.total_materiales_venta - self.total_materiales_coste

    @property
    def subtotal(self):
        """Subtotal antes de descuento"""
        return self.total_materiales_venta + self.coste_mano_obra

    @property
    def descuento_importe(self):
        """Importe del descuento"""
        return self.subtotal * (self.descuento_global / 100.0)

    @property
    def total_final(self):
        """Precio total final de venta"""
        return self.subtotal - self.descuento_importe

    def __repr__(self):
        return f"Presupuesto {self.numero} - {self.cliente} - {self.total_final:.2f}€"


class LineaPresupuesto(Base):
    """Modelo de Línea de Presupuesto"""
    __tablename__ = 'lineas_presupuesto'

    id = Column(Integer, primary_key=True, autoincrement=True)
    presupuesto_id = Column(Integer, ForeignKey('presupuestos.id'), nullable=False)
    material_id = Column(Integer, ForeignKey('materiales.id'), nullable=False)
    cantidad = Column(Float, nullable=False, default=1.0)
    precio_compra_unitario = Column(Float, nullable=False)  # Precio de compra en el momento
    margen_ganancia_porc = Column(Float, nullable=False)  # Porcentaje de ganancia aplicado
    orden = Column(Integer, default=0)  # Para mantener el orden de las líneas
    descripcion_personalizada = Column(Text)  # Descripción específica para esta línea

    # Relaciones
    presupuesto = relationship("Presupuesto", back_populates="lineas")
    material = relationship("Material", back_populates="lineas_presupuesto")

    @property
    def coste_total(self):
        """Coste total de esta línea (precio de compra * cantidad)"""
        return self.precio_compra_unitario * self.cantidad

    @property
    def ganancia_importe(self):
        """Ganancia en importe de esta línea

        Fórmula: ganancia = precio_venta - coste
        Donde: precio_venta = coste / (1 - margen/100)
        """
        precio_venta = self.coste_total / (1 - self.margen_ganancia_porc / 100.0)
        return precio_venta - self.coste_total

    @property
    def precio_venta_unitario(self):
        """Precio de venta unitario

        Fórmula: precio_venta = precio_coste / (1 - margen/100)
        Ejemplo: margen 30% -> precio_venta = precio_coste / 0.7
        """
        return self.precio_compra_unitario / (1 - self.margen_ganancia_porc / 100.0)

    @property
    def precio_venta_total(self):
        """Precio de venta total de esta línea

        Fórmula: precio_venta_total = coste_total / (1 - margen/100)
        """
        return self.coste_total / (1 - self.margen_ganancia_porc / 100.0)

    def __repr__(self):
        return f"{self.material.nombre} x{self.cantidad} - {self.precio_venta_total:.2f}€"


class ParteTrabajo(Base):
    """Modelo de Parte de Trabajo"""
    __tablename__ = 'partes_trabajo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(50), unique=True, nullable=False)
    presupuesto_id = Column(Integer, ForeignKey('presupuestos.id'), nullable=True)  # Puede estar asociado a un presupuesto o no
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    ubicacion = Column(String(200))
    estado = Column(String(20), default='en_curso')  # en_curso, finalizado, facturado
    contenido_html = Column(Text)  # HTML editado del parte de trabajo
    notas = Column(Text)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    presupuesto = relationship("Presupuesto", back_populates="partes_trabajo")
    detalles_mano_obra = relationship("DetalleManoObra", back_populates="parte_trabajo", cascade="all, delete-orphan")
    materiales_usados = relationship("MaterialUsado", back_populates="parte_trabajo", cascade="all, delete-orphan")

    @property
    def total_coste_mano_obra(self):
        """Calcula el coste total de mano de obra"""
        return sum(detalle.coste_total for detalle in self.detalles_mano_obra)

    @property
    def total_coste_materiales(self):
        """Calcula el coste total de materiales usados"""
        return sum(mat.coste_total for mat in self.materiales_usados)

    @property
    def coste_total(self):
        """Coste total del parte (mano de obra + materiales)"""
        return self.total_coste_mano_obra + self.total_coste_materiales

    @property
    def total_horas(self):
        """Total de horas trabajadas"""
        return sum(detalle.horas for detalle in self.detalles_mano_obra)

    def __repr__(self):
        return f"Parte {self.numero} - {self.titulo} - {self.coste_total:.2f}€"


class DetalleManoObra(Base):
    """Modelo de Detalle de Mano de Obra en un Parte de Trabajo"""
    __tablename__ = 'detalles_mano_obra'

    id = Column(Integer, primary_key=True, autoincrement=True)
    parte_trabajo_id = Column(Integer, ForeignKey('partes_trabajo.id'), nullable=False)
    trabajador_id = Column(Integer, ForeignKey('trabajadores.id'), nullable=False)
    fecha = Column(Date, nullable=False)
    horas = Column(Float, nullable=False, default=0.0)
    coste_hora_aplicado = Column(Float, nullable=False)  # Coste por hora en el momento
    labor_realizada = Column(Text)
    comentarios = Column(Text)

    # Relaciones
    parte_trabajo = relationship("ParteTrabajo", back_populates="detalles_mano_obra")
    trabajador = relationship("Trabajador", back_populates="detalles_mano_obra")

    @property
    def coste_total(self):
        """Coste total de esta entrada (horas * coste_hora)"""
        return self.horas * self.coste_hora_aplicado

    def __repr__(self):
        return f"{self.trabajador.nombre} - {self.fecha} - {self.horas}h - {self.coste_total:.2f}€"


class MaterialUsado(Base):
    """Modelo de Material Usado en un Parte de Trabajo"""
    __tablename__ = 'materiales_usados'

    id = Column(Integer, primary_key=True, autoincrement=True)
    parte_trabajo_id = Column(Integer, ForeignKey('partes_trabajo.id'), nullable=False)
    material_id = Column(Integer, ForeignKey('materiales.id'), nullable=False)
    cantidad = Column(Float, nullable=False, default=0.0)
    precio_compra_unitario = Column(Float, nullable=False)  # Precio en el momento
    fecha_uso = Column(Date, nullable=False)
    comentarios = Column(Text)

    # Relaciones
    parte_trabajo = relationship("ParteTrabajo", back_populates="materiales_usados")
    material = relationship("Material", back_populates="materiales_usados")

    @property
    def coste_total(self):
        """Coste total de este material usado"""
        return self.cantidad * self.precio_compra_unitario

    def __repr__(self):
        return f"{self.material.nombre} x{self.cantidad} - {self.coste_total:.2f}€"
