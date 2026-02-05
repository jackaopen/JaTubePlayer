# Authentication Module Documentation

## Overview

1. **google_login.py** - Google OAuth2 authentication management
2. **fernet_pubnew_class.py** - Credential and API key encryption/decryption

---

## File: fernet_pubnew_class.py

### Purpose
Handles encryption and decryption of sensitive data (Google credentials and YouTube API keys) using Fernet symmetric encryption, with keys protected by Windows DPAPI (Data Protection API).

### Class: `Ferner_encrptor`

#### Constructor Parameters
- `user_data_dir: str` - Path to the user data directory where encrypted files are stored
- `ctk_messagebox: ctk_messagebox` - Instance of the custom messagebox for displaying errors/warnings

#### Attributes
- `self.user_data_dir` - Storage location for encrypted files
- `self.ctk_messagebox` - Messagebox instance for UI notifications
- `self.Fernet_cred` - Fernet cipher instance for credential encryption
- `self.Fernet_API` - Fernet cipher instance for API key encryption

#### File Structure
The class manages four encrypted files:
1. `fernet_cred_key.enc` - Encrypted Fernet key for credential encryption (protected by Windows DPAPI)
2. `fernet_API_key.enc` - Encrypted Fernet key for API encryption (protected by Windows DPAPI)
3. `cred.enc` - Encrypted Google OAuth2 credentials
4. `API.enc` - Encrypted YouTube API key

### Methods

#### `check_and_create_sys_key()`
**Purpose:** Ensures encryption keys exist; creates them if missing.

**Workflow:**
1. Check if `fernet_cred_key.enc` exists
   - If not: Create new key via `_create_cred_key()`
   - Warn user if `cred.enc` exists (will be deleted)
   - Delete `cred.enc` to prevent decryption with wrong key
2. Check if `fernet_API_key.enc` exists
   - If not: Create new key via `_create_API_key()`
   - Warn user if `API.enc` exists (will be deleted)
   - Delete `API.enc` to prevent decryption with wrong key
3. Load both Fernet instances

**Security Note:** Regenerating keys invalidates previously encrypted data.

---

#### `_create_cred_key()` (Private)
**Purpose:** Generate and save a new Fernet key for credential encryption.

**Workflow:**
1. Generate random Fernet key using `Fernet.generate_key()`
2. Protect key using Windows DPAPI (`win32crypt.CryptProtectData()`)
3. Save encrypted key blob to `fernet_cred_key.enc`

---

#### `_create_API_key()` (Private)
**Purpose:** Generate and save a new Fernet key for API encryption.

**Workflow:**
1. Generate random Fernet key
2. Protect with Windows DPAPI
3. Save to `fernet_API_key.enc`

---

#### `_get_cred_key() -> Fernet` (Private)
**Purpose:** Load and decrypt the credential encryption key.

**Workflow:**
1. Read `fernet_cred_key.enc`
2. Decrypt using Windows DPAPI (`win32crypt.CryptUnprotectData()`)
3. Return Fernet cipher instance

**Error Handling:**
- On DPAPI error: Show fatal error messagebox and terminate app (`os._exit(1)`)
- Instructs user to delete `fernet_cred_key.enc` and restart

---

#### `_get_API_key() -> Fernet` (Private)
**Purpose:** Load and decrypt the API encryption key.

**Workflow:**
1. Read `fernet_API_key.enc`
2. Decrypt using Windows DPAPI
3. Return Fernet cipher instance

**Error Handling:**
- On DPAPI error: Show fatal error and exit
- Instructs user to delete `fernet_API_key.enc` and restart

---

#### `encrypt_api(api: str)`
**Purpose:** Encrypt and save YouTube API key.

**Workflow:**
1. Verify encryption keys exist (`check_and_create_sys_key()`)
2. Encode API string to bytes
3. Encrypt using `self.Fernet_API.encrypt()`
4. Write encrypted data to `API.enc`

---

#### `decrypte_api() -> str`
**Purpose:** Decrypt and return YouTube API key.

**Workflow:**
1. Read `API.enc`
2. Decrypt using `self.Fernet_API.decrypt()`
3. Decode bytes to string and return

**Returns:**
- `str` - Decrypted API key
- `None` - If file not found or decryption fails

**Error Handling:**
- `FileNotFoundError`: Return `None`
- Other exceptions: Show error messagebox and return `None`

---

#### `encrypt_cred(cred: Credentials)`
**Purpose:** Encrypt and save Google OAuth2 credentials.

