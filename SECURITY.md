# Security Guidelines

## 🔒 Protecting Sensitive Information

This repository is **PUBLIC**, but sensitive files are protected using `.gitignore`. Follow these guidelines to keep your credentials safe.

## ✅ What's Protected (Never Committed to Git)

The following files are automatically excluded from Git:

### Environment Variables & Secrets
- `.env` - Your actual API keys and secrets
- `.env.local`, `.env.development`, `.env.production`
- Any file ending with `.env`

### API Keys & Credentials
- `*.key` - Private key files
- `*.pem`, `*.p12`, `*.pfx` - Certificate files
- `secrets.json`, `credentials.json`
- `service-account*.json` - Service account files

### Local Configuration
- `config.local.*` - Local configuration overrides
- Any file matching `*-config.local.*`

## 🚀 Setting Up Your Environment

### First Time Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual credentials:**
   ```bash
   # Open .env in your editor and add your real API keys
   GEMINI_API_KEY=your_actual_google_ai_api_key
   APP_ACCESS_CODE=your_actual_access_code
   ```

3. **Never commit `.env` to Git** - It's already in `.gitignore`

### For Collaborators

If someone clones this repository, they should:
1. Copy `.env.example` to `.env`
2. Add their own API keys to `.env`
3. Never share their `.env` file

## 🛡️ Best Practices

### ✅ DO:
- ✅ Keep all API keys in `.env` file
- ✅ Use `.env.example` to document required variables (with placeholder values)
- ✅ Rotate API keys if they're accidentally exposed
- ✅ Use environment variables in your code (e.g., `os.getenv('GEMINI_API_KEY')`)
- ✅ Add new sensitive file patterns to `.gitignore` if needed

### ❌ DON'T:
- ❌ Hardcode API keys in source code
- ❌ Commit `.env` file to Git
- ❌ Share your `.env` file with others
- ❌ Include real credentials in `.env.example`
- ❌ Push sensitive data to GitHub

## 🔍 Checking for Exposed Secrets

Before pushing to GitHub, verify no secrets are staged:

```bash
# Check what files are staged for commit
git status

# View the diff of staged changes
git diff --cached

# Make sure .env is not listed
git ls-files | grep .env
```

If `.env` appears in `git ls-files`, it means it was committed before. See the section below to remove it.

## 🚨 If You Accidentally Committed Secrets

If you accidentally committed sensitive files:

### Option 1: Remove from Latest Commit (if not pushed yet)
```bash
# Remove .env from the last commit
git rm --cached .env
git commit --amend -m "Remove sensitive .env file"
```

### Option 2: Remove from Git History (if already pushed)
```bash
# Remove .env from entire Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push to update remote
git push origin --force --all
```

### Option 3: Use BFG Repo-Cleaner (Recommended for large repos)
```bash
# Install BFG (https://rtyley.github.io/bfg-repo-cleaner/)
# Then run:
bfg --delete-files .env
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push origin --force --all
```

**⚠️ IMPORTANT:** After removing secrets from Git history:
1. **Rotate all exposed API keys immediately**
2. Generate new keys from your API provider
3. Update your local `.env` with new keys

## 🌐 Deployment Security

When deploying to platforms like Vercel, Netlify, or Heroku:

1. **Never include `.env` in deployment**
2. **Use platform environment variables:**
   - Vercel: Project Settings → Environment Variables
   - Netlify: Site Settings → Environment Variables
   - Heroku: Settings → Config Vars

3. **Set environment variables in deployment platform:**
   ```
   GEMINI_API_KEY=your_actual_key
   APP_ACCESS_CODE=your_actual_code
   ```

## 📝 Adding New Sensitive Files

If you create new files with sensitive data:

1. **Add the pattern to `.gitignore`:**
   ```bash
   echo "new-secret-file.json" >> .gitignore
   ```

2. **Create an example template:**
   ```bash
   # Create a template without real data
   cp new-secret-file.json new-secret-file.example.json
   # Edit the example to use placeholders
   ```

3. **Commit the example, not the real file:**
   ```bash
   git add new-secret-file.example.json .gitignore
   git commit -m "Add template for new secret file"
   ```

## 🔐 Current Protected Files in This Project

- `.env` - Contains `GEMINI_API_KEY` and `APP_ACCESS_CODE`
- `.venv/` - Python virtual environment
- `node_modules/` - Node.js dependencies
- `.vercel/` - Vercel deployment configuration

## 📞 Questions?

If you're unsure whether a file should be committed:
1. Does it contain API keys, passwords, or tokens? → **Don't commit**
2. Is it auto-generated (like `node_modules/`)? → **Don't commit**
3. Is it specific to your local machine? → **Don't commit**
4. Is it needed for others to run the project? → **Commit an example template**

---

**Remember:** When in doubt, don't commit it. You can always add it later, but removing sensitive data from Git history is difficult.
