#!/usr/bin/env python
import sys
import re

import requests
import lxml.html


search = lambda x, pat: re.search(pat, x).group(0).strip() \
                        if re.search(pat, x) is not None \
                        else None


class UbuCollection(object):

    def __init__(self, collection_url):
        self.collection_url = collection_url
        self.request = requests.get(collection_url)
        self.phtml = lxml.html.fromstring(self.request.text)
        self.artist_urls = self.get_artist_urls()

    def get_artist_urls(self):
        return [self.collection_url + x[2].strip('./') \
                for x in self.phtml.iterlinks() \
                if x[2].startswith('./')]


class UbuArtist(object):
    
    def __init__(self, artist_url):
        self.artist_url = artist_url
        self.collection_url = '/'.join(artist_url.split('/')[:-1])
        self.request = requests.get(artist_url)
        self.phtml = lxml.html.fromstring(self.request.text)
        self.creator = self.phtml.xpath('//font[@color="#000"]/b/text()')[0]
        self.item_urls = self.get_item_urls()

    def get_item_urls(self):
        return [self.collection_url + '/' + x.getnext().attrib['href'] \
                for x in \
                self.phtml.xpath('//img[starts-with(@src, "../images/arrow")]') \
                if not x.getnext().attrib['href'].startswith('http://') and \
                not x.getnext().attrib['href'].startswith('../')]


class UbuItem(object):

    def __init__(self, item_url):
        self.item_url = item_url
        self.request = requests.get(item_url)
        self.phtml = lxml.html.fromstring(self.request.text)

    def get_metadata(self):

        pat = re.compile("""
                         (?<=\<\!--\ INSERT\ DESCRIPTION\ PARAGRAPHS\ HERE\ --\>)
                         .*
                         (?=\<\!--\ END\ DESCRIPTION\ PARAGRAPHS\ --\>)
                         """, re.VERBOSE|re.DOTALL)
        html = self.request.text
        description = search(html, pat)


        match = self.phtml.xpath('//a[re:match(@href, \
                                 "^http.*ubu.*\.(mp4|mpg|mpeg|wmv|mov|avi)$")]', \
                                 namespaces={"re": \
                                 "http://exslt.org/regular-expressions"})
        title = None
        date = None
        source = None
        if match != []:                                  
            source = match[0].attrib.get('href')
            title = match[0].text                              
            if title:                                               
                title = '('.join(match[0].text.split('(')[:-1])
                date = re.search('(19|20)\d{2}', match[0].text)
                if date:                                            
                    date = date.group(0)                            

        return {'date': date, 'title': title, 'source': source, 
                'description': description,
        }
