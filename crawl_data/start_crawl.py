import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from tqdm import tqdm


class RealEstateScraper:
    BASE_URL = "https://hanoirealestate.com.vn"
    USER_AGENT = "Your User-Agent"
    SESSION_COOKIE = "Your Cookie Value"

    def __init__(self):
        self.headers = {
            "User-Agent": RealEstateScraper.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
        self.cookies = {"session_cookie": RealEstateScraper.SESSION_COOKIE}
    def main_page_links(self, i):
        return f"https://hanoirealestate.com.vn/vi/cho-thue-can-ho/next-page-{i}.html"
    def get_full_url(self, path):
        return f"{RealEstateScraper.BASE_URL}{path}"

    def get_page_content(self, url):
        try:
            response = requests.get(url, headers=self.headers, cookies=self.cookies)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_property_links(self, url):
        soup = self.get_page_content(url)
        if soup:
            ulpro = soup.find("ul", class_="ulpro")
            if ulpro:
                return [
                    self.get_full_url(li.find("a")["href"])
                    for li in ulpro.find_all("li")
                ]
        return []

    def extract_property_data(self, url):
        soup = self.get_page_content(url)
        if soup:
            try:
                title = soup.find("h1").text
                price = soup.find("div", class_="proright").find("span").text
                image_wrapper = soup.find(
                    "div", class_="property-gallery-preview property-box-image-inner"
                )
                image_urls = [
                    self.get_full_url(img["src"])
                    for img in image_wrapper.find_all("img")
                ]

                props = soup.find("ul", class_="ultech").find_all("li")
                property_info = {
                    prop.text.split(":\xa0")[0]: prop.text.split(":\xa0")[1]
                    for prop in props
                }

                description_parts = soup.find("div", class_="dbox").find_all("div")
                description = "\n".join(p.text.strip() for p in description_parts)
                id = soup.find("div", class_="proleft").find("span").text
                return {
                    "title": title,
                    "price": price,
                    "image_urls": image_urls,
                    "property_info": property_info,
                    "description": description,
                    "id": id,
                }
            except (AttributeError, IndexError) as e:
                print(f"Error parsing property data: {e}")
        return {}


def main():
    scraper = RealEstateScraper()
    N_PAGE = 10
    page_links = [scraper.main_page_links(i) for i in range(1, N_PAGE + 1)]
    total_data = []
    for main_page_url in tqdm(page_links):
        property_links = scraper.get_property_links(main_page_url)
        properties_data = [scraper.extract_property_data(link) for link in property_links]
        total_data.extend(properties_data)

    with open("estate_data.json", "w", encoding="utf-8") as f:
        json.dump(total_data, f, indent=4, ensure_ascii=False)

    df = pd.DataFrame(total_data).to_csv("estate_data.csv", index=False)
    # Further processing with df if needed


if __name__ == "__main__":
    main()
