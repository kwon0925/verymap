# VeryMap - 베리챗 상점

베리챗 상점 정보를 국가/지역별로 쉽게 찾아볼 수 있는 모바일 최적화 웹앱입니다.

## 기능

- 🌍 국가별 상점 필터링
- 📍 시도/시군구 드롭다운 필터
- 📱 모바일 최적화 반응형 디자인
- 🔍 상점 정보 (이름, 주소, 카테고리, VERY 단가, 결제비율)

## 시작하기

### 의존성 설치

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 개발 서버 실행

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 열어 확인하세요.

### 데이터 크롤링

⚠️ **주의**: 크롤링 전에 반드시 이용약관을 확인하세요!

#### 방법 1: Python + Selenium (권장 ⭐)

```bash
# 1. Python 의존성 설치
pip install -r requirements.txt

# 2. 크롤링 실행 (자동으로 public/data/shops.json에 저장)
python crawl_python.py
```

자세한 내용: [Python 크롤링 가이드](./PYTHON_CRAWL_GUIDE.md)

#### 방법 2: TypeScript + Puppeteer

```bash
# 628개의 모든 상점 데이터 크롤링
npm run crawl

# 데이터 복사
copy data\shops.json public\data\shops.json  # Windows
cp data/shops.json public/data/shops.json    # Mac/Linux
```

자세한 내용: [TypeScript 크롤링 가이드](./CRAWLING_GUIDE.md)

## 배포

Vercel을 통해 쉽게 배포할 수 있습니다.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/kwon0925/verymap)

## 기술 스택

- **Next.js 14** - React 프레임워크
- **TypeScript** - 타입 안정성
- **Tailwind CSS** - 스타일링
- **Puppeteer** - 웹 크롤링

## 라이선스

MIT
