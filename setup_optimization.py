"""
Script de inicialização para converter dados e imagens para formatos otimizados.
Execute este script uma vez antes de rodar o dashboard.
"""
import os
import sys

def main():
    print("=" * 60)
    print("Otimização do Dashboard - Conversão de Dados e Imagens")
    print("=" * 60)
    print()
    
    # Converte Excel para Parquet
    print("1. Convertendo arquivos Excel para Parquet...")
    try:
        from convert_excel_to_parquet import convert_excel_to_parquet, convert_csv_to_parquet
        import glob
        
        # Converte Excel
        excel_files = glob.glob("*.xlsx")
        for excel_file in excel_files:
            if os.path.exists(excel_file):
                print(f"   Convertendo {excel_file}...")
                convert_excel_to_parquet(excel_file, "processed")
        
        # Converte CSV principais
        csv_configs = [
            ("RM_banco_SRAG.csv", ["RM", "RM_nome", "DT_INTERNA", "DT_SIN_PRI", "mes", "ano"], 
             {"RM": "category", "RM_nome": "category", "mes": "category", "ano": "Int64"}),
            ("serie_SIH_final.RData.csv", None, None),
            ("banco_dados_climaticos_consolidado (2).csv", None, None)
        ]
        
        for csv_file, usecols, dtype in csv_configs:
            if os.path.exists(csv_file):
                print(f"   Convertendo {csv_file}...")
                convert_csv_to_parquet(csv_file, "processed", usecols, dtype)
        
        print("   ✓ Conversão de dados concluída!")
    except Exception as e:
        print(f"   ✗ Erro na conversão de dados: {e}")
    
    print()
    
    # Converte imagens para WebP
    print("2. Convertendo imagens para WebP...")
    try:
        from convert_images_to_webp import convert_to_webp
        import glob
        
        assets_dir = "assets"
        if os.path.exists(assets_dir):
            extensions = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')
            converted = 0
            
            for file in os.listdir(assets_dir):
                if file.lower().endswith(extensions):
                    input_path = os.path.join(assets_dir, file)
                    result = convert_to_webp(input_path, "images/webp")
                    if result:
                        converted += 1
            
            print(f"   ✓ {converted} imagens convertidas!")
        else:
            print(f"   ⚠ Diretório {assets_dir} não encontrado")
    except Exception as e:
        print(f"   ✗ Erro na conversão de imagens: {e}")
    
    print()
    print("=" * 60)
    print("Otimização concluída!")
    print("=" * 60)
    print()
    print("Próximos passos:")
    print("1. Execute o dashboard normalmente: python app.py")
    print("2. O sistema usará automaticamente os arquivos otimizados")
    print()

if __name__ == "__main__":
    main()

