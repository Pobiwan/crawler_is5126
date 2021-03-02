import scrapy
import csv
import re
from ..items import CrawlerIs5126Item, CrawlerIs5126TeamItem
import logging
from scrapy.utils.log import configure_logging 


class BballSpider(scrapy.Spider):
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    header_written = {
        "2009/2010": False,
        "2010/2011": False,
        "2011/2012": False,
        "2012/2013": False,
        "2013/2014": False,
        "2014/2015": False,
        "2015/2016": False,
        "2016/2017": False,
        "2017/2018": False,
        "2018/2019": False,
        "2019/2020": False
    }
    name = "bballrefTeam"
    def start_requests(self):
        urls = [
            #'https://www.basketball-reference.com/leagues/NBA_2010_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2011_totals.html',
            'https://www.basketball-reference.com/leagues/NBA_2012_totals.html', 
            'https://www.basketball-reference.com/leagues/NBA_2013_totals.html',
            'https://www.basketball-reference.com/leagues/NBA_2014_totals.html', 
            'https://www.basketball-reference.com/leagues/NBA_2015_totals.html',
            'https://www.basketball-reference.com/leagues/NBA_2016_totals.html']
            #'https://www.basketball-reference.com/leagues/NBA_2017_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2018_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2019_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2020_totals.html',
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        print('Crawling for ', response.url , ' has started for teams')
        for player_row in response.css('.full_table, .partial_table'):
                player_link = player_row.css('td a::attr(href)').get()
                player_next_page = response.urljoin(player_link)
                yield scrapy.Request(player_next_page,callback=self.parse_player,dont_filter=False)

    def parse_player(self,response):
            player_team_link = response.xpath('//p [strong="Team"]/a/@href' ).get()
            print('player team link is ', player_team_link)
            if(player_team_link):
                team_next_page = response.urljoin(player_team_link)
            else:
                print('Player has already retired after the current season')
           
            yield scrapy.Request(team_next_page, callback=self.parse_player_team, dont_filter=False)

    def parse_player_team(self,response):
            #print('item is ',response.meta['item'])
            myTeamItem = CrawlerIs5126TeamItem()
            name_list = response.css('h1[itemprop="name"] span::text').getall()
            
            if(name_list):
                name = name_list[1]
                season =  name_list[0]
                myTeamItem['name'] = name
            location_str = response.xpath('normalize-space(//p [strong="Arena:"])').get()
            if(location_str):
                location_str.split(':')[1]
                myTeamItem['location'] = location_str.strip()


            filename = f'bball-ref-team-{response.meta["season_alt"]}.csv'
            with open('./csv/'+ filename,'a+', newline='',encoding="utf-8") as file:

                if(self.header_written[myItem["season"]]):
                    print('Header already written for ', myItem['season'])
                else:
                    csv_writer_normal = csv.writer(file)
                    csv_writer_normal.writerow(response.meta['header_row'])
                    self.header_written[myItem["season"]] = True
                    print('Header written for ', self.header_written)
                csv_writer = csv.DictWriter(file, fieldnames=response.meta['header_row'])
                csv_writer.writerow(myItem)



    