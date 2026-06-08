import requests
import traceback

# ── Config ──────────────────────────────────────────────────────

confURL = 'https://api.rolimons.com/tradeads/v1/getrecentads'
rolimonURL = 'https://www.rolimons.com/itemapi/itemdetails'
adAmount = 10

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept' : 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.rolimons.com/',
    'Origin': 'https://www.rolimons.com',
}

# ── Colors ──────────────────────────────────────────────────────

RED         = '\033[31m'
GREEN       = '\033[32m'
YELLOW      = '\033[33m'
BLUE        = '\033[34m'
MAGENTA     = '\033[35m'
CYAN        = '\033[36m'

BOLD        = '\033[1m'
RESET       = '\033[0m'

# ── Key ─────────────────────────────────────────────────────────

tags = {
    1: 'Demand',
    2: 'Rare',
    3: 'Robux',
    4: 'Any',
    5: 'Upgrade',
    6: 'Downgrade',
    7: 'Rap',
    8: 'Wishlist',
    9: 'Projecteds',
    10: 'Adds',
}

# ── Cache ───────────────────────────────────────────────────────


rolimon_cache = {}

def loadRolimonCache():
    response = requests.get(rolimonURL, headers=headers, timeout=10)

    if response.status_code == 200:
        rolimon_cache.update(response.json()['items'])
        print(f'Loaded {len(rolimon_cache)} items into cache')
    else:
        print(f'Failed to cache items: {response.status_code}')

def rolimonLookUp(item_id):
    itemInfo = rolimon_cache.get(str(item_id), None)
    url = f'https://www.rolimons.com/item/{item_id}'

    if itemInfo:
        name = itemInfo[0]
        price = itemInfo[4] if itemInfo[4] != -1 else 0
        rap = itemInfo[2] if itemInfo[4] != -1 else 0
    else:
        roblox = robloxLookUp(item_id)
        if roblox:
            print(roblox['name'])
            name = roblox['name']
            price = roblox['price']
            rap = roblox['rap']
        else:
            name = str(item_id)
            price = 0
            rap = 0
    
    item = {
        'name': f'\033]8;;{url}\033\\{name}\033]8;;\033\\',
        'price': price,
        'rap': rap,
    }

    return item


roblox_cache = {}

def robloxLookUp(item_id):
    if str(item_id) in roblox_cache:
        return roblox_cache[str(item_id)]
    
    try:
        response = requests.get(f'https://economy.roblox.com/v2/assets/{item_id}/details', headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(data)
            result = {
                'name': data['Name'],
                'price': data['CollectiblesItemDetails'][0] or 0,
                'rap': 0
            }

            roblox_cache[str(item_id)] = result
            return result
    except Exception:
        pass
    return None
    

# ── Functions ───────────────────────────────────────────────────


def colored(text, color):
    return (f'{color}{text}{RESET}')

def apiRequest():
    session = requests.Session()
    session.headers.update(headers)

    session.get('https://www.rolimons.com', timeout=10)
    response = session.get(confURL, timeout=10)

    if response.status_code == 200:
        parseData(response)
    else:
        print(f"Request failed, status code: {response.status_code}")



def parseData(response):
    data = response.json()
    trade_ads = data['trade_ads'][:adAmount]

    print(f'─────────────────────────────────────────────────')
    for i, trade in enumerate(trade_ads):

        #Item Info
        offerTable = []
        requestTable = []
        
        if not isinstance(trade[4], dict) or 'items' not in trade[4]:
            continue
        if not isinstance(trade[5], dict) or ('items' not in trade[5] and 'tags' not in trade[5]):
            continue
        
        #Index Items
        for offerID in trade[4]['items']:
            offerTable.append(rolimonLookUp(offerID))

        if 'items' in trade[5]:
            for requestID in trade[5]['items']:
                requestTable.append(rolimonLookUp(requestID))
        elif 'tags' in trade[5]:
            for tag in trade[5]['tags']:
                requestTable.append(tags[tag])
        
        #Total Item Info
        totalOfferValue = 0
        totalOfferRap = 0

        for item in offerTable:
            totalOfferValue += int(item['price'])
            totalOfferRap += int(item['rap'])
            
        totalRequestValue = 0
        totalRequestRap = 0

        for item in requestTable:
            if isinstance(item, str): continue
            totalRequestValue += int(item['price'])
            totalRequestRap += int(item['rap'])

        valueDiff = totalRequestValue - totalOfferValue if totalRequestValue > 0 else 'N/A'
        rapDiff = totalRequestRap - totalOfferRap if totalRequestRap > 0 else 'N/A'

        #Player Info
        playerURL = f'https://www.roblox.com/users/{trade[2]}/profile'
        playerName = trade[3]
        playerDisplay = f'\033]8;;{playerURL}\033\\{playerName}\033]8;;\033\\'


        # ── PRINT INFO ──────────────────────────────────────────
        print()

        #PRINT USERNAME
        print(colored(f'Username: {playerDisplay}', YELLOW))
        print()

        #PRINT OFFERS
        print(colored(f'OFFER', GREEN))
        print(colored(f'    TOTAL VALUE: {totalOfferValue}', GREEN))
        print(colored(f'    TOTAL RAP: {totalOfferRap}', GREEN))
        print(colored(f'    Items:', GREEN))
        for offer in offerTable:
            print(colored(f'        {offer['name']}', GREEN))
        print()

        #PRINT REQUESTS
        print(colored(f'REQUESTS ', BLUE))
        print(colored(f'    TOTAL VALUE: {totalRequestValue}', BLUE))
        print(colored(f'    TOTAL RAP: {totalRequestRap}', BLUE))
        print(colored(f'    Items:', BLUE))
        for request in requestTable:
            if isinstance(request, dict):
                print(colored(f'        {request['name']}', BLUE))
            else:
                print(colored(f'        {request}', BLUE))
        print()

        print(colored(f'DIFFERENCES', MAGENTA))
        print(colored(f'    Value Diff: {valueDiff}', MAGENTA))
        print(colored(f'    Rap Diff: {rapDiff}', MAGENTA))
        print()
        print(f'─────────────────────────────────────────────────')


# ── Main ────────────────────────────────────────────────────────


def main():
    
    try:
        print('Loading Items Into Cache...')
        loadRolimonCache()
        print('Attempting To Fetch Most Recent Trade Ads...')
        apiRequest()
    except Exception as e:
        print(f'Error: {e}')
        traceback.print_exc()

if __name__ == "__main__":
    main()