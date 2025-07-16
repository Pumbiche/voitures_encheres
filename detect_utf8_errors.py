import os

def detect_encoding_errors(base_path):
    print("🔍 Analyse des fichiers pour erreurs d'encodage...\n")
    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Ignore les fichiers binaires courants
            if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico', '.db', '.zip')):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError as e:
                print(f"❌ Erreur d'encodage dans : {file_path}")
                print(f"   → {e}\n")
            except Exception as e:
                print(f"⚠️  Problème inattendu dans : {file_path}")
                print(f"   → {e}\n")
    print("✅ Analyse terminée.")

# Exemple d'utilisation :
# Remplace le chemin par le tien si nécessaire
detect_encoding_errors(".")
