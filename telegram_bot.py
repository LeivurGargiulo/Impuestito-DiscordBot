#!/usr/bin/env python3
"""
Telegram Bot para Impuestito
Bot de Telegram que proporciona información sobre cotizaciones de monedas
y cálculos de impuestos en Argentina usando el paquete impuestito.
"""

import asyncio
import logging
from typing import Dict, Any
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import impuestito
from impuestito.main import (
    cotization, oficial, blue, euro, euro_blue, 
    calcularImpuestoPais, CDolarOficial
)

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot - REEMPLAZAR CON TU TOKEN REAL
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /start - Mensaje de bienvenida"""
    welcome_message = """
🤖 *Bot de Impuestito*

¡Hola! Soy un bot que te proporciona información sobre cotizaciones de monedas y cálculos de impuestos en Argentina.

📋 *Comandos disponibles:*

• `/start` - Muestra este mensaje de ayuda
• `/cotizacion` - Cotización actual de todas las monedas
• `/oficial` - Cotización del dólar oficial
• `/blue` - Cotización del dólar blue
• `/euro` - Cotización del euro oficial
• `/euro_blue` - Cotización del euro blue
• `/impuesto_pais <cantidad>` - Calcula el impuesto país (ej: `/impuesto_pais 100`)
• `/dolar_pesos <cantidad>` - Convierte dólares a pesos (ej: `/dolar_pesos 100`)

💡 *Ejemplo:* `/impuesto_pais 100` para calcular el impuesto país sobre $100 USD
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def cotizacion_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /cotizacion - Cotización completa"""
    try:
        # Obtener cotización completa
        cotizacion_data = cotization
        
        # Formatear respuesta
        response = "📊 *Cotizaciones Actuales*\n\n"
        
        # Dólar Oficial
        if 'oficial' in cotizacion_data:
            oficial_data = cotizacion_data['oficial']
            response += f"💵 *Dólar Oficial:*\n"
            response += f"  • Compra: ${oficial_data.get('value_buy', 'N/A')}\n"
            response += f"  • Venta: ${oficial_data.get('value_sell', 'N/A')}\n"
            response += f"  • Promedio: ${oficial_data.get('value_avg', 'N/A')}\n\n"
        
        # Dólar Blue
        if 'blue' in cotizacion_data:
            blue_data = cotizacion_data['blue']
            response += f"💙 *Dólar Blue:*\n"
            response += f"  • Compra: ${blue_data.get('value_buy', 'N/A')}\n"
            response += f"  • Venta: ${blue_data.get('value_sell', 'N/A')}\n"
            response += f"  • Promedio: ${blue_data.get('value_avg', 'N/A')}\n\n"
        
        # Euro Oficial
        if 'oficial_euro' in cotizacion_data:
            euro_oficial_data = cotizacion_data['oficial_euro']
            response += f"🇪🇺 *Euro Oficial:*\n"
            response += f"  • Compra: ${euro_oficial_data.get('value_buy', 'N/A')}\n"
            response += f"  • Venta: ${euro_oficial_data.get('value_sell', 'N/A')}\n"
            response += f"  • Promedio: ${euro_oficial_data.get('value_avg', 'N/A')}\n\n"
        
        # Euro Blue
        if 'blue_euro' in cotizacion_data:
            euro_blue_data = cotizacion_data['blue_euro']
            response += f"🇪🇺💙 *Euro Blue:*\n"
            response += f"  • Compra: ${euro_blue_data.get('value_buy', 'N/A')}\n"
            response += f"  • Venta: ${euro_blue_data.get('value_sell', 'N/A')}\n"
            response += f"  • Promedio: ${euro_blue_data.get('value_avg', 'N/A')}\n\n"
        
        # Última actualización
        if 'last_update' in cotizacion_data:
            response += f"🕐 *Última actualización:* {cotizacion_data['last_update']}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en cotizacion_command: {e}")
        await update.message.reply_text("❌ Error al obtener las cotizaciones. Intenta más tarde.")

async def oficial_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /oficial - Dólar oficial"""
    try:
        response = f"💵 *Dólar Oficial:* ${oficial}"
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error en oficial_command: {e}")
        await update.message.reply_text("❌ Error al obtener el dólar oficial.")

