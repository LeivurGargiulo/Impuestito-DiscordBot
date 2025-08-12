# 🤖 Impuestito Discord Bot - Production Ready

A clean, optimized, and maintainable Discord bot that provides currency exchange and tax calculation information for Argentina using the impuestito package.

## ✨ Features

### 🚀 Performance & Stability
- **Efficient Async Handling**: Non-blocking event processing for smooth operation
- **Intelligent Caching**: Reduces API calls and improves response times
- **Rate Limiting**: Prevents abuse and ensures fair usage
- **Health Monitoring**: Real-time bot health checks and diagnostics
- **Error Recovery**: Comprehensive error handling with automatic recovery

### 🔒 Security & Reliability
- **Environment Variables**: Secure configuration management
- **Input Validation**: Robust parameter validation and sanitization
- **API Protection**: Rate limiting and timeout management
- **Logging**: Comprehensive logging for debugging and monitoring

### 📊 Monitoring & Analytics
- **Performance Metrics**: Real-time bot performance tracking
- **System Monitoring**: CPU, memory, disk, and network usage
- **Error Tracking**: Detailed error logging and analysis
- **Cache Analytics**: Cache hit rates and performance optimization

### 🛠️ Developer Experience
- **Modular Architecture**: Clean, maintainable code structure
- **Comprehensive Documentation**: Detailed code comments and examples
- **Easy Configuration**: Simple environment-based configuration
- **Testing Support**: Built-in testing framework support

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd discord-bot-impuestito
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up your Discord bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section
   - Copy your bot token
   - Add the token to your `.env` file

5. **Run the bot**
   ```bash
   python bot.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Required
DISCORD_BOT_TOKEN=your_bot_token_here

# Optional
BOT_OWNER_ID=your_user_id_here
BOT_PREFIX=!
DEBUG_MODE=false

# Rate Limiting
RATE_LIMIT_COMMANDS=5
RATE_LIMIT_WINDOW=60

# Caching
CACHE_TTL=300
CACHE_MAXSIZE=1000

# API Settings
API_TIMEOUT=10
MAX_RETRIES=3

# Health Checks
HEALTH_CHECK_INTERVAL=300
```

### Bot Permissions

Your bot needs the following permissions:
- Send Messages
- Embed Links
- Read Message History
- Use Slash Commands (if using slash commands)

## 📋 Commands

### 💰 Currency Commands
- `!cotizacion` - Get all currency exchange rates
- `!oficial` - Get official dollar rate
- `!blue` - Get blue dollar rate
- `!euro` - Get official euro rate
- `!euro_blue` - Get blue euro rate
- `!impuesto_pais <amount>` - Calculate country tax
- `!dolar_pesos <amount>` - Convert USD to ARS
- `!pesos_dolar <amount>` - Convert ARS to USD
- `!comparar <amount>` - Compare official vs blue rates

### 🔧 Utility Commands
- `!help` - Show help information
- `!status` - Bot status and statistics
- `!ping` - Check bot latency
- `!info` - Server information

### 🛠️ Debug Commands (Admin Only)
- `!system` - System information
- `!performance` - Performance metrics
- `!errors` - Recent errors
- `!rate_limits` - Rate limit information
- `!cache_info` - Cache statistics
- `!guilds` - Guild information
- `!test_api` - API connectivity test
- `!reload` - Reload cogs
- `!debug` - Debug information

## 🏗️ Architecture

### Modular Design
```
bot.py                 # Main bot file
├── cogs/             # Command modules
│   ├── currency_commands.py
│   └── debug_commands.py
├── config/           # Configuration
├── logs/             # Log files
└── tests/            # Test files
```

### Key Components

1. **ImpuestitoBot Class**: Enhanced bot with production features
2. **BotConfig**: Centralized configuration management
3. **Caching System**: TTL-based caching for API responses
4. **Rate Limiting**: User-based rate limiting
5. **Health Monitoring**: Automated health checks
6. **Error Handling**: Comprehensive error management

## 🔧 Advanced Configuration

### Redis Integration (Optional)

For distributed caching, you can use Redis:

1. **Install Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   ```

2. **Configure Redis URL**
   ```env
   REDIS_URL=redis://localhost:6379/0
   ```

### Custom Cogs

To add custom functionality:

1. **Create a new cog file**
   ```python
   # cogs/my_cog.py
   from discord.ext import commands
   
   class MyCog(commands.Cog):
       def __init__(self, bot):
           self.bot = bot
       
       @commands.command()
       async def mycommand(self, ctx):
           await ctx.send("Hello!")
   
   async def setup(bot):
       await bot.add_cog(MyCog(bot))
   ```

2. **The bot will automatically load it**

## 📊 Monitoring

### Health Checks
The bot performs automatic health checks every 5 minutes:
- Latency monitoring
- Error rate analysis
- Cache performance
- System resource usage

### Logging
Logs are written to both console and file:
- Command execution
- Error tracking
- Performance metrics
- System events

### Metrics Available
- Commands executed per hour
- Error rates
- Cache hit rates
- API response times
- System resource usage

## 🚀 Performance Optimization

### Caching Strategy
- **TTL-based caching**: 5-minute cache for currency data
- **Intelligent invalidation**: Automatic cache cleanup
- **Memory efficient**: Configurable cache size limits

### Rate Limiting
- **User-based limits**: 5 commands per minute per user
- **Command-specific limits**: Different limits for different commands
- **Automatic cleanup**: Old rate limit data is cleaned up

### API Optimization
- **Connection pooling**: Reuses HTTP connections
- **Timeout management**: Configurable API timeouts
- **Retry logic**: Automatic retry for failed requests

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=.
```

### Test Structure
```
tests/
├── test_bot.py
├── test_currency_commands.py
├── test_debug_commands.py
└── conftest.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check bot token in `.env`
   - Verify bot permissions
   - Check bot is online

2. **Commands not working**
   - Verify command prefix
   - Check bot permissions in server
   - Review error logs

3. **High latency**
   - Check internet connection
   - Monitor system resources
   - Review API response times

4. **Cache issues**
   - Check cache configuration
   - Monitor cache hit rates
   - Review cache cleanup logs

### Debug Commands
Use the built-in debug commands to diagnose issues:
- `!system` - System resource usage
- `!performance` - Bot performance metrics
- `!errors` - Recent error logs
- `!test_api` - API connectivity test

## 📈 Scaling

### Horizontal Scaling
For high-traffic scenarios:
1. **Use Redis**: Enable distributed caching
2. **Load Balancing**: Run multiple bot instances
3. **Database**: Add persistent storage for analytics

### Vertical Scaling
For single-instance optimization:
1. **Increase cache size**: Adjust `CACHE_MAXSIZE`
2. **Optimize rate limits**: Adjust rate limiting parameters
3. **System resources**: Increase CPU/memory allocation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- Follow PEP 8
- Add type hints
- Include docstrings
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [impuestito](https://github.com/impuestito/impuestito) - Argentine tax calculations
- [aiohttp](https://github.com/aio-libs/aiohttp) - Async HTTP client
- [cachetools](https://github.com/tkem/cachetools) - Caching utilities

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting section

---

**Made with ❤️ for the Argentine developer community**