import json
from collections import OrderedDict

# Load your majors.json file
with open('./master/master_json/majors.json', encoding='utf-8') as f:
    data = json.load(f)

fixtures = []
category_map = {}
category_pk = 1
major_pk = 1

for item in data:
    category_name = item.get("Major_Category")

    if category_name not in category_map:
        category_map[category_name] = category_pk

        fixtures.append({
            "model": "master.majorcategory",
            "pk": category_pk,
            "fields": {
                "name": category_name if category_name else "Unknown"
            }
        })
        category_pk += 1

    # ---------- Create Major entry ----------
    fixtures.append({
        "model": "master.major",
        "pk": major_pk,
        "fields": {
            "code": item["FOD1P"],
            "name": item["Major"],
            "category": category_map[category_name]
        }
    })

    major_pk += 1

# Save fixture file
with open('./master/master_json/major_fixture.json', "w", encoding="utf-8") as f:
    json.dump(fixtures, f, indent=4, ensure_ascii=False)

print("Fixture created successfully!")
