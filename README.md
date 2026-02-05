# 🔐 LinkVault Bot

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0+-green.svg)](https://docs.pyrogram.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, secure Telegram bot for managing and sharing channel invite links with auto-expiring functionality. Built from scratch with custom UI, beautiful design, and enterprise-grade features.

## ✨ Features

### 🎯 Core Features
- 🔗 **Secure Invite Links** - Generate one-time, auto-expiring invite links
- ⏱️ **Auto-Expiry** - Links automatically expire after 5 minutes
- 📢 **Multi-Channel Support** - Manage unlimited Telegram channels
- 👥 **User Management** - Track users and their activity
- 📊 **Statistics Dashboard** - Comprehensive bot analytics
- 🎨 **Beautiful UI** - Modern inline keyboards and formatting

### 🛡️ Admin Features
- 👑 **Admin Panel** - Full control over bot operations
- 📢 **Broadcast Messages** - Send announcements to all users
- 📈 **Detailed Analytics** - User engagement and channel statistics
- 🔧 **Channel Management** - Add/remove channels dynamically
- 🗑️ **Auto Cleanup** - Automatic removal of expired links

### 🎯 User Features
- 🚀 **Instant Access** - Get channel links with one click
- 📱 **Mobile-Friendly** - Optimized for mobile devices
- 🔒 **Privacy First** - Secure and private link generation
- 💬 **Easy Navigation** - Intuitive button-based interface

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- MongoDB database (free tier available at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas))
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)
- Bot token from [@BotFather](https://t.me/BotFather)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/linkvault-bot.git
cd linkvault-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Run the bot**
```bash
python main.py
```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Telegram API Credentials
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Administration
OWNER_ID=123456789
ADMIN_IDS=123456789 987654321

# Database
DATABASE_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=LinkVaultDB

# Storage Channel (must be private and bot must be admin)
STORAGE_CHANNEL_ID=-1001234567890

# Optional Settings
LINK_EXPIRY_MINUTES=5
AUTO_APPROVE=False
```

### 📝 Getting Configuration Values

| Variable | How to Get |
|----------|------------|
| `API_ID` & `API_HASH` | Visit [my.telegram.org](https://my.telegram.org) → API Development Tools |
| `BOT_TOKEN` | Message [@BotFather](https://t.me/BotFather) → /newbot |
| `OWNER_ID` | Message [@userinfobot](https://t.me/userinfobot) |
| `DATABASE_URL` | Create free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) |
| `STORAGE_CHANNEL_ID` | Create private channel → Add bot as admin → Get ID from [@userinfobot](https://t.me/userinfobot) |

## 📖 Commands

### User Commands
- `/start` - Start the bot and see main menu
- `/help` - Get help and information
- `/stats` - View bot statistics
- `/channels` - See all available channels

### Admin Commands
- `/addchannel <channel_id>` - Add a channel to the bot
- `/removechannel <channel_id>` - Remove a channel from the bot
- `/broadcast` - Broadcast message to all users (reply to a message)

## 🐳 Docker Deployment

### Using Docker

1. **Build the image**
```bash
docker build -t linkvault-bot .
```

2. **Run the container**
```bash
docker run -d \
  --name linkvault \
  --env-file .env \
  --restart unless-stopped \
  linkvault-bot
```

3. **View logs**
```bash
docker logs -f linkvault
```

### Using Docker Compose

```bash
docker-compose up -d
```

## 🖥️ VPS Deployment

### Using systemd service

1. **Create service file**
```bash
sudo nano /etc/systemd/system/linkvault.service
```

2. **Add configuration**
```ini
[Unit]
Description=LinkVault Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/linkvault-bot
ExecStart=/usr/bin/python3 /path/to/linkvault-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Start the service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable linkvault
sudo systemctl start linkvault
```

## 📁 Project Structure

```
linkvault-bot/
│
├── main.py              # Main bot runner
├── config.py            # Configuration and settings
├── database.py          # Database operations
├── handlers.py          # Command and callback handlers
├── ui_components.py     # UI elements and formatting
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
└── README.md            # This file
```

## 🎨 Customization

### Changing Link Expiry Time
Edit `LINK_EXPIRY_MINUTES` in your `.env` file:
```env
LINK_EXPIRY_MINUTES=10  # Links expire in 10 minutes
```

### Customizing Bot Name and Colors
Edit `config.py`:
```python
class Config:
    BOT_NAME: str = "Your Bot Name"
    BOT_VERSION: str = "1.0"
```

### Adding New Features
The bot is modular and easy to extend:
- Add new handlers in `handlers.py`
- Create new UI components in `ui_components.py`
- Extend database operations in `database.py`

## 🔒 Security Features

- ✅ Auto-expiring invite links
- ✅ One-time use links (member_limit=1)
- ✅ Admin-only commands
- ✅ User activity tracking
- ✅ Secure MongoDB connection
- ✅ Environment variable protection

## 📊 Database Schema

### Collections

**channels**
```json
{
  "channel_id": -1001234567890,
  "channel_name": "My Channel",
  "invite_link": "https://t.me/...",
  "added_at": "2024-01-01T00:00:00",
  "total_joins": 100,
  "is_active": true,
  "auto_approve": false
}
```

**users**
```json
{
  "user_id": 123456789,
  "username": "john_doe",
  "first_name": "John",
  "joined_at": "2024-01-01T00:00:00",
  "last_active": "2024-01-02T00:00:00",
  "total_requests": 50,
  "is_banned": false
}
```

**links**
```json
{
  "channel_id": -1001234567890,
  "invite_link": "https://t.me/+abc123",
  "link_type": "invite",
  "created_at": "2024-01-01T00:00:00",
  "expires_at": "2024-01-01T00:05:00",
  "uses": 0,
  "is_active": true
}
```

## 🐛 Troubleshooting

### Bot not responding
- Check if bot token is correct
- Ensure bot is running: `systemctl status linkvault`
- Check logs: `tail -f bot.log`

### Can't generate links
- Make sure bot is admin in the channel
- Bot must have "Create Invite Links" permission
- Channel ID must be correct (negative for channels)

### Database connection fails
- Verify MongoDB URL is correct
- Check if IP is whitelisted in MongoDB Atlas
- Ensure database user has read/write permissions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Pyrogram](https://docs.pyrogram.org/) - Modern Telegram MTProto API framework
- Database powered by [MongoDB](https://www.mongodb.com/)
- Inspired by the need for secure channel link sharing

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/linkvault-bot/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/linkvault-bot/discussions)
- 📧 **Email**: your.email@example.com

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐

---

**Made with ❤️ by [Your Name]**

---

## 📸 Screenshots

### User Interface
![Start Menu](screenshots/start.png)
*Clean and intuitive start menu*

![Channel List](screenshots/channels.png)
*Beautiful channel selection interface*

### Admin Panel
![Admin Dashboard](screenshots/admin.png)
*Comprehensive admin controls*

![Statistics](screenshots/stats.png)
*Detailed analytics and insights*

---

## 🔮 Roadmap

- [ ] Multi-language support
- [ ] Custom link expiry per channel
- [ ] Analytics export (CSV/JSON)
- [ ] Webhook support for channel events
- [ ] User subscription management
- [ ] Advanced anti-spam features
- [ ] Channel categories
- [ ] Search functionality

---

## ⚡ Performance

- ⚡ **Fast**: Asynchronous operations with asyncio
- 💪 **Reliable**: Auto-restart and error recovery
- 🔥 **Scalable**: Handles thousands of concurrent users
- 💾 **Efficient**: Optimized database queries
- 🎯 **Lightweight**: Minimal resource usage

---

**Version 2.0** - Last updated: February 2026
