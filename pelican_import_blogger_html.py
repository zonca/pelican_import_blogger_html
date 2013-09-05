import feedparser
import time

def blogger2fields_html(file):
    """Import Blogger XML file"""

    def entry2fields(entry):
        date = time.strftime("%Y-%m-%d %H:%M", entry.updated_parsed)
        filename = entry.link.rsplit('/',1)[-1].split(".")[0]
        tags = [e['term'] for e in entry.tags if e['term'].find("blogger")<0] if hasattr(entry, "tags") else None
        kind = "article"
        return entry.title, entry.content[0]["value"], filename, date, entry.authors[0]["name"], [], tags, kind, "md"

    feedparser.SANITIZE_HTML = False
    feed = feedparser.parse(file)

    posts = []
    for entry in feed["entries"]:
        kind = [e for e in entry.tags if e["scheme"].endswith("kind")][0]["term"].split("#")[-1]
        if kind == "post":
            posts.append(entry)

    return [entry2fields(entry) for entry in posts]

if __name__ == "__main__":
    from pelican.tools import pelican_import
    import argparse

    parser = argparse.ArgumentParser(
    description="Transform Blogger export XML file to Markdown (actually HTML)",
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(dest='input', help='The input file to read')
    parser.add_argument('-o', '--output', dest='output', default='output',
        help='Output path')
    args = parser.parse_args()

    fields = blogger2fields_html(args.input)
    pelican_import.fields2pelican(fields, out_markup="markdown", output_path=args.output)
