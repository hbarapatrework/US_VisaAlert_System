# Topic Initialization Guide

## Automatic Topic Creation

If `NTFY_TOPIC_VAC` or `NTFY_TOPIC_INTERVIEW` are empty in `.env`, the system will automatically:

1. **Generate unique topics** using UUID
2. **Save them to `.env`** file
3. **Display the URLs** for easy sharing
4. **Start receiving notifications** immediately

## First Run

When you run the system for the first time with empty topics:

```bash
python main_new.py
```

You'll see output like:

```
[2026-07-11 17:30:00] INFO: Topics not configured. Generating new topics...
[2026-07-11 17:30:00] INFO: New topics created and saved to .env:
[2026-07-11 17:30:00] INFO:   VAC Topic: usvisa-vac-a1b2c3d4
[2026-07-11 17:30:00] INFO:   Interview Topic: usvisa-interview-e5f6g7h8
[2026-07-11 17:30:00] INFO: Share these topics to receive notifications:
[2026-07-11 17:30:00] INFO:   https://ntfy.sh/usvisa-vac-a1b2c3d4
[2026-07-11 17:30:00] INFO:   https://ntfy.sh/usvisa-interview-e5f6g7h8
```

The topics are now saved in your `.env` file:

```env
NTFY_TOPIC_VAC=usvisa-vac-a1b2c3d4
NTFY_TOPIC_INTERVIEW=usvisa-interview-e5f6g7h8
```

## Using the Topics

### Subscribe to Notifications

Open the topic URLs in your browser or push notification app:
- VAC Notifications: `https://ntfy.sh/usvisa-vac-a1b2c3d4`
- Interview Notifications: `https://ntfy.sh/usvisa-interview-e5f6g7h8`

### Push Notifications

Download ntfy.sh app and subscribe to the topics:
- **iOS**: Available on App Store
- **Android**: Available on Google Play
- **Web**: Direct browser support

### API Access

You can also poll the API:
```bash
curl https://ntfy.sh/usvisa-vac-a1b2c3d4/json
```

## Custom Topics

To use custom topic names, simply edit `.env`:

```env
NTFY_TOPIC_VAC=my-visa-vac-alerts
NTFY_TOPIC_INTERVIEW=my-visa-interview-alerts
```

The system will use these custom topics on the next run.

## Topic Security

⚠️ **Important:**
- Anyone with the topic URL can receive your notifications
- Topics are not encrypted or password-protected
- Use unique/random topic names (the auto-generation does this)
- Never share your topic URLs publicly if you want privacy

## Re-generating Topics

To generate new topics:

1. Empty the values in `.env`:
   ```env
   NTFY_TOPIC_VAC=
   NTFY_TOPIC_INTERVIEW=
   ```

2. Run the system again:
   ```bash
   python main_new.py
   ```

3. New unique topics will be generated and saved.

## Troubleshooting

### Topics not being created

Check that `.env` file is writable:
```bash
ls -la .env
chmod 644 .env
```

### Old topics still in use

Make sure you restarted the system after changing `.env`:
```bash
pkill -f main_new.py
python main_new.py
```

### Can't receive notifications

1. Verify topic names in `.env`:
   ```bash
   grep NTFY_TOPIC .env
   ```

2. Test the topic URL in browser:
   ```
   https://ntfy.sh/your-topic-name
   ```

3. Check network connectivity:
   ```bash
   curl https://ntfy.sh/test
   ```
