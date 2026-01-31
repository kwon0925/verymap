import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

def crawl_shop_detail(url):
    """상점 상세 페이지 완전 크롤링"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print(f"크롤링 시작: {url}")
        driver.get(url)
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 전체 텍스트
        all_text = soup.get_text()
        
        detail = {
            'phone': '',
            'hours': '',
            'description': '',
            'address_detail': '',
            'price_info': '',
            'payment_methods': []
        }
        
        # 전화번호
        phone_match = re.search(r'(\d{2,3}[-.]?\d{3,4}[-.]?\d{4})', all_text)
        if phone_match:
            detail['phone'] = phone_match.group(1)
        
        # 페이지의 모든 텍스트를 줄 단위로 분석
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            # 영업시간
            if any(kw in line for kw in ['영업시간', '운영시간', 'Hours', '오픈']):
                detail['hours'] = line
                if i + 1 < len(lines):
                    detail['hours'] += ' ' + lines[i + 1]
            
            # VERY 단가
            if 'VERY 단가' in line or 'VERY단가' in line:
                if i + 1 < len(lines):
                    detail['price_info'] = lines[i + 1]
            
            # 결제비율
            if '결제비율' in line or '결제 비율' in line:
                if i + 1 < len(lines):
                    detail['payment_methods'].append(lines[i + 1])
        
        # 설명 (메타 태그에서)
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            detail['description'] = meta_desc.get('content', '')
        
        # 주소
        address_elem = soup.find(['p', 'div', 'span'], string=lambda x: x and '광주' in str(x))
        if address_elem:
            detail['address_detail'] = address_elem.get_text().strip()
        
        print("\n수집된 정보:")
        print(f"  전화번호: {detail['phone']}")
        print(f"  영업시간: {detail['hours']}")
        print(f"  가격정보: {detail['price_info']}")
        print(f"  주소상세: {detail['address_detail']}")
        
        return detail
        
    finally:
        driver.quit()

# 오리궁뎅이 백운점 크롤링
url = "https://pay.verychat.io/shops/cICyq"
detail = crawl_shop_detail(url)

# 기존 데이터 로드
with open('public/data/shops.json', 'r', encoding='utf-8') as f:
    shops = json.load(f)

# 오리궁뎅이 백운점 찾아서 업데이트
for shop in shops:
    if shop['name'] == '오리궁뎅이 백운점':
        shop.update(detail)
        print("\n오리궁뎅이 백운점 데이터 업데이트 완료!")
        break

# 저장
with open('public/data/shops.json', 'w', encoding='utf-8') as f:
    json.dump(shops, f, ensure_ascii=False, indent=2)

print("shops.json 저장 완료!")
