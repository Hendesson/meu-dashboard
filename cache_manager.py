"""
Sistema de cache para dados processados usando joblib e functools.
"""
import os
import hashlib
import pickle
import joblib
from functools import lru_cache
from typing import Any, Optional, Callable
import pandas as pd
import logging
from config_paths import CACHE_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gerenciador de cache para dados processados.
    """
    
    def __init__(self, cache_dir: str = CACHE_DIR):
        """
        Inicializa o gerenciador de cache.
        
        Args:
            cache_dir: Diretório para armazenar cache
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, *args, **kwargs) -> str:
        """
        Gera uma chave única para o cache baseada nos argumentos.
        """
        key_str = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_cache_path(self, key: str, extension: str = ".pkl") -> str:
        """
        Retorna o caminho do arquivo de cache.
        """
        return os.path.join(self.cache_dir, f"{key}{extension}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recupera dados do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            Dados em cache ou None se não existir
        """
        cache_path = self.get_cache_path(key)
        
        if os.path.exists(cache_path):
            try:
                # Tenta carregar com joblib primeiro (mais rápido para DataFrames)
                if cache_path.endswith('.pkl'):
                    return joblib.load(cache_path)
                else:
                    with open(cache_path, 'rb') as f:
                        return pickle.load(f)
            except Exception as e:
                logger.warning(f"Erro ao carregar cache {key}: {e}")
                return None
        
        return None
    
    def set(self, key: str, value: Any, use_joblib: bool = True):
        """
        Armazena dados no cache.
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            use_joblib: Se True, usa joblib (melhor para DataFrames)
        """
        cache_path = self.get_cache_path(key)
        
        try:
            if use_joblib and isinstance(value, pd.DataFrame):
                joblib.dump(value, cache_path, compress=3)
            else:
                with open(cache_path, 'wb') as f:
                    pickle.dump(value, f)
            logger.debug(f"Cache salvo: {key}")
        except Exception as e:
            logger.warning(f"Erro ao salvar cache {key}: {e}")
    
    def clear(self, pattern: Optional[str] = None):
        """
        Limpa o cache.
        
        Args:
            pattern: Padrão de arquivos a limpar (None = todos)
        """
        if pattern:
            import glob
            files = glob.glob(os.path.join(self.cache_dir, pattern))
        else:
            files = [os.path.join(self.cache_dir, f) for f in os.listdir(self.cache_dir) 
                    if f.endswith(('.pkl', '.parquet'))]
        
        for file in files:
            try:
                os.remove(file)
                logger.info(f"Cache removido: {file}")
            except Exception as e:
                logger.warning(f"Erro ao remover {file}: {e}")

# Instância global
cache_manager = CacheManager()

def cached_dataframe(key_prefix: str = ""):
    """
    Decorator para cachear resultados de funções que retornam DataFrames.
    
    Args:
        key_prefix: Prefixo para a chave do cache
    """
    def decorator(func: Callable) -> Callable:
        @lru_cache(maxsize=32)
        def wrapper(*args, **kwargs):
            # Gera chave única
            cache_key = cache_manager._get_cache_key(*args, **kwargs)
            full_key = f"{key_prefix}_{cache_key}" if key_prefix else cache_key
            
            # Tenta recuperar do cache
            cached = cache_manager.get(full_key)
            if cached is not None:
                logger.debug(f"Cache hit: {full_key}")
                return cached
            
            # Executa função e armazena resultado
            logger.debug(f"Cache miss: {full_key}")
            result = func(*args, **kwargs)
            
            if isinstance(result, pd.DataFrame):
                cache_manager.set(full_key, result, use_joblib=True)
            
            return result
        
        return wrapper
    return decorator

