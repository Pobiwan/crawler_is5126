import scrapy
import csv
import re
# will have error of attempted relative import with no known parent package
from crawler_is5126.items import CrawlerIs5126Item, CrawlerIs5126TeamItem
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
    data_stats = []
    def start_requests(self):
        urls = [
            #'https://www.basketball-reference.com/players/a/adebaba01.html']
            #'https://www.basketball-reference.com/leagues/NBA_2010_totals.html'
            'https://www.basketball-reference.com/leagues/NBA_2011_totals.html',
            'https://www.basketball-reference.com/leagues/NBA_2012_totals.html', 
            'https://www.basketball-reference.com/leagues/NBA_2013_totals.html',
            'https://www.basketball-reference.com/leagues/NBA_2014_totals.html', 
            'https://www.basketball-reference.com/leagues/NBA_2015_totals.html',
            'https://www.basketball-reference.com/leagues/NBA_2016_totals.html',
            'https://www.basketball-reference.com/leagues/NBA_2017_totals.html',
            'https://www.basketball-reference.com/leagues/NBA_2018_totals.html',
            'https://www.basketball-reference.com/leagues/NBA_2019_totals.html',
            'https://www.basketball-reference.com/leagues/NBA_2020_totals.html']
        
        for url in urls:
            #yield scrapy.Request(url=url, callback=self.parse_player, meta= { "season": "2020","header":['g','mp','fg','fga','fg_pct','fg3','fg3a','fg3_pct','fg2','fg2a','fg2_pct','ft','fta','ft_pct','orb','drb','trb','ast','stl','blk','tov','pf','pts' ] })
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print('Crawling for ', response.url , ' has started for teams')
        player_header_row = response.css('thead tr th::attr(data-stat)').getall()  
        # remove unnecessary headers
        player_header_row = player_header_row[5:]
        player_header_row.remove('efg_pct')
        player_header_row.remove('gs')
        player_header_row.append('season')  
        player_header_row.append('name')  
        player_header_row.append('location')  
        player_header_row.append('total_salary')  
        player_header_row.append('avg_player_salary')  
        player_header_row.append('avg_team_exp')  
        player_header_row.append('avg_team_age')  
        player_header_row.append('seasons_played')
        player_header_row.append('play_off')
        player_header_row.append('champion')

        teams_list = response.xpath('//td[@data-stat="team_id"] /a/@href').getall() 
        unique_teams_list = list(dict.fromkeys(teams_list))
        print('unique team list is ', unique_teams_list)
        #for player_row in response.css('.full_table, .partial_table'):
                #player_link = player_row.css('td a::attr(href)').get()
                #player_next_page = response.urljoin(player_link)
                #response.url.split('/')[4].split('_')[1]
                #print("changing season to ", response.url.split('/')[4].split('_')[1])
                #season_param = str(int(response.url.split('/')[4].split('_')[1]) - 1) + '-' + response.url.split('/')[4].split('_')[1][-2:]
                #print('season param is ', season_param)
                #yield scrapy.Request(player_next_page,callback=self.parse_player,meta= { "header":player_header_row, "season":season_param }, dont_filter=False)
        for team in unique_teams_list:
            team_next_page = response.urljoin(team)
            yield scrapy.Request(team_next_page,callback=self.parse_player_team,meta= { "header":player_header_row }, dont_filter=False)

    def parse_player(self,response):
            # it will always be https://www.basketball-reference.com/teams/BRK/2021.html
            # player_team_link = response.xpath('//p [strong="Team"]/a/@href' ).get()
            season_param = response.meta['season']
            player_team_links =  response.xpath('//th[@data-stat="season"] /a[text()="'+ season_param +'"] /ancestor::tr /td[@class="left " and @data-stat="team_id"] /a/@href').getall()
            print('player team links here is ', player_team_links)
            # change to the appropriate date     
            player_header_row = response.meta['header']
            if(len(player_team_links)>0):
                for play_team_link in player_team_links:
                #player_team_link_season = player_team_link.replace("2021", response.meta["season"])
                    print('player team link here is ', play_team_link)
                    team_next_page = response.urljoin(play_team_link)
                    yield scrapy.Request(team_next_page, callback=self.parse_player_team, meta= { "header":player_header_row }, dont_filter=False)
            else:
                print('This player is weird')
           
    def parse_player_team(self,response):
            #print('item is ',response.meta['item'])
            myTeamItem = CrawlerIs5126TeamItem()
            team_header_row = response.meta['header']
            print('team_header_row is ', team_header_row)
            if(len(team_header_row)>0):
                for data_stat in team_header_row:
                     #print('data stat is  <tbody><tr ><th.*data-stat="player" >Team.*<td.*data-stat="'+data_stat+'" >(\w*)</td>')
                    value_to_use = response.xpath('//comment()').re(r'<tbody><tr ><th.*data-stat="player" >Team.*<td.*data-stat="'+data_stat+'" >(.?\w*)</td>')
                    myTeamItem[data_stat] = value_to_use[0] if value_to_use else ""
            name_list = response.css('h1[itemprop="name"] span::text').getall()
            if(name_list):
                name = name_list[1]
                season = '' + name_list[0].split("-")[0] + '/' + str(int(name_list[0].split("-")[0]) + 1)
                myTeamItem['name'] = name
                myTeamItem['season'] = season
            location_str = response.xpath('normalize-space(//p [strong="Arena:"])').get()
            if(location_str):
                myTeamItem['location'] = " ".join(location_str.split(':')[1].strip().split(" ")[0:-1])
            # getting avg pay
            all_salaries = response.xpath('//comment()').re(r'<td.*data-stat="salary".*>\$(.*)</td>')
            if(all_salaries):
                for idx, i in enumerate(all_salaries):
                    all_salaries[idx] = all_salaries[idx].replace(',','')
                    all_salaries[idx] = int(all_salaries[idx])
            myTeamItem['avg_player_salary'] = round(sum(all_salaries)/ len(all_salaries),2)
            myTeamItem['total_salary'] = sum(all_salaries)
            # getting avg age
            all_ages = response.xpath('//div[@id="div_per_game"] /table /tbody /tr /td[@data-stat="age"] /text()').getall()
            if(all_ages):
                for idx, i in enumerate(all_ages):
                    all_ages[idx] = int(i)
            myTeamItem['avg_team_age'] = round(sum(all_ages)/ len(all_ages),2)
            # getting avg exp
            all_exp = response.xpath('//td [@data-stat="years_experience"] /text()').getall()
            if(all_exp):
                # change all r to 0 and change all string to int
                for idx, i in enumerate(all_exp):
                    if(all_exp[idx] == 'R'):
                        all_exp[idx] = 0
                    else:
                        all_exp[idx] = int(i)
                myTeamItem['avg_team_exp'] = round((sum(all_exp))/ len(all_exp),2)
            print('my team item is ', myTeamItem)
            # need to turn dont_filter to true as it will be accessing the play_off html over and over again
            yield scrapy.Request("https://www.basketball-reference.com/playoffs/", callback=self.play_off, meta= {"header": team_header_row, "myTeamItem": myTeamItem}, dont_filter=True)

    def play_off(self,response):
        finalTeamItem = response.meta["myTeamItem"]
        finalTeamItem['play_off'] = 0
        finalTeamItem['champion'] = 0
        play_off_season = finalTeamItem['season'].split('/')[1]
        print('play_off_season is', play_off_season)
        season = str(int(play_off_season) - 1) + '-' + finalTeamItem['season'].split('/')[1][-2:]
        #print('text season is ', season)
        runner_up_team = response.xpath('//th[@data-stat="year_id"] /a[text()="'+play_off_season+'"] /parent::*/following-sibling::td[@data-stat="runnerup"] /a/text()').get()
        # get champion & runner up
        #print('runner is ', runner_up_team)
        champion_team = response.xpath('//th[@data-stat="year_id"] /a[text()="'+play_off_season+'"] /parent::*/following-sibling::td[@data-stat="champion"] /a/text()').get()
        if(finalTeamItem['name'] == runner_up_team or finalTeamItem['name'] == champion_team):
            finalTeamItem['play_off'] = 1
            if(finalTeamItem['name'] == champion_team):
                finalTeamItem['champion'] = 1 
        #print('champion is ', champion_team)
        #print('Final ', finalTeamItem)
        print('final before write ',finalTeamItem)
        # 
        filename = f'bball-ref-team-{season}.csv'
        with open('C:\\Users\\157664\\Desktop\\crawler_is5126\\crawler_is5126\\teams\\' + filename,'a+', newline='',encoding="utf-8") as file:
            if(self.header_written[finalTeamItem["season"]]):
                print('Header already written for ', finalTeamItem['season'])
            else:
                csv_writer_normal = csv.writer(file)
                csv_writer_normal.writerow(response.meta['header'])
                self.header_written[finalTeamItem["season"]] = True
                print('Header written for ', self.header_written)
            csv_writer = csv.DictWriter(file, fieldnames=response.meta['header'])
            csv_writer.writerow(finalTeamItem)
