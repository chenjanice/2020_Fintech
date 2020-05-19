#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import configparser
import telegram
from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters

config = configparser.ConfigParser()
config.read('config.ini')
print(config['TELEGRAM']['ACCESS_TOKEN'])
print(config['TELEGRAM']['WEBHOOK_URL'])
access_token = config['TELEGRAM']['ACCESS_TOKEN']
webhook_url = config['TELEGRAM']['WEBHOOK_URL']


# In[8]:


requests.post('https://api.telegram.org/bot'+access_token+'/deleteWebhook').text


# In[9]:


requests.post('https://api.telegram.org/bot'+access_token+'/setWebhook?url='+webhook_url+'/hook').text


# # [完整版]

# In[7]:


# Initial Flask app
# coding: utf-8
from fugle_realtime_restful_api import *
import datetime

app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=config['TELEGRAM']['ACCESS_TOKEN'])
def meta(sym):
    api='b71c49b4c7925bb66e6f59f068f0892f'
    c=intraday.meta(apiToken=api, output='raw', symbolId=sym)
    
    nameZhTw = c['nameZhTw']#股票中文簡稱
    industryZhTw = c['industryZhTw'] #產業別

    typeZhTw = c['typeZhTw']#股票類別
    isIndex = c['isIndex'] #是否為指數
    isWarrant = c['isWarrant']#是否為權證
    isSuspended = c['isSuspended'] #今日是否暫停買賣
    isTerminated = c['isTerminated']#今日是否已終止上市

    priceHighLimit = c['priceHighLimit']#漲停價
    priceLowLimit = c['priceLowLimit']#跌停價
    priceReference = c['priceReference']#今日參考價

    canDayBuySell = c['canDayBuySell'] #是否可先買後賣現股當沖
    canDaySellBuy = c['canDaySellBuy'] #是否可先賣後買現股當沖
    canShortLend = c['canShortLend']   #是否豁免平盤下融券賣出
    canShortMargin = c['canShortMargin']#是否豁免平盤下借券賣出
    
    x=[nameZhTw,industryZhTw,
       typeZhTw,str(isIndex),str(isWarrant),str(isSuspended),str(isTerminated),
       priceHighLimit,priceLowLimit,priceReference,
       str(canDayBuySell),str(canDaySellBuy),str(canShortLend),str(canShortMargin)]
    return x


def chart(sym):
    def time():
        x = datetime.datetime.now()
        x = x - datetime.timedelta(minutes=1)
        x = x - datetime.timedelta(hours=8)
        a1 = x.year 
        a2 = x.month 
        a3 = x.day 
        a4 = x.hour
        a5 = x.minute
        if a2 <= 9 :
            a2 = '0'+str(a2)
        if a3 <= 9 :
            a3 = '0'+str(a3)
        if a4 <= 9 :
            a4 = '0'+str(a4)
        if a5 <= 9 :
            a5 = '0'+str(a5)
        r =str(a1)+'-'+str(a2)+'-'+str(a3)+'T'+str(a4)+':'+str(a5)+':00.000Z'
        return r
    api='b71c49b4c7925bb66e6f59f068f0892f'
    c=intraday.chart(apiToken=api, output='raw', symbolId=sym)
    x=time()
    if x in c.keys():
        a = c[x]
        xclose = a['close']
        xhigh = a['high']
        xlow = a['low']
        xopen = a['open']
        xunit = a['unit']
        xvolume = a['volume']
        xx=[xopen,xhigh,xlow,xclose,xunit,xvolume]
        return xx
    else:
        return '非股票開盤時間'
    
    