**Workflow:**
1. Verify encryption keys exist
2. Convert credentials to JSON string (`cred.to_json()`)
3. Encode to bytes
4. Encrypt using `self.Fernet_cred.encrypt()`
5. Write to `cred.enc`

**Error Handling:**
- Show error messagebox on failure

---

#### `decrypte_cred() -> Credentials`
**Purpose:** Decrypt and return Google OAuth2 credentials.

**Workflow:**
1. Read `cred.enc`
2. Decrypt using `self.Fernet_cred.decrypt()`
3. Decode bytes to string
4. Parse JSON and create Credentials object via `Credentials.from_authorized_user_info()`

**Returns:**
- `Credentials` - Google OAuth2 credentials object
- `None` - If file not found or decryption fails

**Error Handling:**
- `FileNotFoundError`: Return `None`
- Other exceptions: Show error messagebox and return `None`

---

#### `clear_sys_key()`
**Purpose:** Delete all encryption-related files (reset encryption system).

**Workflow:**
Attempts to delete all four files:
1. `fernet_cred_key.enc`
2. `fernet_API_key.enc`
3. `cred.enc`
4. `API.enc`

Sets Fernet instances to `None`.

**Use Case:** Complete reset of authentication/encryption system.

---

## File: google_login.py

### Purpose
Manages Google OAuth2 authentication flow, credential storage, and user information retrieval for YouTube API access.

---

### Class: `custom_chrome`

#### Purpose
Custom browser handler to open OAuth2 flow in Chrome app mode (without browser UI chrome).

#### Method: `open(url, new=0, autoraise=True)`
**Workflow:**
1. Launch Chrome as a subprocess with `--app` flag
2. Opens URL in borderless app window
3. Stores process handle in global `chrome_process`

**Returns:** `True`

---

### Class: `google_auth_control`

#### Purpose
Main authentication controller handling login, logout, credential management, and user info retrieval.

#### Constructor Parameters
- `ver: str` - Application version string
- `current_dir: str` - Application root directory
- `ctk_messagebox: ctk_messagebox` - Messagebox instance for UI notifications
- `log_handle: Callable` - Logging function
- `youtubeAPI: str` - YouTube API key (optional)

#### Attributes
- `self.CONFIG` - Loaded from `user_data/config.json`
- `self.ver` - Application version
- `self.client_secret_path` - Path to Google OAuth2 client secrets JSON
- `self.youtubeAPI` - YouTube API key
- `self.log_handle` - Logging function
- `self.current_dir` - App directory
- `self.ctk_messagebox` - Messagebox instance
- `self.Fernet_encryptor` - Instance of `Ferner_encrptor` for credential encryption
- Custom Chrome browser registered with webbrowser module

---

### Methods

#### `load_token_from_env() -> Credentials | None`
**Purpose:** Load saved credentials and refresh if expired (non-interactive).

**Workflow:**
1. Decrypt credentials using `self.Fernet_encryptor.decrypte_cred()`
2. If credentials don't exist: Return `None`
3. If credentials expired but have refresh token:
   - Attempt to refresh using `cred.refresh(Request())`
   - If successful: Re-encrypt and save updated credentials
   - If failed: Return `None`
4. If valid: Return credentials

**Returns:**
- `Credentials` - Valid OAuth2 credentials
- `None` - If not found, expired without refresh token, or refresh failed

**Error Handling:**
- `FileNotFoundError`: Return `None`
- Other exceptions: Show toast notification and return `None`

**Use Case:** Called at app initialization to check for existing valid credentials.

---

#### `get_userinfo(cred: Credentials) -> dict | None`
**Purpose:** Retrieve Google user profile information.

**Decorator:** `@check_internet_silent` - Silently checks internet connection before execution.

**Workflow:**
1. Check if credentials exist and are not expired
2. Make API request to `https://www.googleapis.com/oauth2/v3/userinfo`
   - Uses Bearer token authentication
3. Parse JSON response
4. Check for error_description in response
   - If error: Show toast notification and return `None`
5. Return user info dictionary

**Returns:**
- `dict` - User information (email, name, picture, etc.)
- `None` - If credentials invalid or API error

**Response Fields (typical):**
- `sub` - User ID
- `name` - Full name
- `email` - Email address
- `picture` - Profile picture URL

**Error Handling:**
- Exception: Show toast notification and return `None`

---

