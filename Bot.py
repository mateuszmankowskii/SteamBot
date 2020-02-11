import requests
import pyotp
import json
from time import sleep
from steampy.client import SteamClient
from time import sleep
from steampy.utils import GameOptions
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio

API_BIT = ''
secret_Bit = ''
token_Bit = pyotp.TOTP(secret_Bit) 

API_OP = ''
secret_OP = ''
token_OP = pyotp.TOTP(secret_OP)

steam_client = SteamClient('')
steam_client.login("", "", "") 


#Sprawdzanie balansu
def balance_Bit():
    
    site_name = "https://bitskins.com/api/v1/get_account_balance/?api_key={}&code={}".format(API_BIT, token_Bit.now())          
    site = requests.get(site_name)
    table = site.json()
    return float(table['data']['available_balance'])

def balance_OP():
    site = requests.get('https://api.opskins.com/IUser/GetBalance/v1/', auth = (API_OP, token_OP.now()))
    table = site.json()
    return float((table['balance'])/100)

#Wyszukiwanie itemu
def search_item_Bit(item_name):
    item_name = json.dumps(item_name).replace(' ', '%20').replace('|', '').replace('"', '')
    site_name = "https://bitskins.com/api/v1/get_inventory_on_sale/?api_key={}&page=1&app_id=730&sort_by=price&order=asc&market_hash_name={}&code={}".format(API_BIT, item_name, token_Bit.now())
    #print(site_name)
    site = requests.get(site_name)
    table = site.json()
    #print(table)
    item_id = table['data']['items'][0]['item_id']
    price = float(table['data']['items'][0]['price'])
    return item_id, price

def search_item_OP(item_name):
    item_name = json.dumps(item_name).replace(' ', '%20').replace('|', '').replace('"', '')
    site_name = 'https://api.opskins.com/ISales/Search/v1/?app=730_2&search_item={}'.format(item_name)
    site = requests.get(site_name, auth = (API_OP, token_OP.now()))
    table = site.json()
    item_id = table['response']['sales'][0]['id']
    prices = float(table['response']['sales'][0]['amount'])/100
    return  item_id, prices


#Kupowanie
def Buying_Bit(item, price): 
    site_name = "https://bitskins.com/api/v1/buy_item/?api_key={}&item_ids={}&prices={}&app_id=730&code={}".format(API_BIT, item, price, token_Bit.now())
    site = requests.get(site_name)
    table = site.json()
    #print(table)
    #return (table['trade_tokens'])

def Buying_OP(item, price):
    payload = {'total': int(price*100), 'saleids': item}
    #print(payload)
    site_name = "https://api.opskins.com/ISales/BuyItems/v1/"
    site = requests.post(site_name, data = payload, auth = (API_OP, token_OP.now()))
    table = site.json()
    #print(table)
    return table['response']['items'][0]['new_itemid']

#Wyjmowanie itemu TYLKO OP
def Withdraw(item_number):
    payload = {'items' : item_number}
    site_name = "https://api.opskins.com/IInventory/Withdraw/v1/"
    site = requests.post(site_name, data = payload, auth = (API_OP, token_OP.now()))
    table = site.json()
    return table['response']['offers'][0]['tradeoffer_id']


#Sprzedaż
def Selling_Bit(item, price):
    #print(item, price)
    site_name = "https://bitskins.com/api/v1/list_item_for_sale/?api_key={}&item_ids={}&prices={}&app_id=730&code={}".format(API_BIT, item, price, token_Bit.now())
    site = requests.get(site_name)
    table = site.json()
    #print(table)
    #return table['data']['trade_tokens']

def Selling_OP(item, price):
    
    item_details = [{'appid' : 730, 'contextid' : 2, 'assetid' : item, 'price' : price}]
    item_details = json.dumps(item_details)
    payload = {'items' : item_details}
    site_name = "https://api.opskins.com/ISales/ListItems/v1/"
    site = requests.post(site_name, data = payload, auth = (API_OP, token_OP.now()))
    table = site.json()
    #return table['response']['tradeoffer_id']


#Pobieranie inventory w sprzedaży 
def Inventory_onsale_Bit(item):
    item = item.replace(' ', '%20').replace('|', '%7C').replace('"', '')
    #print(item)
    site_name = "https://bitskins.com/api/v1/get_item_history/?api_key={}&page=1&names={}&app_id=730&code={}".format(API_BIT, item, token_Bit.now())
    #print(site_name)
    site = requests.get(site_name)
    table = site.json()
    #print(table)
    return table['data']['items']