def quote(sym):
    api='b71c49b4c7925bb66e6f59f068f0892f'
    c=intraday.quote(apiToken=api, output='raw', symbolId = sym)

    isOpenDelayed = c['isOpenDelayed'] #當日是否曾發生延後開盤
    isCloseDelayed = c['isCloseDelayed'] #當日是否曾發生延後收盤
    isClosed = c['isClosed'] #當日是否為已收盤
    isHalting = c['isHalting'] #最近一次更新是否為暫停交易
    isCurbing = c['isCurbing'] #最近一次更新是否為熔斷
    isTrial = c['isTrial'] #最近一次更新是否為試算


    total = c['total'] 
    t_unit = c['total']['unit'] #總成交張數
    t_volume = c['total']['volume'] #總成交量
    priceHigh = c['priceHigh']['price'] #當日之最高價
    priceLow = c['priceLow']['price'] #當日之最低價
    priceOpen = c['priceOpen']['price'] #當日之開盤價

    trial = c['trial'] #最新一筆試撮
    trade = c['trade'] #最新一筆成交
    if c['order']['bestAsks'] ==[]:
        bestAsks = 'None'
    else:
        bestAsks = c['order']['bestAsks']
        
    if c['order']['bestBids'] ==[]:
        bestBids = 'None'
    else:
        bestBids = c['order']['bestBids']
    
    
    x = [isOpenDelayed , isCloseDelayed ,isClosed , isHalting , isCurbing,
        isTrial]
    y = [t_unit , t_volume , priceHigh , priceLow ,priceOpen]
    z = [trial , trade , bestAsks , bestBids]
    
    return x,y,z



@app.route('/hook', methods=['POST'])
def webhook_handler():#接收訊息
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

## reply message
def reply_handler(bot, update):#回覆訊息
    text = update.message.text
    user_id = update.message.from_user.name
    
    if text[0] == '1':
        text = text[2:6]
        x = meta(text)
        a,b,c = quote(text)
        update.message.reply_text('股票中文簡稱：'+ x[0]+
                                      '\n產業別：'+ x[1]+
                                      '\n\n股票類別：'+ x[2] +
                                      '\n是否為指數：'+str(x[3])+
                                      '\n是否為權證：'+ str(x[4])+
                                      '\n今日是否暫停買賣：'+ str(x[5])+
                                      '\n今日是否已終止上市：'+ str(x[6]) +
                                      '\n\n漲停價：'+ str(x[7]) +
                                      '\n跌停價：'+ str(x[8]) +
                                      '\n今日參考價：'+ str(x[9]) +
                                      '\n\n是否可先買後賣現股當沖：'+ str(x[10]) +
                                      '\n是否可先賣後買現股當沖：'+str( x[11]) +
                                      '\n是否豁免平盤下融券賣出：'+ str(x[12]) +
                                      '\n是否豁免平盤下借券賣出：'+ str(x[13]) +
                                      '\n\n當日是否曾發生延後開盤：'+ str(a[0]) +
                                      '\n當日是否曾發生延後收盤：'+ str(a[1]) +
                                      '\n當日是否為已收盤：'+ str(a[2]) +
                                      '\n最近一次更新是否為暫停交易：'+ str(a[3]) +
                                      '\n最近一次更新是否為熔斷：'+ str(a[4]) +
                                      '\n最近一次更新是否為試算：'+ str(a[5])
                                     )
        
    elif text[0] == '2':
        text = text[2:6]
        x = chart(text)
        a,b,c = quote(text)
        if x == '非股票開盤時間':
            update.message.reply_text('非股票開盤時間')
        else:
            update.message.reply_text('此分鐘的開盤價'+ str(x[0])+
                                        '\n此分鐘的最高價：'+ str(x[1])+
                                        '\n此分鐘的最低價：'+ str(x[2])+
                                        '\n此分鐘的收盤價：'+ str(x[3])+
                                        '\n\n此分鐘的交易張數：'+str(x[4])+
                                        '\n此分鐘的交易量：'+str(x[5])+
                                        '\n\n最新一筆試撮：'+str(c[0])+
                                        '\n最新一筆成交：'+str(c[1])+
                                        '\n最新一筆最佳五檔 bestAsks：'+str(c[2])+
                                        '\n最新一筆最佳五檔 bestBids：'+str(c[3])
                                     )
            
    elif text[0] == '3':
        text = text[2:6]
        a,b,c = quote(text)
        update.message.reply_text('\n總成交張數：'+ str(b[0])+
                                  '\n總成交量：'+ str(b[1])+
                                  '\n\n當日之最高價：'+str(b[2])+
                                  '\n當日之最低價：'+str(b[3])+
                                  '\n當日之開盤價：'+str(b[4])
                                 )
        
    elif text[0] == '4':
        update.message.reply_text('hi hi hi!!!')
    
    else:
        update.message.reply_text('需要什麼服務？\n'+
                                 '範例：\n'+
                                 '輸入 {1 股票代碼}: 查詢個股資訊\n'+
                                 '輸入 {2 股票代碼}: 查詢個股即時交易資料\n'+
                                 '輸入 {3 股票代碼}: 查詢個股當日交易資料\n'
                                 )
        
        
        

    
    
