#!/usr/bin/env python3
"""
Script de inicio para el Bot de Impuestito para Discord
Permite elegir entre la versión simple y modular del bot.
"""

import os
import sys
import subprocess

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    try:
        import discord
        import impuestito
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f"❌ Error: Falta la dependencia {e}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False

def check_env_file():
    """Verifica que el archivo .env exista"""
    if not os.path.exists('.env'):
        print("⚠️  Archivo .env no encontrado.")
        print("💡 Copia .env.example a .env y configura tu token:")
        print("   cp .env.example .env")
        return False
    return True

def main():
    """Función principal del script de inicio"""
    print("🤖 Bot de Impuestito para Discord")
    print("=" * 40)
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar archivo .env
    if not check_env_file():
        sys.exit(1)
    
    print("\n📋 Selecciona la versión del bot:")
    print("1. Versión Simple (todo en un archivo)")
    print("2. Versión Modular (recomendada)")
    print("3. Salir")
    
    while True:
        try:
            choice = input("\n🔢 Opción (1-3): ").strip()
            
            if choice == "1":
                print("\n🚀 Iniciando versión simple...")
                if os.path.exists('discord_bot.py'):
                    subprocess.run([sys.executable, 'discord_bot.py'])
                else:
                    print("❌ Error: discord_bot.py no encontrado")
                break
                
            elif choice == "2":
                print("\n🚀 Iniciando versión modular...")
                if os.path.exists('discord_bot_modular.py'):
                    subprocess.run([sys.executable, 'discord_bot_modular.py'])
                else:
                    print("❌ Error: discord_bot_modular.py no encontrado")
                break
                
            elif choice == "3":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción inválida. Por favor, elige 1, 2 o 3.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == '__main__':
    main()