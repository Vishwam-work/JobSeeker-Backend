import json

with open('./master/master_json/currency.json', encoding='utf-8') as f:
    data = json.load(f)

fixture = []
for idx, (currency_code, currency_info) in enumerate(data.items(), start=1):
    fixture.append({
        "model": "master.currency",
        "pk": idx,
        "fields": {
            "name": currency_info["name"],
            "symbol": currency_info["symbol"]
        }
    })

# Save the fixture
with open('./master/master_json/currency_fixture.json', 'w', encoding='utf-8') as f:
    json.dump(fixture, f, indent=4, ensure_ascii=False)