#### `google_logout_clear_data() -> bool | Exception`
**Purpose:** Logout user by deleting all stored authentication data.

**Workflow:**
Attempts to delete three files:
1. `user_data/cred.enc` - Encrypted credentials
2. `user_data/liked.json` - Cached liked videos
3. `user_data/sub.json` - Cached subscriptions

**Returns:**
- `True` - If logout successful
- `Exception` - If error occurs during file deletion

**Error Handling:**
- Silently ignores `FileNotFoundError` for each file

---

#### `get_google_cred_and_save() -> None`
**Purpose:** Execute OAuth2 authentication flow and save credentials.

**Decorator:** `@check_internet` - Checks internet connection; shows error if offline.

**Important Notes:**
- Should run in separate thread (blocks until user completes auth)
- Requires modified `google_auth_oauthlib.flow.py` to support custom HTML success message

**Workflow:**
1. Show toast notification about starting login process
2. Verify `client_secret_path` exists
   - If not: Show error "no client secrets" and return `None`
3. Verify YouTube API key exists
   - If not: Show error "no API" and return `None`
4. Define OAuth2 scopes:
   - `youtube.readonly` - Read YouTube data
   - `userinfo.profile` - Read user profile
5. Create OAuth2 flow from client secrets
6. Read custom success HTML from `_internal/google_login_suc_red_page.html`
7. Run local server for OAuth2 callback:
   - Port: 0 (random available port)
   - Timeout: 120 seconds
   - Browser: `chrome_app` (custom Chrome handler)
   - Success message: Custom HTML page
8. Encrypt and save credentials using `self.Fernet_encryptor.encrypt_cred()`
9. Print success/failure message
10. Return credentials

**Returns:**
- `Credentials` - If authentication successful
- `None` - If error or user cancelled

**Error Handling:**
- Silent exception handling (bare `except: pass`)

---

#### `get_google_cred() -> Credentials | None`
**Purpose:** Force Google login in separate thread and wait for completion.

**Workflow:**
1. Create thread running `get_google_cred_and_save()`
2. Start thread
3. Wait for thread completion (`thread.join()`)
4. Load saved credentials from environment
5. Return credentials

**Returns:**
- `Credentials` - Newly acquired credentials
- `None` - If login failed

**Use Case:** When user explicitly clicks "Login" button.

---

#### `get_cred() -> Credentials | None`
**Purpose:** Get valid credentials (load saved or force login if needed).

**Workflow:**
1. Try to load credentials from environment (`load_token_from_env()`)
2. If no valid credentials:
   - Print "loaded cred from env"
   - Force Google login (`get_google_cred()`)
3. Return credentials

**Returns:**
- `Credentials` - Valid credentials
- `None` - If all methods fail

**Error Handling:**
- Silent exception handling (bare `except: pass`)

---

## Authentication Workflow Diagrams

### Initial App Startup Flow
```
[App Start]
    ↓
[Load Config]
    ↓
[Initialize google_auth_control]
    ↓
[Initialize Ferner_encrptor]
    ↓
[Check/Create Encryption Keys]
    ↓
[load_token_from_env()]
    ↓
    ├─→ [Credentials Found & Valid] → [Load User Info] → [Continue]
    ├─→ [Credentials Expired] → [Attempt Refresh]
    │                               ↓
    │                          [Success] → [Save & Continue]
    │                               ↓
    │                          [Failed] → [Prompt Login]
    └─→ [No Credentials] → [Prompt Login]
```

### Login Flow
```
[User Clicks Login]
    ↓
[Verify Internet Connection]
    ↓
[Check Client Secrets File] ─[Missing]→ [Error: No Client Secrets]
    ↓ [Exists]
[Check API Key] ─[Missing]→ [Error: No API]
    ↓ [Exists]
[Start OAuth2 Flow]
    ↓
[Launch Chrome App Window]
    ↓
[User Logs In Google]
    ↓
[Google Redirects to Localhost]
    ↓
[Receive Authorization Code]
    ↓
[Exchange Code for Tokens]
    ↓
[Credentials Object Created]
    ↓
[Encrypt Credentials]
    ↓
[Save to cred.enc]
    ↓
[Success]
```

### Encryption/Decryption Flow
```
[Credential Object]
    ↓
[Convert to JSON String]
    ↓
[Encode to Bytes]
    ↓
[Fernet Encrypt]
    ↓
[Write to cred.enc]

[Read cred.enc]
    ↓
[Fernet Decrypt]
    ↓
[Decode to String]
    ↓
[Parse JSON]
    ↓
[Create Credentials Object]
```

