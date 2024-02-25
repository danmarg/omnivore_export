import argparse
import os.path
import json

from omnivoreql import OmnivoreQL
from retry import retry


def main():
    parser = argparse.ArgumentParser(description="Backup Omnivore")
    parser.add_argument(
        "--backup", type=str, default="./export", help="Backup directory"
    )
    parser.add_argument("--api_key", type=str, help="API Key")
    args = parser.parse_args()

    if not args.api_key:
        print("Missing required API key!")
        return
    omnivoreql_client = OmnivoreQL(args.api_key)

    @retry(delay=1, backoff=2)
    def get_articles(cursor=None):
        print(f"Fetching page {cursor if cursor else 0}...")
        page = omnivoreql_client.get_articles(cursor=cursor)["search"]
        if not page["pageInfo"]["hasNextPage"]:
            return page["edges"]
        return page["edges"] + get_articles(cursor=page["pageInfo"]["endCursor"])

    @retry(delay=1, backoff=2)
    def get_article(slug):
        return omnivoreql_client.get_article(
                omnivoreql_client.get_profile()["me"]["profile"]["username"],
                slug, format="markdown")["article"]["article"]

    pages = get_articles()

    for article in pages:
        print(f'Saving {article["node"]["slug"]}...')
        path = os.path.join(args.backup, article["node"]["slug"])
        if os.path.exists(path):
            continue
        # Get content
        article = get_article(article["node"]["slug"])
        content = article["content"]
        del article["content"]

        os.mkdir(path)
        with open(os.path.join(path, "meta.json"), "w") as meta:
            with open(os.path.join(path, "content.md"), "w") as markdown:
                markdown.write(content)
                json.dump(article, meta)


main()
