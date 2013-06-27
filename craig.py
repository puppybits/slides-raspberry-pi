#! /usr/bin/python
#
# archstone walnut creek / sat: 9-5 / $1700 / 65 min / 6 school / http://www.archstoneapartments.com/Apartments/California/Northern_California/Archstone_Walnut_Creek/Amenities2.htm
# berkly house / $2250 / 55 min / ? school / http://sfbay.craigslist.org/eby/apa/3601648089.html
#
#
# libs: PyQuery, requests, twilio and lxml
# sudo pip install PyQuery && sudo pip install requests && sudo pip install twilio && sudo pip install lxml
#
import os.path
import smtplib
from lxml import html
import unicodedata
from pyquery import PyQuery as query
import json, os, sys, time
import datetime
import requests
import sched, time
from twilio.rest import TwilioRestClient

password = ''
 
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

f               = '' # file storage for json
crapy_JSON_db   = ''.join([os.path.expanduser('~'),'/.craigslist.json'])

TWILIO_SID      = 'ACca08db03c04d8f29cbd885288c83b847'
TWILIO_TOKEN    = '35da804d73fe9dcf0b314749bd7078a0'
TWILIO_NUMBER   = '+14253744213'
MY_PHONE        = '+14254050516'

url             = 'sfbay.craigslist.org/search/apa/eby'
# url             = 'sfbay.craigslist.org/search/apa/sfc'
min             = '&minAsk='
max             = '&maxAsk='
rooms           = '&bedrooms=2'
dog             = '&addThree=wooof'
# findapturl      = 'http://%s?srchType=A&zoomToPosting=&altView=&query=%s%s%s%s' % (url,min,max,rooms,dog)
findapturl      = 'http://%s?zoomToPosting=&altView=&query=&srchType=A%s%s%s%s' % (url,min,max,rooms,dog)

print findapturl
maxSMSRent      = 2800

sleeptime       = 60 # seconds

# districts       = {'alamo square / nopa'            : 'nopa',
#                     'bernal heights'                : 'brnl',
#                     'castro / upper market'         : 'csto',
#                     'cole valley / ashbury hts'     : 'ashb',
#                     'haight ashbury'                : 'hght',
#                     'inner sunset / UCSF'           : 'isun',
#                     'inner richmond'                : 'irch',
#                     'lower haight'                  : 'lhgt',
#                     'nob hill'                      : 'nobh',
#                     'noe valley'                    : 'noev',
#                     'mission district'              : 'misn',
#                     'north beach / telegraph hill'  : 'nbch',
#                     'russian hill'                  : 'rusn',
#                     'twin peaks / diamond hts'      : 'peak',
#                     'SOMA / south beach'            : 'soma'}
                    
                    
districts        = {'alameda'                             : 'almd',
                    'berkeley'                            : 'bkly',
                    'berkeley north / hills'              : 'bkhl',
                    # 'concord / pleasant hill / martinez'  : 'cnrd',
                    # 'lafayette / orinda / moraga'         : 'ornd',
                    'oakland hills / mills'               : 'okhl',
                    'walnut creek'                        : 'wall'}


validationDistrict = {'inner sunset / UCSF'         : [37.767797, -122.485886, 37.738186, -122.442541],
                    'haight ashbury'                : [37.773971, -122.456703, 37.760266, -122.434216],
                    'north beach / telegraph hill'  : [37.806393, -122.427006, 37.798798, -122.395420]}
                   # 'sf'                           : [37.802731, -122.522621, 37.706640, -122.361259]}



def date_encoder(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return 

def email(body, subject, recipient):
    sender = 'puppybits@gmail.com'
    
    body = "" + body.encode('ascii','ignore') + ""

    headers = ["From: " + sender,
               "Subject: " + subject,
               "To: " + recipient,
               "MIME-Version: 1.0",
               "Content-Type: text/html"]
    headers = "\r\n".join(headers)
 
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
 
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, password)
 
    session.sendmail(sender, recipient, headers + "\r\n\r\n" + body)
    session.quit()

def notify(body, delay=0, sound=False, userInfo={}):
    client  = TwilioRestClient(TWILIO_SID, TWILIO_TOKEN)
    num     = TWILIO_NUMBER
    to      = MY_PHONE
    
    print body[0:160]
    message = client.sms.messages.create(to=to, from_=num, body=body[0:160])

