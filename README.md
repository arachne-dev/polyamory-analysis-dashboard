# 폴리아모리 댓글 분석 대시보드

## 📊 프로젝트 개요
폴리아모리(다자연애)에 대한 유튜브 댓글을 고도화 프레임워크 기반으로 분석하는 인터랙티브 대시보드입니다.

## 🔍 주요 기능
- **4차원 프레임워크 분석**: 대상-정당화-강도-규범 분류체계
- **인터랙티브 시각화**: Plotly 기반 동적 차트
- **댓글 상세 분석**: 마우스 오버시 원문 댓글 표시
- **필터링 기능**: 입장, 감정강도, 좋아요 수 기준 필터링
- **도덕적 프레임워크**: Moral Foundations Theory 기반 분석

## 🚀 실행 방법

### 로컬 실행
```bash
pip install -r requirements.txt
streamlit run interactive_dashboard.py
```

### 온라인 데모
[Streamlit Cloud에서 보기](배포 후 업데이트 예정)

## 📁 파일 구조
- `interactive_dashboard.py`: 메인 대시보드 애플리케이션
- `augmented_polyamory_dataset.csv`: 분석된 댓글 데이터
- `detailed_gemini_analysis.json`: Gemini API 기반 상세 분석 결과
- `quick_framework_analysis_results.json`: 프레임워크 분석 결과
- `requirements.txt`: 패키지 의존성

## 🎯 분석 프레임워크
### 4차원 분류체계
1. **혐오·반론 대상 (What)**: SI, ID, SB, MC, EX
2. **정당화 논리 (Why)**: BIO, SOC, PCN, MAU
3. **감정 강도 (Intensity)**: EXH, SDG, MRJ, MDI
4. **규범·가치 프레임 (Norms)**: REM, NAT, SOR, TFM

## 🛠 기술 스택
- **Frontend**: Streamlit
- **Data Analysis**: Pandas, NumPy
- **Visualization**: Plotly
- **AI Analysis**: Google Gemini API
- **Deployment**: Streamlit Cloud

## 📈 데이터
- 총 459개의 유튜브 댓글 분석
- Gemini 2.0 Flash API를 통한 도덕적 프레임워크 분석
- 입장별, 감정별, 도덕적 정교함별 분류

## 🎨 디자인 특징
- 밝고 세련된 그라데이션 테마
- Inter 폰트 기반 모던 UI
- 반응형 레이아웃
- 호버 애니메이션 효과