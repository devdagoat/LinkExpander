import requests
import chompjs
import random
import re
import json
import undetected_chromedriver as uc

from bs4 import BeautifulSoup

from urllib.parse import urlparse, unquote

from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from random_user_agent.user_agent import UserAgent

ua = UserAgent(limit=50).get_random_user_agent()
headers = {"User-Agent" : ua}


def linktree_bypass(account_id:int, link_id:int) -> str:
    payload = {
        'accountId' : account_id,
        'validationInput' : {
            'acceptedSensitiveContent' : [link_id],
            'age' : random.uniform(19.2, 25.6)
        }
    }

    resp = requests.post("https://linktr.ee/api/profiles/validation/gates", json=payload, headers=headers)

    if resp.ok:
        return resp.json()['links'][0]['url']
    else:
        raise RuntimeError(f"Linktr.ee BYPASS failed: {resp.status_code} :\n\n{resp.text}")


def linktree(url:str) -> dict:
    print("Using Linktr.ee")
    resp = requests.get(url, headers=headers)
    if resp.ok:
        soup = BeautifulSoup(resp.content, 'html.parser')
        data_raw = str(soup.find('script', {'id' : '__NEXT_DATA__'}).contents[0]) # type: ignore
        data_dict = json.loads(data_raw)

        account_dict = data_dict['props']['pageProps']['account']
        account_id = account_dict['id']
        account_username = account_dict['username']
        account_tier = account_dict['tier']
        account_avatar = account_dict['profilePictureUrl']
        account_tz = account_dict['timezone']

        links = account_dict['links']
        packed_links = []
        for link_dict in links:

            link_id = link_dict['id']
            link_title = link_dict['title']
            link_type = link_dict["type"]
            link_domain = link_dict['rules']['gate']['sensitiveContent']['domain']
            link_url = link_dict['url']
            if not link_domain:
                link_domain = urlparse(link_url).netloc

            if link_url == None:
                # sensitive content warning, age verification etc
                if "sensitiveContent" in link_dict['rules']['gate']['activeOrder']:
                    link_url = linktree_bypass(account_id,link_id)
                else:
                    raise RuntimeError(f"Linktr.ee GET_URL Failed: \n\n{link_dict}")

            packed_links.append({
                'id' : link_id,
                'domain' : link_domain,
                'type' : link_type,
                'title' : link_title,
                'url' : link_url
            })

        packed_info = {
            'id' : account_id,
            'username' : account_username,
            'tier' : account_tier,
            'avatar' : account_avatar,
            'tz' : account_tz,
            'links' : packed_links
        }

        return packed_info

    else:
        raise RuntimeError(f"Linktr.ee GET Failed: {resp.status_code} :\n\n{resp.text}")    


def hoobe(url:str) -> dict:
    print("Using Hoo.be")
    resp = requests.get(url, headers=headers)
    if resp.ok:
        soup = BeautifulSoup(resp.content, 'html.parser')
        data_raw = str(soup.find('script', {'id' : '__NEXT_DATA__'}).contents[0]) # type: ignore
        data_dict = json.loads(data_raw)

        account_dict = data_dict['props']['pageProps']['user']
        account_id = account_dict['id']
        account_username = account_dict['handle']
        account_fullname = account_dict['fullName']
        account_usertype = account_dict['userType']
        account_avatar = ''
        account_created = account_dict['createdUtc']
        account_updated = account_dict['updatedUtc']
        if account_dict['hasPhoto']:
            unparsed_url = soup.find('div', {'class' : 'StaticProfileImage_staticImageContainer__PstDk'}).find('img').get('src') #type: ignore
            account_avatar = unquote(re.search(r"\?url=(.*)\&w=", unparsed_url).group(1)) #type: ignore
        
        social_buttons = data_dict['props']['pageProps']['userSocialPlatform']
        packed_links = []
        for button in social_buttons:
            button_id = button['id']
            button_url = button['link']
            button_domain = urlparse(button_url).netloc
            packed_links.append({
                'id' : button_id,
                'domain' : button_domain,
                'url' : button_url
            })

        links = data_dict['props']['pageProps']['content']
        for link in links:
            link_data = link['content']
            link_id = link_data['id']
            link_title = link_data['title']
            link_url = link_data['link']
            link_domain = urlparse(link_url).netloc
            link_created = link_data['createdUtc']
            link_updated = link_data['updatedUtc']
            packed_links.append({
                'id' : link_id,
                'title' : link_title,
                'domain' : link_domain,
                'created' : link_created,
                'updated' : link_updated,
                'url' : link_url
            })

        packed_info = {
            'id' : account_id,
            'username' : account_username,
            'displayname' : account_fullname,
            'usertype' : account_usertype,
            'avatar' : account_avatar,
            'created' : account_created,
            'updated' : account_updated,
            'links' : packed_links
        }

        return packed_info

    else:
        raise RuntimeError(f"Hoo.be GET Failed: {resp.status_code} :\n\n{resp.text}")


