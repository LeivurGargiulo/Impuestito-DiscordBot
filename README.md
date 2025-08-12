# Bot de Telegram para Impuestito

Un bot de Telegram que proporciona información sobre cotizaciones de monedas y cálculos de impuestos en Argentina usando el paquete `impuestito`.

## Características

- 📊 Cotizaciones en tiempo real de dólar oficial, blue, euro oficial y euro blue
- 💰 Cálculo de impuesto país
- 💱 Conversión de dólares a pesos argentinos
- 🤖 Interfaz en español con emojis
- ⚡ Manejo asíncrono de comandos
- 🛡️ Manejo robusto de errores

## Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Obtener token de Telegram:**
   - Habla con [@BotFather](https://t.me/BotFather) en Telegram
   - Crea un nuevo bot con `/newbot`
   - Copia el token que te proporciona

3. **Configurar el bot:**
   - Abre el archivo `telegram_bot.py`
   - Reemplaza `"YOUR_TELEGRAM_BOT_TOKEN"` con tu token real

## Uso

1. **Ejecutar el bot:**
   ```bash
   python telegram_bot.py
   ```

2. **Comandos disponibles:**
   - `/start` - Mensaje de bienvenida y ayuda
   - `/cotizacion` - Cotización completa de todas las monedas
   - `/oficial` - Cotización del dólar oficial
   - `/blue` - Cotización del dólar blue
   - `/euro` - Cotización del euro oficial
   - `/euro_blue` - Cotización del euro blue
   - `/impuesto_pais <cantidad>` - Calcula el impuesto país
   - `/dolar_pesos <cantidad>` - Convierte dólares a pesos

## Ejemplos

```
/impuesto_pais 100
/dolar_pesos 50
/cotizacion
```

## Estructura del Proyecto

```
├── telegram_bot.py      # Código principal del bot
├── requirements.txt     # Dependencias del proyecto
└── README.md           # Este archivo
```

## Tecnologías Utilizadas

- **python-telegram-bot** (v20+) - Framework para bots de Telegram
- **impuestito** - Paquete para obtener cotizaciones argentinas
- **asyncio** - Programación asíncrona
- **logging** - Sistema de logs

## Notas

- El bot utiliza la API de `impuestito` para obtener datos en tiempo real
- Todos los mensajes están en español
- El bot maneja errores de forma elegante y proporciona mensajes informativos
- Los datos se actualizan automáticamente con cada consulta

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.