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
        yield AnimeItem(
            main_title = response.css("h1").css("strong::text").extract_first(),
            other_titles = response.xpath("//div[@style='width: 225px']/div[@class='spaceit_pad']/text()").extract(),
            score = response.css(".score-label::text").extract_first(),
            synopsis = response.css("td").css("p::text").extract_first(),
            ranked_popularity = response.css(".di-ib").css("strong::text").extract(),
            genres = response.xpath("//span[@itemprop='genre']/text()").extract(),
            producers = response.xpath("//div[@style='width: 225px']").xpath("//a[contains(@href,'/anime/producer')]/text()").extract(),
            Type = response.xpath("//div[@style='width: 225px']").xpath('//a[contains(@href,"//myanimelist.net/topanime.php?type=")]/text()').extract_first(),
            related_anime = {
            "table":response.xpath("//table[@class='anime_detail_related_anime']/tr/td").extract(),
            "rownames":response.xpath("//table[@class='anime_detail_related_anime']/tr/td/text()").extract(),
            "names":response.xpath("//table[@class='anime_detail_related_anime']/tr/td/a/text()").extract()
            },
            duration_rating = response.xpath("//div[@style='width: 225px']/div/text()").extract()
        )

