"""
Optimized Debug Commands Cog
Provides comprehensive debugging, monitoring, and system diagnostic tools.
"""

import logging
import psutil
import platform
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import traceback

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

class DebugCommands(commands.Cog):
    """Advanced debugging and monitoring commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.command_history = []
        self.max_history = 100
    
    def _add_to_history(self, command_info: Dict[str, Any]):
        """Add command execution to history"""
        self.command_history.append(command_info)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Network information
            network = psutil.net_io_counters()
            
            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else 'N/A'
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                }
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def _get_bot_performance_metrics(self) -> Dict[str, Any]:
        """Get bot performance metrics"""
        uptime = datetime.now() - datetime.fromtimestamp(self.bot.stats['start_time'])
        
        # Calculate command rate
        commands_per_hour = (self.bot.stats['commands_executed'] / max(uptime.total_seconds() / 3600, 1))
        
        # Calculate error rate
        error_rate = (self.bot.stats['errors_occurred'] / max(self.bot.stats['commands_executed'], 1)) * 100
        
        # Calculate cache efficiency
        total_cache_requests = self.bot.stats['cache_hits'] + self.bot.stats['cache_misses']
        cache_hit_rate = (self.bot.stats['cache_hits'] / max(total_cache_requests, 1)) * 100
        
        return {
            'uptime': uptime,
            'commands_executed': self.bot.stats['commands_executed'],
            'errors_occurred': self.bot.stats['errors_occurred'],
            'api_calls': self.bot.stats['api_calls'],
            'cache_hits': self.bot.stats['cache_hits'],
            'cache_misses': self.bot.stats['cache_misses'],
            'commands_per_hour': commands_per_hour,
            'error_rate': error_rate,
            'cache_hit_rate': cache_hit_rate,
            'latency': self.bot.latency * 1000,  # Convert to milliseconds
            'guilds': len(self.bot.guilds),
            'users': len(self.bot.users),
            'cogs_loaded': len(self.bot.cogs)
        }
    
    @commands.command(name='system')
    @commands.cooldown(1, 60, commands.BucketType.user)  # 1 use per minute per user
    async def system_command(self, ctx):
        """Get detailed system information"""
        try:
            system_info = self._get_system_info()
            
            if not system_info:
                await ctx.send("❌ Error al obtener información del sistema.")
                return
            
            embed = discord.Embed(
                title="🖥️ Información del Sistema",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Platform information
            embed.add_field(
                name="💻 Plataforma",
                value=f"• Sistema: {system_info['platform']}\n"
                      f"• Python: {system_info['python_version']}",
                inline=True
            )
            
            # CPU information
            cpu_info = system_info['cpu']
            embed.add_field(
                name="⚡ CPU",
                value=f"• Uso: {cpu_info['percent']:.1f}%\n"
                      f"• Núcleos: {cpu_info['count']}\n"
                      f"• Frecuencia: {cpu_info['frequency']:.0f} MHz" if isinstance(cpu_info['frequency'], (int, float)) else f"• Frecuencia: {cpu_info['frequency']}",
                inline=True
            )
            
            # Memory information
            memory_info = system_info['memory']
            embed.add_field(
                name="🧠 Memoria",
                value=f"• Total: {self._format_bytes(memory_info['total'])}\n"
                      f"• Usado: {self._format_bytes(memory_info['used'])}\n"
                      f"• Libre: {self._format_bytes(memory_info['available'])}\n"
                      f"• Uso: {memory_info['percent']:.1f}%",
                inline=True
            )
            
            # Disk information
            disk_info = system_info['disk']
            embed.add_field(
                name="💾 Disco",
                value=f"• Total: {self._format_bytes(disk_info['total'])}\n"
                      f"• Usado: {self._format_bytes(disk_info['used'])}\n"
                      f"• Libre: {self._format_bytes(disk_info['free'])}\n"
                      f"• Uso: {disk_info['percent']:.1f}%",
                inline=True
            )
            
            # Network information
            network_info = system_info['network']
            embed.add_field(
                name="🌐 Red",
                value=f"• Enviado: {self._format_bytes(network_info['bytes_sent'])}\n"
                      f"• Recibido: {self._format_bytes(network_info['bytes_recv'])}",
                inline=True
            )
            
            embed.set_footer(text="Información del sistema en tiempo real")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in system_command: {e}")
            await ctx.send("❌ Error al obtener información del sistema.")
    
    @commands.command(name='performance')
    @commands.cooldown(1, 30, commands.BucketType.user)  # 1 use per 30 seconds per user
    async def performance_command(self, ctx):
        """Get bot performance metrics"""
        try:
            metrics = self._get_bot_performance_metrics()
            
            embed = discord.Embed(
                title="📊 Métricas de Rendimiento",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            # Basic metrics
            embed.add_field(
                name="⏱️ Tiempo y Uso",
                value=f"• Uptime: {str(metrics['uptime']).split('.')[0]}\n"
                      f"• Comandos/hora: {metrics['commands_per_hour']:.1f}\n"
                      f"• Latencia: {metrics['latency']:.0f}ms",
                inline=True
            )
            
            # Statistics
            embed.add_field(
                name="📈 Estadísticas",
                value=f"• Comandos ejecutados: {metrics['commands_executed']:,}\n"
                      f"• Errores: {metrics['errors_occurred']:,}\n"
                      f"• Tasa de error: {metrics['error_rate']:.2f}%",
                inline=True
            )
            
            # Cache performance
            embed.add_field(
                name="💾 Cache",
                value=f"• Hits: {metrics['cache_hits']:,}\n"
                      f"• Misses: {metrics['cache_misses']:,}\n"
                      f"• Hit rate: {metrics['cache_hit_rate']:.1f}%",
                inline=True
            )
            
            # API usage
            embed.add_field(
                name="🔗 API",
                value=f"• Llamadas API: {metrics['api_calls']:,}\n"
                      f"• Cogs cargados: {metrics['cogs_loaded']}",
                inline=True
            )
            
            # Connection info
            embed.add_field(
                name="🔗 Conexión",
                value=f"• Servidores: {metrics['guilds']}\n"
                      f"• Usuarios: {metrics['users']}",
                inline=True
            )
            
            # Health status
            health_color = discord.Color.green() if self.bot.health_status['status'] == 'healthy' else discord.Color.red()
            embed.add_field(
                name="🏥 Estado de Salud",
                value=f"• Estado: {self.bot.health_status['status'].title()}\n"
                      f"• Último check: {datetime.fromtimestamp(self.bot.health_status['last_check']).strftime('%H:%M:%S')}",
                inline=True
            )
            
            embed.set_footer(text="Métricas de rendimiento del bot")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in performance_command: {e}")
            await ctx.send("❌ Error al obtener métricas de rendimiento.")
    
    @commands.command(name='errors')
    @commands.cooldown(1, 60, commands.BucketType.user)  # 1 use per minute per user
    async def errors_command(self, ctx):
        """Show recent errors and their details"""
        try:
            if not self.bot.recent_errors:
                embed = discord.Embed(
                    title="✅ Sin Errores",
                    description="No se han registrado errores recientes.",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                await ctx.send(embed=embed)
                return
            
            # Get the most recent errors
            recent_errors = self.bot.recent_errors[-10:]  # Last 10 errors
            
            embed = discord.Embed(
                title="❌ Errores Recientes",
                description=f"Mostrando los últimos {len(recent_errors)} errores",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            
            for i, error in enumerate(reversed(recent_errors), 1):
                error_time = error['timestamp'].strftime('%H:%M:%S')
                command = error['command']
                error_type = error['error_type']
                error_msg = error['error_message'][:100] + "..." if len(error['error_message']) > 100 else error['error_message']
                
                embed.add_field(
                    name=f"#{i} - {error_time}",
                    value=f"**Comando:** {command}\n"
                          f"**Tipo:** {error_type}\n"
                          f"**Error:** {error_msg}",
                    inline=False
                )
            
            embed.set_footer(text=f"Total de errores: {len(self.bot.recent_errors)}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in errors_command: {e}")
            await ctx.send("❌ Error al obtener información de errores.")
    
    @commands.command(name='rate_limits')
    @commands.cooldown(1, 60, commands.BucketType.user)  # 1 use per minute per user
    async def rate_limits_command(self, ctx):
        """Show current rate limit information"""
        try:
            if not self.bot.rate_limits:
                embed = discord.Embed(
                    title="✅ Sin Rate Limits",
                    description="No hay usuarios con rate limits activos.",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="⏰ Rate Limits Activos",
                description=f"Usuarios con rate limits: {len(self.bot.rate_limits)}",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            
            # Show top 10 users with most rate limit entries
            sorted_users = sorted(
                self.bot.rate_limits.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:10]
            
            for user_id, timestamps in sorted_users:
                try:
                    user = await self.bot.fetch_user(user_id)
                    user_name = user.name
                except:
                    user_name = f"Usuario {user_id}"
                
                embed.add_field(
                    name=f"👤 {user_name}",
                    value=f"• Comandos recientes: {len(timestamps)}\n"
                          f"• Último comando: {datetime.fromtimestamp(timestamps[-1]).strftime('%H:%M:%S')}",
                    inline=True
                )
            
            embed.set_footer(text="Rate limits por usuario")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in rate_limits_command: {e}")
            await ctx.send("❌ Error al obtener información de rate limits.")
    
    @commands.command(name='cache_info')
    @commands.cooldown(1, 30, commands.BucketType.user)  # 1 use per 30 seconds per user
    async def cache_info_command(self, ctx):
        """Show cache information and statistics"""
        try:
            # Get cache statistics from currency cog if available
            currency_cog = self.bot.get_cog('CurrencyCommands')
            cache_stats = {}
            
            if currency_cog:
                cache_stats = {
                    'entries': len(currency_cog.cached_data),
                    'oldest_entry': None,
                    'newest_entry': None
                }
                
                if currency_cog.cached_data:
                    timestamps = [entry[0] for entry in currency_cog.cached_data.values()]
                    cache_stats['oldest_entry'] = min(timestamps)
                    cache_stats['newest_entry'] = max(timestamps)
            
            embed = discord.Embed(
                title="💾 Información de Cache",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Bot cache stats
            total_cache_requests = self.bot.stats['cache_hits'] + self.bot.stats['cache_misses']
            cache_hit_rate = (self.bot.stats['cache_hits'] / max(total_cache_requests, 1)) * 100
            
            embed.add_field(
                name="📊 Estadísticas Generales",
                value=f"• Hits: {self.bot.stats['cache_hits']:,}\n"
                      f"• Misses: {self.bot.stats['cache_misses']:,}\n"
                      f"• Hit rate: {cache_hit_rate:.1f}%",
                inline=True
            )
            
            # Currency cache info
            if cache_stats:
                embed.add_field(
                    name="💰 Cache de Monedas",
                    value=f"• Entradas: {cache_stats['entries']}\n"
                          f"• Duración: 5 minutos",
                    inline=True
                )
                
                if cache_stats['newest_entry']:
                    embed.add_field(
                        name="🕐 Última Actualización",
                        value=f"• Entrada más nueva: {cache_stats['newest_entry'].strftime('%H:%M:%S')}",
                        inline=True
                    )
            
            # Cache configuration
            embed.add_field(
                name="⚙️ Configuración",
                value=f"• TTL: 5 minutos\n"
                      f"• Tamaño máximo: 1000 entradas",
                inline=True
            )
            
            embed.set_footer(text="Información del sistema de cache")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in cache_info_command: {e}")
            await ctx.send("❌ Error al obtener información de cache.")
    
    @commands.command(name='guilds')
    @commands.cooldown(1, 120, commands.BucketType.user)  # 1 use per 2 minutes per user
    async def guilds_command(self, ctx):
        """Show information about all guilds the bot is in"""
        try:
            embed = discord.Embed(
                title="🏠 Servidores del Bot",
                description=f"Bot presente en {len(self.bot.guilds)} servidores",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Sort guilds by member count
            sorted_guilds = sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True)
            
            # Show top 10 guilds
            for i, guild in enumerate(sorted_guilds[:10], 1):
                embed.add_field(
                    name=f"#{i} - {guild.name}",
                    value=f"• Miembros: {guild.member_count:,}\n"
                          f"• Canales: {len(guild.channels)}\n"
                          f"• Creado: {guild.created_at.strftime('%d/%m/%Y')}",
                    inline=True
                )
            
            if len(self.bot.guilds) > 10:
                embed.add_field(
                    name="📋 Más Servidores",
                    value=f"Y {len(self.bot.guilds) - 10} servidores más...",
                    inline=False
                )
            
            embed.set_footer(text=f"Total de servidores: {len(self.bot.guilds)}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in guilds_command: {e}")
            await ctx.send("❌ Error al obtener información de servidores.")
    
    @commands.command(name='test_api')
    @commands.cooldown(1, 300, commands.BucketType.user)  # 1 use per 5 minutes per user
    async def test_api_command(self, ctx):
        """Test API connectivity and response times"""
        try:
            embed = discord.Embed(
                title="🔗 Test de API",
                description="Probando conectividad con las APIs...",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Test currency API
            start_time = datetime.now()
            try:
                import impuestito
                from impuestito.main import oficial
                rate = oficial
                api_time = (datetime.now() - start_time).total_seconds() * 1000
                
                embed.add_field(
                    name="✅ API de Monedas",
                    value=f"• Estado: Conectado\n"
                          f"• Tiempo de respuesta: {api_time:.0f}ms\n"
                          f"• Dólar oficial: ${rate:,.2f}",
                    inline=True
                )
            except Exception as e:
                embed.add_field(
                    name="❌ API de Monedas",
                    value=f"• Estado: Error\n"
                          f"• Error: {str(e)[:50]}...",
                    inline=True
                )
            
            # Test Discord API
            start_time = datetime.now()
            try:
                await self.bot.fetch_user(self.bot.user.id)
                discord_time = (datetime.now() - start_time).total_seconds() * 1000
                
                embed.add_field(
                    name="✅ API de Discord",
                    value=f"• Estado: Conectado\n"
                          f"• Tiempo de respuesta: {discord_time:.0f}ms\n"
                          f"• Latencia: {self.bot.latency * 1000:.0f}ms",
                    inline=True
                )
            except Exception as e:
                embed.add_field(
                    name="❌ API de Discord",
                    value=f"• Estado: Error\n"
                          f"• Error: {str(e)[:50]}...",
                    inline=True
                )
            
            embed.set_footer(text="Test de conectividad completado")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in test_api_command: {e}")
            await ctx.send("❌ Error al realizar test de API.")
    
    @system_command.error
    @performance_command.error
    @errors_command.error
    @rate_limits_command.error
    @cache_info_command.error
    @guilds_command.error
    @test_api_command.error
    async def debug_command_error(self, ctx, error):
        """Handle errors specific to debug commands"""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏰ Comando en cooldown. Intenta en {error.retry_after:.1f} segundos."
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes permisos para usar este comando.")
        else:
            logger.error(f"Unexpected error in {ctx.command.name}: {error}")
            await ctx.send("❌ Ocurrió un error inesperado. Por favor, intenta más tarde.")

async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(DebugCommands(bot))