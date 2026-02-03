import json

# shops.json 읽기
with open('public/data/shops.json', 'r', encoding='utf-8') as f:
    shops = json.load(f)

print(f"총 매장 수: {len(shops)}개\n")

# 이름과 주소가 있는 매장 수
valid_shops = [s for s in shops if s.get('name') and s.get('name').strip() and s.get('address') and s.get('address').strip()]
print(f"이름과 주소가 있는 매장: {len(valid_shops)}개\n")

# 이름이 없는 매장
no_name = [s for s in shops if not s.get('name') or not s.get('name').strip()]
print(f"이름이 없는 매장: {len(no_name)}개")
if no_name:
    print("  샘플:")
    for shop in no_name[:3]:
        print(f"    - {shop}")

# 주소가 없는 매장
no_address = [s for s in shops if not s.get('address') or not s.get('address').strip()]
print(f"\n주소가 없는 매장: {len(no_address)}개")
if no_address:
    print("  샘플:")
    for shop in no_address[:3]:
        print(f"    - 이름: {shop.get('name', 'N/A')}")
