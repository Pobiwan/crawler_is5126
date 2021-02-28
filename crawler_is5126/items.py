# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# scrapy item is python item that defines key-value pair. 
# extracted data -> temp containers (items) -> further storage

class CrawlerIs5126Item(scrapy.Item):
    # define the fields for your item here like:

    #headerlist = ['Rk','Player','Pos','Age','Tm','G','GS','MP','FG','FGA','FG%','3P','3PA','3P%','2P','2PA','2P%','eFG%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS']
    player = scrapy.Field()
    rank = scrapy.Field()
    pos = scrapy.Field()
    age = scrapy.Field()
    team_id = scrapy.Field()
    g = scrapy.Field()
    gs = scrapy.Field()
    mp = scrapy.Field()
    fg = scrapy.Field()
    fga = scrapy.Field()
    fg_pct = scrapy.Field()
    fg3 = scrapy.Field()
    fg3a = scrapy.Field()
    fg3_pct = scrapy.Field()
    fg2 = scrapy.Field()
    fg2a = scrapy.Field()
    fg2_pct = scrapy.Field()
    efg_pct = scrapy.Field()
    ft = scrapy.Field()
    fta = scrapy.Field()
    ft_pct = scrapy.Field()
    orb = scrapy.Field()
    drb = scrapy.Field()
    trb = scrapy.Field()
    ast = scrapy.Field()
    stl = scrapy.Field()
    blk = scrapy.Field()
    tov = scrapy.Field()
    pf = scrapy.Field()
    pts = scrapy.Field()
    weight = scrapy.Field()
    height = scrapy.Field()
    pass


    #name = scrapy.Field()
    #rank = scrapy.Field()
    #pos = scrapy.Field()
    #age = scrapy.Field()
    #tm = scrapy.Field()
    #g = scrapy.Field()
    #gs = scrapy.Field()
    #mp = scrapy.Field()
    #fg = scrapy.Field()
    #field_goals_attempts = scrapy.Field()
    #field_goals_percentage = scrapy.Field()
    #three_points_fg = scrapy.Field()
    #three_points_fga = scrapy.Field()
    #three_points_fgpercentage = scrapy.Field()
    #two_points_fg = scrapy.Field()
    #two_points_fga = scrapy.Field()
    #two_points_fgpercentage = scrapy.Field()
    #effective_fgp = scrapy.Field()
    #free_throw = scrapy.Field()
    #free_throw_attempts = scrapy.Field()
    #free_throw_percentage = scrapy.Field()
    #off_rebound = scrapy.Field()
    #def_rebound = scrapy.Field()
    #total_rebound = scrapy.Field()
    #assists = scrapy.Field()
    #steals = scrapy.Field()
    #blocks = scrapy.Field()
    #turnovers = scrapy.Field()
    #fouls = scrapy.Field()
    #points = scrapy.Field()
    #pass

class CrawlerIs5126TeamItem(scrapy.Item):


    pass