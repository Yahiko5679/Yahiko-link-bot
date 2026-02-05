# 🚀 Quick Start Guide - LinkVault Bot

## 5-Minute Setup

### Step 1: Get Your Credentials

1. **Telegram API Credentials**
   - Go to https://my.telegram.org
   - Login with your phone number
   - Click "API Development Tools"
   - Create a new application
   - Copy `API_ID` and `API_HASH`

2. **Bot Token**
   - Message @BotFather on Telegram
   - Send `/newbot`
   - Follow the prompts
   - Copy the bot token

3. **Your User ID**
   - Message @userinfobot on Telegram
   - Copy your user ID

4. **MongoDB Database**
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up for free
   - Create a new cluster (free tier)
   - Click "Connect" → "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database password

5. **Storage Channel**
   - Create a new private Telegram channel
   - Add your bot as admin
   - Forward any message from the channel to @userinfobot
   - Copy the channel ID (will be negative number)

### Step 2: Install the Bot

```bash
# Clone or download the repository
git clone https://github.com/yourusername/linkvault-bot.git
cd linkvault-bot

# Run setup script
bash setup.sh

# Edit configuration
nano .env
```

### Step 3: Configure .env

Paste your credentials into `.env`:

```env
API_ID=12345678
API_HASH=abc123def456...
BOT_TOKEN=1234567890:ABCdef...
OWNER_ID=123456789
ADMIN_IDS=123456789
DATABASE_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=LinkVaultDB
STORAGE_CHANNEL_ID=-1001234567890
```

### Step 4: Run the Bot

**Option A: Run directly**
```bash
source venv/bin/activate
python main.py
```

**Option B: Use systemd (VPS)**
```bash
sudo cp linkvault.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable linkvault
sudo systemctl start linkvault
```

**Option C: Use Docker**
```bash
docker-compose up -d
```

### Step 5: Test the Bot

1. Open Telegram
2. Search for your bot
3. Send `/start`
4. You should see the welcome message!

## Adding Your First Channel

1. Make your bot admin in the channel
2. Send this command to the bot:
   ```
   /addchannel -1001234567890
   ```
   (Replace with your channel ID)

3. Now users can get invite links!

## Common Issues

**Bot not responding?**
- Check if bot token is correct
- Make sure bot is running
- Check logs: `tail -f bot.log`

**Can't add channel?**
- Bot must be admin in the channel
- Channel ID must start with `-100`
- Bot needs "Create Invite Links" permission

**Database error?**
- Check MongoDB connection string
- Whitelist your IP in MongoDB Atlas
- Make sure database user has permissions

## Need Help?

- 📖 Read the full [README.md](README.md)
- 🐛 Report issues on GitHub
- 💬 Join support group (if available)

---

**That's it! You're ready to go! 🎉**
