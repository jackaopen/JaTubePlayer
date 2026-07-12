# Account.py YouTube Cookie API Flow

This file explains the code after `account_handle` in `Account.py`.

`account_handle` owns the local login/cookie storage work:

- WebView2 login
- AES key file handling
- DPAPI decrypt
- encrypted cookie file decrypt

Everything after `account_handle` is only for calling YouTube Innertube with that cookie and parsing the JSON result.

## High Level Flow

```text
saved encrypted cookie
-> account_handle.get_cookie()
-> raw YouTube Cookie header string
-> build SAPISIDHASH Authorization header
-> GET normal YouTube page to read ytcfg
-> POST /youtubei/v1/browse
-> save raw response
-> parse response into videos, shorts, continuation
```

## Function Call Flow

```text
main()
-> account_handle(...)
-> account.get_cookie()
-> browse(...)
-> page_headers(...)
-> base_headers(...)
-> auth(...)
-> session.get(referer)
-> ytcfg(response.text)
-> build payload
-> api_headers(...)
-> base_headers(...)
-> auth(...)
-> session.post(youtubei/v1/browse)
```

`main()`

Reads CLI args like `--page`, `--limit`, `--playlist-id`, and controls the whole run.

`account_handle(...)`

Creates the account/cookie manager. It knows where the encrypted cookie and AES key files are.

`account.get_cookie()`

Decrypts the saved YouTube cookie and returns the raw cookie string. This cookie is the browser login state.

`browse(...)`

Main YouTube API function. It handles one feed/page request: history, liked, subscriptions, playlist, etc.

`page_headers(...)`

Builds headers for the first normal YouTube page GET. This request is for HTML, so it uses browser-page-style headers.

`base_headers(...)`

Builds shared headers used by both page GET and API POST: `Cookie`, `Origin`, `Referer`, `User-Agent`, and `Authorization`.

`auth(...)`

Creates `Authorization: SAPISIDHASH ...` from the cookie. YouTube uses this with cookies for logged-in web API requests.

`session.get(referer)`

Requests the normal YouTube page, for example `https://www.youtube.com/feed/history`. This is mainly to get YouTube page config, not videos.

`ytcfg(response.text)`

Extracts config from `ytcfg.set({...})` in the page HTML. This gives the current `INNERTUBE_API_KEY`, client context, client version, and visitor data.

`build payload`

Creates the JSON body for Innertube, including `context.client` and either `browseId` or `continuation`.

`api_headers(...)`

Builds headers for the Innertube API POST. It adds JSON/API-specific headers like `Content-Type`, `X-YouTube-Client-Name`, `X-YouTube-Client-Version`, and `X-Goog-Visitor-Id`.

`session.post(youtubei/v1/browse)`

Sends the actual Innertube request. This returns the feed, playlist, history, or continuation JSON.

There are now three common command flows:

```powershell
python account_dev\Account.py --page history --limit 10
python account_dev\Account.py --page playlists --limit 20
python account_dev\Account.py --playlist-id LL --limit 10
```

## Why The Cookie Is Enough For Login

The saved cookie string is sent directly as:

```http
Cookie: SID=...; SAPISID=...; __Secure-1PAPISID=...
```

That is the browser login state. YouTube can identify the account from those cookies.

For many logged-in Innertube calls, YouTube also expects an Authorization header derived from the cookie:

```http
Authorization: SAPISIDHASH <timestamp>_<sha1>
```

So the code sends both:

- raw `Cookie`
- generated `Authorization`

The cookie string itself does not need to be fully parsed for the request. It is parsed only to find `SAPISID`, `__Secure-1PAPISID`, and `__Secure-3PAPISID` for the Authorization hash.

## Constants

```python
ORIGIN = "https://www.youtube.com"
```

Used in request headers and in the SAPISID hash input.

```python
UA = "Mozilla/5.0 ..."
```

Basic browser-like user agent. It does not need to be perfect. The important thing is consistency with a normal browser request.

