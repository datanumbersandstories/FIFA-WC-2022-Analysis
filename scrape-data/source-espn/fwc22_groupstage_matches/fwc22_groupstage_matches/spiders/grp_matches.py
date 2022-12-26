"""
    page_listing_all_matches = ['https://www.espn.in/football/scoreboard/_/league/FIFA.WORLD/date/20221120']

    grpA_qatar_vs_ecuador_summary       = [ 'https://www.espn.in/football/match/_/gameId/<match_id>' ]
    grpA_qatar_vs_ecuador_statistics    = [ 'https://www.espn.in/football/matchstats?gameId=<match_id>' ]
    grpA_qatar_vs_ecuador_commentary    = [ 'https://www.espn.in/football/commentary?gameId=633790' ]
    grpA_qatar_vs_ecuador_lineups       = [ 'https://www.espn.in/football/lineups?gameId=<match_id>' ]

    driver.find_element_by_class_name()
    driver.find_element_by_css_selector()
    driver.find_element_by_xpath()
    driver.find_element_by_id()
    driver.find_element_by_tag_name()
    driver.find_elements_by_link_text()
    driver.find_element_by_partial_link_text()

"""

import scrapy
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest
from ..items import CustomItemSummary, CustomItemStats, CustomItemLineUps
import re

class GrpstgMatchesSpider1Spider(scrapy.Spider):
    name = 'grp_matches'
    # allowed_domains = ['www.espn.in']
    # start_urls = ['http://www.espn.in/']

    def __init__(self):
        self.img_counter = 1

        self.url_matches_held_partial      = 'https://www.espn.in/football/scoreboard/_/league/FIFA.WORLD/date/'
        self.match_summary_link_partial    = 'https://www.espn.in/football/match/_/gameId/'
        self.match_stats_link_partial      = 'https://www.espn.in/football/matchstats?gameId='
        self.match_commentary_link_partial = 'https://www.espn.in/football/commentary?gameId='
        self.match_linups_link_partial     = 'https://www.espn.in/football/lineups?gameId='

        self.match_summ_link_full          = ''
        self.match_stats_link_full         = ''
        self.match_lineups_link_full       = ''

        """ Group-Stage Matches were held from 2022-Nov-20 to 2022-Dec-02 """
        self.nov_last_match_day = 20221130
        self.dec_last_match_day = 20221202
        self.match_date         = 20221120  # first group-stage match day

        self.test_nov_last_day  = 20221130   # test code

        # output dictionaries
        self.dict_match_summary = {}
        self.dict_match_stats   = {}

    # custom method : save screenshot from response
    def save_screenshot(self, response, reset_img_counter=False):
        img = response.meta['screenshot']
        img_dir = './scraped_images/'
        img_name = 'sc_' + str(self.img_counter) + '.png'
        img_file_name = img_dir + img_name
        with open(img_file_name, "wb") as f:
            f.write(img)
            f.close()
        if reset_img_counter is True:
            self.img_counter = 0
        else:
            self.img_counter += 1

    # redefined method
    def start_requests(self):
        while self.match_date <= self.nov_last_match_day:
            url_matches_held_full = self.url_matches_held_partial + str(self.match_date)
            yield SeleniumRequest(
                url        = url_matches_held_full,
                wait_time  = 1,
                screenshot = True,
                callback   = self.parse_main
            )
            self.match_date += 1
        if self.match_date == 20221131:
            self.match_date = 20221201
            while self.match_date <= self.dec_last_match_day:
                url_matches_held_full = self.url_matches_held_partial + str(self.match_date)
                self.match_date += 1
                yield SeleniumRequest(
                    url        = url_matches_held_full,
                    wait_time  = 0.1,
                    screenshot = True,
                    callback   = self.parse_main
                )


    def parse_main(self, response):
        # self.save_screenshot(response, reset_img_counter=False)
        print(response.url)
        selector_1 = response.css('article::attr(id)').extract()
        selector_1.sort()
        for el in selector_1:
            self.match_summ_link_full    = self.match_summary_link_partial + str(el)
            self.match_stats_link_full   = self.match_stats_link_partial   + str(el)
            self.match_lineups_link_full = self.match_linups_link_partial  + str(el)

            gen_1 = self.get_generator_match_summary( self.match_summ_link_full )

            gen_2 = self.get_generator_match_stats( self.match_stats_link_full )

            gen_3 = self.get_generator_match_lineups( self.match_lineups_link_full )

            for obj in gen_1:
                yield obj
            for obj in gen_2:
                yield obj
            for obj in gen_3:
                yield  obj

# ----------------------------------------------------------------------------------------------------------------------


    def get_generator_match_summary(self, url_match_summ):
        yield SeleniumRequest(
            url=url_match_summ,
            wait_time=0.1,
            screenshot=True,
            callback=self.parse_match_summary
        )

    def get_generator_match_stats(self, url_match_stats):
        yield SeleniumRequest(
                url=url_match_stats,
                wait_time=0.1,
                screenshot=True,
                callback=self.parse_match_stat
        )

    def get_generator_match_lineups(self, url_match_lineups):
        yield SeleniumRequest(
                url=url_match_lineups,
                wait_time=0.1,
                screenshot=True,
                callback=self.parse_match_lineups
        )

# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------


    def parse_match_summary(self, response):
        # self.save_screenshot(response_summary, reset_img_counter=False)

        date_time = response.css('span::attr(data-date)').extract()
        date      = date_time[0][0:10]

        team1_name_full = response.css('div.team.away span.long-name::text').extract()[0]
        team1_name_abbr = response.css('div.team.away span.abbrev::text').extract()[0]
        team2_name_full = response.css('div.team.home span.long-name::text').extract()[0]
        team2_name_abbr = response.css('div.team.home span.abbrev::text').extract()[0]
        teams = { 'TEAM1' : {'FULL_NAME' : team1_name_full,
                             'ABBREV'    : team1_name_abbr},
                  'TEAM2' : {'FULL_NAME' : team2_name_full,
                             'ABBREV'    : team2_name_abbr } }

        stage_in_tournament = response.css('div.game-details.header::text').extract_first().strip('\n,\t, ')

        stadium = response.css('ul.gi-group li.venue div::text').extract_first().strip('VENUE:')
        location = response.css('ul.gi-group li.location.subdued div.address span::text').extract()
        for el in response.css('ul.gi-group li div::text').extract():
            if 'ATTENDANCE' in el:
                attendance = el.strip('ATTENDANCE:')
        for el in response.css('ul.gi-group li.subdued div::text').extract():
            if 'REFEREE' in el:
                referee = el.strip('\n,\t,REFEREE:')

        items_match_summ = CustomItemSummary(
                                ESPN_MATCH_ID       = response.url[-6:],
                                DATE                = date,
                                TEAMS               = teams,
                                STAGE_IN_TOURNAMENT = stage_in_tournament,
                                STADIUM             = stadium,
                                LOCATION            = location[0],
                                REFEREE             = referee,
                                ATTENDANCE          = attendance
                            )


        yield_key = 'MATCH_' + response.url[-6:] + '_SUMMARY'
        return { yield_key : items_match_summ }


    def parse_match_stat(self, response):
        # self.save_screenshot(response_stats, reset_img_counter=False)
        possession_home_team = response.css('div.possession div.home span.team-name::text').extract()
        possession_away_team = response.css('div.possession div.away span.team-name::text').extract()
        possession_home_perct = response.css('div.possession span.chartValue::text').extract()
        possessions           = { 'TEAM1': ( possession_away_team[0],
                                             int(possession_home_perct[0][0:-1] ) ),
                                  'TEAM2': ( possession_home_team[0],
                                             int(possession_home_perct[1][0:-1])) }


        team1_name = response.css('div.team.away.tied span::text').extract()
        team1_name_full = response.css('div.team.away span.long-name::text').extract()[0]
        team1_name_abbr = response.css('div.team.away span.abbrev::text').extract()[0]
        team2_name = response.css('div.team.home span::text').extract()
        team2_name_full = response.css('div.team.home span.long-name::text').extract()[0]
        team2_name_abbr = response.css('div.team.home span.abbrev::text').extract()[0]

        stats_table = response.css('div.stat-list table tbody tr td::text').extract()
        fouls       = { 'TEAM1' : ( team1_name_abbr,
                                    int(stats_table[0]) ),
                        'TEAM2' : ( team2_name_abbr,
                                    int(stats_table[2]) ) }
        cards_yellow = { 'TEAM1' : ( team1_name_abbr,
                                     int(stats_table[3]) ),
                         'TEAM2' : ( team2_name_abbr,
                                     int(stats_table[5]) ) }
        cards_red    = { 'TEAM1' : ( team1_name_abbr,
                                     int(stats_table[6]) ),
                         'TEAM2' : ( team2_name_abbr,
                                     int(stats_table[8]) ) }
        offsides     = { 'TEAM1' : ( team1_name_abbr,
                                     int(stats_table[9]) ),
                         'TEAM2' : ( team2_name_abbr,
                                     int(stats_table[11]) ) }
        corner_kicks = { 'TEAM1' : ( team1_name_abbr,
                                     int(stats_table[12]) ),
                         'TEAM2' : ( team2_name_abbr,
                                     int(stats_table[14]) ) }
        saves        = { 'TEAM1' : ( team1_name_abbr,
                                     int(stats_table[15]) ),
                         'TEAM2' : ( team2_name_abbr,
                                     int(stats_table[17]) ) }

        # ----- process goal data
        team1_goal_scorers_raw   = response.css('div.team.away ul[data-event-type="goal"] li::text').extract()
        team1_goal_timestamps    = response.css('div.team.away ul[data-event-type="goal"] li span::text').extract()
        team1_goals = []
        team1_goal_scorers = []
        for el in team1_goal_scorers_raw:
            el = el.strip('\n,\t, ')
            if re.search('[A-z]', el):
                team1_goal_scorers.append(el)
        for i in range(len(team1_goal_scorers)):
            scorer       = team1_goal_scorers[i]
            minute_marks = team1_goal_timestamps[i]
            minute_marks = minute_marks.replace("'", "")
            minute_marks = minute_marks.replace("(", "").replace(")", "")
            list_minute_marks = list( map( str, minute_marks.split(', ') ) )
            for el in list_minute_marks:
                is_penalty = 'Y' if ('PEN' in el) else 'N'
                el = el.strip(' PEN')
                team1_goals.append({ 'MINUTE_MARK' : el,
                                     'SCORER'      : scorer,
                                     'IS_PENALTY'  : is_penalty })

        team2_goal_scorers_raw = response.css('div.team.home ul[data-event-type="goal"] li::text').extract()
        team2_goal_timestamps  = response.css('div.team.home ul[data-event-type="goal"] li span::text').extract()
        team2_goals = []
        team2_goal_scorers = []
        for el in team2_goal_scorers_raw:
            el = el.strip('\n,\t, ')
            if re.search('[A-z]', el):
                team2_goal_scorers.append(el)
        for i in range(len(team2_goal_scorers)):
            scorer       = team2_goal_scorers[i]
            minute_marks = team2_goal_timestamps[i]
            minute_marks = minute_marks.replace("'", "")
            minute_marks = minute_marks.replace("(", "").replace(")", "")
            list_minute_marks = list(map(str, minute_marks.split(', ')))
            for el in list_minute_marks:
                is_penalty = 'Y' if ( 'PEN' in el ) else 'N'
                el = el.strip(' PEN')
                team2_goals.append({'MINUTE_MARK': el,
                                    'SCORER'     : scorer,
                                    'IS_PENALTY' : is_penalty})

        goals = { 'TEAM1' : { 'TEAM_ABBR'  : team1_name_abbr,
                              'TEAM_GOALS' : team1_goals },
                  'TEAM2' : { 'TEAM_ABBR'  : team2_name_abbr,
                              'TEAM_GOALS' : team2_goals }  }

        # ----- add output items
        items_match_stats = CustomItemStats(
                                ESPN_MATCH_ID = response.url[-6:],
                                POSSESSION    = possessions,
                                FOULS         = fouls,
                                CARDS_YELLOW  = cards_yellow,
                                CARDS_RED     = cards_red,
                                OFFSIDES      = offsides,
                                CORNER_KICKS  = corner_kicks,
                                SAVES         = saves,
                                GOALS         = goals
                             )
        yield_key = 'MATCH_' + response.url[-6:] + '_STATS'
        return {yield_key: items_match_stats}


    def parse_match_lineups(self, response):
        # self.save_screenshot(response_summary, reset_img_counter=False)

        team1_name_full = response.css('div.team.away span.long-name::text').extract()[0]
        team1_name_abbr = response.css('div.team.away span.abbrev::text').extract()[0]
        team2_name_full = response.css('div.team.home span.long-name::text').extract()[0]
        team2_name_abbr = response.css('div.team.home span.abbrev::text').extract()[0]

        # formations
        formations = response.css('div.formation div.formations__text::text').extract()

        # players
        tables_lineup = response.css('table[data-behavior = "table_accordion"]')
        tab1 = tables_lineup[0]
        tab2 = tables_lineup[1]

        tab1_bodies = tab1.css('tbody')
        tab2_bodies = tab2.css('tbody')

        list1 = tab1.css('div.accordion-header.lineup-player span a::text').extract()
        list2 = tab2.css('div.accordion-header.lineup-player span a::text').extract()

        team1_players_active_raw = tab1_bodies[0].css('div.accordion-header.lineup-player span a::text').extract()
        team1_players_bench_raw  = tab1_bodies[1].css('div.accordion-header.lineup-player span a::text').extract()

        team2_players_active_raw = tab2_bodies[0].css('div.accordion-header.lineup-player span a::text').extract()
        team2_players_bench_raw  = tab2_bodies[1].css('div.accordion-header.lineup-player span a::text').extract()

        team1_players_active = [ player.strip('\n\t') for player in team1_players_active_raw ]
        team1_players_bench  = [ player.strip('\n\t') for player in team1_players_bench_raw ]

        team2_players_active = [player.strip('\n\t') for player in team2_players_active_raw]
        team2_players_bench  = [player.strip('\n\t') for player in team2_players_bench_raw]

        players = { 'TEAM1' : ( team1_name_abbr,
                                { 'ON_FILED_AND_SUBS' : team1_players_active,
                                  'ON_BENCH'          : team1_players_bench } ),
                    'TEAM2' : ( team2_name_abbr,
                                { 'ON_FILED_AND_SUBS' : team2_players_active,
                                  'ON_BENCH'          : team2_players_bench } )  }


        items_match_lineups = CustomItemLineUps(
            ESPN_MATCH_ID = response.url[-6:],
            FORMATION     = { 'TEAM1' : ( team1_name_abbr, formations[0] ),
                              'TEAM2' : ( team2_name_abbr, formations[1] ) },
            PLAYERS       = players
        )
        yield_key = 'MATCH_' + response.url[-6:] + '_LINEUPS'
        return {yield_key: items_match_lineups}

#-----------------------------------------------------------------------------------------------------------------------