# This class dispatches all kinds of updates to its registered handlers.
dispatcher = Dispatcher(bot, None)#管理所有設立的handler
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == '__main__':
    app.run()


# # [簡化版本]

# In[11]:


# Initial Flask app
# coding: utf-8
from fugle_realtime_restful_api import *
import datetime

app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=config['TELEGRAM']['ACCESS_TOKEN'])
def meta(sym):
    api='b71c49b4c7925bb66e6f59f068f0892f'
    c=intraday.meta(apiToken=api, output='raw', symbolId=sym)
    
    nameZhTw = c['nameZhTw']#股票中文簡稱
    industryZhTw = c['industryZhTw'] #產業別

    typeZhTw = c['typeZhTw']#股票類別
    isIndex = c['isIndex'] #是否為指數
    isWarrant = c['isWarrant']#是否為權證
    isSuspended = c['isSuspended'] #今日是否暫停買賣
    isTerminated = c['isTerminated']#今日是否已終止上市

    priceHighLimit = c['priceHighLimit']#漲停價
    priceLowLimit = c['priceLowLimit']#跌停價
    priceReference = c['priceReference']#今日參考價

    canDayBuySell = c['canDayBuySell'] #是否可先買後賣現股當沖
    canDaySellBuy = c['canDaySellBuy'] #是否可先賣後買現股當沖
    canShortLend = c['canShortLend']   #是否豁免平盤下融券賣出
    canShortMargin = c['canShortMargin']#是否豁免平盤下借券賣出
    
    x=[nameZhTw,industryZhTw,
       typeZhTw,str(isIndex),str(isWarrant),str(isSuspended),str(isTerminated),
       priceHighLimit,priceLowLimit,priceReference,
       str(canDayBuySell),str(canDaySellBuy),str(canShortLend),str(canShortMargin)]
    return x


def chart(sym):
    def time():
        x = datetime.datetime.now()
        x = x - datetime.timedelta(minutes=1)
        x = x - datetime.timedelta(hours=8)
        a1 = x.year 
        a2 = x.month 
        a3 = x.day 
        a4 = x.hour
        a5 = x.minute
        if a2 < 9 :
            a2 = '0'+str(a2)
        if a3 < 9 :
            a3 = '0'+str(a3)
        if a4 < 9 :
            a4 = '0'+str(a4)
        if a5 < 9 :
            a5 = '0'+str(a5)
        r =str(a1)+'-'+str(a2)+'-'+str(a3)+'T'+str(a4)+':'+str(a5)+':00.000Z'
        return r
    api='b71c49b4c7925bb66e6f59f068f0892f'
    c=intraday.chart(apiToken=api, output='raw', symbolId=sym)
    x=time()
    if x in c.keys():
        a = c[x]
        xclose = a['close']
        xhigh = a['high']
        xlow = a['low']
        xopen = a['open']
        xunit = a['unit']
        xvolume = a['volume']
        xx=[xopen,xhigh,xlow,xclose,xunit,xvolume]
        return xx
    else:
        return '非股票開盤時間'
    
    
