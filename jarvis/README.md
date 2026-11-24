# JARVIS — your free personal voice assistant

Say **"Hey Jarvis"** and talk in English or Kannada. Jarvis runs on your Windows PC and acts
for you: it opens apps, controls volume and power, finds files, searches the web, reads you the
news and weather, sets reminders and alarms, handles Gmail and Google Calendar, controls smart
home devices, and remembers things about you.

**Running cost: ₹0.** Every part is free.

| Part | What it uses | Needs internet? |
|---|---|---|
| Wake word | openWakeWord "hey jarvis" (on your PC) | No |
| Ears | Whisper speech recognition (on your PC) | No |
| Brain | Google Gemini free tier → Groq free tier → Ollama on your PC | Ollama works offline |
| Voice | Microsoft Edge neural voices (en-IN, kn-IN) | Yes (falls back to Windows' offline English voice) |
| Web, news, weather | DuckDuckGo, Google News RSS, Open-Meteo, Wikipedia | Yes |
| Gmail / Calendar | Google's free APIs (optional) | Yes |
| Smart home | Home Assistant (optional) | Local network |

---

## Setup (about 15 minutes)

1. **Get a free Gemini key**: go to https://aistudio.google.com/apikey → *Create API key*.
2. **Download this folder** to your PC, for example `C:\Jarvis`.
3. Open the folder, click the address bar, type `powershell` and press Enter. Then run:
   ```
   powershell -ExecutionPolicy Bypass -File .\install.ps1
   ```
   It installs Python if needed, installs the packages, and downloads the voice models (about 1.6 GB, done once).
4. Run `notepad .env`, paste your key after `GEMINI_API_KEY=`, and set your name and city. Save the file.
5. **Start Jarvis.** Double-click `run.bat` and say *"Hey Jarvis"*. To type instead, use `run-text.bat`.

### Optional upgrades
- **Backup brain (recommended):** get a free key at https://console.groq.com/keys and put it in `GROQ_API_KEY`.
  Jarvis switches to Groq when Gemini hits its free-tier limit.
- **Offline brain:** install https://ollama.com and run `ollama pull qwen3:8b`. Jarvis then works with no internet.
  This needs 8 GB+ RAM, and an NVIDIA GPU makes it much faster.
- **Gmail and Calendar:** see [docs/GOOGLE_SETUP.md](docs/GOOGLE_SETUP.md).
- **Smart home:** see [docs/SMART_HOME_SETUP.md](docs/SMART_HOME_SETUP.md).
- **Start with Windows:** press `Win+R`, type `shell:startup`, and put a shortcut to `run.bat` in that folder.

---

## Things to say

| Ask | Jarvis… |
|---|---|
| "Open Chrome" / "Open my Downloads folder" | opens apps, folders and files |
| "Play Arijit Singh on YouTube" | opens YouTube results |
| "Volume to 30" / "Mute" / "Next song" | controls sound and media |
| "Take a screenshot" | saves it to Pictures\Jarvis |
| "How's my battery?" | reports CPU, RAM, disk and battery |
| "Lock the PC" / "Shut down in 10 minutes" | power actions (asks first) |
| "What's the weather tomorrow?" | Open-Meteo forecast for your city |
| "Latest news on ISRO" | top headlines |
| "Who is Rahul Dravid?" | searches the web, Wikipedia |
| "1000 rupees in dollars" / "15% of 2400" | currency and maths |
| "Remind me to call Amma in 20 minutes" | reminders, alarms, timers |
| "Wake me up at 6 am" | alarm |
| "Any new emails?" / "Reply to Ravi saying I'll be late" | Gmail (asks before sending) |
| "What's on my calendar today?" | Google Calendar |
| "Turn off the bedroom light" / "Set AC to 24" | Home Assistant |
| "Remember my wife's birthday is 12 March" | long-term memory |
| "ನಾಳೆ ಹವಾಮಾನ ಹೇಗಿದೆ?" | replies in Kannada |

After Jarvis answers, it keeps listening for about 7 seconds, so you can follow up without saying
"Hey Jarvis" again. Say "thanks" or "that's all" to end the conversation.

## Safety
Jarvis **asks before** it sends or replies to email, adds calendar events, runs PowerShell commands, closes apps,
locks, sleeps, shuts down or restarts the PC, deletes reminders or memories, and opens or unlocks locks, garage doors
and gates. Say "yes" (or "ಹೌದು" / "sari") to go ahead. It blocks disk-wiping commands outright.

## Privacy
- Your voice is processed **on your PC**. Audio is never uploaded.
- What you *say* (as text) goes to the AI brain. **Google may use Gemini free-tier conversations to improve
  its products, and people may review them.** For private matters, use Ollama, which keeps everything on your PC.
  (Set `GEMINI_API_KEY=` to empty to force it.)
- Memories, reminders and Google sign-in tokens are stored in `%USERPROFILE%\.jarvis\`.

## Troubleshooting
| Problem | Fix |
|---|---|
| Doesn't hear "Hey Jarvis" | Check Windows Settings → Privacy → Microphone. Lower `JARVIS_WAKE_THRESHOLD` to 0.35. Or use `run.bat --ptt` (press Enter to talk). |
| Triggers by itself | Raise `JARVIS_WAKE_THRESHOLD` to 0.65 |
| Slow to understand you | Set `WHISPER_MODEL=small` in `.env` |
| Kannada misunderstood | Speak clearly and keep `WHISPER_MODEL=large-v3-turbo`. Kannada recognition is the weakest part of free speech recognition today. |
| "Can't reach my brain" | Check internet, add a Groq key, or install Ollama |
| See what's happening | `run.bat --verbose` |

## Known limits
- Kannada speech recognition is decent, not perfect. English is much more accurate.
- Kannada speech output needs internet. Offline, Kannada replies are shown as text only.
- Free tiers have daily limits. With Gemini plus Groq plus Ollama, you're very unlikely to run out.

## For developers
Every ability is a function with the `@tool` decorator in `jarvis/tools/`. Drop a new file there and Jarvis
picks it up. See `jarvis/tools/__init__.py` for the contract.
