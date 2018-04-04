import json
from urllib.request import urlopen

data = json.loads(urlopen("http://95.46.45.206:8000/public/goods").read())

with open("DeluxeMenu_info.json", "w") as file:
    json.dump(data, file, indent=4)
menu = {}

# Adding categories
for position in data:
    menu[position['subCategoryResponse']['categoryResponse']['name']]\
        = dict()
# Adding subcategories as values of appropriate categories
for position in data:
    category = position['subCategoryResponse']['categoryResponse']['name']
    menu[category].update({position['subCategoryResponse']['name']: []})

# Adding dishes to an appropriate subcategory
for position in data:
    category = position['subCategoryResponse']['categoryResponse']['name']
    subcategory = position['subCategoryResponse']['name']
    menu[category][subcategory].append(position['name'])


print(menu)
