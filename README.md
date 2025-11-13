# 📔 SecureDiary - Your Encrypted Personal Journal

A highly secure, beautifully designed personal diary application with military-grade encryption. Write your thoughts freely, knowing they're completely private and protected.

## ✨ Features

### 📝 Journaling Features
- **Rich Diary Entries** - Write detailed entries with titles, moods, and tags
- **Mood Tracking** - Track your emotional state with 10 different moods
- **Tags & Organization** - Categorize entries with custom tags
- **Favorites** - Mark important entries as favorites
- **Search & Filter** - Find entries by title, mood, or favorites
- **Read-only View** - View entries in a clean, distraction-free mode
- **Edit Anytime** - Update your entries whenever you want
- **Word Counter** - Track how much you've written
- **Beautiful Cards** - Entries displayed as elegant cards with previews

### 🔒 Security Features
- **Military-grade AES-256 Encryption** - All entries encrypted with Fernet
- **Master Password Protection** - Single password to access your entire diary
- **PBKDF2 Key Derivation** - 200,000 iterations with SHA-256
- **Device Binding** - Diary locked to your specific device
- **Auto-lock** - Automatically locks after 10 minutes of inactivity
- **Critical Security Logic** - If diary.key is deleted, ALL entries become undecryptable
- **5 Failed Attempt Limit** - App closes after 5 wrong password attempts
- **No Cloud Sync** - Everything stays on your device

### 🎨 Modern UI/UX
- **Dark Theme** - Easy on the eyes for late-night journaling
- **Clean Interface** - Distraction-free writing experience
- **Responsive Design** - Smooth animations and transitions
- **Emoji Support** - Express yourself with mood emojis
- **Card Layout** - Beautiful card-based entry display
- **Real-time Stats** - See total entries and favorites at a glance

## 🚀 Installation

### Prerequisites
```bash
# Python 3.8 or higher required
python --version
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Application
```bash
python main.py
```

## 🔑 First Time Setup

1. **Create Master Password**
   - Launch the app
   - Enter a strong password (8+ characters minimum)
   - Password strength indicator will guide you
   - ⚠️ **IMPORTANT**: This password protects your entire diary

2. **Remember Your Master Password**
   - ⚠️ **CRITICAL**: If you forget it, your diary is PERMANENTLY locked
   - No password recovery exists (by design for maximum security)
   - Write it down in a secure physical location if needed

3. **Start Writing**
   - Restart the app after creating password
   - Login and start your first entry!

## 📖 How to Use

### Writing Your First Entry

1. Click **✍️ New Entry** button
2. Enter a title for your entry
3. Select your current mood (optional)
4. Add tags to organize (optional)
5. Write your thoughts in the content area
6. Click **💾 Save Entry**

### Organizing Entries

**Moods Available:**
- 😊 Happy
- 😢 Sad
- 🎉 Excited
- 😠 Angry
- 😌 Calm
- 😰 Anxious
- 🙏 Grateful
- 🤔 Reflective
- ❤️ Loved
- 😴 Tired

**Tagging System:**
- Use comma-separated tags: `personal, work, ideas`
- Filter by tags using search
- Helps categorize thoughts and memories

### Finding Entries

- **Search**: Type in the search bar to find entries by title
- **Mood Filter**: Filter entries by specific mood
- **Favorites**: Toggle to show only starred entries
- **Timeline**: Entries sorted by date (newest first)

### Managing Entries

- **👁 Read** - View entry in full-screen read mode
- **✏ Edit** - Modify title, content, mood, or tags
- **⭐ Favorite** - Mark/unmark as favorite
- **🗑 Delete** - Remove entry permanently (with confirmation)

## 🛡️ Security Architecture

### Encryption Layers

```
Master Password
    ↓ (PBKDF2 - 200k iterations)
KEK (Key Encryption Key)
    ↓ (encrypts)
Diary Key (stored in diary.key)
    ↓ (encrypts)
