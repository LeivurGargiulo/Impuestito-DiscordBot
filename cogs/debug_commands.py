"""
Cog para comandos de debug y utilidades del bot
"""

import logging
import time
import sys
from datetime import datetime, timedelta
from discord.ext import commands
import discord

logger = logging.getLogger(__name__)

class DebugCommands(commands.Cog):
    """Comandos de debug y utilidades del bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.command_count = 0
        self.error_count = 0
        self.last_error = None
        self.recent_errors = []
        self.MAX_ERROR_LOG = 10
    
    @commands.command(name='start', aliases=['help', 'ayuda'])
    async def start_command(self, ctx):
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
    
    @commands.command(name='debug')
    @commands.cooldown(1, 30, commands.BucketType.user)  # 1 uso cada 30 segundos por usuario
    async def debug_command(self, ctx):
        """Comando de debug - Información del bot"""
        try:
            # Calcular uptime
            uptime = time.time() - self.start_time
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
                      f"• Comandos ejecutados: {self.command_count}\n"
                      f"• Errores totales: {self.error_count}\n"
                      f"• Servidores: {len(self.bot.guilds)}\n"
                      f"• Usuarios: {len(self.bot.users)}",
                inline=True
            )
            
            embed.add_field(
                name="🔗 Información de Conexión",
                value=f"• Latencia: {round(self.bot.latency * 1000)}ms\n"
                      f"• Versión Discord.py: {discord.__version__}\n"
                      f"• Python: {sys.version.split()[0]}",
                inline=True
            )
            
            # Información del último error
            if self.last_error:
                embed.add_field(
                    name="⚠️ Último Error",
                    value=f"```{str(self.last_error)[:500]}...```" if len(str(self.last_error)) > 500 else f"```{str(self.last_error)}```",
                    inline=False
                )
            
            # Errores recientes
            if self.recent_errors:
                recent_errors_text = "\n".join([
                    f"• {error['timestamp'].strftime('%H:%M:%S')} - {error['command']} - {error['error'][:50]}..."
                    for error in self.recent_errors[-3:]  # Solo los últimos 3 errores
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
    
    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Comando para verificar la latencia del bot"""
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latencia: **{round(self.bot.latency * 1000)}ms**",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='servers', aliases=['guilds'])
    async def servers_command(self, ctx):
        """Comando para mostrar información de servidores"""
        embed = discord.Embed(
            title="🏠 Servidores Conectados",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for guild in self.bot.guilds:
            embed.add_field(
                name=guild.name,
                value=f"• ID: {guild.id}\n"
                      f"• Miembros: {guild.member_count}\n"
                      f"• Creado: {guild.created_at.strftime('%Y-%m-%d')}",
                inline=True
            )
        
        embed.set_footer(text=f"Total: {len(self.bot.guilds)} servidores")
        await ctx.send(embed=embed)
    
    def log_command(self):
        """Registra el uso de un comando"""
        self.command_count += 1
    
    def log_error(self, error, command_name="Unknown", user=None, guild=None):
        """Registra un error"""
        self.error_count += 1
        self.last_error = error
        
        error_info = {
            'timestamp': datetime.now(),
            'command': command_name,
            'user': user,
            'guild': guild,
            'error': str(error)
        }
        
        self.recent_errors.append(error_info)
        
        # Mantener solo los últimos errores
        if len(self.recent_errors) > self.MAX_ERROR_LOG:
            self.recent_errors.pop(0)

async def setup(bot):
    """Función para cargar el cog"""
    await bot.add_cog(DebugCommands(bot))