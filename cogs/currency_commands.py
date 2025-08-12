"""
Cog para comandos de cotizaciones y conversiones de monedas
"""

import logging
from datetime import datetime
from discord.ext import commands
import discord
import impuestito
from impuestito.main import (
    cotization, oficial, blue, euro, euro_blue, 
    calcularImpuestoPais
)

logger = logging.getLogger(__name__)

class CurrencyCommands(commands.Cog):
    """Comandos relacionados con cotizaciones y conversiones de monedas"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='cotizacion', aliases=['cotizaciones', 'cot'])
    async def cotizacion_command(self, ctx):
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
    
    @commands.command(name='oficial')
    async def oficial_command(self, ctx):
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
    
    @commands.command(name='blue')
    async def blue_command(self, ctx):
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
    
    @commands.command(name='euro')
    async def euro_command(self, ctx):
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
    
    @commands.command(name='euro_blue')
    async def euro_blue_command(self, ctx):
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
    
    @commands.command(name='impuesto_pais', aliases=['impuesto'])
    async def impuesto_pais_command(self, ctx, cantidad: float):
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
    
    @commands.command(name='dolar_pesos', aliases=['usd_ars'])
    async def dolar_pesos_command(self, ctx, cantidad_usd: float):
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

async def setup(bot):
    """Función para cargar el cog"""
    await bot.add_cog(CurrencyCommands(bot))