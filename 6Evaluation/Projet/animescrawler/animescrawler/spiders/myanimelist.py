import scrapy
from scrapy import Request
from animescrawler.items import AnimeItem
from animescrawler.utils import get_random_agent
from selenium import webdriver
from time import sleep
from os import uname

retry={}
MAX_RETRY=4
IS_LINUX = uname().sysname=="Linux"

class MyanimelistSpider(scrapy.Spider):
    name = 'myanimelist'
    allowed_domains = ['myanimelist.net']
    start_urls = ['http://myanimelist.net/anime.php',]
    handle_httpstatus_list = [403]

    def __init__(self, CAPTCHA_DETECTION=True, *args, **kwargs):
        super(MyanimelistSpider, self).__init__(*args, **kwargs)
        self.CAPTCHA_DETECTION=CAPTCHA_DETECTION

    def parse(self, response):
        if response.status==403:
            self.handle_403(response,0)
        elif response.status==200:
            self.CAPTCHA_DETECTION=True
            menu_index_links = set(response.css("#horiznav_nav").css("a::attr(href)").extract())
            for index_link in menu_index_links:
                yield Request(index_link,callback=self.parse_index_links,headers=get_random_agent())

    def parse_index_links(self, response):
        if response.status==403:
            self.handle_403(response,1)
        elif response.status==200:
            self.CAPTCHA_DETECTION=True
            try:
                nb_page = int(response.css(".normal_header").css("a::text").extract()[-1])
                last_link_page = response.urljoin(response.css(".normal_header").css("a::attr(href)").extract()[-1]) 
                link_common_part = last_link_page.replace("show="+str((nb_page-1)*50),"show=")
                all_page_links = [ link_common_part+str(i) for i in range(0,nb_page*50,50)]
                for page_link in all_page_links:
                    yield Request(page_link,callback=self.parse_page_links,headers=get_random_agent())
            except IndexError:
                self.handle_403(response,1)
        
    def parse_page_links(self,response):
        if response.status==403:
            self.handle_403(response,2)
        elif response.status==200:
            self.CAPTCHA_DETECTION=True
            all_anime_links = set(response.css(".hoverinfo_trigger").css("a::attr(href)").extract())
            for anime_link in all_anime_links:
                yield Request(anime_link,callback=self.parse_anime_links,headers=get_random_agent())

    def parse_anime_links(self,response):
        if response.status==403:
            self.handle_403(response,3)
        elif response.status==200:
            self.CAPTCHA_DETECTION=True
            border = response.xpath("//div[@style='width: 225px']")
            
            border_infos=dict([(key,None) for key in ["Duration:","Rating:","Type:","Episodes:","Status:"]])
            divs= [div for div in border.css("div") if div.css("span::text").extract_first() in border_infos.keys()]
            for div in divs:
                border_infos[div.css("span::text").extract_first()]=div.css("::text").extract()[-1]

            table= response.xpath("//table[@class='anime_detail_related_anime']/tr")
            related_anime= dict([(tr.css("td::text").extract_first().replace(":",""),tr.css("td a::text").extract()) for tr in table])

            yield AnimeItem(
                main_title = response.css("h1 strong::text").extract_first(),
                other_titles = border.xpath("//div[@class='spaceit_pad']/text()").extract(),
                score = response.css(".score-label::text").extract_first(),
                synopsis = response.xpath("//p[@itemprop='description']").css("::text").extract(),
                ranked = response.xpath("//div[@class='di-ib ml12 pl20 pt8']/span[@class='numbers ranked']/strong/text()").extract_first(),
                popularity = response.xpath("//div[@class='di-ib ml12 pl20 pt8']/span[@class='numbers popularity']/strong/text()").extract_first(),
                genres = response.xpath("//span[@itemprop='genre']/text()").extract(),
                producers=border.xpath("//a[contains(@href,'/anime/producer')]/text()").extract(),
                Type= border_infos["Type:"],
                related_anime=related_anime,
                episodes=border_infos["Episodes:"],
                status=border_infos["Status:"],
                duration=border_infos["Duration:"],
                rating= border_infos["Rating:"]
            )

    def handle_403(self,response,func_nb):
        print(5*"\n","CAPTCHA POTENTIELLEMENT ACTIF")
        self.captcha_solving(response)
        if response.url not in retry.keys():
            retry[response.url]=1
            print("PARSE",func_nb,":",response.url,"non scrapé")
        if retry[response.url]<MAX_RETRY:
            print("PARSE",func_nb,":","Echec de la tentative de scraping",retry[response.url],"de",response.url)
            retry[response.url]+=1
            if func_nb==0:
                print("PARSE 0: Tentative",retry[response.url],"de scraping planifiée")
                return Request('http://myanimelist.net/anime.php',callback=self.parse)
            elif func_nb==1:
                print("PARSE 1: Tentative",retry[response.url],"de scraping planifiée")
                return Request(response.url,callback=self.parse_index_links)
            elif func_nb==2:
                print("PARSE 2: Tentative",retry[response.url],"de scraping planifiée")
                return Request(response.url,callback=self.parse_page_links)
            elif func_nb==3:
                print("PARSE 3: Tentative",retry[response.url],"de scraping planifiée")
                return Request(response.url,callback=self.parse_anime_links)
        else:
            print("PARSE",func_nb,":","Nombre maximal d'essais (",MAX_RETRY,") atteint pour",response.url,"(url non scrapé)")
        return None

    def captcha_solving(self,response):
        try:
            if self.CAPTCHA_DETECTION:
                self.CAPTCHA_DETECTION=False
                print("OUVERTURE DE SELENIUM","RESOLUTION DU CAPTCHA LANCEE",sep="\n")
                chrome = webdriver.Chrome(executable_path="./chromedriver_mac" if not IS_LINUX else "./chromedriver_linux")
                chrome.get(response.url)
                button=chrome.find_elements_by_xpath("//button[@type='submit'][@class='g-recaptcha']")[0]
                button.click()
                sleep(30)
                print("RESOLUTION TERMINEE","FERMETURE DE SELENIUM",sep="\n")
                self.CAPTCHA_DETECTION=True
                chrome.close()
            else:
                print("RESOLUTION DU CAPTCHA EN COURS")
        except IndexError:
            return "CAPTCHA NON DETECTE, SITE ACCESSIBLE"
        return "SITE ACCESSIBLE DANS QUELQUES SECONDES"+5*"\n"