def Inventory_onsale_OP():
   
    site_name = "https://api.opskins.com/ISales/GetSales/v2/?state=2"
    site = requests.get(site_name, auth = (API_OP, token_OP.now()))
    table = site.json()
    return table['response']['sales']

#Akceptowanie ofert(wymaga trade_id)
def Accept(trade_id):
    if steam_client.is_session_alive() == True:
        steam_client.accept_trade_offer(trade_offer_id = trade_id)
    else:
        steam_client.login("", "", "")
        steam_client.accept_trade_offer(trade_offer_id = trade_id)

#Powiadomienia
def alert_bit(message, sell, buy):
    bot = commands.Bot(command_prefix='#')
    @bot.event
    async def on_ready():
        user = await bot.get_user_info('')
        await bot.send_message(user, content="OP - > Bit {} : {} | {} | {}".format(message, str(sell), str(buy), str(round(sell * 0.95-buy, 2))))
        await bot.close()
    bot.run("")

def alert_op(message, sell, buy):
    bot = commands.Bot(command_prefix='#')
    @bot.event
    async def on_ready():
        user = await bot.get_user_info('')
        await bot.send_message(user, content="Bit - > OP {} : {} | {} | {}".format(message, str(sell), str(buy), str(round(sell * 0.95-buy, 2))))
        await bot.close()
    bot.run("")


def Accept_any():
    summary = steam_client.get_trade_offers(merge = True)
    trade_id = summary['response']['trade_offers_received'][0]['tradeofferid']
    steam_client.accept_trade_offer(trade_offer_id = trade_id)

def new_id():
    inventory = steam_client.get_my_inventory(game = GameOptions.CS)
    for k in inventory:
        return k

#OD LEWEJ DO PRAWEJ; BIT, OP, INVENTORY

d = open("data.txt", "r")
data = json.load(d)
d.close()

while True:
    b = 0
    licznik = False
    
    money_bit = balance_Bit()
    money_op = balance_OP()
    for dic in data:
        for key in dic:
            #print(key)
            id_Bit, price_Bit = search_item_Bit(key)
            id_OP, price_OP = search_item_OP(key)
            if price_Bit * 0.95 - price_OP >= price_OP * 0.02 and data[b][key][0] == 0 and money_op >= price_OP:
                id = Buying_OP(id_OP, price_OP)
                sleep(10)
                money_op -= price_OP
                trade_id = Withdraw(id)
                sleep(10)
                Accept(trade_id)
                sleep(30)
                #sprawdzic
                Selling_Bit(new_id(), round(price_Bit - 0.01, 2))
                data[b][key][0] += 1
                sleep(10)
                Accept_any()
                #alert_bit(key, round(price_Bit - 0.01, 2), price_OP)
                licznik = True
            elif price_OP * 0.95 - price_Bit >= price_Bit * 0.02 and data[b][key][1] == 0 and money_bit >= price_Bit:
                id = Buying_Bit(id_Bit, price_Bit)
                sleep(10)
                money_bit -= price_Bit
                Accept_any()
                sleep(30)
                Selling_OP(new_id(), round((price_OP - 0.01),2)*100)
                data[b][key][1] += 1
                sleep(10)
                Accept_any()
                #alert_op(key, round((price_OP - 0.01),2), price_Bit)
                licznik = True
            else:
                sleep(5)
            b += 1
    c = open("data.txt", "w")
    c.write(json.dumps(data))
    c.close()
    e = 0
    for inventory in data:
        for key in inventory:
            #print(key)
            #print(data[0][key][0])
            for key in inventory:   
                #print(key) 
                for item in Inventory_onsale_Bit(key):
                    #print(item)
                    if item == []:
                        continue
                    else:
                        if item["on_sale"] == False:
                            #print(e)
                            data[e][key][0] = 1
                            
                            continue
                    
                        else:
                            data[e][key][0] = 0
        e += 1
    e = 0
    for inventory in data:
        for key in inventory:    
            for item in Inventory_onsale_OP():
                #print(item["market_hash_name"])
                #print(key)
                
                if item["market_hash_name"] == key:
                    data[e][key][1] = 1
                    e += 1
                    continue
                    
                else:
                    data[e][key][1] = 0
                e += 1
    if not licznik:
        sleep(30)