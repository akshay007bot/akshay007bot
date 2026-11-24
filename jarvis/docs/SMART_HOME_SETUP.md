# Smart home setup (optional, free)

Jarvis controls lights, fans, plugs, ACs, TVs, curtains and locks through
**Home Assistant**, a free, open-source smart-home hub that runs on your own
hardware at home. Jarvis talks to it over your home network, so nothing goes
through a paid cloud service.

> **No smart devices? Skip this page.** Jarvis works fully without it. If you
> ask for a light, it just says "Smart home isn't connected yet".

---

## 1. What Home Assistant is

Home Assistant (HA) is one app that connects to almost every smart-device
brand (over 2,000 "integrations"). Once your devices are in HA, Jarvis can
switch them with one voice command, whatever brand they are. It also gives you
a dashboard in the browser and a phone app.

## 2. Run Home Assistant for free

Pick one:

### Option A: a virtual machine on your Windows PC (no extra hardware)

1. Install **VirtualBox** (free): <https://www.virtualbox.org/>.
2. Download the **Home Assistant OS** image for VirtualBox (`.vdi` file) from
   <https://www.home-assistant.io/installation/windows>.
3. In VirtualBox: **New** > name `Home Assistant`, type **Linux**, version
   **Other Linux (64-bit)**, 2 GB RAM, 2 CPUs. Choose **Use an existing virtual
   hard disk** and select the `.vdi` file.
4. Open **Settings** for the VM:
   - **System** > tick **Enable EFI**.
   - **Network** > Adapter 1 > **Bridged Adapter** (so it gets its own address
     on your Wi-Fi).
5. Start the VM. After a few minutes, open <http://homeassistant.local:8123>
   in your browser. If that doesn't load, use the IP address shown in the VM
   window, for example `http://192.168.1.50:8123`.
6. Create your account in the onboarding screens.

Downside: HA only runs while your PC is on.

### Option B: a Raspberry Pi (always on)

A Raspberry Pi 4 or 5 (about ₹5,000 to ₹8,000 one time) uses very little power.
Use **Raspberry Pi Imager** > *Other specific-purpose OS* > *Home assistants
and home automation* > **Home Assistant**, write it to a microSD card, plug the
Pi into your router with a cable and open <http://homeassistant.local:8123>.

## 3. Add your devices

In HA go to **Settings > Devices & services > Add integration**, then search
for the brand. Common devices sold in India:

| Brand / app | Integration to add | Notes |
|---|---|---|
| **Philips WiZ** bulbs | `WiZ` | Found automatically on the same Wi-Fi. |
| **Wipro Smart**, **Syska**, **Havells**, **Halonix**, most "Smart Life" / "Tuya" plugs, bulbs and IR remotes | `Tuya` | Log in with your Smart Life / Tuya app account, or scan the QR code it shows with the app. Wipro's own app is Tuya-based. If the Wipro app won't link, set the device up again in the free **Smart Life** app first. |
| **Mi / Xiaomi** (Mi bulbs, Mi purifier, Mi robot vacuum) | `Xiaomi Miio` or `Xiaomi Home` | Log in with your Mi account. Pick the **India** server region. |
| **Philips Hue** | `Philips Hue` | Press the button on the Hue bridge when asked. |
| **TP-Link Tapo / Kasa** plugs | `TP-Link Smart Home` | Found automatically. |
| **Smart TVs** (Samsung, LG webOS, Android TV / Google TV) | `Samsung Smart TV`, `LG webOS`, `Android TV Remote` | Accept the prompt on the TV. |
| **Google Home / Chromecast** speakers | `Google Cast` | Found automatically. |
| **Alexa** devices | Not directly. Add the devices themselves through their own brand above. | |

**Tip:** give devices simple names in HA (`Bedroom light`, `Hall fan`,
`Bedroom AC`). Jarvis matches what you say against these names, so
"turn on the bedroom light" works even if the name isn't exact.

**Scenes and scripts:** under **Settings > Automations & scenes** you can create
scenes such as `Movie time` or scripts such as `Good night`. Jarvis can run them:
"Jarvis, run movie time".

## 4. Create a long-lived access token

1. In HA, click your **profile** (your name, bottom-left).
2. Open the **Security** tab.
3. Scroll to **Long-lived access tokens** > **Create token**, name it `Jarvis`.
4. **Copy the token now.** HA shows it only once.

## 5. Tell Jarvis

Open the `.env` file in the Jarvis folder (copy `.env.example` if you don't have
one) and fill in:

```env
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=paste-the-long-token-here
```

If `homeassistant.local` doesn't work on your PC, use the IP address instead,
for example `http://192.168.1.50:8123`. Restart Jarvis.

## 6. Try it

- "Jarvis, what devices do I have?"
- "Turn on the bedroom light" / "Set the living room lamp to 40 percent"
- "Make the bedroom light warm white" / "...red"
- "Set the AC to 24 degrees" / "Is the AC on?" / "What's the balcony temperature?"
- "Close the curtains" / "Run good night"
- "Lock the front door" / "Open the garage". For **locks, garage doors and
  alarms** Jarvis always asks "shall I go ahead?" first.

## Troubleshooting

| Jarvis says | Fix |
|---|---|
| "Smart home isn't connected yet" | Both `.env` values are empty. Fill them in and restart. |
| "can't reach Home Assistant" | HA is off, or the URL is wrong. Open the URL in your browser to check. PC and HA must be on the same network. |
| "rejected the token" | The token was deleted or copied wrongly. Create a new one (step 4). |
| "couldn't find a device called..." | Ask "list devices" to hear the exact names, or rename the device in HA. |
