import scrapy
import csv
from ..items import CrawlerIs5126Item

class BballSpider(scrapy.Spider):
    name = "bballref"
    # self means the BballSpider class
        # start_urls is an array of urls to crawl and is the shortcut for the start_request() method
    start_urls = [
            'https://www.basketball-reference.com/leagues/NBA_2020_totals.html'
        ]
    # parse is the default callback called for requests without an explicitly assigned callback.
    # css selectors are patterns used to select styled elements
    # xpath or XML path language, is a query language for selecting nodes from an XML document. Xpath uses path expressions to navigate through elements and attributes
    # in an xml document, xpath is more powerful as it also looks at the content in addition to the HTML structure
    def parse(self, response):
        #page = response.url.split("/")[-2]
        #.log(f'page is ', {page})
        # f means string
        #filename = f'bball-{page}.html'
        #with open(filename, 'wb') as f:
            #f.write(response.body)
        #self.log(f'Saved file {filename}')
        # Step 0: Extract the headers and append more fields to the headers
        player_header_row = response.css('thead tr th::text').getall()
        player_header_row.append('height')
        player_header_row.append('weight')
        data_stats = []
        # Step 1: Extract all the player row. 
        self.log(f'Player header row is {player_header_row}')
        for player_row in response.css('.full_table'):
                myItem = CrawlerIs5126Item()
                player_rank = player_row.css('th::text').get()
                #player_name = player_row.css('td[data-stat="player"] ::text').get()
                if(len(data_stats)>0):
                    #print('data_stats already populated', len(data_stats)) 
                    myItem[data_stats[0]] = player_rank
                    #continue
                else:
                    #print('data_stats not yet populated')
                    data_stats =  player_row.css('td::attr(data-stat)').getall()
                    #continue
                for data_stat in data_stats:
                    #print('data stat is ', data_stat, type(data_stat),player_row.xpath('//td[@data-stat="'+data_stat+'"]'))
                    myItem[data_stat] = player_row.xpath('.//td[@data-stat="'+data_stat+'"] //text()').get()
                    #myItem[data_stat] = player_row.css("td[data-stat={data_stat}").get();
                    #print('my item is ', data_stat, myItem[data_stat])

                myItem['rank'] = player_rank
                #print('player stats is', myItem, len(myItem))
                #myItem['name'] = player_name
                # it will split by space by default, need to get all
                #player_name = player_row.css('td a::text').get()
                #self.log(f'Player detail is {player_details}')
                player_link = player_row.css('td a::attr(href)').get()
                #self.log(f'link is {player_link}')
                # try to follow player link
                player_next_page = response.urljoin(player_link)
                yield scrapy.Request(player_next_page,callback=self.parse_player, meta={'item': myItem})


    def parse_player(self,response):
        myItem = response.meta['item']
        # take note that no space between itemprop and h1
        player_name = response.css('h1[itemprop=name] span::text').get()
        #print('playername is ', player_name, myItem['player'])
        if(player_name == myItem['player']):
            #print('Names matched')
            # get weight 
            player_weight = response.css('span [itemprop=weight]').get()
            # get height
            player_height = response.css('span [itemprop=height]').get()
            #print(response.meta['item'])
            #player_team_link = response.xpath('//p /*[contains(text(),"Team")]/parent:: /a/@href' ).get()
            player_team_link = response.xpath('//p [strong="Team"]/a/@href' ).get()
            team_next_page = response.urljoin(player_team_link)
            yield scrapy.Request(team_next_page,callback=self.parse_player_team, meta={'item': myItem})
        else:
            return
    def parse_player_team(self,response):
        print('nth')


    