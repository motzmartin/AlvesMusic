# 🎵 AlvesMusic - A Discord Music Bot Playing from YouTube 🎶

AlvesMusic is a simple yet powerful Discord music bot that allows you to **play music from YouTube**
directly in your voice channels. It supports **queues, playlists, shuffling, and more**.

## 📌 Features
✅ Play music from **YouTube**  
✅ **Queue management** (play, clear, shuffle)  
✅ **Playback controls** (pause, resume, skip, stop)  
✅ **Supports YouTube playlists**  
✅ Uses **cookies.txt** to bypass YouTube restrictions  
✅ **Self-hosted** and **lightweight**  

---

## 📥 Installation

### 1️⃣ Clone the repository
Make sure you have **Git** installed, then run:

```bash
git clone https://github.com/motzmartin/AlvesMusic.git
cd AlvesMusic
```

### 2️⃣ Create a virtual environment (recommended)
Using **Python virtual environment** avoids dependency conflicts:

```bash
python -m venv venv
```

Then, activate it:
- **Windows:**  
  ```bash
  venv\Scripts\activate
  ```
- **Linux/macOS:**  
  ```bash
  source venv/bin/activate
  ```

### 3️⃣ Install dependencies
Run:

```bash
pip install -r requirements.txt
```

The bot requires:
- `discord.py` (for Discord bot functionality)
- `yt_dlp` (to extract and stream YouTube audio)
- `python-dotenv` (to load environment variables)

---

## ⚙️ Setup

### 1️⃣ Configure your `.env` file
Create a `.env` file in the **root directory** and add your Discord bot token:

```
BOT_TOKEN=your_discord_bot_token_here
```

### 2️⃣ Download YouTube cookies
To **bypass YouTube restrictions**, you need to **export your YouTube cookies** using a browser extension:

- **Chrome:** Install [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
- **Firefox:** Use a similar extension like "cookies.txt exporter"

#### Steps:
1. Go to [YouTube](https://www.youtube.com) and **log into your account**.  
   ⚠️ **USE A BURNER ACCOUNT!** ⚠️
2. Use the extension to **export your cookies** as `cookies.txt`.
3. Place the `cookies.txt` file in the **root directory** of the bot.

---

## 🎮 Usage

### 🔹 Run the bot
Start AlvesMusic with:

```bash
python main.py
```

If you’re using a virtual environment, make sure it’s activated before running the bot.

### 🔹 Using `screen` to Keep the Bot Running (Linux)
If you want to **keep the bot running even after closing your terminal**, you can use `screen`:

1. **Create a new screen session:**
```bash
screen -S alvesmusic
```

2. **Start the bot inside the screen session:**
```bash
python main.py
```

3. **Detach the screen session (leave it running in the background):**  
Press `Ctrl + A`, then `D`.

4. **Reconnect to the screen session later:**  
```bash
screen -r alvesmusic
```

5. **To list all running screen sessions:**  
```bash
screen -ls
```

6. **To terminate the screen session:**  
Reconnect to it using `screen -r alvesmusic`, then exit with:  
```bash
exit
```

### 🔹 Commands
| Command               | Description                          |
|-----------------------|--------------------------------------|
| `!play <search\|URL>` | Plays a song or adds it to the queue |
| `!queue [page]`       | Displays the current queue           |
| `!playing`            | Shows the currently playing song     |
| `!clear`              | Clears the queue                     |
| `!shuffle`            | Randomly shuffles the queue          |
| `!skip`               | Skips to the next song               |
| `!stop`               | Stops playback and clears the queue  |
| `!pause`              | Pauses the current song              |
| `!resume`             | Resumes the paused song              |

---

## 🛠 Hosting Options

AlvesMusic is **self-hosted**, meaning you can run it on:
- **Your local machine** (Windows, Linux, macOS)
- **A VPS (Virtual Private Server)** for 24/7 uptime
- **A Raspberry Pi** for a lightweight solution

---

## 🔒 Security Reminder
- **Never share your `.env` file** or Discord bot token!
- Add `.env` and `cookies.txt` to your `.gitignore` file:

```
.env
cookies.txt
```

---

## 📜 License
This project is open-source and available under the **MIT License**.

---

## 🙌 Contributing
Contributions are welcome! Feel free to fork this repository and submit a pull request. 😊

---

## 📞 Support
If you encounter any issues, feel free to **open an issue** on GitHub.

🚀 **Enjoy your music on Discord!**
