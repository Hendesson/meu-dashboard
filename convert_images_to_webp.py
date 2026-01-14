"""
Script para converter imagens PNG/JPG para WebP com redimensionamento otimizado.
"""
import os
from pathlib import Path
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tamanhos máximos para diferentes tipos de imagens
MAX_SIZES = {
    'logo': (800, 800),  # Logos podem ser maiores
    'photo': (1200, 1200),  # Fotos de pessoas
    'map': (2000, 2000),  # Mapas podem ser grandes
    'default': (1500, 1500)  # Tamanho padrão
}

def get_max_size(image_path: str) -> tuple:
    """
    Determina o tamanho máximo baseado no nome do arquivo.
    """
    name_lower = image_path.lower()
    
    if any(x in name_lower for x in ['logo', 'cnpq', 'unb', 'ufrj', 'fiocruz', 'lmi', 'ird', 'observatorio', 'geocalor', 'lattes', 'research']):
        return MAX_SIZES['logo']
    elif any(x in name_lower for x in ['helen', 'eliane', 'eucilene', 'amarilis', 'bruno', 'peter', 'adriana', 'caio', 'rafaela', 'hend', 'isabella', 'livia']):
        return MAX_SIZES['photo']
    elif any(x in name_lower for x in ['dias', 'mapa', 'temperatura', 'limiares']):
        return MAX_SIZES['map']
    else:
        return MAX_SIZES['default']

def resize_image(img: Image.Image, max_size: tuple) -> Image.Image:
    """
    Redimensiona a imagem mantendo a proporção.
    """
    if img.size[0] <= max_size[0] and img.size[1] <= max_size[1]:
        return img
    
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    return img

def convert_to_webp(input_path: str, output_dir: str = "images/webp", quality: int = 85) -> str:
    """
    Converte uma imagem para WebP.
    
    Args:
        input_path: Caminho da imagem original
        output_dir: Diretório de saída
        quality: Qualidade WebP (0-100)
        
    Returns:
        Caminho da imagem WebP gerada
    """
    if not os.path.exists(input_path):
        logger.error(f"Arquivo não encontrado: {input_path}")
        return None
    
    try:
        # Abre a imagem
        img = Image.open(input_path)
        
        # Converte para RGB se necessário (WebP não suporta RGBA com transparência em alguns casos)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Mantém transparência se for PNG
            if img.format == 'PNG' and img.mode == 'RGBA':
                pass  # Mantém RGBA
            else:
                img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensiona se necessário
        max_size = get_max_size(input_path)
        img = resize_image(img, max_size)
        
        # Gera nome do arquivo de saída
        input_name = Path(input_path).stem
        output_path = os.path.join(output_dir, f"{input_name}.webp")
        
        # Cria diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Salva como WebP
        save_kwargs = {'format': 'WEBP', 'quality': quality, 'method': 6}
        if img.mode == 'RGBA':
            save_kwargs['lossless'] = False  # WebP com compressão para RGBA
        
        img.save(output_path, **save_kwargs)
        
        original_size = os.path.getsize(input_path) / 1024
        webp_size = os.path.getsize(output_path) / 1024
        reduction = (1 - webp_size / original_size) * 100
        
        logger.info(f"Convertido: {input_path}")
        logger.info(f"  Original: {original_size:.2f} KB")
        logger.info(f"  WebP: {webp_size:.2f} KB ({reduction:.1f}% redução)")
        logger.info(f"  Tamanho: {img.size}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Erro ao converter {input_path}: {e}")
        return None

if __name__ == "__main__":
    assets_dir = "assets"
    output_dir = "images/webp"
    
    if not os.path.exists(assets_dir):
        logger.error(f"Diretório não encontrado: {assets_dir}")
        exit(1)
    
    # Extensões suportadas
    extensions = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')
    
    # Converte todas as imagens
    converted = 0
    for file in os.listdir(assets_dir):
        if file.lower().endswith(extensions):
            input_path = os.path.join(assets_dir, file)
            convert_to_webp(input_path, output_dir)
            converted += 1
    
    logger.info(f"Conversão concluída! {converted} imagens convertidas.")

