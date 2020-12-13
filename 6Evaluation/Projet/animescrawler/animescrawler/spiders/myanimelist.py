import scrapy
from scrapy import Request
from animescrawler.items import AnimeItem


class MyanimelistSpider(scrapy.Spider):
    name = 'myanimelist'
    allowed_domains = ['myanimelist.net']
    start_urls = ['http://myanimelist.net/anime.php',]
    handle_httpstatus_list = [403]
    #download_delay=1

    def parse(self, response):
        menu_index_links = set(response.css("#horiznav_nav").css("a::attr(href)").extract())
        #yield {"menu_index":menu_index_links}
        for index_link in menu_index_links:
            yield Request(index_link,callback=self.parse_index_links)

    def parse_index_links(self, response):
        nb_page = int(response.css(".normal_header").css("a::text").extract()[-1])
        last_link_page = response.urljoin(response.css(".normal_header").css("a::attr(href)").extract()[-1]) 
        link_common_part = last_link_page.replace("show="+str((nb_page-1)*50),"show=")
        all_page_links = [ link_common_part+str(i) for i in range(0,nb_page*50,50)]
        #yield {"all_page_links":all_page_links}
        for page_link in all_page_links:
            yield Request(page_link,callback=self.parse_page_links)
       
    def parse_page_links(self,response):
        all_anime_links = set(response.css(".hoverinfo_trigger").css("a::attr(href)").extract())
        #yield {"all_anime_links":all_anime_links}
        for anime_link in all_anime_links:
            yield Request(anime_link,callback=self.parse_anime_links)

    def parse_anime_links(self,response):
        border = response.xpath("//div[@style='width: 225px']")
        
        divs= [div for div in border.css("div") if div.css("span::text").extract_first() in ["Duration:","Rating:","Type:"]]
        border_infos=dict([(div.css("span::text").extract_first(),div.css("::text").extract()[-1])for div in divs])

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
            duration=border_infos["Duration:"],
            rating= border_infos["Rating:"]
        )