```python
PAGES = {
    "home": ("FEwhat_to_watch", "https://www.youtube.com/"),
    "subscriptions": ("FEsubscriptions", "https://www.youtube.com/feed/subscriptions"),
    "history": ("FEhistory", "https://www.youtube.com/feed/history"),
    "liked": ("VLLL", "https://www.youtube.com/playlist?list=LL"),
    "playlists": (None, "https://www.youtube.com/feed/playlists"),
}
```

Each entry has:

- `browseId`
- page URL used as `Referer` and to read `ytcfg`

`playlists` is different. It does not use a stable feed browse ID here. The code opens `/feed/playlists` and parses `ytInitialData` from the page HTML to list playlist IDs.

## auth(cookie)

Purpose: create YouTube's cookie Authorization header.

Logic:

```text
split cookie string into name/value pairs
get current Unix timestamp
for each SAPISID-style cookie:
    sha1("<timestamp> <cookie value> https://www.youtube.com")
    build "<scheme> <timestamp>_<hash>"
join all schemes into one Authorization value
```

Why it exists:

The raw cookie proves browser login state. The SAPISID hash proves the request came from a script/page that knows the cookie value and origin.

## ytcfg(html)

Purpose: extract YouTube's page config from HTML.

It searches for:

```javascript
ytcfg.set({...})
```

Useful values from this config:

- `INNERTUBE_API_KEY`
- `INNERTUBE_CONTEXT`
- `INNERTUBE_CLIENT_VERSION`
- `INNERTUBE_CONTEXT_CLIENT_NAME`
- `VISITOR_DATA`

Why it exists:

The Innertube API key and client version can change. Reading them from YouTube's own page avoids hardcoding stale values.

## browse(cookie, page, continuation, query)

Purpose: call YouTube's Innertube browse API.

Step 1: choose browse ID and referer:

```python
browse_id, referer = PAGES[page]
```

Step 2: build base headers:

```http
Accept: application/json
Content-Type: application/json
Cookie: <raw cookie string>
Origin: https://www.youtube.com
Referer: <page URL>
User-Agent: <UA>
X-Origin: https://www.youtube.com
Authorization: SAPISIDHASH ...
```

Step 3: GET the page URL.

This is not for videos. It is only to read `ytcfg`.

Step 4: build payload.

First page:

```json
{
  "context": { "client": { "...": "..." } },
  "browseId": "FEhistory"
}
```

Next page:

```json
{
  "context": { "client": { "...": "..." } },
  "continuation": "<token>"
}
```

History search:

```json
{
  "context": { "client": { "...": "..." } },
  "browseId": "FEhistory",
  "query": "keyword"
}
```

Step 5: POST:

```text
https://www.youtube.com/youtubei/v1/browse?key=<INNERTUBE_API_KEY>&prettyPrint=false
```

Returns:

- full response JSON
- small metadata: page, HTTP status code, browse ID

If `playlist_id` is passed, `browse()` uses:

```python
browse_id = "VL" + playlist_id
referer = "https://www.youtube.com/playlist?list=" + playlist_id
```

Examples:

```text
LL -> VLLL
WL -> VLWL
PLabc... -> VLPLabc...
```

This is the flow for getting the contents of a known playlist.

## list_playlists(cookie)

Purpose: list playlist IDs from the signed-in user's playlists page.

It requests:

```text
https://www.youtube.com/feed/playlists
```

Then it extracts:

```javascript
ytInitialData
```

and passes that JSON to `parse_browse()`.

Why it does not use `youtubei/v1/browse`:

The `/feed/playlists` page exposed playlist IDs in its HTML response during testing, while `FEplaylist` returned HTTP 400. Parsing the page data is simpler and currently works for listing playlist IDs.

Typical parsed output:

```json
{
  "playlists": [
    {
      "playlist_id": "LL",
      "title": "Liked videos",
      "url": "https://www.youtube.com/playlist?list=LL",
      "thumbnail": null,
      "video_count": "Private"
    }
  ],
  "continuation": "..."
}
```

