import json

# shops.json 읽기
with open('public/data/shops.json', 'r', encoding='utf-8') as f:
    shops = json.load(f)

# 한국 시도 목록
korean_sidos = [
    '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', 
    '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원특별자치도',
    '충청북도', '충청남도', '전북특별자치도', '전라남도', '경상북도', 
    '경상남도', '제주특별자치도'
]

# 축약형 패턴
sido_patterns = {
    '서울특별시': ['서울'],
    '부산광역시': ['부산'],
    '대구광역시': ['대구'],
    '인천광역시': ['인천'],
    '광주광역시': ['광주'],
    '대전광역시': ['대전'],
    '울산광역시': ['울산'],
    '세종특별자치시': ['세종'],
    '경기도': ['경기'],
    '강원특별자치도': ['강원'],
    '충청북도': ['충북', '충청북'],
    '충청남도': ['충남', '충청남'],
    '전북특별자치도': ['전북', '전라북', '전라북도'],
    '전라남도': ['전남', '전라남'],
    '경상북도': ['경북', '경상북'],
    '경상남도': ['경남', '경상남'],
    '제주특별자치도': ['제주'],
}

def is_korean_shop(shop):
    address = shop.get('address', '').replace(' ', '')
    if not address:
        return False
    
    # 시도 이름 직접 포함 확인
    for sido in korean_sidos:
        if sido in address:
            return True
    
    # 축약형 패턴 확인
    for sido, patterns in sido_patterns.items():
        for pattern in patterns:
            if pattern in address:
                return True
    
    return False

# 한국 매장 필터링
korean_shops = [s for s in shops if is_korean_shop(s)]
print(f"한국 매장 총 수: {len(korean_shops)}개\n")

# VERY 단가가 있는 한국 매장
korean_with_price = []
for shop in korean_shops:
    price = shop.get('veryPrice', '')
    if price and price != '-':
        # 원 단위만 확인
        if '원' in price:
            korean_with_price.append(shop)

print(f"VERY 단가가 있는 한국 매장: {len(korean_with_price)}개\n")

# 원 단위가 있는 한국 매장 (평균 단가 계산 기준)
won_prices = []
for shop in korean_shops:
    price = shop.get('veryPrice', '')
    if price and price != '-':
        if '원' in price:
            # 숫자 추출
            import re
            number_match = re.search(r'[\d,]+\.?\d*', price)
            if number_match:
                won_prices.append(shop)

print(f"원 단위 VERY 단가가 있는 한국 매장: {len(won_prices)}개")
