"""
Script para verificar y corregir la transparencia del logo
"""
from PIL import Image
from pathlib import Path

logo_path = Path("assets/logo.png")

if logo_path.exists():
    print("Analizando logo...")
    img = Image.open(logo_path)
    
    print(f"Modo actual: {img.mode}")
    print(f"Tamaño: {img.size}")
    print(f"Formato: {img.format}")
    
    if img.mode == 'RGBA':
        print("✓ La imagen tiene canal alpha (transparencia)")
        
        # Verificar si realmente usa transparencia
        has_transparency = False
        for pixel in img.getdata():
            if len(pixel) == 4 and pixel[3] < 255:
                has_transparency = True
                break
        
        if has_transparency:
            print("✓ La imagen usa transparencia real")
        else:
            print("⚠ La imagen tiene canal alpha pero no usa transparencia")
            print("  El fondo puede ser blanco opaco")
    else:
        print("⚠ La imagen NO tiene canal alpha")
        print("  Convirtiendo a RGBA...")
        
        # Si tiene modo P (palette), convertir primero
        if img.mode == 'P':
            img = img.convert('RGBA')
        else:
            # Crear versión con transparencia
            img_rgba = Image.new('RGBA', img.size, (255, 255, 255, 0))
            if img.mode == 'RGB':
                # Hacer blanco transparente
                img = img.convert('RGBA')
                data = img.getdata()
                
                new_data = []
                for item in data:
                    # Cambiar píxeles blancos a transparentes
                    if item[0] > 240 and item[1] > 240 and item[2] > 240:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)
                
                img.putdata(new_data)
        
        # Guardar versión corregida
        output_path = Path("assets/logo_transparent.png")
        img.save(output_path, 'PNG')
        print(f"✓ Versión con transparencia guardada en: {output_path}")
else:
    print("❌ No se encontró assets/logo.png")
