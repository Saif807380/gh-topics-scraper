import click
from .scraper import GithubScraper

gh_scraper = GithubScraper()

@click.group()
def ghs():
    pass

@ghs.command()
@click.option(
    "-f",
    "--file-name", 
    type=click.Path(writable=True),
    help="Generates list of topics"
)
def init(file_name):
    gh_scraper.scrape_topics_page(file_name)

@ghs.command()
def topics():
    gh_scraper.list_all_topics()

@ghs.command()
@click.argument("topic", nargs=1)
def scrape(topic):
    gh_scraper.scrape_repos_of_topic(topic)

if __name__ == "__main__":
    ghs()