### Logout Flow
```
[User Clicks Logout]
    ↓
[Delete cred.enc]
    ↓
[Delete liked.json]
    ↓
[Delete sub.json]
    ↓
[Clear UI Session]
    ↓
[Return to Login State]
```

---

## Security Considerations

### Encryption Architecture
1. **Two-Layer Encryption:**
   - Layer 1: Fernet symmetric encryption for credentials/API
   - Layer 2: Windows DPAPI for Fernet keys
   
2. **Key Storage:**
   - Fernet keys never stored in plaintext
   - Keys protected by Windows user account (DPAPI)
   - Keys cannot be decrypted by different Windows user

3. **Key Regeneration:**
   - If encryption keys are lost/corrupted, system auto-regenerates
   - Old encrypted data becomes inaccessible (intentional security feature)
   - User must re-authenticate

### OAuth2 Security
1. **Scopes:** Minimal scopes requested (readonly + profile)
2. **Token Storage:** Access/refresh tokens encrypted at rest
3. **Auto-Refresh:** Expired tokens automatically refreshed without user interaction
4. **Timeout:** 2-minute timeout for OAuth2 flow

### Error Handling Philosophy
- Fatal errors (DPAPI failure): Terminate app to prevent security bypass
- Non-fatal errors: Show user-friendly message and gracefully degrade
- Sensitive errors: Don't expose internal details to user

---

## Dependencies

### External Libraries
- `cryptography.fernet` - Symmetric encryption
- `google.oauth2.credentials` - OAuth2 credential objects
- `google_auth_oauthlib.flow` - OAuth2 authentication flow
- `google.auth.transport.requests` - Token refresh
- `win32crypt` - Windows DPAPI
- `pywintypes` - Windows error types
- `requests` - HTTP client for API calls

### Internal Dependencies
- `notification.wintoast_notify.ToastNotification` - Windows toast notifications
- `notification.ctkmessagebox.ctk_messagebox` - Custom messagebox
- `utils.check_internet` - Internet connectivity decorators

---

## Configuration Files

### config.json
Located in `user_data/config.json`

**Required Fields:**
- `client_secret_path` - Path to Google OAuth2 client secrets JSON file

### Client Secrets JSON (Google OAuth2)
Downloaded from Google Cloud Console

**Contains:**
- Client ID
- Client secret
- Redirect URIs
- Auth URIs

---

## File Permissions & Access

### Windows DPAPI Binding
- Encryption keys bound to Windows user account
- Cannot be accessed by:
  - Different Windows user on same machine
  - Same username on different machine
  - Administrator accounts (without user credentials)

### Portability Limitations
- Encrypted data not portable between machines
- User must re-authenticate when:
  - Switching Windows accounts
  - Moving to new computer
  - Reinstalling Windows

---

## Error Messages & Troubleshooting

### "FATAL ERROR: get credential key failed"
**Cause:** DPAPI cannot decrypt `fernet_cred_key.enc`

**Reasons:**
- File corrupted
- Created by different Windows user
- System integrity compromised

**Solution:** Delete `fernet_cred_key.enc` and restart app

---

### "FATAL ERROR: get API key failed"
**Cause:** DPAPI cannot decrypt `fernet_API_key.enc`

**Solution:** Delete `fernet_API_key.enc` and restart app

---

### "ERROR: decrypt credential failed"
**Cause:** Fernet decryption failed on `cred.enc`

**Possible Reasons:**
- File corrupted
- Mismatched encryption key
- File modified externally

**Result:** Returns `None`, user must re-login

---

### "There is no client secrets"
**Cause:** `client_secret_path` in config.json doesn't exist or is invalid

**Solution:** Download client secrets from Google Cloud Console and update config

---

### "There is no API"
**Cause:** YouTube API key not configured

**Solution:** Set YouTube API key in settings

---


## API Endpoints Used

### Google OAuth2
- **Authorization:** `https://accounts.google.com/o/oauth2/auth`
- **Token:** `https://oauth2.googleapis.com/token`
- **User Info:** `https://www.googleapis.com/oauth2/v3/userinfo`

### YouTube Data API v3
- Used by other modules (not directly in these files)
- Requires scopes: `youtube.readonly`

---

*Last Updated: February 4, 2026*
*Module Version: Compatible with JaTubePlayer 2.0*
