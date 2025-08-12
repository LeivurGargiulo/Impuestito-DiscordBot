#!/usr/bin/env python3
"""
Discord Bot para Impuestito - Versión Modular
Bot de Discord que proporciona información sobre cotizaciones de monedas
y cálculos de impuestos en Argentina usando el paquete impuestito.
Convertido desde el bot de Telegram original con estructura modular.
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
import traceback

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Crear bot con prefijo '!'
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Variables globales para tracking
bot_start_time = time.time()
recent_errors = []
MAX_ERROR_LOG = 10

class BotStats:
    """Clase para manejar estadísticas del bot"""
    def __init__(self):
        self.start_time = time.time()
        self.command_count = 0
        self.error_count = 0
        self.last_error = None

bot_stats = BotStats()

# ============================================================================
# EVENTOS DEL BOT
# ============================================================================

@bot.event
async def on_ready():
    """Evento que se ejecuta cuando el bot está listo"""
    logger.info(f'🤖 Bot conectado como {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'📊 Servidores conectados: {len(bot.guilds)}')
    
    # Cambiar estado del bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="!help para comandos"
        )
    )
    
    # Iniciar tarea de limpieza de errores
    cleanup_errors.start()
    
    # Cargar cogs
    await load_cogs()

@bot.event
async def on_command(ctx):
    """Evento que se ejecuta cuando se usa un comando"""
    bot_stats.command_count += 1
    logger.info(f'Comando ejecutado: {ctx.command.name} por {ctx.author} en {ctx.guild}')

@bot.event
async def on_command_error(ctx, error):
    """Manejador global de errores para comandos"""
    bot_stats.error_count += 1
    bot_stats.last_error = error
    
    # Agregar error al log reciente
    error_info = {
        'timestamp': datetime.now(),
        'command': ctx.command.name if ctx.command else 'Unknown',
        'user': f"{ctx.author.name}#{ctx.author.discriminator}",
        'guild': ctx.guild.name if ctx.guild else 'DM',
        'error': str(error),
        'traceback': traceback.format_exc()
    }
    recent_errors.append(error_info)
    
    # Mantener solo los últimos errores
    if len(recent_errors) > MAX_ERROR_LOG:
        recent_errors.pop(0)
    
    logger.error(f"Error en comando {ctx.command}: {error}")
    logger.error(traceback.format_exc())
    
    # Mensaje de error para el usuario
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Comando no encontrado. Usa `!help` para ver los comandos disponibles.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Faltan argumentos requeridos. Usa `!help {ctx.command.name}` para más información.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Argumento inválido. Verifica el formato del comando.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ Comando en cooldown. Intenta en {error.retry_after:.1f} segundos.")
    else:
        await ctx.send("❌ Ocurrió un error inesperado. Por favor, intenta más tarde.")

# ============================================================================
# TAREAS EN SEGUNDO PLANO
# ============================================================================

@tasks.loop(hours=1)
async def cleanup_errors():
    """Limpia errores antiguos del log"""
    current_time = datetime.now()
    global recent_errors
    
    # Remover errores más antiguos de 24 horas
    recent_errors = [
        error for error in recent_errors 
        if current_time - error['timestamp'] < timedelta(hours=24)
    ]
    
    logger.info(f"Limpieza de errores completada. {len(recent_errors)} errores en log.")

@tasks.loop(minutes=30)
async def update_presence():
    """Actualiza el estado del bot periódicamente"""
    try:
        # Cambiar entre diferentes estados
        activities = [
            discord.Activity(type=discord.ActivityType.watching, name="!help para comandos"),
            discord.Activity(type=discord.ActivityType.playing, name="con cotizaciones"),
            discord.Activity(type=discord.ActivityType.listening, name="!cotizacion")
        ]
        
        current_activity = activities[int(time.time() / 1800) % len(activities)]
        await bot.change_presence(activity=current_activity)
        
    except Exception as e:
        logger.error(f"Error actualizando presencia: {e}")

# ============================================================================
# FUNCIONES DE CARGA DE COGS
# ============================================================================

async def load_cogs():
    """Carga todos los cogs del bot"""
    try:
        # Crear directorio cogs si no existe
        if not os.path.exists('cogs'):
            logger.warning("Directorio 'cogs' no encontrado. Creando...")
            os.makedirs('cogs')
            logger.info("Directorio 'cogs' creado.")
            return
        
        # Cargar cogs
        cog_files = [f for f in os.listdir('cogs') if f.endswith('.py') and not f.startswith('__')]
        
        for cog_file in cog_files:
            try:
                cog_name = f"cogs.{cog_file[:-3]}"
                await bot.load_extension(cog_name)
                logger.info(f"✅ Cog cargado: {cog_name}")
            except Exception as e:
                logger.error(f"❌ Error cargando cog {cog_file}: {e}")
        
        logger.info(f"📦 Total de cogs cargados: {len(bot.cogs)}")
        
    except Exception as e:
        logger.error(f"Error en load_cogs: {e}")

# ============================================================================
# COMANDOS BÁSICOS (mantenidos en el archivo principal)
# ============================================================================

@bot.command(name='reload')
@commands.is_owner()  # Solo el dueño del bot puede usar este comando
async def reload_command(ctx):
    """Recarga todos los cogs (solo para el dueño del bot)"""
    try:
        await load_cogs()
        embed = discord.Embed(
            title="🔄 Recarga Completada",
            description="Todos los cogs han sido recargados exitosamente.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error en reload_command: {e}")
        await ctx.send("❌ Error al recargar los cogs.")

@bot.command(name='status')
async def status_command(ctx):
    """Muestra el estado general del bot"""
    try:
        uptime = time.time() - bot_stats.start_time
        uptime_str = str(timedelta(seconds=int(uptime)))
        
        embed = discord.Embed(
            title="📊 Estado del Bot",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🕐 Información General",
            value=f"• Uptime: {uptime_str}\n"
                  f"• Servidores: {len(bot.guilds)}\n"
                  f"• Usuarios: {len(bot.users)}\n"
                  f"• Latencia: {round(bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="📈 Estadísticas",
            value=f"• Comandos ejecutados: {bot_stats.command_count}\n"
                  f"• Errores totales: {bot_stats.error_count}\n"
                  f"• Cogs cargados: {len(bot.cogs)}",
            inline=True
        )
        
        # Estado de las tareas
        tasks_status = []
        if cleanup_errors.is_running():
            tasks_status.append("✅ Limpieza de errores")
        else:
            tasks_status.append("❌ Limpieza de errores")
            
        if update_presence.is_running():
            tasks_status.append("✅ Actualización de presencia")
        else:
            tasks_status.append("❌ Actualización de presencia")
        
        embed.add_field(
            name="⚙️ Tareas en Segundo Plano",
            value="\n".join(tasks_status),
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error en status_command: {e}")
        await ctx.send("❌ Error al obtener el estado del bot.")

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal que ejecuta el bot"""
    # Obtener token del bot desde variables de entorno
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not bot_token:
        logger.error("❌ No se encontró DISCORD_BOT_TOKEN en las variables de entorno.")
        logger.error("Por favor, crea un archivo .env con: DISCORD_BOT_TOKEN=tu_token_aqui")
        return
    
    try:
        logger.info("🤖 Iniciando bot de Discord (versión modular)...")
        
        # Iniciar tarea de actualización de presencia
        update_presence.start()
        
        bot.run(bot_token)
    except discord.LoginFailure:
        logger.error("❌ Token de bot inválido. Verifica tu DISCORD_BOT_TOKEN.")
    except Exception as e:
        logger.error(f"❌ Error al iniciar el bot: {e}")

if __name__ == '__main__':
    main()