Individual Diary Entries (stored in database)
```

### Critical Security Logic 🔒

```
If diary_data/diary.key is deleted:
→ New diary key is created
→ OLD entries remain encrypted with OLD key
→ Result: OLD entries become "🔒 Undecryptable"
```

**Why this design?**
- Prevents attackers from decrypting your entries
- Even with database access, entries are useless without the key
- If someone tampers with files, data becomes unreadable
- This is intentional security, not a bug!

### What Gets Encrypted

✅ **Encrypted:**
- All entry content
- Your thoughts and feelings
- Everything you write

❌ **Not Encrypted (metadata):**
- Entry titles (for search functionality)
- Moods (for filtering)
- Tags (for organization)
- Timestamps (for sorting)

## ⚠️ Important Security Notes

### DO NOT Delete These Files:
- ❌ `diary_data/diary.key` - Makes ALL entries undecryptable forever
- ❌ `diary_data/salt.bin` - Breaks master password verification
- ❌ `diary_data/master.key` - Loses master password hash
- ❌ `diary_data/device.lock` - Breaks device binding

### Backup Your Diary

**To backup:**
```bash
# Copy entire diary_data folder to safe location
cp -r diary_data/ ~/backups/diary_backup_$(date +%Y%m%d)/
```

**Important:**
- Backup entire `diary_data/` folder, not individual files
- Keep backups in a secure, private location
- Never store backups in plaintext online
- Consider encrypting backup folder with separate tool

## 🎯 Use Cases

### Personal Journaling
- Daily thoughts and reflections
- Gratitude journaling
- Dream journaling
- Travel memories

### Mental Health
- Mood tracking over time
- Anxiety management
- Therapy progress notes
- Emotional processing

### Creative Writing
- Story ideas
- Poetry drafts
- Character development
- Writing prompts

### Life Tracking
- Goals and progress
- Milestones and achievements
- Lessons learned
- Important memories

## 🐛 Troubleshooting

### "Undecryptable" Entries

**Problem**: Entries show "🔒 Undecryptable"

**Causes**:
- `diary.key` file was deleted or corrupted
- Database was modified directly
- Encryption key mismatch

**Solution**: These entries cannot be recovered. This is permanent and by design.

### Can't Login

**Solutions**:
1. Check Caps Lock is OFF
2. Ensure you're on the correct device
3. Verify `diary_data/device.lock` exists
4. After 5 failed attempts, app will close

## 💡 Tips for Best Experience

### Writing Tips
1. **Write regularly** - Make it a daily habit
2. **Be honest** - No one else can read this
3. **Add details** - Include sensory details and emotions
4. **Use moods** - Track emotional patterns over time
5. **Tag smartly** - Create consistent tag categories

### Security Tips
1. **Choose strong password** - Use 12+ characters
2. **Never share password** - Keep it completely private
3. **Lock when leaving** - Use manual lock button
4. **Regular backups** - Copy diary_data folder monthly
5. **Physical security** - Protect device access too

### Organization Tips
1. **Consistent titles** - Use clear, descriptive titles
2. **Tag categories** - Create tag system (personal/work/ideas)
3. **Use favorites** - Mark meaningful entries
4. **Review regularly** - Read past entries to reflect
5. **Date context** - Include date-specific events in entries

## 🆚 Why SecureDiary?

| Feature | SecureDiary | Other Apps | Physical Diary |
|---------|-------------|------------|----------------|
| Privacy | ✅ Encrypted | ❌ Cloud sync | ✅ Private |
| Security | ✅ AES-256 | ⚠️ Varies | ❌ Physical theft |
| Search | ✅ Instant | ✅ Yes | ❌ Manual |
| Backups | ✅ Easy copy | ✅ Auto | ❌ Can be lost |
| Access | 🔒 Password | ⚠️ Anyone | 👀 Anyone |
| Mood Tracking | ✅ Built-in | ⚠️ Maybe | ❌ Manual |
| Free | ✅ Forever | ❌ Subscription | 💰 One-time |

## 📝 Example Entry

```
Title: Amazing Day at the Beach
Mood: 😊 Happy
Tags: vacation, family, summer

Today was absolutely perfect! We drove to the coast early in 
the morning and spent the entire day at the beach. The kids 
built an incredible sandcastle, and we watched the sunset 
together. These are the moments I want to remember forever.

The water was cool and refreshing, and I finally felt all my 
work stress melt away. I'm so grateful for days like these.
```

## 🔐 Security Guarantees

✅ **We Guarantee:**
- Military-grade AES-256 encryption
- PBKDF2 with 200,000 iterations
- Master password never stored in plaintext
- Device-specific binding
- No network access or cloud sync
- Open source code (you can verify)

❌ **We Cannot Help With:**
- Forgotten master passwords (no recovery possible)
- Lost diary.key file (entries become undecryptable)
- Corrupted database files
- Stolen device access (protect your device!)

## 📜 License

Personal use only. Your diary, your data, your privacy.

## 🤝 Support

This is a personal security tool. For issues:
1. Check troubleshooting section
2. Verify file integrity
3. Review security notes
4. Consider fresh install if corrupted

---

## ⚡ Quick Start

```bash
# Install
pip install -r requirements.txt

# Run
python main.py

# First time: Create master password
# Then: Write your first entry!
```

---

**🔒 Remember: Your master password is the key to your memories. Guard it well!**

📔 *Happy journaling! Your thoughts are safe here.* ✍️
