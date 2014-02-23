import feedparser
import time
import urllib
import os
from bs4 import BeautifulSoup
import logging as l
import urlparse

def prettify(content):
    """Prettify without adding <html> and <body>"""
    content.html.unwrap()
    content.body.unwrap()
    return content.prettify()

def blogger2fields_html(file, download_images=False, output_path=None, blogger_only_images=False):
    """Import Blogger XML file"""

    # Downloading images only from Blogger implies downloading images.
    if blogger_only_images:
        download_images = True

    images_path = os.path.join(output_path, "images")
    if download_images:
        try:
            os.makedirs(images_path)
        except:
            pass

    def entry2fields(entry, download_images):
        date = time.strftime("%Y-%m-%d %H:%M", entry.published_parsed)
        filename = entry.link.rsplit('/',1)[-1].split(".")[0]
        tags = [e['term'] for e in entry.tags if e['term'].find("blogger")<0] if hasattr(entry, "tags") else None
        kind = "article"
        content = BeautifulSoup(entry.content[0]["value"])
        if download_images:
            for img in content.findAll("img"):
                for attr_name, tag in [("src", img), ("href", img.find_parent(name="a"))]:
                    if tag:
                        img_url = tag.get(attr_name)
                        if not blogger_only_images or (blogger_only_images and 'bp.blogspot.com' in img_url):
                            # path is of the form:
                            # 'http://4.bp.blogspot.com/.../s640/awsjobdetails.png'
                            # where s640 is the size
                            img_filename = "_".join([filename] + urlparse.urlsplit(img_url).path.split("/")[-2:])
                            img_local_path = os.path.join(images_path, img_filename)
                            l.warning("Retrieving %s" % img_url)
                            urllib.urlretrieve(img_url, img_local_path)
                            img_pelican_url = "/".join(["|filename|", "images", img_filename])
                            tag[attr_name] = img_pelican_url
        return entry.title, prettify(content), filename, date, entry.authors[0]["name"], [], tags, kind, "md"

    feedparser.SANITIZE_HTML = False
    feed = feedparser.parse(file)

    posts = []
    for entry in feed["entries"]:
        kind = [e for e in entry.tags if e["scheme"].endswith("kind")][0]["term"].split("#")[-1]
        if kind == "post":
            posts.append(entry)

    return [entry2fields(entry, download_images) for entry in posts]

if __name__ == "__main__":
    from pelican.tools import pelican_import
    import argparse

    parser = argparse.ArgumentParser(
    description="Transform Blogger export XML file to Markdown (actually HTML)",
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(dest='input', help='The input file to read')
    parser.add_argument('--download-images', action='store_true', dest='download_images',
        help='Download images locally')
    parser.add_argument('-o', '--output', dest='output', default='output',
        help='Output path')
    parser.add_argument('--only-blogger-images', action='store_true', dest='blogger_only_images',
                        help='Download images only from Blogger (implies --download-images)')
    args = parser.parse_args()

    fields = blogger2fields_html(args.input, download_images=args.download_images or False, output_path=args.output,
                                 blogger_only_images=args.blogger_only_images or False)
    pelican_import.fields2pelican(fields, out_markup="markdown", output_path=args.output)
