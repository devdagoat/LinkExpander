# LinkExpander
Link expander in Python which parses and returns the URLs and information in common link domains. (The currently supported links are in below)

**REQUIRES PYTHON>=3.10**

## Supported Links:

- **Linktr.ee**
- **Hoo.be**
- **Snipfeed.co**\*
- **Beacons.ai**
- **Allmylinks.com**\*
- **Msha.ke**
- **Linkr.bio**
- **Carrd.co**
- **Lnk.bio**
- **Direct.me**\*

_* These sites heavily rely on Cloudflare bypass and can be patched at any time. (Despite using UndetectedChromedriver)_

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

## Credits

Credits 100% to @devdagoat
