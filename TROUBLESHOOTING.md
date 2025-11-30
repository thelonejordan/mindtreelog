# Troubleshooting Guide

## Twitter API SSL Certificate Errors

If you see errors like:
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain
```

### Quick Fix (Development Only)

Add to your `.env` file:
```shell
TWITTER_VERIFY_SSL=false
```

⚠️ **Warning**: This disables SSL verification. Only use for development/debugging.

### Proper Solutions

Choose the solution that matches your situation:

#### Solution 1: Install/Update Python Certificates (macOS)

If you're on macOS and installed Python via official installer:

```shell
# Run the certificate installer that comes with Python
cd /Applications/Python\ 3.13/
./Install\ Certificates.command
```

Or manually:
```shell
pip install --upgrade certifi
```

#### Solution 2: Update System CA Certificates

**macOS:**
```shell
# Using Homebrew
brew install ca-certificates

# Or update certificates via system update
softwareupdate --install --all
```

**Ubuntu/Debian:**
```shell
sudo apt-get update
sudo apt-get install ca-certificates
sudo update-ca-certificates
```

#### Solution 3: Corporate Proxy/Firewall

If you're behind a corporate proxy that intercepts SSL:

1. Export your corporate proxy's CA certificate
2. Set environment variable:
   ```shell
   export REQUESTS_CA_BUNDLE=/path/to/corporate-ca-bundle.crt
   ```
3. Add to `.env`:
   ```shell
   REQUESTS_CA_BUNDLE=/path/to/corporate-ca-bundle.crt
   ```

#### Solution 4: Use certifi Certificates

```python
# In your .env file, you can specify:
SSL_CERT_FILE=/path/to/certifi/cacert.pem
```

Find certifi location:
```shell
python -c "import certifi; print(certifi.where())"
```

### Verify Fix

After applying any solution, test with:

```shell
python -c "import ssl; import urllib.request; urllib.request.urlopen('https://api.twitter.com')"
```

If no error, SSL is working correctly!

## Other Common Issues

### Issue: "Twitter API rate limit exceeded"

**Symptoms:**
```
Twitter API rate limit exceeded (Free tier: 1,500 tweets/month)
💡 Tip: Posts are still saved with placeholder text. Edit in admin or wait for limit reset.
```

**Causes:**
- You've exceeded your API quota (Free tier: 1,500 tweets/month)
- Rate limits reset monthly

**Solutions:**

1. **Wait for reset** - Limits reset on the 1st of each month
2. **Use placeholder text** - Posts are still saved, you can:
   - Edit text manually in Django admin (`/admin/`)
   - Keep using the app (adding works, just without auto-fetch)
3. **Upgrade API tier** - If you need more:
   - Basic: $100/month for 10,000 tweets
   - Pro: $5,000/month for 1M tweets
4. **Use Twitter embeds** - No API needed (see below)

### Issue: "Could not fetch post information"

**Causes:**
1. Invalid/expired Twitter API token
2. Rate limit exceeded
3. Tweet is deleted or private
4. Network connectivity issues

**Solution:**
- Check your bearer token is correct
- Verify API tier limits
- Posts will still be added with placeholder text (editable in admin)

### Issue: "Invalid X/Twitter URL"

**Causes:**
- Incorrect URL format
- Missing tweet ID

**Supported formats:**
- `https://x.com/username/status/1234567890`
- `https://twitter.com/username/status/1234567890`

### Issue: Django admin not accessible

**Solution:**
1. Create superuser:
   ```shell
   .venv/bin/python manage.py createsuperuser
   ```
2. Access admin at: `http://127.0.0.1:8000/admin/`

## Alternative: Use Twitter Embeds (No API Needed!)

If you don't want to deal with API limits or SSL issues, you can use Twitter's embed feature instead:

### Benefits:
- ✅ No API token needed
- ✅ No SSL configuration
- ✅ No rate limits
- ✅ Always shows current tweet state (likes, retweets)
- ✅ Full Twitter functionality (like, reply, retweet)

### How to Switch:

The current implementation stores minimal info and uses the API. To use embeds instead, you could:

1. **Keep storing just the URL**
2. **Embed tweets on the page** using Twitter's widget:
   ```html
   <blockquote class="twitter-tweet" data-theme="dark">
       <a href="{{ post.post_url }}"></a>
   </blockquote>
   <script async src="https://platform.twitter.com/widgets.js"></script>
   ```

3. **Let Twitter handle the display** - No API calls needed!

This approach is simpler and has no rate limits. The trade-off is that you need JavaScript enabled and tweets load from Twitter on page view.

## Getting Help

If issues persist:
1. Check Django logs for detailed errors
2. Verify all environment variables are set correctly
3. Ensure Python 3.13 is being used
4. Try in a fresh virtual environment