def quote(sym):
    api='b71c49b4c7925bb66e6f59f068f0892f'
    c=intraday.quote(apiToken=api, output='raw', symbolId = sym)

    isOpenDelayed = c['isOpenDelayed'] #當日是否曾發生延後開盤
    isCloseDelayed = c['isCloseDelayed'] #當日是否曾發生延後收盤
    isClosed = c['isClosed'] #當日是否為已收盤
    isHalting = c['isHalting'] #最近一次更新是否為暫停交易
    isCurbing = c['isCurbing'] #最近一次更新是否為熔斷
    isTrial = c['isTrial'] #最近一次更新是否為試算


    total = c['total'] 
    t_unit = c['total']['unit'] #總成交張數
    t_volume = c['total']['volume'] #總成交量
    priceHigh = c['priceHigh']['price'] #當日之最高價
    priceLow = c['priceLow']['price'] #當日之最低價
    priceOpen = c['priceOpen']['price'] #當日之開盤價

    trial = c['trial'] #最新一筆試撮
    trade = c['trade'] #最新一筆成交
    if c['order']['bestAsks'] ==[]:
        bestAsks = 'None'
    else:
        bestAsks = c['order']['bestAsks']
        
    if c['order']['bestBids'] ==[]:
        bestBids = 'None'
    else:
        bestBids = c['order']['bestBids']
    
    
    x = [isOpenDelayed , isCloseDelayed ,isClosed , isHalting , isCurbing,
        isTrial]
    y = [t_unit , t_volume , priceHigh , priceLow ,priceOpen]
    z = [trial , trade , bestAsks , bestBids]
    
    return x,y,z



@app.route('/hook', methods=['POST'])
def webhook_handler():#接收訊息
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

## reply message
def reply_handler(bot, update):#回覆訊息
    text = update.message.text
    user_id = update.message.from_user.name
    
    if text[0] == '1':
        text = text[2:6]
        x = meta(text)
        #a,b,c = quote(text)
        update.message.reply_text('股票中文簡稱：'+ x[0]+
                                      '\n產業別：'+ x[1]+
                                      '\n\n股票類別：'+ x[2] +
                                      '\n是否為指數：'+str(x[3])+
                                      '\n是否為權證：'+ str(x[4])+
                                      '\n今日是否暫停買賣：'+ str(x[5])+
                                      '\n今日是否已終止上市：'+ str(x[6]) +
                                      '\n\n漲停價：'+ str(x[7]) +
                                      '\n跌停價：'+ str(x[8]) +
                                      '\n今日參考價：'+ str(x[9]) +
                                      '\n\n是否可先買後賣現股當沖：'+ str(x[10]) +
                                      '\n是否可先賣後買現股當沖：'+str( x[11]) +
                                      '\n是否豁免平盤下融券賣出：'+ str(x[12]) +
                                      '\n是否豁免平盤下借券賣出：'+ str(x[13])
                                     )
        
    elif text[0] == '2':
        text = text[2:6]
        x = chart(text)
        #a,b,c = quote(text)
        if x == '非股票開盤時間':
            update.message.reply_text('非股票開盤時間')
        else:
            update.message.reply_text('此分鐘的開盤價：'+ str(x[0])+
                                        '\n此分鐘的最高價：'+ str(x[1])+
                                        '\n此分鐘的最低價：'+ str(x[2])+
                                        '\n此分鐘的收盤價：'+ str(x[3])+
                                        '\n\n此分鐘的交易張數：'+str(x[4])+
                                        '\n此分鐘的交易量：'+str(x[5]))
            
    elif text[0] == '3':
        text = text[2:6]
        a,b,c = quote(text)
        update.message.reply_text('\n總成交張數：'+ str(b[0])+
                                  '\n總成交量：'+ str(b[1])+
                                  '\n\n當日之最高價：'+str(b[2])+
                                  '\n當日之最低價：'+str(b[3])+
                                  '\n當日之開盤價：'+str(b[4]))
        
    elif text[0] == '4':
        update.message.reply_text('hi !!!')
    
    else:
        update.message.reply_text('需要什麼服務？\n'+
                                 '範例：\n'+
                                 '輸入 {1 股票代碼}: 查詢個股資訊\n'+
                                 '輸入 {2 股票代碼}: 查詢個股即時交易資料\n'+
                                 '輸入 {3 股票代碼}: 查詢個股當日交易資料\n'
                                 )
        
        
        

    
    