async def blue_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /blue - Dólar blue"""
    try:
        response = f"💙 *Dólar Blue:* ${blue}"
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error en blue_command: {e}")
        await update.message.reply_text("❌ Error al obtener el dólar blue.")

async def euro_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /euro - Euro oficial"""
    try:
        response = f"🇪🇺 *Euro Oficial:* ${euro}"
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error en euro_command: {e}")
        await update.message.reply_text("❌ Error al obtener el euro oficial.")

async def euro_blue_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /euro_blue - Euro blue"""
    try:
        response = f"🇪🇺💙 *Euro Blue:* ${euro_blue}"
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error en euro_blue_command: {e}")
        await update.message.reply_text("❌ Error al obtener el euro blue.")

async def impuesto_pais_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /impuesto_pais - Calcula impuesto país"""
    try:
        # Verificar si se proporcionó una cantidad
        if not context.args:
            await update.message.reply_text(
                "❌ Por favor proporciona una cantidad.\n"
                "Ejemplo: `/impuesto_pais 100`", 
                parse_mode='Markdown'
            )
            return
        
        # Obtener cantidad del argumento
        try:
            cantidad = float(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ La cantidad debe ser un número válido.")
            return
        
        # Calcular impuesto país
        resultado = calcularImpuestoPais(cantidad)
        
        # Formatear respuesta
        response = f"💰 *Cálculo Impuesto País*\n\n"
        response += f"• Cantidad original: ${resultado['cantidadVieja']} USD\n"
        response += f"• Impuesto agregado: ${resultado['agregado']} USD\n"
        response += f"• Cantidad final: ${resultado['cantidadFinal']} USD\n\n"
        response += f"💡 El impuesto país es del 30% sobre la cantidad original."
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en impuesto_pais_command: {e}")
        await update.message.reply_text("❌ Error al calcular el impuesto país.")

async def dolar_pesos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /dolar_pesos - Convierte dólares a pesos"""
    try:
        # Verificar si se proporcionó una cantidad
        if not context.args:
            await update.message.reply_text(
                "❌ Por favor proporciona una cantidad.\n"
                "Ejemplo: `/dolar_pesos 100`", 
                parse_mode='Markdown'
            )
            return
        
        # Obtener cantidad del argumento
        try:
            cantidad_usd = float(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ La cantidad debe ser un número válido.")
            return
        
        # Calcular conversión usando el dólar oficial
        pesos = oficial * cantidad_usd
        
        # Formatear respuesta
        response = f"💱 *Conversión Dólar a Pesos*\n\n"
        response += f"• Cantidad: ${cantidad_usd} USD\n"
        response += f"• Cotización: ${oficial} ARS/USD\n"
        response += f"• Resultado: ${pesos:,.2f} ARS"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en dolar_pesos_command: {e}")
        await update.message.reply_text("❌ Error al convertir dólares a pesos.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja errores del bot"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Enviar mensaje de error al usuario si es posible
    if update and hasattr(update, 'message') and update.message:
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. Por favor, intenta más tarde."
        )

def main() -> None:
    """Función principal que ejecuta el bot"""
    # Crear aplicación
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Agregar manejadores de comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("cotizacion", cotizacion_command))
    application.add_handler(CommandHandler("oficial", oficial_command))
    application.add_handler(CommandHandler("blue", blue_command))
    application.add_handler(CommandHandler("euro", euro_command))
    application.add_handler(CommandHandler("euro_blue", euro_blue_command))
    application.add_handler(CommandHandler("impuesto_pais", impuesto_pais_command))
    application.add_handler(CommandHandler("dolar_pesos", dolar_pesos_command))
    
    # Agregar manejador de errores
    application.add_error_handler(error_handler)
    
    # Iniciar el bot
    print("🤖 Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()