from datetime import timedelta
from time import sleep

from travelscanner.errors import NoCrawlersException
from travelscanner.options.travel_options import TravelOptions


class Agent(object):
    def __init__(self):
        self.crawlers = []
        self.travel_options = TravelOptions()
        self.crawl_interval = timedelta(seconds=5)

    def get_travel_options(self):
        return self.travel_options

    def add_crawler(self, crawler):
        crawler.set_agent(self)
        self.crawlers.append(crawler)

    def set_scanning_interval(self, scan_interval):
        self.crawl_interval = scan_interval

    def crawl_loop(self):
        if len(self.crawlers) == 0:
            raise NoCrawlersException()

        while True:
            travels = set()

            for crawler in self.crawlers:
                travels.update(set(crawler.crawl()))

            if self.crawl_interval is None:
                break
            else:
                for travel in travels:
                    travel.save_or_update()

                sleep(self.crawl_interval.total_seconds())