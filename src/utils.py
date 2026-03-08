from datetime import datetime

from typing import Final
import requests
import json
import os

from data_objects import ElectionData
from db_utils import save_to_db, combine_student_group_data, separate_total_vote_count, separate_turnout_data


def get_all_data_file_names(path: str) -> list[str]:
    return [filename for filename in os.listdir(path) if filename.endswith(".json")]


def save_json_data(data: ElectionData, filename: str) -> None:
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def load_json_data(filename: str) -> ElectionData:
    with open(filename, "r") as file:
        return json.load(file)


def get_data(url: str) -> ElectionData:
    return requests.get(url=url).json()


def get_generated_date(data: ElectionData) -> str:
    guild_dt: str = data["DateGenerated"]

    guild_dt = guild_dt[:19]

    guild_dt = guild_dt.replace(":", "")

    return guild_dt


def convert_generated_dt_to_object(generated_dt: str) -> datetime:
    return datetime.strptime(generated_dt, "%Y-%m-%dT%H%M%S")


def combine_json_data(data_to_combine: list[ElectionData]) -> ElectionData:
    # because MSL is fucking STUPID
    # we have to merge the two json objects
    # both objects have the same initial data, followed by "Groups"
    # put all the items from "Groups" from soc_data into general_data and return
    all_data: ElectionData = data_to_combine[0]

    for item in data_to_combine[1:]:
        all_data["Groups"] = all_data["Groups"] + item["Groups"]

    return all_data


def get_all_election_data() -> None:
    """
    IDs:
    1 - AGE
    2 - Data source
    3 - Fee status
    4 - Mode of Study
    5 - Residency
    6 - Sex
    7 - Student Type (UG, PGT, PGR)
    8 - Year of Study
    9 - Department
    10 - College
    """

    GENERAL_DATA_URL: Final[str] = (
        "https://www.guildofstudents.com/svc/voting/stats/election/paramstats/388?groupIds=1,6,7,8,9,10&sortBy=itemname&sortDirection=ascending"
    )
    SOC_DATA_URL: Final[str] = (
        "https://www.guildofstudents.com/svc/voting/stats/election/membershipstats/388?groupIds=1,2,3,4,5,6,7,8,9,10&sortBy=itemname&sortDirection=ascending"
    )

    general_data: ElectionData = get_data(url=GENERAL_DATA_URL)
    soc_data: ElectionData = get_data(url=SOC_DATA_URL)

    all_data: ElectionData = combine_json_data(data_to_combine=[general_data, soc_data])

    date_generated: datetime = convert_generated_dt_to_object(
        generated_dt=get_generated_date(data=all_data)
    )

    save_json_data(data=all_data, filename=f"../data/json/raw/{date_generated}.json")

    save_to_db(data=all_data, date_generated=date_generated)

    combine_student_group_data()

    separate_turnout_data()

    separate_total_vote_count()
