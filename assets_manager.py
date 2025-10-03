"""
Gestión de recursos de la aplicación (imágenes, logos, etc.)
"""
from PIL import Image, ImageTk
from config import ASSETS_DIR

class AssetManager:
    """Gestor de recursos de la aplicación"""
    
    def __init__(self):
        self._image_cache = {}
        self._ensure_assets_dir()
    
    def _ensure_assets_dir(self):
        """Asegura que el directorio de assets existe"""
        ASSETS_DIR.mkdir(exist_ok=True)
    
    def load_logo(self, width=None, height=None):
        """
        Carga el logo de la empresa
        
        Args:
            width: Ancho deseado en píxeles
            height: Alto deseado en píxeles
            
        Returns:
            ImageTk.PhotoImage o None si no se puede cargar
        """
        logo_path = ASSETS_DIR / "logo.png"
        
        # Si no existe el logo, crear uno por defecto
        if not logo_path.exists():
            return self._create_default_logo(width or 80, height or 60)
        
        try:
            # Crear clave de cache
            cache_key = f"logo_{width}_{height}"
            
            if cache_key in self._image_cache:
                return self._image_cache[cache_key]
            
            # Cargar y redimensionar imagen
            image = Image.open(logo_path)
            
            if width or height:
                # Mantener proporción si solo se especifica una dimensión
                if width and not height:
                    ratio = width / image.width
                    height = int(image.height * ratio)
                elif height and not width:
                    ratio = height / image.height
                    width = int(image.width * ratio)
                
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Guardar en cache
            self._image_cache[cache_key] = photo
            
            return photo
            
        except Exception as e:
            print(f"Error cargando logo: {e}")
            return self._create_default_logo(width or 80, height or 60)
    
    def _create_default_logo(self, width=80, height=60):
        """Crea un logo por defecto si no existe archivo"""
        try:
            # Crear imagen por defecto con gradiente y texto
            image = Image.new('RGBA', (width, height), (255, 107, 0, 255))
            
            # Añadir texto simple (requiere PIL con soporte de fuentes)
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(image)
                
                # Intentar usar una fuente del sistema
                try:
                    font = ImageFont.truetype("arial.ttf", max(12, height // 4))
                except:
                    font = ImageFont.load_default()
                
                # Dibujar texto
                text = "BP"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                
                draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
                
            except ImportError:
                pass  # Sin texto si no hay ImageDraw/ImageFont
            
            photo = ImageTk.PhotoImage(image)
            
            # Guardar en cache
            cache_key = f"default_logo_{width}_{height}"
            self._image_cache[cache_key] = photo
            
            return photo
            
        except Exception as e:
            print(f"Error creando logo por defecto: {e}")
            return None
    
    def save_logo_from_file(self, source_path):
        """
        Guarda un archivo de logo en el directorio de assets
        
        Args:
            source_path: Ruta al archivo de imagen fuente
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            logo_path = ASSETS_DIR / "logo.png"
            
            # Abrir imagen fuente
            image = Image.open(source_path)
            
            # Convertir a RGBA si es necesario
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Guardar como PNG
            image.save(logo_path, 'PNG')
            
            # Limpiar cache para forzar recarga
            self._image_cache.clear()
            
            return True
            
        except Exception as e:
            print(f"Error guardando logo: {e}")
            return False
    
    def get_icon(self, icon_name, size=16):
        """
        Obtiene un icono del tema
        
        Args:
            icon_name: Nombre del icono
            size: Tamaño en píxeles
            
        Returns:
            PhotoImage o None
        """
        # Por ahora devuelve None, se puede expandir para iconos personalizados
        return None

# Instancia global del gestor
asset_manager = AssetManager()