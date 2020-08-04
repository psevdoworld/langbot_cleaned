import bs4
import requests
urls_list = []
for page in range(1, 4):
	res = requests.get(f"https://www.englishdom.com/skills/glossary/?page={page}")
	soup = bs4.BeautifulSoup(res.text)
	links = soup.find_all("a", {"class":"b-set b-second-bg js-filter-list-item tutorial_glossary_system-set phn__glossary__wordset__item-link"})
	for link in links:
		urls_list.append(link.get("href"))
print(len(urls_list))

