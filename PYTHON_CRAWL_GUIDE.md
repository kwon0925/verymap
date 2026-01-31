# Python 크롤링 가이드

## 🐍 Python으로 크롤링하기

TypeScript/Puppeteer 대신 Python + Selenium을 사용한 더 안정적인 크롤링 방법입니다.

## 📋 사전 준비

### 1. Python 설치
- Python 3.8 이상 필요
- [python.org](https://www.python.org/downloads/)에서 다운로드

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install selenium beautifulsoup4 pandas webdriver-manager
```

## 🚀 크롤링 실행

### 기본 실행 (브라우저 창 보이기)
```bash
python crawl_python.py
```

### 백그라운드 실행 (헤드리스)
`crawl_python.py` 파일에서 아래 줄의 주석을 해제:
```python
chrome_options.add_argument("--headless")
```

그 후 실행:
```bash
python crawl_python.py
```

## 📊 실행 과정

1. ✅ Chrome 드라이버 자동 다운로드 및 설정
2. ✅ VeryPay 상점 페이지 접속
3. ✅ "더보기" 버튼 자동 클릭 (최대 628개 로드)
4. ✅ 모든 상점 데이터 수집
5. ✅ 데이터 파싱 및 정리
6. ✅ 자동 저장:
   - `data/verychat_shops.csv` - CSV 파일
   - `data/shops.json` - 백업용 JSON
   - `public/data/shops.json` - 웹앱용 JSON

## 📁 결과 파일

### CSV 파일 (`data/verychat_shops.csv`)
- Excel에서 바로 열어볼 수 있음
- 데이터 분석에 용이

### JSON 파일 (`public/data/shops.json`)
- 웹앱에서 자동으로 사용됨
- 브라우저에서 바로 로드

## ⏱️ 예상 소요 시간

- 약 **2~4분** (네트워크 속도에 따라 다름)
- 628개 상점 기준

## 🔧 트러블슈팅

### 오류: "Chrome driver not found"
```bash
pip install --upgrade webdriver-manager
```

### 오류: "No module named 'selenium'"
```bash
pip install selenium
```

### 오류: "Permission denied"
관리자 권한으로 실행:
```bash
# Windows
python crawl_python.py

# Mac/Linux
sudo python3 crawl_python.py
```

### 크롤링이 중간에 멈춤
- 네트워크 연결 확인
- `time.sleep()` 시간을 늘려보기 (1.5초 → 3초)

### 데이터가 적게 수집됨
- HTML 선택자가 변경되었을 수 있음
- 웹사이트를 직접 열어서 구조 확인 필요

## 🎯 실행 후

### 1. 데이터 확인
```bash
# CSV 파일 확인 (Excel로 열기)
start data\verychat_shops.csv

# JSON 파일 확인
type public\data\shops.json
```

### 2. 웹앱 실행
```bash
npm run dev
```

브라우저에서 http://localhost:3000 접속!

### 3. Git 커밋
```bash
git add public/data/shops.json
git commit -m "Update: 크롤링 데이터 업데이트 (628개 상점)"
git push
```

## 🔄 TypeScript 크롤링과 비교

| 항목 | Python (Selenium) | TypeScript (Puppeteer) |
|------|-------------------|------------------------|
| 안정성 | ⭐⭐⭐⭐⭐ 매우 높음 | ⭐⭐⭐ 보통 |
| 속도 | ⭐⭐⭐⭐ 빠름 | ⭐⭐⭐⭐⭐ 매우 빠름 |
| 설정 난이도 | ⭐⭐⭐ 쉬움 | ⭐⭐⭐⭐ 약간 복잡 |
| 디버깅 | ⭐⭐⭐⭐⭐ 매우 쉬움 | ⭐⭐⭐ 보통 |

## 💡 팁

### 1. 데이터 업데이트
주기적으로 크롤링하여 최신 데이터 유지:
```bash
# 매주 월요일 실행
python crawl_python.py
```

### 2. 에러 로그 저장
```bash
python crawl_python.py > crawl_log.txt 2>&1
```

### 3. 특정 지역만 필터링
크롤링 후 데이터 가공:
```python
# 한국 상점만 필터링 예시
import json

with open('public/data/shops.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

korea_shops = [s for s in data if '한국' in s['address'] or '서울' in s['address']]
print(f"한국 상점: {len(korea_shops)}개")
```

## ⚠️ 주의사항

1. **법적 책임**: 크롤링 전 반드시 사이트 이용약관 확인
2. **서버 부하**: 과도한 요청 자제
3. **개인정보**: 수집된 데이터 보호에 주의
4. **상업적 사용**: 라이선스 및 법적 자문 필요

## 📞 문제 발생 시

1. GitHub Issues에 보고
2. 에러 메시지 전체 복사
3. Python 버전 정보 포함
4. Chrome 버전 정보 포함
