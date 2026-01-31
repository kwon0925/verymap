import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

def crawl_shop_detail(driver, shop_url):
    """개별 상점 상세 페이지 크롤링"""
    try:
        print(f"   상세 페이지 방문: {shop_url}")
        driver.get(shop_url)
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        detail_info = {
            'phone': '',
            'hours': '',
            'description': ''
        }
        
        # 전체 텍스트에서 전화번호 패턴 찾기
        all_text = soup.get_text()
        phone_patterns = [
            r'(\d{2,3}[-.\s]?\d{3,4}[-.\s]?\d{4})',
            r'(010-?\d{4}-?\d{4})',
            r'(02-?\d{3,4}-?\d{4})'
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, all_text)
            if phone_match:
                detail_info['phone'] = phone_match.group(1).strip()
                print(f"      전화번호 발견: {detail_info['phone']}")
                break
        
        # tel: 링크에서 전화번호 찾기
        if not detail_info['phone']:
            tel_link = soup.find('a', href=lambda x: x and x.startswith('tel:'))
            if tel_link:
                detail_info['phone'] = tel_link['href'].replace('tel:', '').strip()
                print(f"      전화번호(링크): {detail_info['phone']}")
        
        # 영업시간 찾기
        hours_keywords = ['영업시간', '운영시간', 'Hours', 'Open', '오픈']
        for elem in soup.find_all(['p', 'div', 'span']):
            text = elem.get_text()
            if any(keyword in text for keyword in hours_keywords):
                detail_info['hours'] = text.strip()
                print(f"      영업시간: {detail_info['hours'][:30]}...")
                break
        
        # 설명 찾기 (긴 텍스트)
        for elem in soup.find_all(['p', 'div']):
            text = elem.get_text().strip()
            if len(text) > 50 and len(text) < 500:
                detail_info['description'] = text
                print(f"      설명: {text[:30]}...")
                break
        
        return detail_info
        
    except Exception as e:
        print(f"      오류: {e}")
        return None

# 테스트: 오리궁뎅이 백운점만 크롤링
print("=" * 60)
print("[테스트] 오리궁뎅이 백운점 상세 크롤링")
print("=" * 60)

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 테스트할 상점
test_shop = {
    "name": "오리궁뎅이 백운점",
    "link": "https://pay.verychat.io/shops/cICyq"
}

print(f"\n[크롤링] {test_shop['name']}")
detail = crawl_shop_detail(driver, test_shop['link'])

if detail:
    print("\n[결과]")
    print(f"  전화번호: {detail['phone'] or '없음'}")
    print(f"  영업시간: {detail['hours'] or '없음'}")
    print(f"  설명: {detail['description'][:100] if detail['description'] else '없음'}...")
else:
    print("\n[결과] 크롤링 실패")

driver.quit()
print("\n[완료] 테스트 종료")