## parse_browse(data)

Purpose: turn huge Innertube JSON into a small app-friendly structure.

Output shape:

```json
{
  "videos": [],
  "shorts": [],
  "playlists": [],
  "continuation": "..."
}
```

It looks for these YouTube item types:

- `lockupViewModel`: current web video item
- `shortsLockupViewModel`: Shorts item
- `videoRenderer`: older/common video item
- `gridVideoRenderer`: older/common grid video item
- `playlistRenderer`: older/common playlist item
- `gridPlaylistRenderer`: older/common grid playlist item
- `lockupViewModel` with playlist content type: current web playlist item
- `continuationCommand`: next page token

Why this is needed:

Innertube responses are huge. They include real items, menus, share commands, feedback commands, topbar data, tracking params, and UI config. The parser extracts only the useful parts.

For normal videos, it returns:

- `type`
- `video_id`
- `title`
- `url`
- `thumbnail`
- `channel`
- `views`

For Shorts, it returns:

- `type`
- `video_id`
- `title`
- `url`
- `thumbnail`
- `views`

For playlists, it returns:

- `playlist_id`
- `title`
- `url`
- `thumbnail`
- `video_count`

## Limit

`--limit` restricts how many parsed items are kept in each parsed list.

Example:

```powershell
python account_dev\Account.py --page history --limit 5
```

This can save a huge raw response, but the parsed response will keep at most:

- 5 videos
- 5 Shorts
- 5 playlists

The continuation token is still saved if YouTube returns one.

Important: `--limit` does not ask YouTube to return fewer items. It only limits the local parsed output after the response arrives. YouTube Innertube generally controls page size itself.

## main()

Command-line entry point.

It:

1. Reads CLI args.
2. Gets cookie through `account_handle`.
3. Calls `browse()` for feeds or playlist contents.
4. Calls `list_playlists()` for `--page playlists`.
4. Saves raw JSON.
5. Saves parsed JSON.
6. Saves metadata JSON.

Default output files:

```text
account_dev/temp_retrever.json
account_dev/temp_retrever_parsed.json
account_dev/temp_retrever_meta.json
```

## Is Reading A Huge JSON Suspicious?

No.

Parsing `temp_retrever.json` is local file reading. YouTube cannot see that.

YouTube only sees network requests:

- the GET to the normal page
- the POST to `/youtubei/v1/browse`
- any continuation requests

The response being large is normal. A big local JSON file is not suspicious.

Things that can be suspicious:

- calling continuation pages too fast
- calling many feeds repeatedly
- using stale or invalid cookies
- switching IP/location/device behavior often
- sending mismatched fake headers

## Are The Headers Complete Enough?

For this flow, yes. The working tested set is:

```http
Cookie
Authorization
Origin
Referer
User-Agent
X-Origin
X-Goog-Visitor-Id
X-YouTube-Client-Name
X-YouTube-Client-Version
Content-Type
Accept
Accept-Language
```

The code does not try to fake every browser header. That is intentional. Over-faking headers often creates inconsistent requests.

The best signal is consistency:

- use the real saved cookie
- use YouTube's current `ytcfg`
- use normal request pacing
- refresh cookie through WebView2 when needed

## Simplest Possible Version

The smallest mental model is:

```python
cookie = account_handle(APP_ROOT, box, print).get_cookie()
data, meta = browse(cookie, "history")
parsed = parse_browse(data)
```

At the HTTP level:

```text
1. Send Cookie to YouTube page.
2. Extract INNERTUBE_API_KEY from ytcfg.
3. Send Cookie + SAPISIDHASH to youtubei/v1/browse.
4. Parse lockupViewModel and continuationCommand.
```

The absolute smallest code would hardcode the API key and client version, but that is fragile. The current version is still small while avoiding stale hardcoded YouTube config.
