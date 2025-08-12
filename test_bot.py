#!/usr/bin/env python3
"""
Script de prueba para verificar que el bot funciona correctamente
"""

import sys
import os

def test_imports():
    """Prueba que todas las importaciones funcionen"""
    print("🔍 Probando importaciones...")
    
    try:
        import discord
        print("✅ discord.py importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando discord.py: {e}")
        return False
    
    try:
        import impuestito
        from impuestito.main import cotization, oficial, blue, euro, euro_blue, calcularImpuestoPais
        print("✅ impuestito importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando impuestito: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando python-dotenv: {e}")
        return False
    
    return True

def test_impuestito_functions():
    """Prueba las funciones de impuestito"""
    print("\n🔍 Probando funciones de impuestito...")
    
    try:
        from impuestito.main import cotization, oficial, blue, euro, euro_blue, calcularImpuestoPais
        
        # Probar cotizaciones
        print(f"✅ Dólar oficial: ${oficial}")
        print(f"✅ Dólar blue: ${blue}")
        print(f"✅ Euro oficial: ${euro}")
        print(f"✅ Euro blue: ${euro_blue}")
        
        # Probar cálculo de impuesto país
        resultado = calcularImpuestoPais(100)
        print(f"✅ Impuesto país $100: {resultado}")
        
        # Probar cotización completa
        print(f"✅ Cotización completa: {len(cotization)} elementos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando impuestito: {e}")
        return False

def test_env_config():
    """Prueba la configuración del archivo .env"""
    print("\n🔍 Probando configuración...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv('DISCORD_BOT_TOKEN')
        if token and token != 'tu_token_del_bot_aqui':
            print("✅ Token de Discord configurado")
            return True
        else:
            print("⚠️  Token de Discord no configurado o usando valor por defecto")
            print("💡 Configura tu token en el archivo .env")
            return False
            
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return False

def test_bot_files():
    """Prueba que los archivos del bot existan"""
    print("\n🔍 Probando archivos del bot...")
    
    files_to_check = [
        'discord_bot.py',
        'discord_bot_modular.py',
        'cogs/currency_commands.py',
        'cogs/debug_commands.py'
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} existe")
        else:
            print(f"❌ {file_path} no encontrado")
            all_exist = False
    
    return all_exist

def main():
    """Función principal de pruebas"""
    print("🧪 Pruebas del Bot de Impuestito para Discord")
    print("=" * 50)
    
    tests = [
        ("Importaciones", test_imports),
        ("Funciones de impuestito", test_impuestito_functions),
        ("Configuración", test_env_config),
        ("Archivos del bot", test_bot_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASÓ")
        else:
            print(f"❌ {test_name} - FALLÓ")
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El bot está listo para usar.")
        print("\n💡 Para ejecutar el bot:")
        print("   python run_bot.py")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("\n💡 Comandos útiles:")
        print("   pip install -r requirements.txt")
        print("   cp .env.example .env")
        print("   # Edita .env con tu token de Discord")

if __name__ == '__main__':
    main()