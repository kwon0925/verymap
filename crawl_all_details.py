import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

def crawl_shop_detail(url, driver):
    """상점 상세 페이지 완전 크롤링"""
    try:
        print(f"크롤링 중: {url}")
        driver.get(url)
        time.sleep(2)  # 페이지 로딩 대기
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_text = soup.get_text()
        
        detail = {
            'phone': '',
            'hours': '',
            'description': '',
            'address_detail': '',
            'price_info': '',
            'payment_methods': []
        }
        
        # 전화번호 추출
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
                        if len(phone) == 11 and phone.startswith('010'):
                            phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
                    detail['phone'] = phone
                    break
        
        # 페이지의 모든 텍스트를 줄 단위로 분석
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        # 매장 소개 정보 찾기
        description_parts = []
        found_intro = False
        
        for i, line in enumerate(lines):
            # 영업시간
            if any(kw in line for kw in ['영업시간', '운영시간', 'Hours', '오픈']):
                detail['hours'] = line
                if i + 1 < len(lines):
                    detail['hours'] += ' ' + lines[i + 1]
            
            # 매장 소개 시작점 찾기
            if any(kw in line for kw in ['오리불고기', '오리주물럭', '오리탕', '점심특선', '쌈밥', '신선한야채', '건강밥상', '결제', '베리']):
                found_intro = True
            
            # 매장 소개 정보 수집
            if found_intro:
                # VERY 단가나 결제비율 섹션 전까지 모든 줄 수집
                if any(kw in line for kw in ['VERY 단가', 'VERY단가', '결제비율', '결제 비율']):
                    if 'VERY 단가' in line or 'VERY단가' in line:
                        if i + 1 < len(lines):
                            detail['price_info'] = lines[i + 1]
                    if '결제비율' in line or '결제 비율' in line:
                        if i + 1 < len(lines):
                            detail['payment_methods'].append(lines[i + 1])
                    break
                
                # 의미있는 텍스트만 수집 (헤더/푸터 제외)
                skip_keywords = ['KR', 'verypay', 'verychain', 'verychat', 'veryads', 'VeryPay', 'Logo']
                if line and len(line) > 1:
                    if not any(skip in line for skip in skip_keywords):
                        if line not in description_parts:
                            description_parts.append(line)
        
        # 매장 소개를 하나의 문자열로 합치기
        if description_parts:
            detail['description'] = '\n'.join(description_parts)
        
        # 설명이 없으면 메타 태그에서 찾기
        if not detail['description']:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                detail['description'] = meta_desc.get('content', '')
        
        return detail
        
    except Exception as e:
        print(f"  [오류] 상세 페이지 크롤링 중 오류 발생 ({url}): {e}")
        return {
            'phone': '',
            'hours': '',
            'description': '',
            'address_detail': '',
            'price_info': '',
            'payment_methods': []
        }

# 메인 실행
if __name__ == '__main__':
    # 기존 데이터 로드
    with open('public/data/shops.json', 'r', encoding='utf-8') as f:
        shops = json.load(f)
    
    print(f"총 {len(shops)}개의 매장 상세 정보 크롤링 시작...")
    
    # 브라우저 설정
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        updated_count = 0
        for i, shop in enumerate(shops, 1):
            if not shop.get('link'):
                continue
            
            # 이미 상세 정보가 있는 경우 스킵 (선택사항)
            # if shop.get('phone') or shop.get('description'):
            #     continue
            
            detail = crawl_shop_detail(shop['link'], driver)
            
            # 기존 데이터에 상세 정보 업데이트
            shop.update(detail)
            updated_count += 1
            
            # 진행 상황 출력
            if i % 10 == 0:
                print(f"\n진행 상황: {i}/{len(shops)} ({updated_count}개 업데이트)")
            
            # 서버 부하 방지를 위한 대기
            time.sleep(1)
        
        print(f"\n총 {updated_count}개의 매장 상세 정보 크롤링 완료!")
        
        # 저장
        with open('public/data/shops.json', 'w', encoding='utf-8') as f:
            json.dump(shops, f, ensure_ascii=False, indent=2)
        
        print("shops.json 저장 완료!")
        
    finally:
        driver.quit()
