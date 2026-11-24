# Connect Jarvis to Gmail and Google Calendar

This takes about 10 minutes, once. It is free: you create your own small "app"
in Google Cloud that only you use. No credit card is needed.

When you are done Jarvis can read and summarise your email, send replies and
drafts (it always asks you first before sending), read your calendar, and add
events.

> Reminders, alarms and timers do **not** need any of this. They work offline.

---

## 1. Create a Google Cloud project

1. Open <https://console.cloud.google.com/> and sign in with the Google
   account whose Gmail and Calendar you want Jarvis to use.
2. If asked, accept the terms of service (choose your country).
3. At the top left, click the project picker (it may say **Select a project**)
   and then **New project**.
4. Name it `Jarvis`, leave **Location** as it is, and click **Create**.
5. Wait a few seconds, then make sure the project picker at the top shows
   **Jarvis**. Every step below happens inside this project.

## 2. Turn on the Gmail API and the Google Calendar API

1. Open <https://console.cloud.google.com/apis/library/gmail.googleapis.com>
   and click **Enable**.
2. Open <https://console.cloud.google.com/apis/library/calendar-json.googleapis.com>
   and click **Enable**.

(Or search for "Gmail API" and "Google Calendar API" under
**APIs & Services > Library**.)

## 3. Set up the OAuth consent screen

This is the screen Google shows you when Jarvis asks for permission.

1. Go to **APIs & Services > OAuth consent screen**
   (<https://console.cloud.google.com/apis/credentials/consent>).
   On newer consoles this is called **Google Auth Platform**; click
   **Get started**.
2. **App name:** `Jarvis`. **User support email:** your own email. Click **Next**.
3. **Audience / User type:** choose **External**. Click **Next**.
   (Internal is only available for Google Workspace business accounts.)
4. **Contact information:** your email again. Click **Next**, tick the
   agreement, and click **Create** (or **Save and continue**).
5. **Test users:** open the **Audience** page (older consoles: the
   **Test users** step) and click **Add users**. Add **your own Gmail
   address** and save. While the app is in "Testing", only the people listed
   here can sign in, so do not skip this.
6. Scopes: you do not need to add any here. Jarvis asks for them when you sign in.

## 4. Create a Desktop OAuth client and download it

1. Go to **APIs & Services > Credentials**
   (<https://console.cloud.google.com/apis/credentials>), or **Clients** in
   Google Auth Platform.
2. Click **Create credentials > OAuth client ID** (or **Create client**).
3. **Application type:** **Desktop app**. Name: `Jarvis desktop`. Click **Create**.
4. In the window that appears, click **Download JSON**. If you closed it,
   click the download icon next to the client in the list.
5. Move and rename the file to:

   ```
   %USERPROFILE%\.jarvis\google_credentials.json
   ```

   This is usually `C:\Users\<your name>\.jarvis\google_credentials.json`.
   In File Explorer, type `%USERPROFILE%\.jarvis` in the address bar and press
   Enter to open the folder (Jarvis creates it the first time it runs; you can
   also create it yourself). Make sure Windows did not save the file as
   `google_credentials.json.json`. Turn on **View > File name extensions** to check.

   To keep the file somewhere else, set `GOOGLE_CREDENTIALS_FILE=C:\path\to\file.json`
   in your `.env` file.

Treat this file like a password. Do not share it or put it on GitHub.

## 5. Sign in once

Open a terminal in the Jarvis folder (the one with `run.bat`) and run:

```
pip install -r requirements-google.txt
python -m jarvis.tools.google_workspace --login
```

Your browser opens:

1. Pick your Google account.
2. You will see **"Google hasn't verified this app"**. This is expected,
   because it is your own app. Click **Continue** (sometimes under
   **Advanced > Go to Jarvis (unsafe)**).
3. Tick every permission box (Gmail and Calendar) and click **Continue**.
4. When the page says "Jarvis is connected to Google", close the tab.

The terminal should print something like
`Connected as you@gmail.com. Gmail OK. Calendar OK.`
The sign-in is saved in `%USERPROFILE%\.jarvis\google_token.json`.

Other commands:

```
python -m jarvis.tools.google_workspace --status   # check the connection
python -m jarvis.tools.google_workspace --logout   # forget the saved sign-in
```

Now try saying: *"Check my email"*, *"Read the second one"*,
*"What's on my calendar tomorrow?"*, *"Add dentist on Friday at 4 pm"*,
*"Reply to the latest email from Rahul saying I'll be there."*

## 6. Stop it from logging you out every 7 days

While your app's **Publishing status** is **Testing**, Google makes the
sign-in expire after **7 days**. Jarvis will then say your Google sign-in has
expired, and you would have to run `--login` again.

To avoid this, publish the app. For personal use it does not need Google's review:

1. Go to **OAuth consent screen** (or **Google Auth Platform > Audience**).
2. Under **Publishing status**, click **Publish app** and confirm.
3. Run `python -m jarvis.tools.google_workspace --login` one more time.
   Sign-ins made before publishing still expire after 7 days.

Google may show a notice that the app "needs verification" because Gmail
access is a sensitive permission. You can ignore it for an app only you use:
you will keep seeing the "hasn't verified this app" warning when you sign in,
and personal use is capped at 100 users, which is far more than you need.
Do not submit the app for verification.

## Troubleshooting

| Jarvis says / you see | Fix |
| --- | --- |
| "Google isn't connected yet" | The JSON file isn't at `%USERPROFILE%\.jarvis\google_credentials.json` (check the name and the `.json.json` problem), or you haven't run `--login`. |
| "the Google libraries aren't installed" | `pip install -r requirements-google.txt` |
| `Error 403: access_denied` in the browser | Add your Gmail address as a **test user** (step 3.5), or publish the app (step 6). |
| `Error 400: redirect_uri_mismatch` | The client was not created as **Desktop app**. Create a new Desktop client (step 4) and download it again. |
| "Your Google sign-in has expired" | Run `--login` again. Publish the app (step 6) to stop it recurring. |
| "Google refused that request" | You probably left a permission box unticked. Run `--login` and tick all boxes. Also check that both APIs are enabled (step 2). |
| The browser does not open | Copy the link printed in the terminal into your browser. |

To revoke Jarvis's access at any time, open
<https://myaccount.google.com/permissions>, pick **Jarvis** and choose
**Delete all connections**.
