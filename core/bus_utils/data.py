from dataclasses import dataclass


@dataclass
class BusSchedule:
    places: str
    time: str
    groups: list[str]
    quantity: str
    comment: str

    # previous_route: int
    # this_route: int
    # next_route: int


@dataclass
class BusesSchedules:
    name: str
    route: str
    schedule: list[BusSchedule]