def snipfeed(url:str) -> dict:
    print("Using Snipfeed.co")
    options = uc.ChromeOptions()
    options.add_argument('headless')
    #drv = uc.Chrome(driver_executable_path=CHROMEDRIVER, options=options)
    drv = uc.Chrome(driver_executable_path=ChromeDriverManager().install(), options=options)
    drv.get(url)
    drv.reconnect(timeout=3)

    timeout = 1000

    try:
        element_present = EC.presence_of_element_located((By.ID, 'modal-portal'))
        WebDriverWait(drv, timeout).until(element_present)
    except TimeoutException:
        print("Waited enough")

    soup = BeautifulSoup(drv.page_source, 'html.parser')
    data_raw = str(soup.find('script', {'id' : '__NEXT_DATA__'}).contents[0]) # type: ignore
    data_dict = json.loads(data_raw)

    account_dict = data_dict['props']['pageProps']['creatorLink']
    account_id = account_dict['owner']['databaseId']
    account_username = account_dict['username']
    account_avatar = account_dict['profile']['avatarAsset']['facades']['image']['url']

    blocks = account_dict['blocks']
    packed_links = []
    for block in blocks:
        if block['__typename'] == 'SocialIconsBlock':
            for link_dict in block['links']:
                link_id = link_dict['id']
                link_platform = link_dict['platform']
                link_url = link_dict['url']
                link_domain = urlparse(link_url).netloc
                packed_links.append({
                    'id' : link_id,
                    'domain' : link_domain,
                    'platform' : link_platform,
                    'url' : link_url
                })

        elif block['__typename'] == 'CustomBlock':
            link_id = block['id']
            link_url = block['url']
            link_title = block['title']
            link_domain = urlparse(link_url).netloc
            try:
                link_image = block['coverAsset']['facades']['image']['url']
            except TypeError:
                link_image = None

            packed_links.append({
                    'id' : link_id,
                    'domain' : link_domain,
                    'title' : link_title,
                    'image' : link_image,
                    'url' : link_url
                })

    packed_info = {
        'id' : account_id,
        'username' : account_username,
        'avatar' : account_avatar,
        'links' : packed_links
    }

    return packed_info


def beacons(url:str) -> dict:
    print("Using Beacons.ai")
    options = uc.ChromeOptions()
    options.add_argument('headless')
    drv = uc.Chrome(driver_executable_path=ChromeDriverManager().install(), options=options)
    drv.get(url)
    drv.reconnect(timeout=3)

    timeout = 5

    try:
        element_present = EC.presence_of_element_located((By.ID, '__image__'))
        WebDriverWait(drv, timeout).until(element_present)
    except TimeoutException:
        print("Waited enough")

    drv.find_element(By.XPATH, "//*[contains(text(), 'I am 18 or older')]").click()

    soup = BeautifulSoup(drv.page_source, 'html.parser')

    header = soup.find('center', {'aria-label' : 'header block full header'})

    account_username = header.find_all('div')[1].contents[0] # type: ignore
    account_avatar = header.find_all('div')[0].find('img', {'alt' : 'profile'}).get('src') # type: ignore

    link_block = soup.find('div', {'aria-label' : 'links block link buttons'})
    links = link_block.find_all('a') # type: ignore

    packed_links = []
    for link in links:
        link_url = link.get('href')
        link_title = link.find('div', {'class' : 'LinkTitle'}).contents[0]
        link_domain = urlparse(link_url).netloc
        packed_links.append({
            'title' : link_title,
            'domain' : link_domain,
            'url' : link_url
        })

    packed_info = {
        'username' : account_username,
        'avatar' : account_avatar,
        'links' : packed_links
    }

    return packed_info


def allmylinks(url:str) -> dict:
    print("Using Allmylinks.com")
    resp = requests.get(url, headers=headers)
    if resp.ok:
        soup = BeautifulSoup(resp.content, 'html.parser')

        account_username = soup.find('span', {'class' : 'profile-usertag'}).contents[0].replace('@','').strip() # type: ignore
        account_displayname = soup.find('span', {'class' : 'profile-username profile-page'}).contents[0].strip() # type: ignore
        account_avatar = soup.find('img', {'alt' : 'Profile avatar'}).get('src') # type: ignore

        links = soup.find_all('div', {'class' : 'link-content'})
        packed_links = []
        for link in links:
            link_title = link.find('span', {'class' : 'link-title'}).contents[0]
            link_image = f"{urlparse(url).scheme}://{urlparse(url).netloc}{link.find('img', {'class' : 'cover-img'}).get('src')}"
            link_url = link.find('a', {'class' : 'list-item link-type-web link', 'title' : True}).get('data-x-url')
            link_domain = urlparse(link_url).netloc
            packed_links.append({
                'title' : link_title,
                'image' : link_image,
                'domain' : link_domain,
                'url' : link_url
            })

        packed_info = {
            'username' : account_username,
            'displayname' : account_displayname,
            'avatar' : account_avatar,
            'links' : packed_links
        }
        
        return packed_info

    else:
        raise RuntimeError(f"Allmylinks.com GET Failed: {resp.status_code} :\n\n{resp.text}")  
    

