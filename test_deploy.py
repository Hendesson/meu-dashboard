"""
Script de teste para verificar se o projeto está pronto para deploy.
Execute antes de fazer commit.
"""
import os
import sys
from config_paths import BASE_DIR, DATA_DIR, PROCESSED_DIR, CACHE_DIR, ASSETS_DIR

def test_paths():
    """Testa se os caminhos estão configurados corretamente."""
    print("=" * 60)
    print("TESTE DE CONFIGURAÇÃO PARA DEPLOY")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Testa diretórios
    print("\n1. Verificando diretórios...")
    dirs = {
        "BASE_DIR": BASE_DIR,
        "DATA_DIR": DATA_DIR,
        "PROCESSED_DIR": PROCESSED_DIR,
        "CACHE_DIR": CACHE_DIR,
        "ASSETS_DIR": ASSETS_DIR
    }
    
    for name, path in dirs.items():
        if os.path.exists(path):
            print(f"  ✓ {name}: {path}")
        else:
            print(f"  ✗ {name}: {path} (não existe)")
            errors.append(f"Diretório {name} não existe")
    
    # Testa arquivos essenciais
    print("\n2. Verificando arquivos essenciais...")
    essential_files = [
        "app.py",
        "data_processing.py",
        "visualization.py",
        "cache_manager.py",
        "config_paths.py",
        "requirements.txt",
        "Procfile"
    ]
    
    for filename in essential_files:
        path = os.path.join(BASE_DIR, filename)
        if os.path.exists(path):
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} (não encontrado)")
            errors.append(f"Arquivo essencial {filename} não encontrado")
    
    # Testa arquivos de dados
    print("\n3. Verificando arquivos de dados...")
    data_files = [
        "temp.xlsx",
        "mapa_interativo.html"
    ]
    
    for filename in data_files:
        path = os.path.join(DATA_DIR, filename)
        if os.path.exists(path):
            print(f"  ✓ data/{filename}")
        else:
            # Tenta na raiz também
            root_path = os.path.join(BASE_DIR, filename)
            if os.path.exists(root_path):
                print(f"  ⚠ {filename} está na raiz, deveria estar em data/")
                warnings.append(f"{filename} deveria estar em data/")
            else:
                print(f"  ✗ data/{filename} (não encontrado)")
                warnings.append(f"Arquivo de dados {filename} não encontrado")
    
    # Testa imports
    print("\n4. Verificando imports...")
    try:
        from config_paths import BASE_DIR, DATA_DIR
        print("  ✓ config_paths importado com sucesso")
    except Exception as e:
        print(f"  ✗ Erro ao importar config_paths: {e}")
        errors.append(f"Erro ao importar config_paths: {e}")
    
    try:
        import app
        print("  ✓ app.py importado com sucesso")
        if hasattr(app, 'server'):
            print("  ✓ server = app.server encontrado")
        else:
            print("  ✗ server = app.server não encontrado")
            errors.append("server = app.server não encontrado em app.py")
    except Exception as e:
        print(f"  ✗ Erro ao importar app: {e}")
        errors.append(f"Erro ao importar app: {e}")
    
    # Testa caminhos absolutos do Windows
    print("\n5. Verificando caminhos absolutos do Windows...")
    import re
    
    files_to_check = ["app.py", "data_processing.py", "cache_manager.py"]
    for filename in files_to_check:
        filepath = os.path.join(BASE_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if re.search(r'[Cc]:\\|r["\']C:', content):
                    print(f"  ✗ {filename} contém caminhos absolutos do Windows")
                    errors.append(f"{filename} contém caminhos absolutos do Windows")
                else:
                    print(f"  ✓ {filename} sem caminhos absolutos")
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ ERROS ENCONTRADOS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        print("\n⚠️  Corrija os erros antes de fazer deploy!")
    
    if warnings:
        print(f"\n⚠️  AVISOS ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("\n✅ Tudo pronto para deploy!")
        return 0
    elif not errors:
        print("\n⚠️  Há avisos, mas o deploy deve funcionar")
        return 0
    else:
        print("\n❌ Corrija os erros antes de fazer deploy")
        return 1

if __name__ == "__main__":
    sys.exit(test_paths())

