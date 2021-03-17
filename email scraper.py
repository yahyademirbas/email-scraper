#!/usr/bin/env python
# coding: utf-8

# In[1]:


import aiohttp
import asyncio
import async_timeout


import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urlparse, urljoin
import time
import sys
from termcolor import cprint
nest_asyncio.apply()


# In[2]:

#Required Inputs:
ExcelFilePathHere = "" //file path
ExcelSheetNameHere = "United States"
ColumnNameInExcelSheetThatHasTheWebLinks = "Website"

SourceData = pd.read_excel(ExcelFilePathHere, ExcelSheetNameHere, index_col=None, na_values=['NA'])
SourceData.fillna("NoResultCell", inplace=True)
WebsitesToBeScrapedForEmails = SourceData[ColumnNameInExcelSheetThatHasTheWebLinks].tolist()


# In[4]:


#-----------Globals------------#

mails = [];
inp = [];
allLinks = []

#-----------Request URL------------#

async def fetch(session, url):
    with async_timeout.timeout(60):
        async with session.get(url) as response:
            assert response.status == 200
            return await response.text()

async def soup_d(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup
    
#-----------Search For E-Mail Addresses------------#

async def findMails(soup, url):
    global inp
    global mails
    for name in soup.find_all('a'):
        
        if(name is not None):
            emailText=name.text
            match=bool(re.match('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',emailText))
            
            if('@' in emailText and match==True):
                emailText=emailText.replace(" ",'').replace('\r','')
                emailText=emailText.replace('\n','').replace('\t','')
                
                if(len(mails) == 0)or(emailText not in mails):
                    print(emailText)
                
                mails.append(emailText)
                inp.append({'domain': urlparse(url).netloc, 'email': emailText })

#-----------Main Function is the One Below------------#

async def main(raw_url):
    global mails
    global inp
    global allLinks
    
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False, limit=25, limit_per_host=5),
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36"}
    ) as session:
        start_time = time.time()
        print("Please wait. We are collecting links from your list of websites.")
        for i in range(len(raw_url)): 
            url = urlparse(raw_url[i]).scheme +"://"+ urlparse(raw_url[i]).netloc +"/"
            print("Parsed Website URLs.")
            try:
                html = await fetch(session, url)
                
                soup = await soup_d(html)
                
            except asyncio.TimeoutError:
                pass
            except Exception as exc:
                print(f'The coroutine raised an exception: {exc!r}')
                pass
            links = [a.attrs.get('href') for a in soup.select('a[href]')]
            
            for i in links:
                allLinks.append(i)
        allLinks=set(allLinks)
        a=((5*len(allLinks))/60)
        b=len(allLinks)
        c=len(raw_url)
        print("Found"+" "+str(b)+" "+"links from"+" "+str(c)+" "+"websites.")
        time.sleep(3)
        print("The process will start in 10 seconds and will take around"+" "+str(a)+" "+"minutes.")
        time.sleep(10)
        processed = []
        for link in allLinks:
            
            start_ = time.time()
            if(link.startswith("http") or link.startswith("www") or link.startswith("https")):
                print(link)
                try:
                    data= await fetch(session, link)
                    soup= await soup_d(data)
                except Exception as exc:
                    print(f'The coroutine raised an exception: {exc!r}')
                    pass
                await findMails(soup, link) 
                processed.append(link)
            else:
                if(link.startswith("/")):
                    link = link[1:]
                if(link.startswith("./")):
                    link = link[2:]
                newurl = url+link
                print(newurl)
                try:
                    data= await fetch(session, newurl)
                    soup= await soup_d(data)
                except Exception as exc:
                    print(f'The coroutine raised an exception: {exc!r}')
                    pass
                await findMails(soup, newurl)
                processed.append(newurl)
            
            d = ((5*(len(allLinks)-len(processed)))/60)
            e = (len(allLinks)-len(processed))
            cprint("Found"+" "+str(len(mails))+" "+"until now", 'magenta', 'on_yellow')
            cprint(str(e)+" "+"links left.", 'green', 'on_red')
            print()
            cprint("Time Left:"+" "+str(d)+" "+"minutes", 'white', 'on_blue')
            print(time.time() - start_, "seconds")
    time.sleep(3)
    print("Tasks Completed!")
    mails=set(mails)
    time.sleep(3)
    print("Total of"+" "+str(len(mails))+" "+"found.")
    df = pd.DataFrame(inp)
    time.sleep(3)
    print("Writing data to CSV file.")
    df.to_csv(r'C:/Users/Yahya/Desktop/locksbridge/output.csv', index = False, header=True)
    time.sleep(3)
    print("Entire process took", time.time()-start_time, "seconds")
    time.sleep(3)
    print("Done. See you next time! Do not forget to change the output file name, otherwise it will overwrite the previous file!")    
loop = asyncio.get_event_loop()
#-----------
try:
    loop.run_until_complete(main(WebsitesToBeScrapedForEmails))
except Exception as exc:
    print(f'The coroutine raised an exception: {exc!r}')
    pass

# Modify the code above with the correct inputs before running the script.
# The coroutine sometimes raises exceptions which you might be able to debug. Good Luck!


# In[ ]:





# In[ ]:




