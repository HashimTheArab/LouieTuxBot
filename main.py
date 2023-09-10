import random
import requests
from bs4 import BeautifulSoup
from time import sleep
import threading

"""------CONFIGURATION------"""
contestant_name = 'Huda Hussain'
proxy_type = 'http' # http, socks4, socks5
proxyFile = False
"""------CONFIGURATION------"""

user_agents = requests.get('https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt')
user_agents = user_agents.text.split('\n')
user_agents.pop()

if proxyFile:
    proxies = open('proxies.txt', 'r').read().split('\n')
    proxies.pop()
else:
    proxies = str(requests.get(f"https://api.proxyscrape.com/?request=getproxies&proxytype={proxy_type}&timeout=10000&country=all").content.decode()).split('\r\n')
    proxies.pop()

contestant_id = ''
amount_votes = 0

def main():
    for i in range(30):
        threading.Thread(target=vote, args=(contestant_name,)).start()
       # try:
            
      #  except AttributeError as e:
      #      print("Banned proxy:", e)
       # except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError) as e:
        #    print("Dead proxy:", e)
        sleep(0.1)
        

def vote(contestant_name: str):
    session = requests.Session()

    modalVoteToken = ''
    ua = gen_user_agent()
   # proxy = get_proxy()
    proxy = {}

    headers={
            "User-Agent": ua,
            "Authority": "www.louiestuxshop.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://www.louiestuxshop.com/model-search/vote",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

    print("Fetching initial request..")
    data = session.get(
        "https://www.louiestuxshop.com/modal/eligible-to-vote",
        headers=headers,
        #cookies={
       #     "CraftSessionId": "gno6r2a8b0tbnj2733p0h09f2v",
       #     "modalVoteToken": "kowd73r2q89dtdh7gw3t9hb4tmf5xt3a"
       # }
        #proxies=proxy
    )

    json = data.json()
    if json['status'] == 'eligible' and json['token']:
        modalVoteToken = json['token']
    else:
        print("Failed checking eligbility")
        print(json.status)
        return

    print("Fetching data with second request..")
    pageData = session.get("https://www.louiestuxshop.com/model-search/vote", headers=headers)
    if(len(pageData.cookies['CRAFT_CSRF_TOKEN']) == 0):
        print("\n\nError: CSRF Token not found")
        return
   
    pageData.cookies['modalVoteToken'] = modalVoteToken
    submit_vote(session, pageData, ua, proxy, contestant_name)
    

def submit_vote(session: requests.Session, pageData: requests.Response, ua: str, proxy: dict, contestant_name: str):
    global contestant_id, amount_votes

    soup = BeautifulSoup(pageData.content.decode(), features='lxml')
    csrf_token_form = soup.find("input", {"name": "CRAFT_CSRF_TOKEN"})['value']
    if contestant_id == '':
        contestant_id = soup.find('a', {'id': 'click-to-vote-btn', 'data-contestant-name': contestant_name})['data-id']
        print(f"Found ID for {contestant_name}: {contestant_id}")

    data = {
        'CraftSessionId': pageData.cookies['CraftSessionId'], # Found in the cookie
        'CRAFT_CSRF_TOKEN': pageData.cookies['CRAFT_CSRF_TOKEN'], # Found in the cookie
        'CRAFT_CSRF_BODY': csrf_token_form, # Found in the HTML
        'modalVoteToken': pageData.cookies['modalVoteToken'], # Response from the elgibility check
        'contestant_id': contestant_id # Fetched from the HTML, using the students name.
    }

    resp = session.post(
        "https://www.louiestuxshop.com/modal/vote",
        headers={
            "User-Agent": ua,
            "Authority": "www.louiestuxshop.com",
            "Origin": "https://www.louiestuxshop.com/",
            "Referer": "https://www.louiestuxshop.com/model-search/vote",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "cookie": f"CraftSessionId={data['CraftSessionId']}; CRAFT_CSRF_TOKEN={data['CRAFT_CSRF_TOKEN']}; form_posted_37=1694147049; modalVoteToken={data['modalVoteToken']};",
        },
        data=f"contestant_id={data['contestant_id']}&validEligibletoken={data['modalVoteToken']}&CRAFT_CSRF_TOKEN={data['CRAFT_CSRF_BODY']}",
        cookies=pageData.cookies,
        #proxies=proxy
    )
    if resp.text == '{"status":"success"}':
        amount_votes += 1
        print(f"Successfully voted! ({amount_votes})")
    else:
        print(resp.status_code, resp.text)

def default_headers():
    return {
        "User-Agent": gen_user_agent(),
        "Accept-Language": "en-US,en;q=" + ("0.9" if random.randint(0, 1) == 0 else "0.5"),
        "Referer": "https://www.louiestuxshop.com/model-search/vote"
    }

def gen_user_agent():
    return random.choice(user_agents)

def get_proxy():
    proxy = random.choice(proxies)
    prefix = proxy_type + '://'
    if proxy_type == 'http':
        prefix = ''
    return {
        "http": prefix + proxy,
        "https": prefix + proxy
    }


main()
