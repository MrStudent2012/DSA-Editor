## ⚡ Quick Deploy to Cloud

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "DSA Editor"
git remote add origin https://github.com/YOUR_USERNAME/dsa-editor.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com (free account)
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. ✅ Auto-configured! (render.yaml sets everything)
5. Click "Create Web Service"
6. Wait 2-3 minutes → Get URL!

If deploy logs show `Running 'gunicorn app:app'`, open Render service settings and clear any manually-set Start Command override, then redeploy. This project expects the render.yaml command.

### Step 3: Use with Friends
- Share URL with friends
- Everyone joins same session ID
- Code together in real-time!

---

**That's it! No npm, no local setup for your friends. Just share the cloud URL!**
