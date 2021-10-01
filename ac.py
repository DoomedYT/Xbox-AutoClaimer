import os
import json
import requests
import ctypes
import threading
import random
import time
from dhooks import Webhook, Embed
from colorama import Fore, init
init()


green = Fore.GREEN                                          
white = Fore.WHITE                                      
red = Fore.RED                                              
yellow = Fore.YELLOW                                        
blue = Fore.BLUE   
cyan = Fore.CYAN  
authS = '[\033[1;32;40m+\033[1;37;40m]'
authF = '[\033[1;31;40mx\033[1;37;40m]'

class Reserve:
    def __init__(self):
        self.webhook = self.return_webhook() 
        self.reserve_url = "https://gamertag.xboxlive.com/gamertags/reserve"
        self.claim_url = "https://accounts.xboxlive.com/users/current/profile/gamertag"
        self.token_url = "https://xsts.auth.xboxlive.com/xsts/authorize"
        self.main_url = "https://accounts.xboxlive.com/users/current/profile"

        self.attempts = 0
        self.errs = 0
        self.rl = 0

        self.banner = f"[{green}*{white}]"
        self.error = f"[{red}404{white}]"
        self.question = f"[{yellow}+{white}]"
        self.idle = f"[{cyan}?{white}]"
        self.avivable = f"[{red}!{white}]"
        self.claimedlol = f"[{cyan}(:{white}]"

    def return_webhook(self):
        with open("config.json") as f:
            raw_json = json.loads(f.read())

        return raw_json["webhook_url"]

    def chunks(self, n, lst):             # split list into smaller sublists of n size
        for i in range(0, len(lst), n):  
            yield lst[i:i + n]

    def reserve(self, gamertag, xuid, token):
        payload = {
            "classicGamertag": f"{gamertag}",
            "reservationId": f"{xuid}",
            "targetGamertagFields": "classicGamertag"
        }
        headers = {
            "x-xbl-contract-version": '1', 
            "Authorization": token
        }

        response = requests.post(self.reserve_url, headers=headers, json=payload)

        if response.status_code == 200:   
            return True
        elif response.status_code == 409: 
            self.attempts += 1      
            return False
        elif response.status_code == 429: 
            self.rl += 1                  
            return False
        else:                             
            self.errs += 1                
            print(response.status_code)
            return False



    def claim(self, xuid, gamertag, token):
        payload = {
            "reservationId": f"{xuid}",
            "gamertag": {
                "classicGamertag": f"{gamertag}",
                "gamertagSuffix": "",
                "classicGamertag": f"{gamertag}"},
                "preview": False,
                "useLegacyEntitlement":False
            }
        headers = {
            "Authorization": token,
            "x-xbl-contract-version": "6",
            "Content-Type": "application/json"
        }
        r = requests.post(self.claim_url, headers=headers, json=payload)

        if r.status_code == 200:
            print('{} Gamertag {} has been detectedas avivable'.format(self.avivable, Gamertag))
            return True
        elif r.status_code == 403:
            print(f"{self.error} Failed to claim. but detected lmao")
            return False
        else:
            with lock:
                log(r.text)
                #print(f"{self.error} Failed to claim {gamertag}. Response: {r.text}")

            return False

    def noti(self, gamertag, xuid, claimed=False):
        hook = self.webhook
        requests.post(hook, json={
            "content": None,
            "embeds": [
                {
                    "title": "forces autoclaimer",
                    "description": "Gamertag Claimed!",
                    "color": None,
                    "fields": [
                        {
                        "name": "Gamertag",
                        "value": gamertag
                        },
                        {
                        "name": "Claimed",
                        "value": claimed
                        }
                    ],
                    "footer": {
                        "text": "ss"
                    },
                    "thumbnail": {
                        "url": "https://i.gifer.com/9WKM.gif"
                    }
                }
            ]
        })

    def log_claimed(self, gamertag, xuid, email):
        with open("Claimed.txt", "a+") as f:
            f.write(f"{gamertag}:{xuid}:{email}\n")

        f.close()

    def grab_token(self, user_token):
        payload = {
            "RelyingParty": "http://xboxlive.com",
            "TokenType": "JWT",
            "Properties": {
                "UserTokens": [user_token],
                "SandboxId": "RETAIL"
            }
        }
        r = requests.post(self.token_url, json=payload)
        if r.status_code == 200:
            res = json.loads(r.text)
            token = res['Token']
            uhs = res['DisplayClaims']['xui'][0]['uhs']
        
            tokens.append(f"XBL3.0 x={uhs};{token}")                                                                                   
    
    

   
    def get_account_data(self, token, email=False):                                                                                    
        r = requests.get(self.main_url, headers={"Authorization": token})
        res = json.loads(r.text)

        return res["xuid"] if not email else res["email"]                                                                              


    def random_spacing(self, s, num_spaces):
        assert(num_spaces <= len(s) - 1)

        space_idx = []
        space_idx.append(random.randint(0, len(s) - 2))
        num_spaces -= 1

        while (num_spaces > 0):
            idx = random.randint(0, len(s) - 2)
            if not idx in space_idx:
                space_idx.append(idx)
                num_spaces -= 1

        result_with_spaces = ''
        for i in range(len(s)):
            result_with_spaces += s[i]
            if i in space_idx:
                result_with_spaces += " "

        return result_with_spaces

    def random_caps(self, gamertag):
        spaced = self.random_spacing(gamertag, random.randint(0, len(gamertag)-1))
        
        return "".join(random.choice((str.upper, str.lower))(c) for c in spaced)

    def plural_check(self, x, y):
        return y if x == 1 else f"{y}s"

    def calc_threads(self, x):
        return int(x / 100 + 1)