def milkshake(url:str) -> dict:
    print('Using Msha.ke')
    resp = requests.get(url, headers=headers)
    if resp.ok:
        soup = BeautifulSoup(resp.content, 'html.parser')

        # :(
        account_username = urlparse(url).path

        link_panel = soup.find('div', {'class' : 'look1-links__links-panel'})
        links = link_panel.find_all('a', {'rel' : 'ugc'}) # type: ignore
        packed_links = []
        for link in links:
            link_url = link.get('href')
            link_title = link.contents[0]
            link_domain = urlparse(link_url).netloc
            packed_links.append({
                'title' : link_title,
                'domain' : link_domain,
                'url' : link_url
            })
        
        packed_info = {
            'username' : account_username,
            'avatar' : "",
            'links' : packed_links
        }

        return packed_info

    else:
        raise RuntimeError(f"Msha.ke GET Failed: {resp.status_code} :\n\n{resp.text}")  


def linkr(url:str) -> dict:
    print("Using Linkr.bio")
    resp = requests.get(url, headers=headers)
    if resp.ok:
        soup = BeautifulSoup(resp.content, 'html.parser')
        raw_data = soup.find('script').contents[0] #type: ignore

        profile = re.search(r"r\.data=(.*);return", raw_data).group(1) #type: ignore
        parsed_profile = chompjs.parse_js_object(profile)

        account_username = urlparse(url).path
        account_avatar = parsed_profile['profilePic']
        account_desc = parsed_profile['bio']

        links = re.search(r"\{modules:(.*),pageInfo:", raw_data).group(1) #type: ignore
        parsed_links = chompjs.parse_js_object(links)
        packed_links = []
        for link in parsed_links:

            if type(link) == str: continue
            link = link['data']

            link_id = link['id']
            link_title = link['title']
            link_image = link['image']
            link_created = link['createdAt']
            link_url = link['ourl']
            link_domain = urlparse(link_url).netloc
            packed_links.append({
                'id' : link_id,
                'title' : link_title,
                'image' : link_image,
                'created' : link_created,
                'domain' : link_domain,
                'url' : link_url
            })

        packed_info = {
            'username' : account_username,
            'description' : account_desc,
            'avatar' : account_avatar,
            'links' : packed_links
        }

        return packed_info

    else:
        raise RuntimeError(f"Linkr.bio GET Failed: {resp.status_code} :\n\n{resp.text}")  


def carrd(url:str) -> dict:
    print("Using Carrd.co")
    resp = requests.get(url, headers=headers)
    if resp.ok:
        soup = BeautifulSoup(resp.content, 'html.parser')

        account_username = soup.find('h1', {'id' : 'text03'}).contents[0].replace('@', '') # type: ignore
        account_avatar_uri = soup.find('div', {'id' : 'image01'}).find('img').get('src') # type: ignore
        account_avatar = f"{url if url.endswith('/') else url + '/'}{account_avatar_uri}" 
        account_desc = soup.find('p', {'id' : 'text02'}).contents[0] # type: ignore

        links = soup.find('ul', {'id' : 'buttons01'}).find_all('li') # type: ignore
        packed_links = []
        for link in links:
            link_title = link.find('span', {'class' : 'label'}).contents[0]
            link_url = link.find('a').get('href')
            link_domain = urlparse(link_url).netloc
            packed_links.append({
                'title' : link_title,
                'domain' : link_domain,
                'url' : link_url
            })

        packed_info = {
            'username' : account_username,
            'avatar' : account_avatar,
            'description' : account_desc,
            'links' : packed_links
        }

        return packed_info

    else:
        raise RuntimeError(f"Carrd.co GET Failed: {resp.status_code} :\n\n{resp.text}")


def gather_links(url:str):
    match urlparse(url).netloc:
        case "linktr.ee":
            return linktree(url)
        case "hoo.be":
            return hoobe(url)
        case "snipfeed.co":
            return snipfeed(url)
        case "beacons.ai":
            return beacons(url)
        case "allmylinks.com":
            return allmylinks(url)
        case "msha.ke":
            return milkshake(url)
        case "linkr.bio":
            return linkr(url)
        case str(string) if "carrd.co" in string:
            return carrd(url)
        case _:
            raise NotImplementedError(f"{url} not supported yet")


