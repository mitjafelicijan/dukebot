import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from markdownify import markdownify

df = pd.read_csv("warcrafttavern.csv")

for index, row in df.dropna().iterrows():
    response = requests.get(row["url"])
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find("h1")
        content = soup.find("div", id="ftwp-postcontent")

        if title and content:
            print(f"> {row['category']} -> {title.text.strip()}")
            
            category_directory = f"../corpus/{row['category']}"
            if not os.path.exists(category_directory):
                os.makedirs(category_directory)

            with open(f"{category_directory}/{row['slug']}.md", "w") as fp:
                fp.write(f"# {title.text.strip()}\n\n")
                fp.write(f"{markdownify(str(content))}")
