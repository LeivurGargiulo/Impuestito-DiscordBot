# 🤖 Bot de Impuestito para Discord

Bot de Discord que proporciona información sobre cotizaciones de monedas y cálculos de impuestos en Argentina usando el paquete `impuestito`. Convertido desde el bot original de Telegram.

## ✨ Características

- **Cotizaciones en tiempo real**: Dólar oficial, blue, euro oficial y euro blue
- **Cálculos de impuestos**: Impuesto país automático
- **Conversiones de monedas**: Dólar a pesos argentinos
- **Comandos intuitivos**: Prefijo `!` con aliases para facilidad de uso
- **Embeds visuales**: Respuestas formateadas y coloridas
- **Sistema de debug**: Información detallada del estado del bot
- **Manejo de errores robusto**: Logging completo y mensajes de error amigables
- **Estructura modular**: Organización en cogs para fácil mantenimiento
- **Tareas en segundo plano**: Limpieza automática y actualización de estado

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- Token de bot de Discord

### Pasos de instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd discord-impuestito-bot
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar el bot**
   ```bash
   cp .env.example .env
   # Editar .env con tu token de Discord
   ```

4. **Obtener token de Discord**
   - Ve a [Discord Developer Portal](https://discord.com/developers/applications)
   - Crea una nueva aplicación
   - Ve a la sección "Bot"
   - Copia el token y agrégalo a tu archivo `.env`

5. **Configurar permisos del bot**
   - En el Developer Portal, ve a "OAuth2" > "URL Generator"
   - Selecciona los scopes: `bot` y `applications.commands`
   - Selecciona los permisos: `Send Messages`, `Use Slash Commands`, `Embed Links`
   - Usa la URL generada para invitar el bot a tu servidor

## 📋 Comandos Disponibles

### Comandos Básicos
- `!start` / `!help` / `!ayuda` - Muestra el mensaje de ayuda
- `!ping` - Verifica la latencia del bot
- `!status` - Estado general del bot
- `!debug` - Información detallada de debug (con cooldown)

### Comandos de Cotizaciones
- `!cotizacion` / `!cotizaciones` / `!cot` - Cotización completa de todas las monedas
- `!oficial` - Cotización del dólar oficial
- `!blue` - Cotización del dólar blue
- `!euro` - Cotización del euro oficial
- `!euro_blue` - Cotización del euro blue

### Comandos de Cálculos
- `!impuesto_pais <cantidad>` / `!impuesto <cantidad>` - Calcula el impuesto país
- `!dolar_pesos <cantidad>` / `!usd_ars <cantidad>` - Convierte dólares a pesos

### Comandos de Administración
- `!reload` - Recarga todos los cogs (solo para el dueño del bot)
- `!servers` / `!guilds` - Muestra información de servidores conectados

## 🏗️ Estructura del Proyecto

```
discord-impuestito-bot/
├── discord_bot.py              # Bot principal (versión simple)
├── discord_bot_modular.py      # Bot principal (versión modular)
├── cogs/
│   ├── currency_commands.py    # Comandos de cotizaciones y conversiones
│   └── debug_commands.py       # Comandos de debug y utilidades
├── requirements.txt            # Dependencias del proyecto
├── .env.example               # Ejemplo de configuración
├── .env                       # Configuración real (crear manualmente)
└── README.md                  # Este archivo
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` con las siguientes variables:

```env
# Token del bot de Discord (requerido)
DISCORD_BOT_TOKEN=tu_token_aqui

# Configuración opcional
PREFIX=!
LOG_LEVEL=INFO
```

### Permisos del Bot

El bot requiere los siguientes permisos:
- **Send Messages**: Para enviar respuestas
- **Embed Links**: Para enviar embeds formateados
- **Use Slash Commands**: Para comandos de barra (futuro)
- **Read Message History**: Para contexto de comandos

## 🚀 Ejecución

### Versión Simple
```bash
python discord_bot.py
```

### Versión Modular (Recomendada)
```bash
python discord_bot_modular.py
```

## 📊 Ejemplos de Uso

### Cotización Completa
```
!cotizacion
```
**Respuesta**: Embed con todas las cotizaciones actuales (oficial, blue, euro oficial, euro blue)

### Cálculo de Impuesto País
```
!impuesto_pais 100
```
**Respuesta**: 
- Cantidad original: $100 USD
- Impuesto agregado: $30 USD
- Cantidad final: $130 USD

### Conversión de Monedas
```
!dolar_pesos 50
```
**Respuesta**: Conversión de $50 USD a pesos argentinos usando el dólar oficial

### Debug del Bot
```
!debug
```
**Respuesta**: Información detallada del estado del bot, estadísticas y errores recientes

## 🔍 Características Técnicas

### Manejo de Errores
- **Logging completo**: Todos los errores se registran con contexto
- **Mensajes amigables**: Los usuarios reciben mensajes de error claros
- **Recuperación automática**: El bot continúa funcionando después de errores
- **Limpieza de logs**: Los errores antiguos se limpian automáticamente

### Rendimiento
- **Async/await**: Todas las operaciones son asíncronas
- **Tareas en segundo plano**: Limpieza automática y actualización de estado
- **Cooldowns**: Prevención de spam en comandos críticos
- **Caching**: Datos de cotizaciones se mantienen actualizados

### Seguridad
- **Validación de argumentos**: Verificación de tipos y rangos
- **Permisos granulares**: Comandos administrativos protegidos
- **Tokens seguros**: Configuración mediante variables de entorno

## 🛠️ Desarrollo

### Agregar Nuevos Comandos

1. **Para comandos de cotizaciones**: Edita `cogs/currency_commands.py`
2. **Para comandos de utilidades**: Edita `cogs/debug_commands.py`
3. **Para comandos principales**: Edita el archivo principal del bot

### Estructura de un Comando

```python
@bot.command(name='mi_comando', aliases=['alias1', 'alias2'])
async def mi_comando(ctx, argumento: float):
    """Descripción del comando"""
    try:
        # Lógica del comando
        embed = discord.Embed(
            title="Título",
            description="Descripción",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error en mi_comando: {e}")
        await ctx.send("❌ Error en el comando.")
```

### Logging

El bot usa el módulo `logging` de Python con configuración detallada:
- **Nivel**: INFO por defecto
- **Formato**: Timestamp, nombre del logger, nivel, mensaje
- **Archivos**: Los logs se pueden redirigir a archivos

## 🚀 Despliegue

### VPS/Cloud
1. Sube el código a tu servidor
2. Instala Python y las dependencias
3. Configura el archivo `.env`
4. Ejecuta el bot con `python discord_bot_modular.py`

### Docker (Próximamente)
```bash
docker build -t discord-impuestito-bot .
docker run -d --env-file .env discord-impuestito-bot
```

### Servicios en la Nube
- **Heroku**: Compatible con Procfile
- **Railway**: Despliegue directo desde GitHub
- **DigitalOcean**: App Platform o Droplet
- **AWS**: EC2 o Lambda

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **impuestito**: Paquete Python para cálculos de impuestos argentinos
- **discord.py**: Biblioteca para crear bots de Discord
- **python-telegram-bot**: Bot original de Telegram que sirvió como base

## 📞 Soporte

Si tienes problemas o preguntas:
1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

**¡Disfruta usando el bot de Impuestito para Discord! 🎉**