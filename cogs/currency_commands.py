"""
Optimized Currency Commands Cog
Handles all currency-related commands with caching, rate limiting, and error handling.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import traceback

import discord
from discord.ext import commands
import impuestito
from impuestito.main import (
    cotization, oficial, blue, euro, euro_blue, 
    calcularImpuestoPais, CDolarOficial
)

logger = logging.getLogger(__name__)

class CurrencyCommands(commands.Cog):
    """Optimized currency and tax calculation commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.last_api_call = 0
        self.api_cooldown = 30  # 30 seconds between API calls
        self.cached_data = {}
        self.cache_duration = 300  # 5 minutes cache
    
    def _get_cache_key(self, command: str, *args) -> str:
        """Generate cache key for command and arguments"""
        return f"{command}:{':'.join(map(str, args))}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cached_data:
            return False
        
        cache_time, _ = self.cached_data[cache_key]
        return datetime.now() - cache_time < timedelta(seconds=self.cache_duration)
    
    def _set_cache(self, cache_key: str, data: Any):
        """Set data in cache with timestamp"""
        self.cached_data[cache_key] = (datetime.now(), data)
    
    def _get_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if self._is_cache_valid(cache_key):
            return self.cached_data[cache_key][1]
        return None
    
    async def _rate_limit_api(self):
        """Rate limit API calls to avoid overwhelming the service"""
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_api_call
        
        if time_since_last < self.api_cooldown:
            wait_time = self.api_cooldown - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_api_call = current_time
    
    async def _safe_api_call(self, api_func, *args, **kwargs):
        """Safely call API functions with error handling and rate limiting"""
        try:
            await self._rate_limit_api()
            self.bot.update_stats('api_calls')
            return api_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API call error: {e}")
            raise
    
    def _format_currency(self, value: float, currency: str = "ARS") -> str:
        """Format currency values with proper formatting"""
        if value is None or value == 0:
            return "N/A"
        
        if currency == "ARS":
            return f"${value:,.2f}"
        elif currency == "USD":
            return f"${value:,.2f}"
        else:
            return f"{value:,.2f}"
    
    def _create_currency_embed(self, title: str, value: float, color: discord.Color, 
                             currency: str = "ARS", additional_info: str = None) -> discord.Embed:
        """Create a standardized currency embed"""
        embed = discord.Embed(
            title=title,
            description=f"**{self._format_currency(value, currency)}**",
            color=color,
            timestamp=datetime.now()
        )
        
        if additional_info:
            embed.add_field(name="ℹ️ Información", value=additional_info, inline=False)
        
        embed.set_footer(text="Datos proporcionados por Impuestito")
        return embed
    
    @commands.command(name='cotizacion', aliases=['cotizaciones', 'cot'])
    @commands.cooldown(1, 30, commands.BucketType.user)  # 1 use per 30 seconds per user
    async def cotizacion_command(self, ctx):
        """Get complete currency exchange rates with caching"""
        cache_key = self._get_cache_key('cotizacion')
        cached_data = self._get_cache(cache_key)
        
        if cached_data:
            self.bot.update_stats('cache_hits')
            embed = cached_data
        else:
            self.bot.update_stats('cache_misses')
            
            try:
                # Get fresh data from API
                cotizacion_data = await self._safe_api_call(lambda: cotization)
                
                embed = discord.Embed(
                    title="📊 Cotizaciones Actuales",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                
                # Process each currency type
                currencies = {
                    'oficial': ('💵 Dólar Oficial', discord.Color.green()),
                    'blue': ('💙 Dólar Blue', discord.Color.blue()),
                    'oficial_euro': ('🇪🇺 Euro Oficial', discord.Color.gold()),
                    'blue_euro': ('🇪🇺💙 Euro Blue', discord.Color.purple())
                }
                
                for key, (name, color) in currencies.items():
                    if key in cotizacion_data:
                        data = cotizacion_data[key]
                        value = f"Compra: {self._format_currency(data.get('value_buy'))}\n"
                        value += f"Venta: {self._format_currency(data.get('value_sell'))}\n"
                        value += f"Promedio: {self._format_currency(data.get('value_avg'))}"
                        
                        embed.add_field(name=name, value=value, inline=True)
                
                # Add last update info
                if 'last_update' in cotizacion_data:
                    embed.set_footer(text=f"Última actualización: {cotizacion_data['last_update']}")
                
                # Cache the embed
                self._set_cache(cache_key, embed)
                
            except Exception as e:
                logger.error(f"Error in cotizacion_command: {e}")
                await ctx.send("❌ Error al obtener las cotizaciones. Intenta más tarde.")
                return
        
        await ctx.send(embed=embed)
    
    @commands.command(name='oficial')
    @commands.cooldown(2, 60, commands.BucketType.user)  # 2 uses per minute per user
    async def oficial_command(self, ctx):
        """Get official dollar rate"""
        cache_key = self._get_cache_key('oficial')
        cached_data = self._get_cache(cache_key)
        
        if cached_data:
            self.bot.update_stats('cache_hits')
            embed = cached_data
        else:
            self.bot.update_stats('cache_misses')
            
            try:
                value = await self._safe_api_call(lambda: oficial)
                embed = self._create_currency_embed(
                    "💵 Dólar Oficial",
                    value,
                    discord.Color.green(),
                    "ARS",
                    "Cotización oficial del Banco Central"
                )
                self._set_cache(cache_key, embed)
                
            except Exception as e:
                logger.error(f"Error in oficial_command: {e}")
                await ctx.send("❌ Error al obtener el dólar oficial.")
                return
        
        await ctx.send(embed=embed)
    
    @commands.command(name='blue')
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def blue_command(self, ctx):
        """Get blue dollar rate"""
        cache_key = self._get_cache_key('blue')
        cached_data = self._get_cache(cache_key)
        
        if cached_data:
            self.bot.update_stats('cache_hits')
            embed = cached_data
        else:
            self.bot.update_stats('cache_misses')
            
            try:
                value = await self._safe_api_call(lambda: blue)
                embed = self._create_currency_embed(
                    "💙 Dólar Blue",
                    value,
                    discord.Color.blue(),
                    "ARS",
                    "Cotización del mercado paralelo"
                )
                self._set_cache(cache_key, embed)
                
            except Exception as e:
                logger.error(f"Error in blue_command: {e}")
                await ctx.send("❌ Error al obtener el dólar blue.")
                return
        
        await ctx.send(embed=embed)
    
    @commands.command(name='euro')
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def euro_command(self, ctx):
        """Get official euro rate"""
        cache_key = self._get_cache_key('euro')
        cached_data = self._get_cache(cache_key)
        
        if cached_data:
            self.bot.update_stats('cache_hits')
            embed = cached_data
        else:
            self.bot.update_stats('cache_misses')
            
            try:
                value = await self._safe_api_call(lambda: euro)
                embed = self._create_currency_embed(
                    "🇪🇺 Euro Oficial",
                    value,
                    discord.Color.gold(),
                    "ARS",
                    "Cotización oficial del euro"
                )
                self._set_cache(cache_key, embed)
                
            except Exception as e:
                logger.error(f"Error in euro_command: {e}")
                await ctx.send("❌ Error al obtener el euro oficial.")
                return
        
        await ctx.send(embed=embed)
    
    @commands.command(name='euro_blue')
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def euro_blue_command(self, ctx):
        """Get blue euro rate"""
        cache_key = self._get_cache_key('euro_blue')
        cached_data = self._get_cache(cache_key)
        
        if cached_data:
            self.bot.update_stats('cache_hits')
            embed = cached_data
        else:
            self.bot.update_stats('cache_misses')
            
            try:
                value = await self._safe_api_call(lambda: euro_blue)
                embed = self._create_currency_embed(
                    "🇪🇺💙 Euro Blue",
                    value,
                    discord.Color.purple(),
                    "ARS",
                    "Cotización del euro en el mercado paralelo"
                )
                self._set_cache(cache_key, embed)
                
            except Exception as e:
                logger.error(f"Error in euro_blue_command: {e}")
                await ctx.send("❌ Error al obtener el euro blue.")
                return
        
        await ctx.send(embed=embed)
    
    @commands.command(name='impuesto_pais', aliases=['impuesto'])
    @commands.cooldown(3, 60, commands.BucketType.user)  # 3 uses per minute per user
    async def impuesto_pais_command(self, ctx, cantidad: float):
        """Calculate country tax with validation and error handling"""
        # Validate input
        if cantidad <= 0:
            await ctx.send("❌ La cantidad debe ser mayor a 0.")
            return
        
        if cantidad > 1000000:  # Limit to prevent abuse
            await ctx.send("❌ La cantidad máxima permitida es $1,000,000 USD.")
            return
        
        cache_key = self._get_cache_key('impuesto_pais', cantidad)
        cached_data = self._get_cache(cache_key)
        
        if cached_data:
            self.bot.update_stats('cache_hits')
            embed = cached_data
        else:
            self.bot.update_stats('cache_misses')
            
            try:
                # Calculate tax
                resultado = await self._safe_api_call(calcularImpuestoPais, cantidad)
                
                embed = discord.Embed(
                    title="💰 Cálculo Impuesto País",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name="📊 Detalles del Cálculo",
                    value=f"• Cantidad original: {self._format_currency(resultado['cantidadVieja'], 'USD')}\n"
                          f"• Impuesto agregado: {self._format_currency(resultado['agregado'], 'USD')}\n"
                          f"• Cantidad final: {self._format_currency(resultado['cantidadFinal'], 'USD')}",
                    inline=False
                )
                
                embed.add_field(
                    name="💡 Información",
                    value="El impuesto país es del 30% sobre la cantidad original.\n"
                          "Este impuesto se aplica a compras en moneda extranjera.",
                    inline=False
                )
                
                embed.set_footer(text="Cálculo basado en la normativa vigente")
                self._set_cache(cache_key, embed)
                
            except ValueError:
                await ctx.send("❌ La cantidad debe ser un número válido.")
                return
            except Exception as e:
                logger.error(f"Error in impuesto_pais_command: {e}")
                await ctx.send("❌ Error al calcular el impuesto país.")
                return
        
        await ctx.send(embed=embed)
    
    @commands.command(name='dolar_pesos', aliases=['usd_ars'])
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def dolar_pesos_command(self, ctx, cantidad_usd: float):
        """Convert USD to ARS with validation"""
        # Validate input
        if cantidad_usd <= 0:
            await ctx.send("❌ La cantidad debe ser mayor a 0.")
            return
        
        if cantidad_usd > 1000000:  # Limit to prevent abuse
            await ctx.send("❌ La cantidad máxima permitida es $1,000,000 USD.")
            return
        
        cache_key = self._get_cache_key('dolar_pesos', cantidad_usd)
        cached_data = self._get_cache(cache_key)
        
        if cached_data:
            self.bot.update_stats('cache_hits')
            embed = cached_data
        else:
            self.bot.update_stats('cache_misses')
            
            try:
                # Get current exchange rate
                cotizacion = await self._safe_api_call(lambda: oficial)
                pesos = cotizacion * cantidad_usd
                
                embed = discord.Embed(
                    title="💱 Conversión Dólar a Pesos",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name="📊 Detalles de la Conversión",
                    value=f"• Cantidad: {self._format_currency(cantidad_usd, 'USD')}\n"
                          f"• Cotización: {self._format_currency(cotizacion, 'ARS')}/USD\n"
                          f"• Resultado: {self._format_currency(pesos, 'ARS')}",
                    inline=False
                )
                
                embed.add_field(
                    name="ℹ️ Información",
                    value="Conversión realizada usando la cotización oficial del dólar.",
                    inline=False
                )
                
                embed.set_footer(text="Cotización oficial del Banco Central")
                self._set_cache(cache_key, embed)
                
            except ValueError:
                await ctx.send("❌ La cantidad debe ser un número válido.")
                return
            except Exception as e:
                logger.error(f"Error in dolar_pesos_command: {e}")
                await ctx.send("❌ Error al convertir dólares a pesos.")
                return
        
        await ctx.send(embed=embed)
    
    @commands.command(name='pesos_dolar', aliases=['ars_usd'])
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def pesos_dolar_command(self, ctx, cantidad_pesos: float):
        """Convert ARS to USD with validation"""
        # Validate input
        if cantidad_pesos <= 0:
            await ctx.send("❌ La cantidad debe ser mayor a 0.")
            return
        
        if cantidad_pesos > 1000000000:  # Limit to prevent abuse
            await ctx.send("❌ La cantidad máxima permitida es $1,000,000,000 ARS.")
            return
        
        cache_key = self._get_cache_key('pesos_dolar', cantidad_pesos)
        cached_data = self._get_cache(cache_key)
        
        if cached_data:
            self.bot.update_stats('cache_hits')
            embed = cached_data
        else:
            self.bot.update_stats('cache_misses')
            
            try:
                # Get current exchange rate
                cotizacion = await self._safe_api_call(lambda: oficial)
                dolares = cantidad_pesos / cotizacion
                
                embed = discord.Embed(
                    title="💱 Conversión Pesos a Dólar",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name="📊 Detalles de la Conversión",
                    value=f"• Cantidad: {self._format_currency(cantidad_pesos, 'ARS')}\n"
                          f"• Cotización: {self._format_currency(cotizacion, 'ARS')}/USD\n"
                          f"• Resultado: {self._format_currency(dolares, 'USD')}",
                    inline=False
                )
                
                embed.add_field(
                    name="ℹ️ Información",
                    value="Conversión realizada usando la cotización oficial del dólar.",
                    inline=False
                )
                
                embed.set_footer(text="Cotización oficial del Banco Central")
                self._set_cache(cache_key, embed)
                
            except ValueError:
                await ctx.send("❌ La cantidad debe ser un número válido.")
                return
            except Exception as e:
                logger.error(f"Error in pesos_dolar_command: {e}")
                await ctx.send("❌ Error al convertir pesos a dólares.")
                return
        
        await ctx.send(embed=embed)
    
    @commands.command(name='comparar')
    @commands.cooldown(2, 120, commands.BucketType.user)  # 2 uses per 2 minutes per user
    async def comparar_command(self, ctx, cantidad: float):
        """Compare different exchange rates for a given amount"""
        # Validate input
        if cantidad <= 0:
            await ctx.send("❌ La cantidad debe ser mayor a 0.")
            return
        
        if cantidad > 100000:  # Limit to prevent abuse
            await ctx.send("❌ La cantidad máxima permitida es $100,000 USD.")
            return
        
        cache_key = self._get_cache_key('comparar', cantidad)
        cached_data = self._get_cache(cache_key)
        
        if cached_data:
            self.bot.update_stats('cache_hits')
            embed = cached_data
        else:
            self.bot.update_stats('cache_misses')
            
            try:
                # Get all exchange rates
                oficial_rate = await self._safe_api_call(lambda: oficial)
                blue_rate = await self._safe_api_call(lambda: blue)
                
                embed = discord.Embed(
                    title="📊 Comparación de Cotizaciones",
                    description=f"Comparación para {self._format_currency(cantidad, 'USD')}",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                
                # Calculate conversions
                oficial_pesos = cantidad * oficial_rate
                blue_pesos = cantidad * blue_rate
                diferencia = blue_pesos - oficial_pesos
                diferencia_porcentual = (diferencia / oficial_pesos) * 100
                
                embed.add_field(
                    name="💵 Dólar Oficial",
                    value=f"• Cotización: {self._format_currency(oficial_rate, 'ARS')}\n"
                          f"• Resultado: {self._format_currency(oficial_pesos, 'ARS')}",
                    inline=True
                )
                
                embed.add_field(
                    name="💙 Dólar Blue",
                    value=f"• Cotización: {self._format_currency(blue_rate, 'ARS')}\n"
                          f"• Resultado: {self._format_currency(blue_pesos, 'ARS')}",
                    inline=True
                )
                
                embed.add_field(
                    name="📈 Diferencia",
                    value=f"• Diferencia: {self._format_currency(diferencia, 'ARS')}\n"
                          f"• Porcentaje: {diferencia_porcentual:+.1f}%",
                    inline=True
                )
                
                embed.set_footer(text="Comparación de cotizaciones oficial vs blue")
                self._set_cache(cache_key, embed)
                
            except Exception as e:
                logger.error(f"Error in comparar_command: {e}")
                await ctx.send("❌ Error al comparar las cotizaciones.")
                return
        
        await ctx.send(embed=embed)
    
    @cotizacion_command.error
    @oficial_command.error
    @blue_command.error
    @euro_command.error
    @euro_blue_command.error
    @impuesto_pais_command.error
    @dolar_pesos_command.error
    @pesos_dolar_command.error
    @comparar_command.error
    async def currency_command_error(self, ctx, error):
        """Handle errors specific to currency commands"""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏰ Comando en cooldown. Intenta en {error.retry_after:.1f} segundos."
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"❌ Faltan argumentos requeridos. Usa `!help {ctx.command.name}` "
                f"para más información."
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argumento inválido. Verifica que el valor sea un número válido.")
        else:
            logger.error(f"Unexpected error in {ctx.command.name}: {error}")
            await ctx.send("❌ Ocurrió un error inesperado. Por favor, intenta más tarde.")

async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(CurrencyCommands(bot))