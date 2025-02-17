import xml.etree.ElementTree as ET
from jinja2 import Template
import shutil
import os

# Parse the XML file
tree = ET.parse('books.xml')
root = tree.getroot()

# Define the Jinja2 template
template_str = '''
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Book Catalog</title>
    <style>
        .book {
            display: inline-block;
            margin: 10px;
        }
        .book img {
            width: 200px;
            height: 300px;
        }
        .book-info {
            display: none;
        }
        .book:hover .book-info {
            display: block;
            position: absolute;
            z-index: 1;
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            padding: 10px;
            max-width: 400px;
        }
    </style>
</head>
<body>
    {% for book in books %}
        <div class="book">
            <a href="#">
                <img src="{{ book.cover }}" alt="{{ book.title }}" />
            </a>
            <div class="book-info">
                <h2>{{ book.title }}</h2>
                <p><strong>Author:</strong> {{ book.authors }}</p>
                <p><strong>Language:</strong> {{ book.language }}</p>
                <p><strong>ISBN:</strong> {{ book.isbn }}</p>
                <p><strong>Publisher:</strong> {{ book.publisher }}</p>
                <p><strong>Published Date:</strong> {{ book.pubdate }}</p>
                <p><strong>Comments:</strong> {{ book.comments }}</p>
                <p><strong>Links:</strong>
                    <ul>
                        {% for link in book.links %}
                            <li><a target="_blank" href="{{ link.url }}">{{ link.name }}</a></li>
                        {% endfor %}
                    </ul>
                </p>
            </div>
        </div>
    {% endfor %}
</body>
</html>
'''
# Create a directory to store the cover images
os.makedirs('dist', exist_ok=True)
os.makedirs('dist/covers', exist_ok=True)

def make_safe_filename(filename):
    return "".join(c for c in filename if c.isalnum()).rstrip()

def copy_cover_image(cover_path):
    # Copy over cover images
    cover_path = "book-default-cover.jpg" if cover_path is None else cover_path
    _, file_extension = os.path.splitext(cover_path)
    parent_dir, _ = os.path.split(cover_path)
    grandparent_dir, parent_dir = os.path.split(parent_dir)
    _, grandparent_dir = os.path.split(grandparent_dir)
    new_image_path = os.path.join('covers', make_safe_filename(grandparent_dir + parent_dir) + file_extension)
    shutil.copy2(cover_path, os.path.join('dist',new_image_path))
    return new_image_path

def build_links(identifiers, title):
    links = []
    if identifiers is not None:
        for identifier in identifiers.split(','):
            key, value = identifier.split(':')
            if key == 'google':
                links.append({
                    'name': 'Google Books',
                    'url': 'https://books.google.com/books?id=' + value
                })
            elif key == 'amazon':
                links.append({
                    'name': 'Amazon',
                    'url': 'https://www.amazon.de/dp/' + value
                })
    # If no links were found or only one from google, add a link to Amazon
    if len(links) == 0 or (len(links) == 1 and links[0]['name'] == 'Google Books'):
        links.append({
            'name': 'Amazon Search',
            'url': 'https://www.amazon.de/gp/search?ie=UTF8&index=books&keywords=' + title
        })
    return links

# Extract book data from XML file
books = []
for record in root.iter('record'):
    cover_path = record.find('cover').text if record.find('cover') is not None else None
    title = record.find('title').text if record.find('title') is not None else None
    identifiers = record.find('identifiers').text if record.find('identifiers') is not None else None
    book = {
        'id': record.find('id').text,
        'title': title,
        'authors': ', '.join([author.text for author in record.findall('authors/author')]),
        'language': record.find('languages').text if record.find('languages') is not None else None,
        'cover': copy_cover_image(cover_path),
        'publisher': record.find('publisher').text if record.find('publisher') is not None else None,
        'isbn': record.find('isbn').text if record.find('isbn') is not None else None,
        'comments': record.find('comments').text if record.find('comments') is not None else None,
        'pubdate': record.find('pubdate').text if record.find('pubdate') is not None else None,
        'links': build_links(identifiers, title)
    }
    books.append(book)


# Render the HTML code with the Jinja2 template
template = Template(template_str)
html_code = template.render(books=books)

# Write the HTML code to a file
with open('dist/index.html', 'w', encoding="utf-8") as f:
    f.write(html_code)
