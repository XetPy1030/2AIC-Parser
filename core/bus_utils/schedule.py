class Schedule:
    def __init__(self, official_buses, not_official_buses, wrong_buses):
        self.official_buses = official_buses
        self.not_official_buses = not_official_buses
        self.wrong_buses = wrong_buses

        self.sort_buses()

    def sort_buses(self):
        self.official_buses.sort(key=lambda x: x['start_time'] if x['start_time'] else x['start_time_the_beginning_of_the_beginning'])
        self.not_official_buses.sort(key=lambda x: x['start_time'] if x['start_time'] else x['start_time_the_beginning_of_the_beginning'])
        self.wrong_buses.sort(key=lambda x: x['start_time'] if x['start_time'] else x['start_time_the_beginning_of_the_beginning'])

    @property
    def all_buses(self):
        buses = self.official_buses + self.not_official_buses + self.wrong_buses
        buses.sort(key=lambda x: x['start_time'] if x['start_time'] else x['start_time_the_beginning_of_the_beginning'])
        return buses

    def get_buses(self, is_official=True, is_not_official=True, is_wrong=False):
        buses = []
        if is_official:
            buses += self.official_buses
        if is_not_official:
            buses += self.not_official_buses
        if is_wrong:
            buses += self.wrong_buses
        buses.sort(key=lambda x: x['start_time'] if x['start_time'] else x['start_time_the_beginning_of_the_beginning'])
        return buses

    @property
    def buses(self):
        return self.get_buses()
