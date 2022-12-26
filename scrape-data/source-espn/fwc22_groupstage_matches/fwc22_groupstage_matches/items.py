from dataclasses import dataclass

# -------------------------------------------------------------------------------------------------------------
#-- Prepare items for extracting Group-Stage match-level details

@dataclass
class CustomItemSummary:

    ESPN_MATCH_ID        : int
    DATE                 : int
    TEAMS                : dict
    STAGE_IN_TOURNAMENT  : str
    STADIUM              : str
    LOCATION             : str
    REFEREE              : str
    ATTENDANCE           : str

@dataclass
class CustomItemStats:

    ESPN_MATCH_ID          : int
    POSSESSION             : dict
    FOULS                  : dict
    CARDS_YELLOW           : dict
    CARDS_RED              : dict
    OFFSIDES               : dict
    CORNER_KICKS           : dict
    SAVES                  : dict
    GOALS                  : dict

@dataclass
class CustomItemLineUps:

    ESPN_MATCH_ID          : int
    FORMATION              : dict
    PLAYERS                : dict