def do_shit():
    pass

def rand_claim(xuid, gamertag, token):
    for _ in range(4):
        random_gamertag = reserve_obj.random_caps(gamertag)
        claimed = reserve_obj.claim(xuid, random_gamertag, token)
        
        if claimed:
            print(f"\n{reserve_obj.claimedlol} Claimed {green}{random_gamertag}{white} after {green}{reserve_obj.attempts}{white} {reserve_obj.plural_check(reserve_obj.attempts, 'attempt')}\n")
            hook = Webhook('')
            embed = Embed(
            description='',
            color=0x5CDBF0
            )
            embed = Embed(
            description='',
            color=0x5CDBF0
            )
            
            embed.add_field(name='Gamertag', value='{}'.format(gamertag))
            embed.set_footer(text='')
            
            embed.set_thumbnail(url='https://media.giphy.com/media/cm5bkjcx7ycaF0Vc2q/giphy.gif')
            hook.send(embed=embed)

            email = reserve_obj.get_account_data(token, email=True)                                                  
            reserve_obj.log_claimed(random_gamertag, xuid, email)                                                          
            reserve_obj.noti(random_gamertag, xuid, claimed=True)                                                                                                                                               
            t = threading.Thread(target=claimer, args=(split_tags[x], split_tokens[x % len(split_tokens)], xuid, claim_token))                 
            t.start()     
def print_shit(gamertag, xuid, token, claimed=False):
    email = reserve_obj.get_account_data(token, email=True)
    reserve_obj.log_claimed(gamertag, xuid, email)      

    if claimed:  
        with lock:       
            print(f"\n{reserve_obj.reserve_obj.claimedlol} Claimed {green}{gamertag}{white} after {green}{reserve_obj.attempts}{white} {reserve_obj.plural_check(reserve_obj.attempts, 'attempt')}\n")
            hook = Webhook('')
            embed = Embed(
            description='',
            color=0x5CDBF0
            )
            embed = Embed(
            description='',
            color=0x5CDBF0
            )
            
            embed.add_field(name='Gamertag', value='{}'.format(gamertag))
            embed.set_footer(text='')
            
            embed.set_thumbnail(url='https://media.giphy.com/media/cm5bkjcx7ycaF0Vc2q/giphy.gif')
            hook.send(embed=embed)
            
            reserve_obj.noti(gamertag, xuid, claimed=True)
            t = threading.Thread(target=claimer, args=(split_tags[x], split_tokens[x % len(split_tokens)], xuid, claim_token))                 
            t.start()     


