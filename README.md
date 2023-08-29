# LinkExpander
Link expander in Python which parses and returns the URLs and information in common link domains. (The currently supported links are in below)

**REQUIRES PYTHON>=3.10**

## Supported Links:

- **Linktr.ee**
- **Hoo.be**
- **Snipfeed.co**\*
- **Beacons.ai**
- **Allmylinks.com**
- **Msha.ke**
- **Linkr.bio**
- **Carrd.co**

_* Snipfeed.co heavily relies on Cloudflare bypass and can be patched at any time. (Despite using UndetectedChromedriver)_

## Usage

First, download and install the dependencies:

`py -m pip install -r requirements.txt`

Then, place the script inside your project directory and import the function:

```python
from LinkExpander import gather_links
```

After that, call gather_links with the URL of the linksite:

```python
...

links_info = gather_links("URL")
```

## Returned Data

#### This will return a dictionary. **Although the different sites will return more/less information than one another, they all will have the following fields:**

- `username`: Account username
- `avatar`: Account avatar
- `links`: A list of the scraped links

#### The `links` list includes:

- `domain`: Domain of the link
- `title`: Title of the link
- `url`: URL of the link

The typical returned dictionary looks like this:
```python
  {
"username" : "Some username",
"avatar" : "URL of the avatar",
"links" : [
  {"title" : "Example1", "domain" : "google.com", "url" : "https://google.com"},
  {"title" : "Example2", "domain" : "facebook.com", "url" : "https://facebook.com/..."}
  ]
}
```

In addition to above, the optional fields are as follows:

---

### Linktr.ee

- `id`: Account ID
- `tier`: Account tier
- `tz`: Account timezone

#### Links

- `id`: Link ID
- `type`: Link Type

---

### Hoo.be

- `id`: Account ID
- `displayname`: Account Display Name
- `usertype`: Account User type (similar to Linktr.ee tiers)
- `created`: Account creation date
- `updated`: Account last update date

#### Links
- `id`: Link ID
- `created`: Link creation date
- `updated`: Link last update date

---

### Snipfeed.co

- `id`: Account ID

**Snipfeed Links are 2 categories: Social Icons and regular Links, each having different fields.**

⚠️ **Social Icons don't have the `title` field!**

#### Social Icons

- `id`: Link ID
- `platform`: Link Platform

#### Links

- `id`: Link ID
- `image`: Link Image

---

### Beacons.ai

**-none-**

---

### Allmylinks.com

- `displayname`: Account Display Name

#### Links

- `image`: Link Image

---

### Msha.ke

**-none-**

---

### Linkr.bio:

- `description`: Account description (bio)

#### Links

- `id`: Link ID
- `image`: Link Image
- `created`: Link creation date

---

### Carrd.co

- `description`: Account description (bio)

---

## Credits

Credits 100% to @devdagoat
