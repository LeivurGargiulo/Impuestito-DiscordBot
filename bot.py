#!/usr/bin/env python3
"""
Production-Ready Discord Bot for Impuestito
A clean, optimized, and maintainable Discord bot that provides currency exchange
and tax calculation information for Argentina using the impuestito package.

Features:
- Efficient asynchronous event handling
- Comprehensive error handling and logging
- Rate limit management
- Intelligent caching system
- Secure environment variable management
- Modular architecture for scalability
- Performance optimizations
- Production-ready monitoring and health checks
"""

import asyncio
import logging
import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import traceback
from pathlib import Path

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import aiohttp
import aioredis
from cachetools import TTLCache

# Load environment variables
load_dotenv()

# Configure logging with proper formatting and levels
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot configuration
class BotConfig:
    """Centralized configuration management"""
    
    def __init__(self):
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.owner_id = int(os.getenv('BOT_OWNER_ID', '0'))
        self.prefix = os.getenv('BOT_PREFIX', '!')
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # Rate limiting configuration
        self.rate_limit_commands = int(os.getenv('RATE_LIMIT_COMMANDS', '5'))
        self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
        
        # Cache configuration
        self.cache_ttl = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes
        self.cache_maxsize = int(os.getenv('CACHE_MAXSIZE', '1000'))
        
        # API configuration
        self.api_timeout = int(os.getenv('API_TIMEOUT', '10'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        # Redis configuration (optional)
        self.redis_url = os.getenv('REDIS_URL')
        
        # Health check configuration
        self.health_check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', '300'))  # 5 minutes

config = BotConfig()

# Initialize bot with proper intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class ImpuestitoBot(commands.Bot):
    """Enhanced Discord bot with production-ready features"""
    
    def __init__(self):
        super().__init__(
            command_prefix=config.prefix,
            intents=intents,
            help_command=None,
            description="Bot de Impuestito - Cotizaciones y cálculos de impuestos"
        )
        
        # Initialize caches
        self.command_cache = TTLCache(
            maxsize=config.cache_maxsize,
            ttl=config.cache_ttl
        )
        self.api_cache = TTLCache(
            maxsize=config.cache_maxsize,
            ttl=config.cache_ttl
        )
        
        # Statistics tracking
        self.stats = {
            'start_time': time.time(),
            'commands_executed': 0,
            'errors_occurred': 0,
            'api_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Rate limiting
        self.rate_limits = {}
        self.recent_errors = []
        self.max_error_log = 50
        
        # Session management
        self.session = None
        self.redis = None
        
        # Health monitoring
        self.health_status = {
            'last_check': time.time(),
            'status': 'healthy',
            'issues': []
        }
    
    async def setup_hook(self):
        """Initialize bot resources"""
        logger.info("🔧 Setting up bot resources...")
        
        # Create aiohttp session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=config.api_timeout)
        )
        
        # Initialize Redis if configured
        if config.redis_url:
            try:
                self.redis = await aioredis.from_url(config.redis_url)
                logger.info("✅ Redis connection established")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}")
        
        # Load cogs
        await self.load_cogs()
        
        logger.info("✅ Bot setup completed")
    
    async def load_cogs(self):
        """Load all cogs from the cogs directory"""
        cogs_dir = Path("cogs")
        if not cogs_dir.exists():
            logger.warning("📁 Cogs directory not found, creating...")
            cogs_dir.mkdir(exist_ok=True)
            return
        
        cog_files = [f for f in cogs_dir.glob("*.py") if f.is_file() and not f.name.startswith("__")]
        
        for cog_file in cog_files:
            try:
                cog_name = f"cogs.{cog_file.stem}"
                await self.load_extension(cog_name)
                logger.info(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                logger.error(f"❌ Failed to load cog {cog_file.name}: {e}")
        
        logger.info(f"📦 Total cogs loaded: {len(self.cogs)}")
    
    async def close(self):
        """Cleanup bot resources"""
        logger.info("🧹 Cleaning up bot resources...")
        
        if self.session:
            await self.session.close()
        
        if self.redis:
            await self.redis.close()
        
        await super().close()
    
    def update_stats(self, stat_type: str, value: int = 1):
        """Update bot statistics"""
        if stat_type in self.stats:
            self.stats[stat_type] += value
    
    def add_error(self, error_info: Dict[str, Any]):
        """Add error to recent errors log"""
        self.recent_errors.append(error_info)
        if len(self.recent_errors) > self.max_error_log:
            self.recent_errors.pop(0)
    
    def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is rate limited"""
        current_time = time.time()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # Remove old entries
        self.rate_limits[user_id] = [
            timestamp for timestamp in self.rate_limits[user_id]
            if current_time - timestamp < config.rate_limit_window
        ]
        
        # Check if user has exceeded rate limit
        if len(self.rate_limits[user_id]) >= config.rate_limit_commands:
            return False
        
        # Add current request
        self.rate_limits[user_id].append(current_time)
        return True
    
    async def get_cached_data(self, key: str) -> Optional[Any]:
        """Get data from cache"""
        if key in self.api_cache:
            self.update_stats('cache_hits')
            return self.api_cache[key]
        
        self.update_stats('cache_misses')
        return None
    
    def set_cached_data(self, key: str, data: Any):
        """Set data in cache"""
        self.api_cache[key] = data

# Create bot instance
bot = ImpuestitoBot()

# ============================================================================
# EVENT HANDLERS
# ============================================================================

@bot.event
async def on_ready():
    """Bot ready event with enhanced logging and status"""
    logger.info(f"🤖 Bot connected as {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"📊 Connected to {len(bot.guilds)} guilds")
    logger.info(f"👥 Serving {len(bot.users)} users")
    
    # Set bot presence
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="!help para comandos"
        )
    )
    
    # Start background tasks
    cleanup_tasks.start()
    health_check.start()
    update_presence.start()
    
    logger.info("✅ Bot is ready and operational")

@bot.event
async def on_command(ctx):
    """Command execution event with enhanced tracking"""
    bot.update_stats('commands_executed')
    
    # Log command usage
    logger.info(
        f"📝 Command executed: {ctx.command.name} by {ctx.author} "
        f"in {ctx.guild.name if ctx.guild else 'DM'}"
    )
    
    # Check rate limiting
    if not bot.check_rate_limit(ctx.author.id):
        await ctx.send(
            f"⏰ Rate limit exceeded. Please wait before using commands again. "
            f"Limit: {config.rate_limit_commands} commands per {config.rate_limit_window} seconds."
        )
        return

@bot.event
async def on_command_error(ctx, error):
    """Enhanced error handling with detailed logging and user feedback"""
    bot.update_stats('errors_occurred')
    
    # Create detailed error info
    error_info = {
        'timestamp': datetime.now(),
        'command': ctx.command.name if ctx.command else 'Unknown',
        'user': f"{ctx.author.name}#{ctx.author.discriminator}",
        'user_id': ctx.author.id,
        'guild': ctx.guild.name if ctx.guild else 'DM',
        'guild_id': ctx.guild.id if ctx.guild else None,
        'channel': ctx.channel.name if hasattr(ctx.channel, 'name') else 'DM',
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc()
    }
    
    bot.add_error(error_info)
    
    # Log error
    logger.error(f"❌ Command error: {error}")
    logger.error(f"📋 Error details: {error_info}")
    
    # Handle specific error types
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "❌ Comando no encontrado. Usa `!help` para ver los comandos disponibles."
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"❌ Faltan argumentos requeridos. Usa `!help {ctx.command.name}` "
            f"para más información."
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "❌ Argumento inválido. Verifica el formato del comando."
        )
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"⏰ Comando en cooldown. Intenta en {error.retry_after:.1f} segundos."
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ No tienes permisos para usar este comando."
        )
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(
            "❌ El bot no tiene los permisos necesarios para ejecutar este comando."
        )
    else:
        # Log unexpected errors
        logger.error(f"🔍 Unexpected error: {traceback.format_exc()}")
        await ctx.send(
            "❌ Ocurrió un error inesperado. Los administradores han sido notificados."
        )

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

@tasks.loop(hours=1)
async def cleanup_tasks():
    """Cleanup old data and maintain bot health"""
    try:
        current_time = time.time()
        
        # Cleanup rate limits
        for user_id in list(bot.rate_limits.keys()):
            bot.rate_limits[user_id] = [
                timestamp for timestamp in bot.rate_limits[user_id]
                if current_time - timestamp < config.rate_limit_window
            ]
            if not bot.rate_limits[user_id]:
                del bot.rate_limits[user_id]
        
        # Cleanup old errors (keep last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        bot.recent_errors = [
            error for error in bot.recent_errors
            if error['timestamp'] > cutoff_time
        ]
        
        logger.info("🧹 Cleanup completed")
        
    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")

@tasks.loop(minutes=config.health_check_interval)
async def health_check():
    """Perform health checks and update status"""
    try:
        issues = []
        
        # Check bot latency
        if bot.latency > 1.0:  # More than 1 second
            issues.append(f"High latency: {bot.latency:.2f}s")
        
        # Check error rate
        if bot.stats['errors_occurred'] > 0:
            error_rate = bot.stats['errors_occurred'] / max(bot.stats['commands_executed'], 1)
            if error_rate > 0.1:  # More than 10% error rate
                issues.append(f"High error rate: {error_rate:.2%}")
        
        # Check cache performance
        total_cache_requests = bot.stats['cache_hits'] + bot.stats['cache_misses']
        if total_cache_requests > 0:
            cache_hit_rate = bot.stats['cache_hits'] / total_cache_requests
            if cache_hit_rate < 0.5:  # Less than 50% cache hit rate
                issues.append(f"Low cache hit rate: {cache_hit_rate:.2%}")
        
        # Update health status
        bot.health_status.update({
            'last_check': time.time(),
            'status': 'unhealthy' if issues else 'healthy',
            'issues': issues
        })
        
        if issues:
            logger.warning(f"⚠️ Health check issues: {issues}")
        else:
            logger.info("✅ Health check passed")
            
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        bot.health_status['status'] = 'error'

@tasks.loop(minutes=5)
async def update_presence():
    """Update bot presence with rotating status messages"""
    try:
        activities = [
            discord.Activity(type=discord.ActivityType.watching, name="!help para comandos"),
            discord.Activity(type=discord.ActivityType.playing, name="con cotizaciones"),
            discord.Activity(type=discord.ActivityType.listening, name="!cotizacion"),
            discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servidores")
        ]
        
        current_activity = activities[int(time.time() / 300) % len(activities)]
        await bot.change_presence(activity=current_activity)
        
    except Exception as e:
        logger.error(f"❌ Presence update error: {e}")

# ============================================================================
# UTILITY COMMANDS
# ============================================================================

@bot.command(name='help', aliases=['ayuda', 'start'])
async def help_command(ctx):
    """Enhanced help command with detailed information"""
    embed = discord.Embed(
        title="🤖 Bot de Impuestito",
        description="Bot optimizado para cotizaciones de monedas y cálculos de impuestos en Argentina.",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="📋 Comandos de Cotización",
        value="""
• `!cotizacion` - Cotización completa de todas las monedas
• `!oficial` - Cotización del dólar oficial
• `!blue` - Cotización del dólar blue
• `!euro` - Cotización del euro oficial
• `!euro_blue` - Cotización del euro blue
        """,
        inline=True
    )
    
    embed.add_field(
        name="💰 Comandos de Cálculo",
        value="""
• `!impuesto_pais <cantidad>` - Calcula el impuesto país
• `!dolar_pesos <cantidad>` - Convierte dólares a pesos
• `!pesos_dolar <cantidad>` - Convierte pesos a dólares
        """,
        inline=True
    )
    
    embed.add_field(
        name="🔧 Comandos de Utilidad",
        value="""
• `!status` - Estado del bot y estadísticas
• `!ping` - Latencia del bot
• `!info` - Información del servidor
        """,
        inline=True
    )
    
    embed.add_field(
        name="💡 Ejemplos",
        value="""
• `!impuesto_pais 100` - Calcula impuesto país sobre $100 USD
• `!dolar_pesos 50` - Convierte $50 USD a pesos
• `!cotizacion` - Ver todas las cotizaciones
        """,
        inline=False
    )
    
    embed.set_footer(text="Bot optimizado para rendimiento y estabilidad")
    
    await ctx.send(embed=embed)

@bot.command(name='status')
async def status_command(ctx):
    """Enhanced status command with detailed bot information"""
    uptime = time.time() - bot.stats['start_time']
    uptime_str = str(timedelta(seconds=int(uptime)))
    
    embed = discord.Embed(
        title="📊 Estado del Bot",
        color=discord.Color.green() if bot.health_status['status'] == 'healthy' else discord.Color.red(),
        timestamp=datetime.now()
    )
    
    # General information
    embed.add_field(
        name="🕐 Información General",
        value=f"• Uptime: {uptime_str}\n"
              f"• Servidores: {len(bot.guilds)}\n"
              f"• Usuarios: {len(bot.users)}\n"
              f"• Latencia: {round(bot.latency * 1000)}ms\n"
              f"• Estado: {bot.health_status['status'].title()}",
        inline=True
    )
    
    # Statistics
    embed.add_field(
        name="📈 Estadísticas",
        value=f"• Comandos ejecutados: {bot.stats['commands_executed']:,}\n"
              f"• Errores totales: {bot.stats['errors_occurred']:,}\n"
              f"• Llamadas API: {bot.stats['api_calls']:,}\n"
              f"• Cogs cargados: {len(bot.cogs)}",
        inline=True
    )
    
    # Cache performance
    total_cache_requests = bot.stats['cache_hits'] + bot.stats['cache_misses']
    if total_cache_requests > 0:
        cache_hit_rate = bot.stats['cache_hits'] / total_cache_requests
        embed.add_field(
            name="💾 Rendimiento de Cache",
            value=f"• Hit rate: {cache_hit_rate:.1%}\n"
                  f"• Hits: {bot.stats['cache_hits']:,}\n"
                  f"• Misses: {bot.stats['cache_misses']:,}",
            inline=True
        )
    
    # Health issues
    if bot.health_status['issues']:
        embed.add_field(
            name="⚠️ Problemas Detectados",
            value="\n".join(f"• {issue}" for issue in bot.health_status['issues']),
            inline=False
        )
    
    embed.set_footer(text=f"Solicitado por {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    """Simple ping command to check bot responsiveness"""
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latencia: **{round(bot.latency * 1000)}ms**",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    
    await ctx.send(embed=embed)

@bot.command(name='info')
async def info_command(ctx):
    """Server information command"""
    guild = ctx.guild
    
    embed = discord.Embed(
        title=f"📋 Información de {guild.name}",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="👥 Miembros",
        value=f"• Total: {guild.member_count}\n"
              f"• Humanos: {len([m for m in guild.members if not m.bot])}\n"
              f"• Bots: {len([m for m in guild.members if m.bot])}",
        inline=True
    )
    
    embed.add_field(
        name="📅 Información",
        value=f"• Creado: {guild.created_at.strftime('%d/%m/%Y')}\n"
              f"• Dueño: {guild.owner.name}\n"
              f"• Región: {guild.region if hasattr(guild, 'region') else 'N/A'}",
        inline=True
    )
    
    embed.add_field(
        name="📊 Canales",
        value=f"• Texto: {len(guild.text_channels)}\n"
              f"• Voz: {len(guild.voice_channels)}\n"
              f"• Categorías: {len(guild.categories)}",
        inline=True
    )
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.set_footer(text=f"ID del servidor: {guild.id}")
    
    await ctx.send(embed=embed)

# ============================================================================
# ADMIN COMMANDS
# ============================================================================

@bot.command(name='reload')
@commands.is_owner()
async def reload_command(ctx):
    """Reload all cogs (owner only)"""
    try:
        await bot.load_cogs()
        embed = discord.Embed(
            title="🔄 Recarga Completada",
            description="Todos los cogs han sido recargados exitosamente.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"❌ Reload error: {e}")
        await ctx.send("❌ Error al recargar los cogs.")

@bot.command(name='debug')
@commands.is_owner()
async def debug_command(ctx):
    """Debug information (owner only)"""
    embed = discord.Embed(
        title="🔧 Información de Debug",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    
    # Recent errors
    if bot.recent_errors:
        recent_errors_text = "\n".join([
            f"• {error['timestamp'].strftime('%H:%M:%S')} - {error['command']} - {error['error_message'][:50]}..."
            for error in bot.recent_errors[-5:]  # Last 5 errors
        ])
        embed.add_field(
            name="📝 Errores Recientes",
            value=recent_errors_text,
            inline=False
        )
    
    # Rate limit info
    rate_limit_info = f"Usuarios con rate limit: {len(bot.rate_limits)}"
    embed.add_field(
        name="⏰ Rate Limits",
        value=rate_limit_info,
        inline=True
    )
    
    # Cache info
    cache_info = f"Tamaño: {len(bot.api_cache)}/{config.cache_maxsize}"
    embed.add_field(
        name="💾 Cache",
        value=cache_info,
        inline=True
    )
    
    embed.set_footer(text="Comando de debug - Solo para administradores")
    
    await ctx.send(embed=embed)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function with proper error handling and validation"""
    # Validate configuration
    if not config.token:
        logger.error("❌ DISCORD_BOT_TOKEN not found in environment variables")
        logger.error("💡 Create a .env file with: DISCORD_BOT_TOKEN=your_token_here")
        return
    
    if not config.owner_id:
        logger.warning("⚠️ BOT_OWNER_ID not set. Some admin commands will be unavailable.")
    
    try:
        logger.info("🤖 Starting Impuestito Discord Bot...")
        logger.info(f"🔧 Configuration: Prefix={config.prefix}, Debug={config.debug_mode}")
        
        # Run the bot
        bot.run(config.token, log_handler=None)
        
    except discord.LoginFailure:
        logger.error("❌ Invalid bot token. Please check your DISCORD_BOT_TOKEN.")
    except discord.HTTPException as e:
        logger.error(f"❌ HTTP error: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    main()