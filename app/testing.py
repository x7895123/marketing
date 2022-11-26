from urllib.parse import unquote

s = '%7b%22cashdesk%22%3a%22aqua%22%7d'


print(unquote(s))