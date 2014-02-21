Import Blogger posts as html in a Pelican blog
==============================================

This Python script parses a Blogger XML export and writes
all posts as Markdown files, WITHOUT converting
HTML to Markdown, Markdown also allows raw HTML.

With this method we have a more reliable import, with
the downside that our old posts will be more difficult 
to edit of course.

It also supports download images locally, just add
`--download-images` as command line argument.

Run as:

    python pelican_import_blogger_html.py blogger_export_file.xml --output=mypelicansite/content/
