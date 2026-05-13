# Publishing `ha-ipool-light` to GitHub

## 1. Create the empty repo on GitHub

Create a public repository named e.g. `ha-ipool-light` (no README/license so the first push can use `main` only).

## 2. Push this folder

In PowerShell (adjust the path if yours differs):

```powershell
cd "C:\Users\Admin\Desktop\R-R-Maintenance-program\ha-ipool-light"
git init
git branch -M main
git add .
git commit -m "Initial iPool Light (BLE) integration for HACS"
git remote add origin https://github.com/randrcomputers/ha-ipool-light.git
git push -u origin main
```

Optional version tag for HACS users who track releases:

```powershell
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

Then on GitHub: **Releases → Draft a new release** from tag `v0.1.0` (optional).

## 3. GitHub About (discoverability)

On the repo page: **⚙** next to **About** → add a short **Description**, optional **Website**, and topic **`home-assistant`**.

## 4. HACS

Users add the repo under **HACS → Custom repositories** → category **Integration** → your repo URL.

If `git push` asks for credentials, use a **Personal Access Token** (classic) with `repo` scope as the HTTPS password, or use **SSH**.