# This class dispatches all kinds of updates to its registered handlers.
dispatcher = Dispatcher(bot, None)#管理所有設立的handler
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == '__main__':
    app.run()


# In[ ]:


# Initial Flask app
# coding: utf-8
from fugle_realtime_restful_api import *
import datetime

app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=config['TELEGRAM']['ACCESS_TOKEN'])
def meta(sym):
    api='b71c49b4c7925bb66e6f59f068f0892f'
    c=intraday.meta(apiToken=api, output='raw', symbolId=sym)
    
    nameZhTw = c['nameZhTw']#股票中文簡稱
    industryZhTw = c['industryZhTw'] #產業別

    typeZhTw = c['typeZhTw']#股票類別
    isIndex = c['isIndex'] #是否為指數
    isWarrant = c['isWarrant']#是否為權證
    isSuspended = c['isSuspended'] #今日是否暫停買賣
    isTerminated = c['isTerminated']#今日是否已終止上市

    priceHighLimit = c['priceHighLimit']#漲停價
    priceLowLimit = c['priceLowLimit']#跌停價
    priceReference = c['priceReference']#今日參考價

    canDayBuySell = c['canDayBuySell'] #是否可先買後賣現股當沖
    canDaySellBuy = c['canDaySellBuy'] #是否可先賣後買現股當沖
    canShortLend = c['canShortLend']   #是否豁免平盤下融券賣出
    canShortMargin = c['canShortMargin']#是否豁免平盤下借券賣出
    
    x=[nameZhTw,industryZhTw,
       typeZhTw,str(isIndex),str(isWarrant),str(isSuspended),str(isTerminated),
       priceHighLimit,priceLowLimit,priceReference,
       str(canDayBuySell),str(canDaySellBuy),str(canShortLend),str(canShortMargin)]
    return x


def chart(sym):
    def time():
        x = datetime.datetime.now()
        x = x - datetime.timedelta(minutes=1)
        x = x - datetime.timedelta(hours=8)
        a1 = x.year 
        a2 = x.month 
        a3 = x.day 
        a4 = x.hour
        a5 = x.minute
        if a2 <= 9 :
            a2 = '0'+str(a2)
        if a3 <= 9 :
            a3 = '0'+str(a3)
        if a4 <= 9 :
            a4 = '0'+str(a4)
        if a5 <= 9 :
            a5 = '0'+str(a5)
        r =str(a1)+'-'+str(a2)+'-'+str(a3)+'T'+str(a4)+':'+str(a5)+':00.000Z'
        return r
    api='b71c49b4c7925bb66e6f59f068f0892f'
    c=intraday.chart(apiToken=api, output='raw', symbolId=sym)
    x=time()
    if x in c.keys():
        a = c[x]
        xclose = a['close']
        xhigh = a['high']
        xlow = a['low']
        xopen = a['open']
        xunit = a['unit']
        xvolume = a['volume']
        xx=[xopen,xhigh,xlow,xclose,xunit,xvolume]
        return xx
    else:
        return '非股票開盤時間'
    
    
def quote(sym):
    api='b71c49b4c7925bb66e6f59f068f0892f'
    c=intraday.quote(apiToken=api, output='raw', symbolId = sym)

    isOpenDelayed = c['isOpenDelayed'] #當日是否曾發生延後開盤
    isCloseDelayed = c['isCloseDelayed'] #當日是否曾發生延後收盤
    isClosed = c['isClosed'] #當日是否為已收盤
    isHalting = c['isHalting'] #最近一次更新是否為暫停交易
    isCurbing = c['isCurbing'] #最近一次更新是否為熔斷
    isTrial = c['isTrial'] #最近一次更新是否為試算


    total = c['total'] 
    t_unit = c['total']['unit'] #總成交張數
    t_volume = c['total']['volume'] #總成交量
    priceHigh = c['priceHigh']['price'] #當日之最高價
    priceLow = c['priceLow']['price'] #當日之最低價
    priceOpen = c['priceOpen']['price'] #當日之開盤價

    trial = c['trial'] #最新一筆試撮
    trade = c['trade'] #最新一筆成交
    if c['order']['bestAsks'] ==[]:
        bestAsks = 'None'
    else:
        bestAsks = c['order']['bestAsks']
        
    if c['order']['bestBids'] ==[]:
        bestBids = 'None'
    else:
        bestBids = c['order']['bestBids']
    
    
    x = [isOpenDelayed , isCloseDelayed ,isClosed , isHalting , isCurbing,
        isTrial]
    y = [t_unit , t_volume , priceHigh , priceLow ,priceOpen]
    z = [trial , trade , bestAsks , bestBids]
    
    return x,y,z