def claimer(tag_list, tokens_list, xuid, claim_token):
    while True:                                                                                                                       
        for i in range(len(tag_list)):
            gamertag = gamertags[i]                                                                                                    
            token = tokens_list[i % len(tokens_list)]                                                                                   
            reserved = reserve_obj.reserve(gamertag, xuid, token)                                                                      

            if reserved:                                                                                                               
                with lock:
                    print(f"\n{reserve_obj.reserve_obj.claimedlol} Claimed {green}{gamertag}{white} after {green}{reserve_obj.attempts}{white} {reserve_obj.plural_check(reserve_obj.attempts, 'attempt')}\n")
                    hook = Webhook('')
                    embed = Embed(
                    description='',
                    color=0x5CDBF0
                    )
                    embed = Embed(
                    description='',
                    color=0x5CDBF0
                    )
                    
                    embed.add_field(name='Gamertag', value='{}'.format(gamertag))
                    embed.set_footer(text='')
                    
                    embed.set_thumbnail(url='https://media.giphy.com/media/cm5bkjcx7ycaF0Vc2q/giphy.gif')
                    hook.send(embed=embed)
                    t = threading.Thread(target=claimer, args=(split_tags[x], split_tokens[x % len(split_tokens)], xuid, claim_token))                 
                    t.start()     
                claimed = reserve_obj.claim(xuid, gamertag, claim_token)
                
                if not claimed:
                    rand_claim(xuid, gamertag, claim_token)
                    with lock:
                        print(f"{reserve_obj.error} Couldn't claim {gamertag}. Claim manually. Email and token logged")
                        print(f"\n{reserve_obj.banner} Missed {green}{gamertag}{white} after {green}{reserve_obj.attempts}{white} {reserve_obj.plural_check(reserve_obj.attempts, 'attempt')}\n")
                        hook = Webhook('')
                        embed = Embed(
                        description='',
                        color=0x5CDBF0
                        )
                        embed = Embed(
                        description='',
                        color=0x5CDBF0
                        )
                        
                        embed.add_field(name='Gamertag', value='{}'.format(gamertag))
                        embed.set_footer(text='')
                        
                        embed.set_thumbnail(url='https://media.giphy.com/media/cm5bkjcx7ycaF0Vc2q/giphy.gif')
                        hook.send(embed=embed)
                        email = reserve_obj.get_account_data(claim_token, email=True)
                        reserve_obj.log_claimed(gamertag, xuid, email)
                        reserve_obj.noti(gamertag, xuid)
                        t = threading.Thread(target=claimer, args=(split_tags[x], split_tokens[x % len(split_tokens)], xuid, claim_token))                 
                        t.start()     
        
                else:
                    with lock:
                        print_shit(gamertag, xuid, claim_token, claimed=True)
                    
                claim_token = random.choice(tokens)
                xuid = reserve_obj.get_account_data(claim_token)
            else:
                with lock:
                    print(f"{reserve_obj.banner} Attempts: {reserve_obj.attempts} | RL: {reserve_obj.rl} | Errors: {reserve_obj.errs}", end="\r", flush=True)
                    

def log(e):
    with open("Response.txt", "a+") as f:
        f.write(f"{e}\n")


if __name__ == '__main__':
    user_tokens = [x.strip("\n") for x in open("tokens.txt").readlines() if x]                                                            
    gamertags = [x.strip("\n") for x in open("gamertags.txt").readlines() if x]         
    tokens = []                                                                                                                                
                                                        
    reserve_obj = Reserve()                                                                                                                    
    lock = threading.Lock()
            
    for x in range(len(user_tokens)):                                                                                                          
        t = threading.Thread(target=reserve_obj.grab_token, args=(user_tokens[x],))                                                            
        t.start()                          
        t.join()
        
        with lock:
            print(f"{reserve_obj.idle} Checking Tokens {len(tokens)}/{len(user_tokens)}", end="\r", flush=True)              
            
    print(f"\n{reserve_obj.idle} Tokens Authed: {len(tokens)}\n")       
    split_tags = list(reserve_obj.chunks(250, gamertags))                                                                                      
    split_tokens = list(reserve_obj.chunks(250, tokens))                                                                                                  
                                                                                                                      
    print('{}'.format(authS), end='');thread_count = int(input(' Threads: '))       
            
    try:                                                                                                                                       
        for x in range(len(split_tags)):
            claim_token = random.choice(tokens)                                                                                                
            xuid = reserve_obj.get_account_data(claim_token)                                                                                   
            t = threading.Thread(target=claimer, args=(split_tags[x], split_tokens[x % len(split_tokens)], xuid, claim_token))       
            t.start()                                                                                                                          
    except Exception as e:             
        log(e)             
        pass                                                                                                                                   