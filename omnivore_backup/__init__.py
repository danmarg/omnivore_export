import argparse
import os.path
import csv
import datetime
import json

from omnivoreql import OmnivoreQL
from retry import retry


def main():
    parser = argparse.ArgumentParser(description="Backup Omnivore")
    parser.add_argument(
        "--backup", type=str, default="", help="Backup directory"
    )
    parser.add_argument(
        # Export in Instapaper format: URL,Title,Selection,Folder,Timestamp
        "--csv", type=str, default="", help="CSV to export URLs to"
    )
    parser.add_argument("--api_key", type=str, help="API Key")
    args = parser.parse_args()

    if not args.api_key:
        print("Missing required API key!")
        return
    omnivoreql_client = OmnivoreQL(args.api_key)

    @retry(delay=1, backoff=2)
    def get_articles(cursor=0):
        print(f"Fetching page {cursor if cursor else 0}...")
        page = omnivoreql_client.get_articles(query="in:all", after=cursor)["search"]
        if not page["pageInfo"]["hasNextPage"]:
            return page["edges"]
        return page["edges"] + get_articles(cursor=page["pageInfo"]["endCursor"])

    @retry(delay=1, backoff=2)
    def get_article(slug):
        return omnivoreql_client.get_article(
                omnivoreql_client.get_profile()["me"]["profile"]["username"],
                slug, format="markdown")["article"]["article"]

    pages = get_articles()

    writer = None
    csv_writer = None
    if args.csv:
        writer = open(args.csv, "w", newline="")
        csv_writer = csv.writer(writer, delimiter=",")
        csv_writer.writerow(["URL", "Title", "Selection", "Folder", "Timestamp"])
    for article in pages:
        print(f'Saving {article["node"]["slug"]}...')
        if args.backup:
            path = os.path.join(args.backup, article["node"]["slug"])
            meta = article["node"]
            if os.path.exists(path):
                # Update the metadata only:
                with open(os.path.join(path, "meta.json"), "w") as metadata:
                    json.dump(meta, metadata)
                continue
            # Get content:
            os.mkdir(path)
            content = get_article(article["node"]["slug"])["content"]
            with open(os.path.join(path, "meta.json"), "w") as metadata:
                json.dump(meta, metadata)
            with open(os.path.join(path, "content.md"), "w") as markdown:
                markdown.write(content)
        if args.csv:
            folder = "Unread"
            labels = article["node"]["labels"]
            if labels:
                folder = labels[0]["name"]
            elif article["node"]["isArchived"]:
                folder = "Archive"
            csv_writer.writerow([
                article["node"]["url"], 
                article["node"]["title"],
                "",
                folder,
                int(datetime.datetime.fromisoformat(article["node"]["createdAt"]).timestamp())
                ,
            ])




main()
