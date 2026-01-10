# Instant Photo Sharing - Alpha Release Setup

Quick setup guide for the Telegram-based instant photo sharing bot.

## Prerequisites

- Python 3.8 or higher
- A Telegram account
- Internet connection

## Quick Start (5 minutes)

### 1. Create Your Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` to BotFather
3. Follow the prompts:
   - Choose a name (e.g., "Party Photos Bot")
   - Choose a username (e.g., "myparty_photos_bot")
4. Copy the **bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Install Dependencies

```bash
# Clone or navigate to the project directory
cd instant-photography-sharing

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure the Bot

```bash
# Copy the example environment file
copy .env.example .env   # Windows
# or
cp .env.example .env     # Mac/Linux

# Edit .env and add your bot token
# TELEGRAM_BOT_TOKEN=your_actual_token_here
```

### 4. Run the Bot

```bash
python bot.py
```

You should see: `Starting bot...`

### 5. Test It

1. **Register a guest**: Open Telegram, search for your bot username, send `/start`
2. **Send a photo**: Send any photo to the bot
3. **Check delivery**: The registered guest should receive the photo instantly!

## Usage at Events

### Before the Event

1. Start the bot on your laptop or deploy to Railway.app (see Deployment section)
2. Share your bot username with guests (e.g., "@myparty_photos_bot")
3. Ask guests to send `/start` to register

### During the Event

1. Take photos with your Android phone
2. Open Telegram and send photos to your bot
3. Photos are instantly distributed to all registered guests!

### Commands

**For Guests:**
- `/start` - Register to receive photos
- `/help` - Show help information

**For Photographer:**
- `/guests` - List all registered guests
- `/stats` - Show event statistics
- Just send photos to distribute them!

## Deployment Options

### Option 1: Run on Your Laptop (Simplest)

Just keep your laptop running with the bot during events. Make sure it stays connected to the internet.

**Pros:** Free, instant setup
**Cons:** Laptop must be on and connected

### Option 2: Deploy to Railway.app (Recommended)

1. Create account at [railway.app](https://railway.app)
2. Create new project from GitHub
3. Add environment variable: `TELEGRAM_BOT_TOKEN`
4. Deploy!

**Pros:** Always online, free tier ($5 credit/month)
**Cons:** Requires GitHub account

### Option 3: Deploy to Render.com

Similar to Railway, but free tier spins down after inactivity (30-60s startup delay).

## Troubleshooting

**Bot doesn't respond:**
- Check that bot is running (`python bot.py`)
- Verify TELEGRAM_BOT_TOKEN is set correctly
- Check internet connection

**Photos not being delivered:**
- Run `/guests` to confirm users are registered
- Check console for error messages
- Ensure guests haven't blocked the bot

**"No module named 'telegram'":**
- Install dependencies: `pip install -r requirements.txt`
- Activate virtual environment if you created one

## Advanced Configuration

### Restrict Photo Uploads

To only allow specific user to upload photos, edit `.env`:

```
PHOTOGRAPHER_USERNAME=your_telegram_username
```

### Change Database Location

```
DB_PATH=/path/to/custom/database.db
```

## Database Schema

The bot uses SQLite with two tables:

**guests:** Stores registered users
- user_id, username, first_name, last_name, registered_at, photo_count

**photos:** Logs uploaded photos
- id, file_id, photographer_id, uploaded_at, caption

## Next Steps

After successfully using the alpha:

1. Add facial recognition for selective photo sending
2. Build web registration portal
3. Add support for WhatsApp/SMS delivery
4. Implement DSLR auto-upload integration

## Cost

**Alpha Release:** $0/month
- Telegram Bot API: Free
- SQLite database: Free
- Railway.app: Free tier sufficient

## Questions?

Check the main [README.md](README.md) for the full vision and roadmap.
