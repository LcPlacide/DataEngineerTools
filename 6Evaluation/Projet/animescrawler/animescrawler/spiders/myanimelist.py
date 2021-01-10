import scrapy
from scrapy import Request
from animescrawler.items import AnimeItem
from animescrawler.utils import get_random_agent
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
from os import uname

class MyanimelistSpider(scrapy.Spider):
    name = 'myanimelist'
    allowed_domains = ['myanimelist.net']
    start_urls = ['http://myanimelist.net/anime.php',]
    handle_httpstatus_list = [403,404]

    def __init__(self, *args, **kwargs):
        """
        Initialisation des variables utilisés
        pour résoudre d'éventuels captcha
        """
        super(MyanimelistSpider, self).__init__(*args, **kwargs)
        self.CAPTCHA_DETECTION=True
        self.browser= webdriver.Remote("http://selenium:4444/wd/hub", DesiredCapabilities.FIREFOX)
        self.retry={"MAX_RETRY":4}

    def parse(self, response):
        """
        Récupération dans start_urls[0] des url pointant
        sur les premières pages des indexs classant les animés
        (Upcomming,Just Added,#,A,...,Z)
        """
        if response.status in [403,404]:
            self.handle_error(response,0)
        elif response.status==200:
            self.CAPTCHA_DETECTION=True
            menu_index_links = set(response.css("#horiznav_nav").css("a::attr(href)").extract())
            for index_link in menu_index_links:
                yield Request(index_link,callback=self.parse_index_links,headers=get_random_agent())

    def parse_index_links(self, response):
        """
        Récupération dans les premières pages de chaque
        indexs des url pointant vers des pages complémentaires
        """
        if response.status in [403,404]:
            self.handle_error(response,1)
        elif response.status==200:
            self.CAPTCHA_DETECTION=True
            try:
                nb_page = int(response.css(".normal_header").css("a::text").extract()[-1])
                last_link_page = response.urljoin(response.css(".normal_header").css("a::attr(href)").extract()[-1]) 
                link_common_part = last_link_page.replace("show="+str((nb_page-1)*50),"show=")
                if nb_page%20==0 and find_page_nb(response.url,link_common_part)<find_page_nb(last_link_page,link_common_part):
                    yield Request(last_link_page,callback=self.parse_index_links,headers=get_random_agent())
                elif nb_page%20!=0:
                    all_page_links = [ link_common_part+str(i) for i in range(0,(nb_page)*50,50)]
                    for page_link in all_page_links:
                        yield Request(page_link,callback=self.parse_page_links,headers=get_random_agent())
                else:
                    all_page_links = [ link_common_part+str(i) for i in range(0,(nb_page+1)*50,50)]
                    for page_link in all_page_links:
                        yield Request(page_link,callback=self.parse_page_links,headers=get_random_agent())
            except IndexError:
                self.handle_error(response,1)
        
    def parse_page_links(self,response):
        """
        Récupération sur les pages de chaque index des url 
        pointant vers les page spécifiques à chaque animés
        """
        if response.status in [403,404]:
            self.handle_error(response,2)
        elif response.status==200:
            self.CAPTCHA_DETECTION=True
            all_anime_links = set(response.css(".hoverinfo_trigger").css("a::attr(href)").extract())
            for anime_link in all_anime_links:
                yield Request(anime_link,callback=self.parse_anime_links,headers=get_random_agent())

    def parse_anime_links(self,response):
        """
        Récupération sur les pages spécifiques à chaque animé
        des informations utiles pour construire le AnimeItems
        """
        if response.status in [403,404]:
            self.handle_error(response,3)
        elif response.status==200:
            self.CAPTCHA_DETECTION=True
            border = response.xpath("//div[@style='width: 225px']")
            
            border_infos=dict([(key,None) for key in ["Duration:","Rating:","Type:","Episodes:","Status:","Aired:","Premiered:"]])
            divs= [div for div in border.css("div") if div.css("span::text").extract_first() in border_infos.keys()]
            for div in divs:
                key=div.css("span::text").extract_first()
                if key!="Premiered:":
                    border_infos[div.css("span::text").extract_first()]=div.css("::text").extract()[-1]
                else:
                    val=div.css("::text").extract()
                    val.remove(key)
                    border_infos[div.css("span::text").extract_first()]= "".join(val)
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
                producers = border.xpath("//a[contains(@href,'/anime/producer')]/text()").extract(),
                Type = border_infos["Type:"],
                related_anime = related_anime,
                episodes = border_infos["Episodes:"],
                status = border_infos["Status:"],
                duration = border_infos["Duration:"],
                rating = border_infos["Rating:"],
                aired = {"Aired:":border_infos["Aired:"],"Premiered:":border_infos["Premiered:"]},
                image = border.css("img::attr(data-src)").extract_first(),
                url = response.url
            )

    def handle_error(self,response,func_nb):
        """
        Traitement des erreurs 403 et 404:
        - Appel de la fonction détetant et résolvant les captchas
        - Planification de nouvelles tentatives de scraping pour
          les pages érronées
        """
        if response.status==403:
            print(5*"\n","CAPTCHA POTENTIELLEMENT ACTIF")
            self.captcha_solving(response)
        if response.url not in self.retry.keys():
            self.retry[response.url]=1
        if self.retry[response.url]<self.retry["MAX_RETRY"]:
            print("Echec de la tentative de scraping",self.retry[response.url],"de",response.url)
            self.retry[response.url]+=1
            print("Tentative",self.retry[response.url],"de scraping planifiée")
            if func_nb==0:
                return Request('http://myanimelist.net/anime.php',callback=self.parse)
            elif func_nb==1:
                return Request(response.url,callback=self.parse_index_links)
            elif func_nb==2:
                return Request(response.url,callback=self.parse_page_links)
            elif func_nb==3:
                return Request(response.url,callback=self.parse_anime_links)
        else:
            print("Nombre maximal d'essais (",self.retry["MAX_RETRY"],") atteint pour",response.url,"(url non scrapé)")
        return None

    def captcha_solving(self,response):
        """
        Détection et résolution de catcah sur le site à scraper
        via un navigateur distant commander par selenium
        """
        try:
            if self.CAPTCHA_DETECTION:
                self.CAPTCHA_DETECTION=False
                print("RESOLUTION DU CAPTCHA LANCEE",sep="\n")
                self.browser.get(response.url)
                button=self.browser.find_elements_by_xpath("//button[@type='submit'][@class='g-recaptcha']")[0]
                button.click()
                sleep(60)
                print("RESOLUTION TERMINEE",sep="\n")
                self.CAPTCHA_DETECTION=True
            else:
                print("RESOLUTION DU CAPTCHA EN COURS")
        except IndexError:
            return "CAPTCHA NON DETECTE, SITE ACCESSIBLE"
        return "SITE ACCESSIBLE DANS QUELQUES SECONDES"+5*"\n"

def find_page_nb(url,common_part):
    try:
        return int(url.replace(common_part,""))
    except ValueError:
        return 0