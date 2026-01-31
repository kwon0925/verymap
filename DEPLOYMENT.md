# 배포 가이드

## 1. GitHub에 코드 업로드

### 초기 설정
```bash
git init
git add .
git commit -m "Initial commit: VeryMap 프로젝트"
git branch -M main
git remote add origin https://github.com/kwon0925/verymap.git
git push -u origin main
```

## 2. Vercel 배포

### 방법 1: Vercel 웹사이트에서 배포 (권장)

1. [Vercel](https://vercel.com)에 접속하여 로그인
2. "Add New Project" 클릭
3. GitHub 계정 연결
4. `kwon0925/verymap` 레포지토리 선택
5. "Deploy" 클릭

### 방법 2: Vercel CLI 사용

```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

## 3. 데이터 크롤링 (선택사항)

⚠️ **주의**: 크롤링 전에 반드시 해당 사이트의 이용약관을 확인하세요.

### 로컬에서 크롤링 실행

```bash
# 의존성 설치
npm install

# 크롤링 실행
npm run crawl
```

크롤링이 완료되면 `data/shops.json` 파일이 생성됩니다.

이 파일을 `public/data/shops.json`으로 복사하세요:

```bash
# Windows
copy data\shops.json public\data\shops.json

# Mac/Linux
cp data/shops.json public/data/shops.json
```

그 후 다시 GitHub에 푸시:

```bash
git add public/data/shops.json
git commit -m "Update shop data"
git push
```

## 4. 환경 변수 (필요시)

현재는 환경 변수가 필요하지 않지만, 나중에 API를 사용하게 되면 Vercel 대시보드에서 설정할 수 있습니다.

## 5. 도메인 연결 (선택사항)

Vercel 대시보드에서:
1. Project Settings > Domains
2. 원하는 도메인 입력
3. DNS 설정 따라하기

## 문제 해결

### 빌드 오류
- `npm run build`를 로컬에서 먼저 실행해보세요
- 에러 메시지를 확인하고 수정하세요

### 데이터가 표시되지 않음
- `public/data/shops.json` 파일이 존재하는지 확인
- 브라우저 개발자 도구의 Network 탭에서 shops.json 요청 확인

### 크롤링 실패
- Puppeteer가 제대로 설치되었는지 확인
- 웹사이트 구조가 변경되었을 수 있으니 `scripts/crawl.ts` 수정 필요
