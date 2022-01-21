import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

class GithubScraper:
    def __init__(self) -> None:
        self.BASE_URL = "https://github.com"
        self.topics_end_page = 6
        self.TOPICS_DF_PATH = "datasets/topics.csv"
        self.topics_df = None
        if os.path.exists(self.TOPICS_DF_PATH):
            self.topics_df = pd.read_csv(self.TOPICS_DF_PATH)

    def scrape_topics_page(self, file_name):
        if file_name is not None:
            self.TOPICS_DF_PATH = file_name
        page_content = ""
        topics_start_page = 1

        while topics_start_page <= self.topics_end_page:
            print(f"Scraping /topics?page={topics_start_page}")
            topics_page_url = f"{self.BASE_URL}/topics?page={topics_start_page}"
            r = requests.get(topics_page_url)
            if r.status_code != 200:
                print(f"Unable to load page {topics_page_url}")
            else:
                page_content += f"\n{r.text}"
            topics_start_page += 1

        soup = BeautifulSoup(page_content,'html.parser')

        # extracting topic titles
        topic_title_ptags = soup.find_all('p',{'class':'f3 lh-condensed mb-0 mt-1 Link--primary'})
        topic_titles =[]
        for title in topic_title_ptags:
            topic_titles.append(title.text)
            
        # extracting description
        desc_ptags = soup.find_all('p',{'class':'f5 color-fg-muted mb-0 mt-1'})
        topic_descs =[]
        for desc in desc_ptags:
            topic_descs.append(desc.text.strip())
            
        # extracting topic urls
        topic_url_tags = soup.find_all('a',{'class':'no-underline flex-1 d-flex flex-column'})
        topic_urls =[]
        for url in topic_url_tags:
            topic_urls.append(self.BASE_URL + url['href'])
            
        # creating a dictionary to store the scraped data
        topics_dict = {
            'Topics': topic_titles,
            'Description': topic_descs,
            'Topic_URL': topic_urls
        }

        df = pd.DataFrame(topics_dict)
        df.to_csv(self.TOPICS_DF_PATH, index=False)

    def scrape_repos_of_topic(self, topic_name: str):
        if self.topics_df is None:
            print("No topics.csv found. Run 'ghs init' first")
            return
        topic = self.topics_df[self.topics_df["Topics"] == topic_name]
        if len(topic) == 0:
            print("Topic not found. Run 'ghs topics' to see list of supported topics.")
            return
        topic_url = topic["Topic_URL"].iloc[0] + "?o=desc&s=stars&page="
        repo_page_start = 1
        page_content = ''
        while repo_page_start <= 4:
            print(f"Scraping page={repo_page_start}")
            r = requests.get(topic_url + str(repo_page_start))
            if r.status_code != 200:
                print(f"Unable to load page {topic_url + str(repo_page_start)}")
                return
            page_content += f"\n{r.text}"
            repo_page_start += 1
        soup = BeautifulSoup(page_content,'html.parser')

        # get star count for repos
        star_spans = soup.find_all("span", { "id": "repo-stars-counter-star" }, limit=100)
        stars = self.__parse_stars(star_spans)

        h3_tags = soup.find_all("h3", { "class": "f3 color-fg-muted text-normal lh-condensed"}, limit=100)

        usernames, repo_names, repo_urls = self.__parse_repo_details(h3_tags)

        df = pd.DataFrame({
            "Owner": usernames,
            "Repository Name": repo_names,
            "Repository Url": repo_urls,
            "Stars Received": stars
        })

        df.to_csv(f"datasets/{topic_name}.csv", index=False)

    def list_all_topics(self):
        if self.topics_df is None:
            print("No topics.csv found. Run ghs init first")
            return
        print("Below is the list of supported topics: ")
        for _, row in self.topics_df.iterrows():
            print(row["Topics"])

    def __parse_stars(self, star_spans):
        return list(map(lambda span: span["title"], star_spans))

    def __parse_repo_details(self, h3_tags):
        usernames, repo_names, repo_urls = [], [], []
        for tag in h3_tags:
            a_tags = tag.find_all("a")
            usernames.append(a_tags[0].text.strip())
            repo_names.append(a_tags[1].text.strip())
            repo_urls.append(self.BASE_URL + a_tags[1]["href"])
        
        return usernames, repo_names, repo_urls