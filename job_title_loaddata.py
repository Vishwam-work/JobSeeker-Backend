import json

with open('./job_titles.json') as f:
    data = json.load(f)

fixtures = []
category_pk = 1
title_pk = 1

category_pk_map = {}  # map for assigning FK to titles

for item in data:
    category_name = item['category']
    titles = item['keywords']

    # Create JobCategory fixture
    category_fixture = {
        "model": "master.jobcategory",
        "pk": category_pk,
        "fields": {
            "name": category_name
        }
    }
    fixtures.append(category_fixture)
    category_pk_map[category_name] = category_pk
    category_pk += 1

    # Create JobTitle fixtures
    for title in titles:
        full_title = ' '.join(title).strip()
        title_fixture = {
            "model": "master.jobtitle",
            "pk": title_pk,
            "fields": {
                "title": full_title,
                "category": category_pk_map[category_name]
            }
        }
        fixtures.append(title_fixture)
        title_pk += 1

# Save to job_titles_fixture.json
with open('./master/master_json/job_titles_fixture.json', 'w', encoding='utf-8') as f:
    json.dump(fixtures, f, indent=4)
