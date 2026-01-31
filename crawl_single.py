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
        
        # 디버깅: HTML 저장
        with open('debug_shop_detail.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("디버그: HTML 저장 완료 (debug_shop_detail.html)")
        
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
        
        # 전화번호 - 더 정확한 패턴
        # 010-xxxx-xxxx, 010-xxxx-xxxx, 02-xxx-xxxx 등
        phone_patterns = [
            r'010[-.\s]?\d{4}[-.\s]?\d{4}',  # 010-xxxx-xxxx
            r'\+82[-.\s]?10[-.\s]?\d{4}[-.\s]?\d{4}',  # +82-10-xxxx-xxxx
            r'02[-.\s]?\d{3,4}[-.\s]?\d{4}',  # 02-xxx-xxxx
            r'0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}',  # 기타 지역번호
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, all_text)
            if phone_match:
                phone = phone_match.group(0).replace(' ', '').replace('.', '-')
                # 주소의 숫자 패턴 제외 (72-1 같은 것)
                if not re.match(r'^\d{1,2}-\d{1,2}$', phone):
                    # +82-10-xxxx-xxxx 형식을 010-xxxx-xxxx로 변환
                    if phone.startswith('+82'):
                        phone = phone.replace('+82', '0').replace('-', '')
                        # 010xxxxxxxx 형식을 010-xxxx-xxxx로 변환
                        if len(phone) == 11 and phone.startswith('010'):
                            phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
                    detail['phone'] = phone
                    break
        
        # 페이지의 모든 텍스트를 줄 단위로 분석
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        # 전체 텍스트에서 매장 소개 부분 찾기 (한 줄에 모든 정보가 있을 수 있음)
        description_parts = []
        
        for i, line in enumerate(lines):
            # 영업시간
            if any(kw in line for kw in ['영업시간', '운영시간', 'Hours', '오픈']):
                detail['hours'] = line
                if i + 1 < len(lines):
                    detail['hours'] += ' ' + lines[i + 1]
            
            # 매장 소개가 포함된 줄 찾기
            if any(kw in line for kw in ['오리불고기', '오리주물럭', '오리탕', '점심특선', '쌈밥', '신선한야채', '건강밥상']):
                # 한 줄에 모든 정보가 있을 수 있으므로 분리
                # "오리불고기전문점", "오리주물럭(매꼼.맛짱)", "오리탕" 등을 찾아서 분리
                
                # 정규식으로 메뉴 정보 추출
                menu_patterns = [
                    r'오리불고기전문점',
                    r'오리주물럭\([^)]+\)',
                    r'오리탕',
                    r'점심특선[ㅡ-]?쌈밥정식',
                    r'\(신선한야채[^)]+건강밥상\)',
                    r'결제\s*\d+%\.\s*1베리\s*\d+원'
                ]
                
                for pattern in menu_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if match not in description_parts:
                            description_parts.append(match)
                
                # 패턴으로 찾지 못한 경우, 키워드 기준으로 분리 시도
                if not description_parts:
                    # "오리불고기전문점" 찾기
                    if '오리불고기전문점' in line:
                        description_parts.append('오리불고기전문점')
                    
                    # "오리주물럭(매꼼.맛짱)" 찾기
                    if '오리주물럭' in line:
                        start = line.find('오리주물럭')
                        end = line.find(')', start) + 1 if ')' in line[start:] else start + 20
                        menu_item = line[start:end]
                        if menu_item not in description_parts:
                            description_parts.append(menu_item)
                    
                    # "오리탕" 찾기
                    if '오리탕' in line and '오리탕' not in description_parts:
                        description_parts.append('오리탕')
                    
                    # "점심특선ㅡ쌈밥정식" 찾기
                    if '점심특선' in line or '쌈밥정식' in line:
                        if '점심특선' in line:
                            start = line.find('점심특선')
                            end = line.find('정식', start) + 2 if '정식' in line[start:] else start + 10
                            lunch = line[start:end]
                            if lunch not in description_parts:
                                description_parts.append(lunch)
                    
                    # "(신선한야채랑 함께하는건강밥상)" 찾기
                    if '신선한야채' in line or '건강밥상' in line:
                        if '(' in line and ')' in line:
                            start = line.find('(')
                            end = line.find(')', start) + 1
                            veggie = line[start:end]
                            if veggie not in description_parts:
                                description_parts.append(veggie)
                    
                    # "결제 100%. 1베리 10원" 찾기
                    if '결제' in line and '베리' in line:
                        payment_match = re.search(r'결제\s*\d+%\.\s*1베리\s*\d+원', line)
                        if payment_match:
                            payment_info = payment_match.group(0)
                            if payment_info not in description_parts:
                                description_parts.append(payment_info)
        
        # 매장 소개를 하나의 문자열로 합치기
        if description_parts:
            detail['description'] = '\n'.join(description_parts)
        
        # 설명이 없으면 메타 태그에서 찾기
        if not detail['description']:
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
        print(f"  매장소개: {detail['description'][:100] if detail['description'] else '없음'}...")
        
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
