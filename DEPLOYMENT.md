# 🚀 Deployment Guide

This guide covers various deployment options for the Impuestito Discord Bot.

## 📋 Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Git

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker Compose

1. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd discord-bot-impuestito
   cp .env.example .env
   # Edit .env with your Discord bot token
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Check logs**
   ```bash
   docker-compose logs -f discord-bot
   ```

### Manual Docker Build

1. **Build the image**
   ```bash
   docker build -t impuestito-discord-bot .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name discord-bot \
     --env-file .env \
     -v $(pwd)/logs:/app/logs \
     impuestito-discord-bot
   ```

## ☁️ Cloud Deployment

### Heroku

1. **Create Heroku app**
   ```bash
   heroku create your-bot-name
   ```

2. **Set environment variables**
   ```bash
   heroku config:set DISCORD_BOT_TOKEN=your_token_here
   heroku config:set BOT_OWNER_ID=your_user_id_here
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **Scale the dyno**
   ```bash
   heroku ps:scale worker=1
   ```

### Railway

1. **Connect your GitHub repository**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically on push**

### DigitalOcean App Platform

1. **Create a new app**
2. **Connect your GitHub repository**
3. **Set environment variables**
4. **Deploy**

### AWS EC2

1. **Launch EC2 instance**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip git
   ```

2. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd discord-bot-impuestito
   pip3 install -r requirements.txt
   cp .env.example .env
   # Edit .env
   ```

3. **Run with systemd**
   ```bash
   # Create service file
   sudo nano /etc/systemd/system/discord-bot.service
   ```

   ```ini
   [Unit]
   Description=Impuestito Discord Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/discord-bot-impuestito
   ExecStart=/usr/bin/python3 bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl enable discord-bot
   sudo systemctl start discord-bot
   sudo systemctl status discord-bot
   ```

## 🐧 VPS Deployment

### Ubuntu/Debian

1. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git nginx
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install bot**
   ```bash
   git clone <repository-url>
   cd discord-bot-impuestito
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env
   ```

4. **Setup systemd service**
   ```bash
   sudo nano /etc/systemd/system/discord-bot.service
   ```

   ```ini
   [Unit]
   Description=Impuestito Discord Bot
   After=network.target

   [Service]
   Type=simple
   User=your_user
   WorkingDirectory=/path/to/discord-bot-impuestito
   Environment=PATH=/path/to/discord-bot-impuestito/venv/bin
   ExecStart=/path/to/discord-bot-impuestito/venv/bin/python bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

5. **Enable and start service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable discord-bot
   sudo systemctl start discord-bot
   ```

### CentOS/RHEL

1. **Install dependencies**
   ```bash
   sudo yum update
   sudo yum install python3 python3-pip git
   ```

2. **Follow similar steps as Ubuntu/Debian**

## 🔧 Production Configuration

### Environment Variables

```env
# Required
DISCORD_BOT_TOKEN=your_bot_token_here

# Recommended for production
BOT_OWNER_ID=your_user_id_here
DEBUG_MODE=false
LOG_LEVEL=INFO

# Performance tuning
RATE_LIMIT_COMMANDS=10
RATE_LIMIT_WINDOW=60
CACHE_TTL=300
CACHE_MAXSIZE=2000
API_TIMEOUT=15
MAX_RETRIES=5

# Monitoring
HEALTH_CHECK_INTERVAL=300
ENABLE_FILE_LOGGING=true
LOG_FILE=/var/log/discord-bot/bot.log
```

### Redis Configuration (Optional)

For high-traffic scenarios, enable Redis:

1. **Install Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt install redis-server
   
   # CentOS/RHEL
   sudo yum install redis
   ```

2. **Configure Redis**
   ```bash
   sudo nano /etc/redis/redis.conf
   # Set bind 127.0.0.1
   # Set requirepass your_password
   ```

3. **Add to .env**
   ```env
   REDIS_URL=redis://:your_password@localhost:6379/0
   ```

### Logging Configuration

1. **Create log directory**
   ```bash
   sudo mkdir -p /var/log/discord-bot
   sudo chown your_user:your_user /var/log/discord-bot
   ```

2. **Setup log rotation**
   ```bash
   sudo nano /etc/logrotate.d/discord-bot
   ```

   ```
   /var/log/discord-bot/*.log {
       daily
       missingok
       rotate 7
       compress
       delaycompress
       notifempty
       create 644 your_user your_user
   }
   ```

## 📊 Monitoring

### Health Checks

The bot includes built-in health monitoring:

- **Automatic health checks** every 5 minutes
- **Performance metrics** tracking
- **Error rate monitoring**
- **Cache performance analysis**

### External Monitoring

1. **Uptime Robot**
   - Monitor bot response times
   - Set up alerts for downtime

2. **Grafana + Prometheus**
   - Custom metrics dashboard
   - Performance visualization

3. **Discord Webhooks**
   - Bot status notifications
   - Error alerts

### Log Monitoring

```bash
# View real-time logs
tail -f /var/log/discord-bot/bot.log

# Search for errors
grep "ERROR" /var/log/discord-bot/bot.log

# Monitor performance
grep "performance" /var/log/discord-bot/bot.log
```

## 🔒 Security Best Practices

### Bot Security

1. **Use environment variables** for sensitive data
2. **Restrict bot permissions** to minimum required
3. **Regular token rotation**
4. **Monitor for suspicious activity**

### Server Security

1. **Firewall configuration**
   ```bash
   sudo ufw allow ssh
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **SSH hardening**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set PermitRootLogin no
   # Set PasswordAuthentication no
   ```

3. **Regular updates**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

## 🔄 Updates and Maintenance

### Updating the Bot

1. **Pull latest changes**
   ```bash
   git pull origin main
   ```

2. **Update dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Restart service**
   ```bash
   sudo systemctl restart discord-bot
   ```

### Backup Strategy

1. **Configuration backup**
   ```bash
   cp .env .env.backup
   ```

2. **Log backup**
   ```bash
   tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
   ```

3. **Database backup (if using Redis)**
   ```bash
   redis-cli BGSAVE
   cp /var/lib/redis/dump.rdb redis-backup-$(date +%Y%m%d).rdb
   ```

## 🚨 Troubleshooting

### Common Issues

1. **Bot not responding**
   ```bash
   # Check service status
   sudo systemctl status discord-bot
   
   # Check logs
   sudo journalctl -u discord-bot -f
   ```

2. **High memory usage**
   ```bash
   # Monitor memory
   htop
   
   # Check cache size
   docker exec discord-bot python -c "import psutil; print(psutil.virtual_memory())"
   ```

3. **API rate limiting**
   ```bash
   # Check rate limit logs
   grep "rate limit" /var/log/discord-bot/bot.log
   ```

### Performance Optimization

1. **Increase cache size** for high-traffic servers
2. **Adjust rate limits** based on usage patterns
3. **Use Redis** for distributed caching
4. **Monitor and optimize** database queries

## 📞 Support

For deployment issues:

1. **Check logs** for error messages
2. **Verify configuration** in .env file
3. **Test connectivity** to Discord API
4. **Review system resources**

---

**Happy deploying! 🚀**