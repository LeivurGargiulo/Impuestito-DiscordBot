#!/usr/bin/env python3
"""
Discord Bot para Impuestito
Bot de Discord que proporciona información sobre cotizaciones de monedas
y cálculos de impuestos en Argentina usando el paquete impuestito.
Convertido desde el bot de Telegram original.
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import traceback

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import impuestito
from impuestito.main import (
    cotization, oficial, blue, euro, euro_blue, 
    calcularImpuestoPais, CDolarOficial
)

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

# ============================================================================
# COMANDOS DEL BOT
# ============================================================================

@bot.command(name='start', aliases=['help', 'ayuda'])
async def start_command(ctx):
    """Comando de inicio - Mensaje de bienvenida"""
    embed = discord.Embed(
        title="🤖 Bot de Impuestito",
        description="¡Hola! Soy un bot que te proporciona información sobre cotizaciones de monedas y cálculos de impuestos en Argentina.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📋 Comandos disponibles:",
        value="""
• `!start` - Muestra este mensaje de ayuda
• `!cotizacion` - Cotización actual de todas las monedas
• `!oficial` - Cotización del dólar oficial
• `!blue` - Cotización del dólar blue
• `!euro` - Cotización del euro oficial
• `!euro_blue` - Cotización del euro blue
• `!impuesto_pais <cantidad>` - Calcula el impuesto país
• `!dolar_pesos <cantidad>` - Convierte dólares a pesos
• `!debug` - Información de estado del bot
        """,
        inline=False
    )
    
    embed.add_field(
        name="💡 Ejemplo:",
        value="`!impuesto_pais 100` para calcular el impuesto país sobre $100 USD",
        inline=False
    )
    
    embed.set_footer(text="Bot de Impuestito para Discord")
    embed.timestamp = datetime.now()
    
    await ctx.send(embed=embed)

@bot.command(name='cotizacion', aliases=['cotizaciones', 'cot'])
async def cotizacion_command(ctx):
    """Comando de cotización completa"""
    try:
        # Crear embed para la respuesta
        embed = discord.Embed(
            title="📊 Cotizaciones Actuales",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        # Obtener cotización completa
        cotizacion_data = cotization
        
        # Dólar Oficial
        if 'oficial' in cotizacion_data:
            oficial_data = cotizacion_data['oficial']
            embed.add_field(
                name="💵 Dólar Oficial",
                value=f"Compra: ${oficial_data.get('value_buy', 'N/A')}\n"
                      f"Venta: ${oficial_data.get('value_sell', 'N/A')}\n"
                      f"Promedio: ${oficial_data.get('value_avg', 'N/A')}",
                inline=True
            )
        
        # Dólar Blue
        if 'blue' in cotizacion_data:
            blue_data = cotizacion_data['blue']
            embed.add_field(
                name="💙 Dólar Blue",
                value=f"Compra: ${blue_data.get('value_buy', 'N/A')}\n"
                      f"Venta: ${blue_data.get('value_sell', 'N/A')}\n"
                      f"Promedio: ${blue_data.get('value_avg', 'N/A')}",
                inline=True
            )
        
        # Euro Oficial
        if 'oficial_euro' in cotizacion_data:
            euro_oficial_data = cotizacion_data['oficial_euro']
            embed.add_field(
                name="🇪🇺 Euro Oficial",
                value=f"Compra: ${euro_oficial_data.get('value_buy', 'N/A')}\n"
                      f"Venta: ${euro_oficial_data.get('value_sell', 'N/A')}\n"
                      f"Promedio: ${euro_oficial_data.get('value_avg', 'N/A')}",
                inline=True
            )
        
        # Euro Blue
        if 'blue_euro' in cotizacion_data:
            euro_blue_data = cotizacion_data['blue_euro']
            embed.add_field(
                name="🇪🇺💙 Euro Blue",
                value=f"Compra: ${euro_blue_data.get('value_buy', 'N/A')}\n"
                      f"Venta: ${euro_blue_data.get('value_sell', 'N/A')}\n"
                      f"Promedio: ${euro_blue_data.get('value_avg', 'N/A')}",
                inline=True
            )
        
        # Última actualización
        if 'last_update' in cotizacion_data:
            embed.set_footer(text=f"Última actualización: {cotizacion_data['last_update']}")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error en cotizacion_command: {e}")
        await ctx.send("❌ Error al obtener las cotizaciones. Intenta más tarde.")

@bot.command(name='oficial')
async def oficial_command(ctx):
    """Comando para dólar oficial"""
    try:
        embed = discord.Embed(
            title="💵 Dólar Oficial",
            description=f"**${oficial}**",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error en oficial_command: {e}")
        await ctx.send("❌ Error al obtener el dólar oficial.")

@bot.command(name='blue')
async def blue_command(ctx):
    """Comando para dólar blue"""
    try:
        embed = discord.Embed(
            title="💙 Dólar Blue",
            description=f"**${blue}**",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error en blue_command: {e}")
        await ctx.send("❌ Error al obtener el dólar blue.")

@bot.command(name='euro')
async def euro_command(ctx):
    """Comando para euro oficial"""
    try:
        embed = discord.Embed(
            title="🇪🇺 Euro Oficial",
            description=f"**${euro}**",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error en euro_command: {e}")
        await ctx.send("❌ Error al obtener el euro oficial.")

@bot.command(name='euro_blue')
async def euro_blue_command(ctx):
    """Comando para euro blue"""
    try:
        embed = discord.Embed(
            title="🇪🇺💙 Euro Blue",
            description=f"**${euro_blue}**",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error en euro_blue_command: {e}")
        await ctx.send("❌ Error al obtener el euro blue.")

@bot.command(name='impuesto_pais', aliases=['impuesto'])
async def impuesto_pais_command(ctx, cantidad: float):
    """Comando para calcular impuesto país"""
    try:
        # Calcular impuesto país
        resultado = calcularImpuestoPais(cantidad)
        
        # Crear embed
        embed = discord.Embed(
            title="💰 Cálculo Impuesto País",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📊 Detalles",
            value=f"• Cantidad original: ${resultado['cantidadVieja']} USD\n"
                  f"• Impuesto agregado: ${resultado['agregado']} USD\n"
                  f"• Cantidad final: ${resultado['cantidadFinal']} USD",
            inline=False
        )
        
        embed.add_field(
            name="💡 Información",
            value="El impuesto país es del 30% sobre la cantidad original.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except ValueError:
        await ctx.send("❌ La cantidad debe ser un número válido.")
    except Exception as e:
        logger.error(f"Error en impuesto_pais_command: {e}")
        await ctx.send("❌ Error al calcular el impuesto país.")

@bot.command(name='dolar_pesos', aliases=['usd_ars'])
async def dolar_pesos_command(ctx, cantidad_usd: float):
    """Comando para convertir dólares a pesos"""
    try:
        # Calcular conversión usando el dólar oficial
        pesos = oficial * cantidad_usd
        
        # Crear embed
        embed = discord.Embed(
            title="💱 Conversión Dólar a Pesos",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📊 Conversión",
            value=f"• Cantidad: ${cantidad_usd} USD\n"
                  f"• Cotización: ${oficial} ARS/USD\n"
                  f"• Resultado: ${pesos:,.2f} ARS",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except ValueError:
        await ctx.send("❌ La cantidad debe ser un número válido.")
    except Exception as e:
        logger.error(f"Error en dolar_pesos_command: {e}")
        await ctx.send("❌ Error al convertir dólares a pesos.")

@bot.command(name='debug')
@commands.cooldown(1, 30, commands.BucketType.user)  # 1 uso cada 30 segundos por usuario
async def debug_command(ctx):
    """Comando de debug - Información del bot"""
    try:
        # Calcular uptime
        uptime = time.time() - bot_stats.start_time
        uptime_str = str(timedelta(seconds=int(uptime)))
        
        # Crear embed de debug
        embed = discord.Embed(
            title="🔧 Información de Debug",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📊 Estadísticas del Bot",
            value=f"• Uptime: {uptime_str}\n"
                  f"• Comandos ejecutados: {bot_stats.command_count}\n"
                  f"• Errores totales: {bot_stats.error_count}\n"
                  f"• Servidores: {len(bot.guilds)}\n"
                  f"• Usuarios: {len(bot.users)}",
            inline=True
        )
        
        embed.add_field(
            name="🔗 Información de Conexión",
            value=f"• Latencia: {round(bot.latency * 1000)}ms\n"
                  f"• Versión Discord.py: {discord.__version__}\n"
                  f"• Python: {discord.sys.version.split()[0]}",
            inline=True
        )
        
        # Información del último error
        if bot_stats.last_error:
            embed.add_field(
                name="⚠️ Último Error",
                value=f"```{str(bot_stats.last_error)[:500]}...```" if len(str(bot_stats.last_error)) > 500 else f"```{str(bot_stats.last_error)}```",
                inline=False
            )
        
        # Errores recientes
        if recent_errors:
            recent_errors_text = "\n".join([
                f"• {error['timestamp'].strftime('%H:%M:%S')} - {error['command']} - {error['error'][:50]}..."
                for error in recent_errors[-3:]  # Solo los últimos 3 errores
            ])
            embed.add_field(
                name="📝 Errores Recientes",
                value=recent_errors_text,
                inline=False
            )
        
        embed.set_footer(text=f"Debug solicitado por {ctx.author.name}")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error en debug_command: {e}")
        await ctx.send("❌ Error al obtener información de debug.")

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
        logger.info("🤖 Iniciando bot de Discord...")
        bot.run(bot_token)
    except discord.LoginFailure:
        logger.error("❌ Token de bot inválido. Verifica tu DISCORD_BOT_TOKEN.")
    except Exception as e:
        logger.error(f"❌ Error al iniciar el bot: {e}")

if __name__ == '__main__':
    main()