def in_district():
    for item in this:
        for c in districts.keys():
            if c in html.tostring(item):
                return True
    return False

def parse_item(i):
    d = {}
    q = query(i)
    
    d['lat'] = float(q.attr('data-latitude')) if len(q.attr('data-latitude')) > 1 else ''
    d['lng'] = float(q.attr('data-longitude')) if len(q.attr('data-longitude')) > 1 else ''
    d['postdata'] = q.find('.itemdate').text()
    d['price'] = q.find('.itemph').text().split(' ')[0]
    d['title'] = q.find('a').text()
    d['link'] = q.find('a').attr('href')
    
    # print d['title']
    
    d['district'] = ''
    district = q.find('.itempn').find('font').text()
    if district is not None and district is not "":
        for dis in districts.keys():
            if dis in district:
                d['district'] = districts[dis]
                break
    
    for k in validationDistrict.keys():
        r = validationDistrict[k]
        # print '%s > %s > %s' % (r[0], d['lat'], r[2])
        if r[0] > d['lat'] and d['lat'] > r[2]:
            # print '  %s > %s > %s' % (r[1], d['lng'], r[3])
            if r[1] < d['lng'] and d['lng'] < r[3]:
                d['district'] = districts[k]
                # print '%s %s - %s [%s]' % (k, d['price'], d['title'], d['link'])
    
    return d if d['district'] is not '' else None



def main(sc):
    q = query(findapturl)
    print 'starting: %s' % (q('p').eq(0).find('.itemph').text())
    
    geo = q('*[data-latitude]').filter(lambda i: query(this).attr('data-latitude') != '')
    district = q('p').filter(lambda i: query(this).find('.itempn').each(in_district))
    
    results = []
    resultNodes = geo + district
    for item in resultNodes:
        obj = parse_item(item)
        if obj:
            results.append( obj )
    
    f = open(''.join([os.path.expanduser('~'),'/.craigslist.json']), 'r+')
    for item in results:
        if len(item['link']) > 1 and item['link'] not in data:
            print item['price']
            try:
                cost = int(item['price'].replace('$',''))
            except:
                continue
            
            if cost < maxSMSRent:
                shortened = requests.get('http://is.gd/create.php?format=simple&url=%s' % (item['link']))
                # notify( '%s [%s] %s %s' % (item['price'], item['district'], shortened.text, item['title']) )
                
                page = requests.get(item['link'])
                email(page.text, item['link'], 'puppybits@gmail.com')
                # email(page.text, item['link'], 'm.laura.schultz@gmail.com')
                
            item['added'] = datetime.datetime.now()
            data[item['link']] = item
    
    
    f = open(''.join(crapy_JSON_db), 'w')
    f.write(json.dumps(data, indent=4, default=date_encoder))
    f.close()
    
    sc.enter(sleeptime, 1, main, (sc,))
    
if __name__ == "__main__":
    
    
    if not os.path.isfile(crapy_JSON_db):
        f = open(temp_path, 'w')
        f.write('{}')
        f.close()

    f = open(crapy_JSON_db, 'r+')
    jsonstring = f.read()
    data = json.loads(jsonstring)
    f.close()
    
    s = sched.scheduler(time.time, time.sleep)
    s.enter(1, 1, main, (s,))
    s.run()
    
    

#  alamo square / nopa
#  bayview
#  bernal heights
#  castro / upper market
#  cole valley / ashbury hts
#  downtown / civic / van ness
#  excelsior / outer mission
#  financial district
#  glen park
#  haight ashbury
#  hayes valley
#  ingleside / SFSU / CCSF
#  inner richmond
#  inner sunset / UCSF
#  laurel hts / presidio
#  lower haight
#  lower nob hill
#  lower pac hts
#  marina / cow hollow
#  mission district
#  nob hill
#  noe valley
#  north beach / telegraph hill
#  pacific heights
#  portola district
#  potrero hill
#  richmond / seacliff
#  russian hill
#  SOMA / south beach
#  sunset / parkside
#  tenderloin
#  treasure island
#  twin peaks / diamond hts
#  USF / panhandle
#  visitacion valley
#  west portal / forest hill
#  western addition