@app.route('/hook', methods=['POST'])
def webhook_handler():#接收訊息
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

## reply message
def reply_handler(bot, update):#回覆訊息
    text = update.message.text
    user_id = update.message.from_user.name
    
    if text[0] == '1':
        text = text[2:6]
        x = meta(text)
        a,b,c = quote(text)
        update.message.reply_text('股票中文簡稱：'+ x[0]+
                                      '\n產業別：'+ x[1]+
                                      '\n\n股票類別：'+ x[2] +
                                      '\n是否為指數：'+str(x[3])+
                                      '\n是否為權證：'+ str(x[4])+
                                      '\n今日是否暫停買賣：'+ str(x[5])+
                                      '\n今日是否已終止上市：'+ str(x[6]) +
                                      '\n\n漲停價：'+ str(x[7]) +
                                      '\n跌停價：'+ str(x[8]) +
                                      '\n今日參考價：'+ str(x[9]) +
                                      '\n\n是否可先買後賣現股當沖：'+ str(x[10]) +
                                      '\n是否可先賣後買現股當沖：'+str( x[11]) +
                                      '\n是否豁免平盤下融券賣出：'+ str(x[12]) +
                                      '\n是否豁免平盤下借券賣出：'+ str(x[13]) +
                                      '\n\n當日是否曾發生延後開盤：'+ str(a[0]) +
                                      '\n當日是否曾發生延後收盤：'+ str(a[1]) +
                                      '\n當日是否為已收盤：'+ str(a[2]) +
                                      '\n最近一次更新是否為暫停交易：'+ str(a[3]) +
                                      '\n最近一次更新是否為熔斷：'+ str(a[4]) +
                                      '\n最近一次更新是否為試算：'+ str(a[5])
                                     )
        
    elif text[0] == '2':
        text = text[2:6]
        x = chart(text)
        a,b,c = quote(text)
        if x == '非股票開盤時間':
            update.message.reply_text('非股票開盤時間')
        else:
            update.message.reply_text('此分鐘的開盤價'+ str(x[0])+
                                        '\n此分鐘的最高價：'+ str(x[1])+
                                        '\n此分鐘的最低價：'+ str(x[2])+
                                        '\n此分鐘的收盤價：'+ str(x[3])+
                                        '\n\n此分鐘的交易張數：'+str(x[4])+
                                        '\n此分鐘的交易量：'+str(x[5]))
            
    elif text[0] == '3':
        text = text[2:6]
        a,b,c = quote(text)
        update.message.reply_text('\n總成交張數：'+ str(b[0])+
                                  '\n總成交量：'+ str(b[1])+
                                  '\n\n當日之最高價：'+str(b[2])+
                                  '\n當日之最低價：'+str(b[3])+
                                  '\n當日之開盤價：'+str(b[4])
                                 )
        
    elif text[0] == '4':
        update.message.reply_text('hi hi hi!!!')
    
    else:
        update.message.reply_text('需要什麼服務？\n'+
                                 '範例：\n'+
                                 '輸入 {1 股票代碼}: 查詢個股資訊\n'+
                                 '輸入 {2 股票代碼}: 查詢個股即時交易資料\n'+
                                 '輸入 {3 股票代碼}: 查詢個股當日交易資料\n'
                                 )
        
        
        

    
    
# This class dispatches all kinds of updates to its registered handlers.
dispatcher = Dispatcher(bot, None)#管理所有設立的handler
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == '__main__':
    app.run()


# In[ ]:



   

