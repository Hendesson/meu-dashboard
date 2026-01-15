"""
Script para limpar o cache e forçar recarregamento dos dados.
"""
import os
from cache_manager import cache_manager
from config_paths import CACHE_DIR

def limpar_cache():
    """Limpa todo o cache."""
    print("=" * 50)
    print("Limpando cache...")
    print("=" * 50)
    
    # Limpa usando o cache_manager
    cache_manager.clear()
    
    # Também limpa manualmente arquivos .pkl
    if os.path.exists(CACHE_DIR):
        arquivos = [f for f in os.listdir(CACHE_DIR) if f.endswith('.pkl')]
        for arquivo in arquivos:
            caminho = os.path.join(CACHE_DIR, arquivo)
            try:
                os.remove(caminho)
                print(f"✅ Removido: {arquivo}")
            except Exception as e:
                print(f"❌ Erro ao remover {arquivo}: {e}")
    
    print("\n" + "=" * 50)
    print("Cache limpo com sucesso!")
    print("=" * 50)
    print("\nAgora execute o app novamente para recarregar os dados.")

if __name__ == "__main__":
    limpar_cache()

