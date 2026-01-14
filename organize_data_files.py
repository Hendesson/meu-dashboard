"""
Script para organizar arquivos de dados na pasta data/ para deploy.
Execute este script antes de fazer commit para GitHub.
"""
import os
import shutil
from config_paths import BASE_DIR, DATA_DIR

def organize_files():
    """
    Move arquivos de dados para a pasta data/
    """
    print("Organizando arquivos de dados...")
    
    # Arquivos a mover para data/
    files_to_move = [
        "temp.xlsx",
        "temp1.xlsx",
        "medias_HW_Severe_Extreme.xlsx",
        "banco_dados_climaticos_consolidado (2).xlsx",
        "banco_dados_climaticos_consolidado (2).csv",
        "RM_banco_SRAG.csv",
        "serie_SIH_final.RData.csv",
        "mapa_interativo.html"
    ]
    
    moved = 0
    skipped = 0
    
    for filename in files_to_move:
        source = os.path.join(BASE_DIR, filename)
        dest = os.path.join(DATA_DIR, filename)
        
        if os.path.exists(source):
            try:
                # Não sobrescreve se já existe
                if not os.path.exists(dest):
                    shutil.copy2(source, dest)
                    print(f"✓ Movido: {filename}")
                    moved += 1
                else:
                    print(f"⊘ Já existe: {filename}")
                    skipped += 1
            except Exception as e:
                print(f"✗ Erro ao mover {filename}: {e}")
        else:
            print(f"⊘ Não encontrado: {filename}")
    
    print(f"\nResumo: {moved} arquivos movidos, {skipped} já existiam")
    print(f"Arquivos estão em: {DATA_DIR}")

if __name__ == "__main__":
    organize_files()

