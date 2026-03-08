from typing import TypedDict, Optional, List


class Organisation(TypedDict):
    Id: int
    Name: str
    GroupingType: Optional[str]
    Organisation: Optional[str]
    FullName: str


class GroupItem(TypedDict):
    Name: str
    Voters: int
    NonVoters: int
    Eligible: int
    IsOtherItem: bool
    Turnout: float
    RelativeTurnout: float


class Group(TypedDict):
    Name: str
    Items: List[GroupItem]


class ElectionData(TypedDict):
    Id: int
    Title: str
    Organisation: Organisation
    Eligible: int
    Voters: int
    NonVoters: int
    Votes: int
    PostCount: int
    CandidateCount: int
    IndividualCandidateCount: int
    DateGenerated: str
    Groups: List[Group]
    Turnout: float


def combine_groups(groups: List[Group], group_name: str) -> Group:
    combined_group: Group = {"Name": group_name, "Items": []}
    for group in groups:
        for item in group["Items"]:
            combined_group["Items"].append(item)

    return combined_group
