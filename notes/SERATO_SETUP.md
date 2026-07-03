# Serato setup (local-first)

## Architecture

```text
NAS Master  →  sync/refresh  →  ~/Music/_Serato_/Imported/Latest Import  →  Serato
                                                                                ↓
                                                                         /Volumes/DJ_USB (gig export)
```

Never point Serato at the NAS (`buckles`) or read music from `/Volumes/buckles/_Serato_`.

---

## One-time Serato configuration

1. **Sync library locally** (wait for this to finish):
   ```bash
   python ~/dev/dj-library-tools/dj.py sync serato
   ```

2. **Serato → Settings → Library + Display → Drives**
   - **Remove:** `buckles`, any old USB names (`SSK SSD`, etc.)
   - **Add only:** `~/Music/_Serato_/Imported/Latest Import`

3. **Remove missing tracks**
   - Library → show missing → remove from library

4. **Analyze**
   - Select all in Latest Import → Analyze (local files; no yellow triangles from SMB)

5. **Gig USB**
   - Stick is formatted as **`DJ_USB`** → `/Volumes/DJ_USB`
   - Use Serato export / Prepare USB to that drive before gigs

---

## Daily workflow

```bash
python ~/dev/dj-library-tools/dj.py pipeline --serato --no-rekordbox   # new music
python ~/dev/dj-library-tools/dj.py refresh                          # before Serato session
```

Frozen Master tracks are never renamed or re-processed.
