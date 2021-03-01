import scrapy
import csv
import re
from ..items import CrawlerIs5126Item

class BballSpider(scrapy.Spider):

    header_written=False;
    name = "bballref"
    # self means the BballSpider class
        # start_urls is an array of urls to crawl and is the shortcut for the start_request() method
        # start with the most recent league first 
        # check player's debut when looping through 
    start_urls = [
            'https://www.basketball-reference.com/leagues/NBA_2010_totals.html'
    ]
            #'https://www.basketball-reference.com/leagues/NBA_2011_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2012_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2013_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2014_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2015_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2016_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2017_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2018_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2019_totals.html',
            #'https://www.basketball-reference.com/leagues/NBA_2020_totals.html',
        #]
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
        print('Crawling for ', response.url , ' has started ')
        player_header_row = response.css('thead tr th::attr(data-stat)').getall()   
        player_header_row = list(map(lambda x:x.lower(),player_header_row))
        player_header_row.append('height')
        player_header_row.append('weight')
        player_header_row.append('salary')
        player_header_row.append('re_rank')
        player_header_row.append('season')
        player_header_row.append('draft_team')
        player_header_row.append('exp')
        data_stats = []
        # Step 1: Extract all the player row. 
        #self.log(f'Player header row is {player_header_row}')
        for player_row in response.css('.full_table'):
                myItem = CrawlerIs5126Item()
                myItem['season'] = '' + str(int(re.findall("NBA_(\w*)_", response.url)[0])-1) + '-' + re.findall("NBA_(\w*)_", response.url)[0][-2:]
                #print('season is ', myItem['season'])
                player_rank = player_row.css('th::text').get()
                #player_name = player_row.css('td[data-stat="player"] ::text').get()
                if(len(data_stats)>0):
                    #print('data_stats already populated', len(data_stats)) 
                    #continue
                    for data_stat in data_stats:
                        myItem[data_stat] = player_row.xpath('.//td[@data-stat="'+data_stat+'"] //text()').get()
                else:
                    #print('data_stats not yet populated')
                    data_stats =  player_row.css('td::attr(data-stat)').getall()
                    #continue
                    for data_stat in data_stats:
                    #print('data stat is ', data_stat, type(data_stat),player_row.xpath('//td[@data-stat="'+data_stat+'"]'))
                        myItem[data_stat] = player_row.xpath('.//td[@data-stat="'+data_stat+'"] //text()').get()
                    #myItem[data_stat] = player_row.css("td[data-stat={data_stat}").get();
                    #print('my item is ', data_stat, myItem[data_stat])
                myItem['ranker'] = player_rank
                #print('player stats is', myItem, len(myItem))
                #myItem['name'] = player_name
                # it will split by space by default, need to get all
                #player_name = player_row.css('td a::text').get()
                #self.log(f'Player detail is {player_details}')
                player_link = player_row.css('td a::attr(href)').get()
                #self.log(f'link is {player_link}')
                # try to follow player link
                player_next_page = response.urljoin(player_link)
                #print('player next page is ', player_next_page)
                yield scrapy.Request(player_next_page,callback=self.parse_player, meta={'item': myItem, 'header_row':player_header_row})

    def parse_player(self,response):
        myItem = response.meta['item']
        # take note that no space between itemprop and h1
        player_name = response.css('h1[itemprop=name] span::text').get()
        #print('playername is ', player_name, myItem['player'])
        # 1st check to make sure player names are the same
        if(player_name == myItem['player']):
            #print('Names matched')
            #player_debut = response.xpath('//p[contains(strong,"Debut:")] /a/text()').get()
            #player_debut_year = response.xpath('//p[contains(strong,"Debut:")] /a/text()').get().split(',')[1].strip()
            #player_exp = response.xpath('//p[contains(strong,"Experience:")] /text()').re(r'(\d*) years')
            player_active_years = response.xpath('//comment()').re(r'<tr id="totals.*<th.*data-stat="season" ><a.*>(\w*-\w*)</a>')    
            print('index is ', player_active_years, myItem['season'], player_active_years.index(myItem['season']))
            myItem['exp'] = player_active_years.index(myItem['season']) + 1
            # get weight 
            # xpath must contain "" for string condition, there is no need for css
            # player_weight = response.css('/span[itemprop=weight]::text').get()
            weightandheight = response.xpath('//span[@itemprop="weight"] /parent::*').re(r'\((\w*),\s*(\w*)\)')
            myItem['weight'] = weightandheight[0]
            # get height
            # player_height = response.css('span[itemprop=height]::text').get()
            myItem['height'] = weightandheight[1]
            #player_team_link = response.xpath('//p /*[contains(text(),"Team")]/parent::* /a/@href' ).get()
            # get re_rank, re_rank may be null
            re_rank_list = response.xpath('//p[strong="Recruiting Rank: "]').re(r'\((\d*)\)')
            if(len(re_rank_list)>0):
                myItem['re_rank'] = re_rank_list[0]
            # get salaries
            # print('current_season is ', myItem['season'])
            # crawling comments as salaries table is dynamic content
            salary = response.xpath('//comment()').re(r'<th .* data-stat="season" >'+myItem['season']+'</th>.*data-stat="salary" csk="(\w*)"')
            myItem['salary'] = salary[0]
            # get draft_team
            myItem['draft_team'] = response.xpath('//p[contains(strong,"Draft:")] /a/text()').get()
            # get per and ws ?
            # a player may be retiring this current season, so team not be avail
            # print('salary is ', myItem['salary'], ' for season ', myItem['season'], ' for player ', myItem['player'])
            # print('Final player info is ', myItem)
            # print('player header row is ', response.meta['header_row'])
            player_team_link = response.xpath('//p [strong="Team"]/a/@href' ).get()
            print('player team link is ', player_team_link)
            if(player_team_link):
                team_next_page = response.urljoin(player_team_link)
            else:
                print('Player has already retired after the current season')
            #print('team next page is ', myItem)
            #yield scrapy.Request(team_next_page, callback=self.parse_player_team, meta={'item': myItem})

            filename = f'bball-ref-{myItem["season"]}.csv'
            with open(filename,'a+', newline='') as file:

                if(self.header_written):
                    print('Header already written')
                else:
                    csv_writer_normal = csv.writer(file)
                    csv_writer_normal.writerow(response.meta['header_row'])
                    self.header_written = True
                csv_writer = csv.DictWriter(file, fieldnames=response.meta['header_row'])
                csv_writer.writerow(myItem)
        else:
            return

    def parse_player_team(self,response):
            print('item is ',response.meta['item'])


    