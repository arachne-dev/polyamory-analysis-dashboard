import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np
from collections import defaultdict, Counter

# 페이지 설정
st.set_page_config(
    page_title="폴리아모리 댓글 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - 밝고 세련된 테마
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }

    .main-header h1 {
        color: white !important;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }

    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0;
        font-weight: 300;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid #667eea;
        transition: transform 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    .metric-card h4 {
        color: #667eea;
        margin: 0;
        font-weight: 500;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-card h2 {
        margin: 0.5rem 0;
        color: #2d3748;
        font-weight: 700;
    }

    .framework-tag {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    .stSelectbox > div > div {
        background: white;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }

    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* 사이드바 스타일링 */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }

    /* 차트 컨테이너 스타일링 */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """데이터 로드"""
    import os

    # 현재 디렉토리 기준 상대 경로로 변경
    base_path = os.path.dirname(os.path.abspath(__file__))

    try:
        # 증강된 데이터셋 로드
        df = pd.read_csv(os.path.join(base_path, 'augmented_polyamory_dataset.csv'))

        # 상세 분석 결과 로드
        with open(os.path.join(base_path, 'detailed_gemini_analysis.json'), 'r', encoding='utf-8') as f:
            detailed_analysis = json.load(f)

        # 프레임워크 분석 결과 로드
        with open(os.path.join(base_path, 'quick_framework_analysis_results.json'), 'r', encoding='utf-8') as f:
            framework_results = json.load(f)

        return df, detailed_analysis, framework_results
    except FileNotFoundError as e:
        st.error(f"데이터 파일을 찾을 수 없습니다: {e}")
        st.info("샘플 데이터로 진행합니다.")

        # 샘플 데이터 생성
        sample_df = pd.DataFrame({
            'comment': ['샘플 댓글 1', '샘플 댓글 2'],
            'likes': [10, 5],
            'stance': ['anti_polyamory', 'neutral'],
            'emotional_intensity': [3.5, 2.0],
            'moral_sophistication': [2.5, 3.0]
        })
        return sample_df, {}, {}

@st.cache_data
def classify_comments_by_framework(df):
    """고도화 프레임워크 기준으로 댓글 분류"""
    framework_dimensions = {
        'target_categories': {
            'SB': {'name': 'Sexual Behavior', 'keywords': ['문란', '난잡', '성병', '쓰리썸', '스와핑']},
            'ID': {'name': 'Individual Identity', 'keywords': ['미친', '정신', '이상', '병']},
            'MC': {'name': 'Moral Character', 'keywords': ['타락', '부도덕', '문제', '잘못']},
            'SI': {'name': 'Social Influence', 'keywords': ['아이', '청소년', '방송', '교육']},
            'EX': {'name': 'Existential Disgust', 'keywords': ['역겨', '징그럽', '드러움', '토나와']}
        },
        'justification_logic': {
            'MAU': {'name': 'Moral Authority', 'keywords': ['도덕', '죄', '잘못', '선']},
            'PCN': {'name': 'Protective Concern', 'keywords': ['아이', '청소년', '보호', '걱정']},
            'BIO': {'name': 'Biological Essentialism', 'keywords': ['자연', '동물', '본능', '생물학']},
            'SOC': {'name': 'Social Functionality', 'keywords': ['사회', '질서', '법', '시스템']}
        },
        'norm_frames': {
            'TFM': {'name': 'Traditional Family', 'keywords': ['가족', '결혼', '부부', '전통']},
            'REM': {'name': 'Religious-Moral', 'keywords': ['도덕', '윤리', '종교', '신']},
            'SOR': {'name': 'Social Order', 'keywords': ['질서', '사회', '법', '규칙']},
            'NAT': {'name': 'Natural Order', 'keywords': ['자연', '본능', '생물학', '동물']}
        }
    }

    classified_data = []

    for idx, row in df.iterrows():
        comment = row['comment']

        # 각 차원별 분류
        targets = []
        justifications = []
        norms = []

        # 대상 분류
        for code, data in framework_dimensions['target_categories'].items():
            for keyword in data['keywords']:
                if keyword in comment:
                    targets.append(f"{code} ({data['name']})")
                    break

        # 정당화 논리 분류
        for code, data in framework_dimensions['justification_logic'].items():
            for keyword in data['keywords']:
                if keyword in comment:
                    justifications.append(f"{code} ({data['name']})")
                    break

        # 규범 프레임 분류
        for code, data in framework_dimensions['norm_frames'].items():
            for keyword in data['keywords']:
                if keyword in comment:
                    norms.append(f"{code} ({data['name']})")
                    break

        # 감정 강도 분류
        intensity_score = row['emotional_intensity']
        if intensity_score >= 4:
            intensity = 'EXH (Extreme Hatred)'
        elif intensity_score >= 3:
            intensity = 'SDG (Strong Disgust)'
        elif intensity_score >= 2:
            intensity = 'MRJ (Moderate Rejection)'
        else:
            intensity = 'MDI (Mild Discomfort)'

        classified_data.append({
            'comment_id': idx,
            'comment': comment,
            'comment_short': comment[:100] + '...' if len(comment) > 100 else comment,
            'likes': row['likes'],
            'stance': row['stance'],
            'emotional_valence': row['emotional_valence'],
            'emotional_intensity': row['emotional_intensity'],
            'moral_sophistication': row['moral_sophistication'],
            'targets': targets,
            'justifications': justifications,
            'norms': norms,
            'intensity': intensity,
            'author': row['author'],
            'date': row['date']
        })

    return pd.DataFrame(classified_data)

def create_framework_distribution_chart(classified_df):
    """프레임워크 분포 차트 생성"""
    # 대상 카테고리 빈도
    target_freq = defaultdict(int)
    justification_freq = defaultdict(int)
    norm_freq = defaultdict(int)
    intensity_freq = defaultdict(int)

    for idx, row in classified_df.iterrows():
        for target in row['targets']:
            target_freq[target] += 1
        for justification in row['justifications']:
            justification_freq[justification] += 1
        for norm in row['norms']:
            norm_freq[norm] += 1
        intensity_freq[row['intensity']] += 1

    # 서브플롯 생성
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('혐오·반론 대상', '정당화 논리', '감정 강도', '규범·가치 프레임'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )

    # 대상 카테고리
    if target_freq:
        target_data = sorted(target_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        fig.add_trace(
            go.Bar(
                x=[item[1] for item in target_data],
                y=[item[0] for item in target_data],
                orientation='h',
                name='대상',
                marker_color='lightblue',
                text=[f"{item[1]}개" for item in target_data],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>빈도: %{x}개<extra></extra>'
            ),
            row=1, col=1
        )

    # 정당화 논리
    if justification_freq:
        justification_data = sorted(justification_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        fig.add_trace(
            go.Bar(
                x=[item[1] for item in justification_data],
                y=[item[0] for item in justification_data],
                orientation='h',
                name='정당화',
                marker_color='lightgreen',
                text=[f"{item[1]}개" for item in justification_data],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>빈도: %{x}개<extra></extra>'
            ),
            row=1, col=2
        )

    # 감정 강도
    intensity_data = sorted(intensity_freq.items(), key=lambda x: x[1], reverse=True)
    fig.add_trace(
        go.Bar(
            x=[item[1] for item in intensity_data],
            y=[item[0] for item in intensity_data],
            orientation='h',
            name='강도',
            marker_color='orange',
            text=[f"{item[1]}개" for item in intensity_data],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>빈도: %{x}개<extra></extra>'
        ),
        row=2, col=1
    )

    # 규범 프레임
    if norm_freq:
        norm_data = sorted(norm_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        fig.add_trace(
            go.Bar(
                x=[item[1] for item in norm_data],
                y=[item[0] for item in norm_data],
                orientation='h',
                name='규범',
                marker_color='pink',
                text=[f"{item[1]}개" for item in norm_data],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>빈도: %{x}개<extra></extra>'
            ),
            row=2, col=2
        )

    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="고도화 프레임워크 4차원 분포",
        title_x=0.5
    )

    return fig

def create_stance_analysis_chart(df):
    """입장별 분석 차트 생성"""
    stance_counts = df['stance'].value_counts()
    stance_likes = df.groupby('stance')['likes'].mean()
    stance_intensity = df.groupby('stance')['emotional_intensity'].mean()

    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{'type': 'pie'}, {'type': 'bar'}, {'type': 'bar'}]],
        subplot_titles=('입장 분포', '입장별 평균 좋아요', '입장별 감정 강도')
    )

    # 입장 분포 파이 차트
    fig.add_trace(
        go.Pie(
            labels=stance_counts.index,
            values=stance_counts.values,
            name="입장 분포",
            hovertemplate='<b>%{label}</b><br>%{value}개 (%{percent})<extra></extra>'
        ),
        row=1, col=1
    )

    # 평균 좋아요
    fig.add_trace(
        go.Bar(
            x=stance_likes.index,
            y=stance_likes.values,
            name="평균 좋아요",
            marker_color='coral',
            text=[f"{val:.1f}" for val in stance_likes.values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>평균 좋아요: %{y:.1f}개<extra></extra>'
        ),
        row=1, col=2
    )

    # 감정 강도
    fig.add_trace(
        go.Bar(
            x=stance_intensity.index,
            y=stance_intensity.values,
            name="감정 강도",
            marker_color='lightcoral',
            text=[f"{val:.2f}" for val in stance_intensity.values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>평균 강도: %{y:.2f}/5<extra></extra>'
        ),
        row=1, col=3
    )

    fig.update_layout(
        height=400,
        showlegend=False,
        title_text="입장별 분석",
        title_x=0.5
    )

    return fig

def create_moral_foundations_heatmap(df):
    """도덕적 기반 히트맵 생성"""
    moral_foundations = ['mf_care_harm_score', 'mf_fairness_cheating_score',
                        'mf_loyalty_betrayal_score', 'mf_authority_subversion_score',
                        'mf_sanctity_degradation_score', 'mf_liberty_oppression_score']

    foundation_names = ['Care/Harm', 'Fairness/Cheating', 'Loyalty/Betrayal',
                       'Authority/Subversion', 'Sanctity/Degradation', 'Liberty/Oppression']

    # 감정 극성별 도덕적 기반 평균 계산
    valence_data = []
    valence_labels = []

    for valence in ['positive', 'negative', 'neutral', 'mixed']:
        valence_subset = df[df['emotional_valence'] == valence]
        if len(valence_subset) > 0:
            valence_avg = [valence_subset[foundation].mean() for foundation in moral_foundations]
            valence_data.append(valence_avg)
            valence_labels.append(f"{valence} ({len(valence_subset)}개)")

    if valence_data:
        fig = go.Figure(data=go.Heatmap(
            z=valence_data,
            x=foundation_names,
            y=valence_labels,
            colorscale='RdYlBu_r',
            text=[[f"{val:.2f}" for val in row] for row in valence_data],
            texttemplate="%{text}",
            textfont={"size": 10},
            hovertemplate='<b>%{y}</b><br><b>%{x}</b><br>점수: %{z:.2f}<extra></extra>'
        ))

        fig.update_layout(
            title="감정 극성별 도덕적 기반 점수",
            title_x=0.5,
            height=300
        )

        return fig
    return None

def create_interactive_scatter(df):
    """인터랙티브 산점도 생성"""
    # 댓글 요약 컬럼 생성 (50자 제한)
    df = df.copy()
    df['comment_preview'] = df['comment'].str[:50] + '...'

    fig = px.scatter(
        df,
        x='moral_sophistication',
        y='likes',
        color='stance',
        size='emotional_intensity',
        hover_data={'comment_preview': True, 'author': True, 'date': True},
        title="📈 도덕적 정교함 vs 좋아요 수 분석",
        labels={
            'moral_sophistication': '도덕적 정교함',
            'likes': '좋아요 수',
            'stance': '입장',
            'comment_preview': '댓글 미리보기'
        },
        color_discrete_map={
            'anti_polyamory': '#FF6B6B',
            'pro_polyamory': '#4ECDC4',
            'neutral': '#95E1D3',
            'questioning': '#F8B500',
            'anti_hedonism': '#845EC2'
        }
    )

    fig.update_traces(
        hovertemplate='<b>도덕적 정교함:</b> %{x:.2f}<br>' +
                     '<b>좋아요 수:</b> %{y}<br>' +
                     '<b>입장:</b> %{color}<br>' +
                     '<b>댓글:</b> %{customdata[0]}<br>' +
                     '<b>작성자:</b> %{customdata[1]}<br>' +
                     '<b>날짜:</b> %{customdata[2]}<extra></extra>'
    )

    fig.update_layout(height=500)

    return fig

def display_comment_details(classified_df, selected_categories=None):
    """선택된 카테고리의 댓글 상세 정보 표시"""
    if selected_categories:
        filtered_df = classified_df[
            classified_df['targets'].apply(lambda x: any(cat in x for cat in selected_categories)) |
            classified_df['justifications'].apply(lambda x: any(cat in x for cat in selected_categories)) |
            classified_df['norms'].apply(lambda x: any(cat in x for cat in selected_categories))
        ]
    else:
        filtered_df = classified_df.head(20)

    st.subheader("💬 댓글 상세 정보")

    for idx, row in filtered_df.head(10).iterrows():
        with st.expander(f"댓글 {row['comment_id']} - {row['stance']} (좋아요: {row['likes']}개)"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write("**원문:**")
                st.write(row['comment'])

                st.write("**프레임워크 분류:**")
                if row['targets']:
                    st.write("🎯 **대상:**", ", ".join(row['targets']))
                if row['justifications']:
                    st.write("💭 **정당화:**", ", ".join(row['justifications']))
                if row['norms']:
                    st.write("📏 **규범:**", ", ".join(row['norms']))
                st.write("🌡️ **감정강도:**", row['intensity'])

            with col2:
                st.metric("좋아요", row['likes'])
                st.metric("감정강도", f"{row['emotional_intensity']}/5")
                st.metric("도덕정교함", f"{row['moral_sophistication']}/5")
                st.write("**작성자:**", row['author'])
                st.write("**날짜:**", row['date'])

def main():
    # 메인 헤더
    st.markdown("""
    <div class="main-header">
        <h1>📊 폴리아모리 댓글 분석 대시보드</h1>
        <p>고도화 프레임워크 기반 인터랙티브 시각화 및 분석</p>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 로드
    with st.spinner('데이터를 로드하는 중...'):
        df, detailed_analysis, framework_results = load_data()
        classified_df = classify_comments_by_framework(df)

    # 사이드바 - 필터링 옵션
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <h3 style="color: white; margin: 0; text-align: center;">🎛️ 필터링 옵션</h3>
    </div>
    """, unsafe_allow_html=True)

    # 입장 필터
    stance_filter = st.sidebar.multiselect(
        "입장 선택",
        options=df['stance'].unique(),
        default=df['stance'].unique()
    )

    # 감정 강도 필터
    intensity_filter = st.sidebar.slider(
        "감정 강도 범위",
        min_value=float(df['emotional_intensity'].min()),
        max_value=float(df['emotional_intensity'].max()),
        value=(float(df['emotional_intensity'].min()), float(df['emotional_intensity'].max()))
    )

    # 좋아요 수 필터
    likes_filter = st.sidebar.slider(
        "좋아요 수 범위",
        min_value=int(df['likes'].min()),
        max_value=int(df['likes'].max()),
        value=(int(df['likes'].min()), int(df['likes'].max()))
    )

    # 필터 적용
    filtered_df = df[
        (df['stance'].isin(stance_filter)) &
        (df['emotional_intensity'] >= intensity_filter[0]) &
        (df['emotional_intensity'] <= intensity_filter[1]) &
        (df['likes'] >= likes_filter[0]) &
        (df['likes'] <= likes_filter[1])
    ]

    filtered_classified_df = classified_df[
        (classified_df['stance'].isin(stance_filter)) &
        (classified_df['emotional_intensity'] >= intensity_filter[0]) &
        (classified_df['emotional_intensity'] <= intensity_filter[1]) &
        (classified_df['likes'] >= likes_filter[0]) &
        (classified_df['likes'] <= likes_filter[1])
    ]

    # 메트릭 카드 - 세련된 스타일
    st.subheader("📈 주요 지표")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>총 댓글 수</h4>
            <h2>{}</h2>
        </div>
        """.format(len(filtered_df)), unsafe_allow_html=True)

    with col2:
        anti_ratio = len(filtered_df[filtered_df['stance'] == 'anti_polyamory']) / len(filtered_df) * 100
        st.markdown("""
        <div class="metric-card">
            <h4>반대 의견 비율</h4>
            <h2>{:.1f}%</h2>
        </div>
        """.format(anti_ratio), unsafe_allow_html=True)

    with col3:
        avg_intensity = filtered_df['emotional_intensity'].mean()
        st.markdown("""
        <div class="metric-card">
            <h4>평균 감정 강도</h4>
            <h2>{:.2f}/5</h2>
        </div>
        """.format(avg_intensity), unsafe_allow_html=True)

    with col4:
        avg_likes = filtered_df['likes'].mean()
        st.markdown("""
        <div class="metric-card">
            <h4>평균 좋아요</h4>
            <h2>{:.1f}개</h2>
        </div>
        """.format(avg_likes), unsafe_allow_html=True)

    # 메인 차트들
    st.header("📊 고도화 프레임워크 분석")

    # 프레임워크 분포 차트
    framework_chart = create_framework_distribution_chart(filtered_classified_df)
    st.plotly_chart(framework_chart, use_container_width=True)

    # 두 개 컬럼으로 나누어 차트 배치
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎭 입장별 분석")
        stance_chart = create_stance_analysis_chart(filtered_df)
        st.plotly_chart(stance_chart, use_container_width=True)

    with col2:
        st.subheader("🧠 도덕적 기반 히트맵")
        heatmap = create_moral_foundations_heatmap(filtered_df)
        if heatmap:
            st.plotly_chart(heatmap, use_container_width=True)

    # 인터랙티브 산점도
    st.subheader("🎯 인터랙티브 분석")
    scatter_chart = create_interactive_scatter(filtered_df)
    st.plotly_chart(scatter_chart, use_container_width=True)

    # 댓글 상세 정보 섹션
    st.header("💬 댓글 상세 분석")

    # 프레임워크 카테고리 선택
    st.subheader("🔍 프레임워크 카테고리별 댓글 탐색")

    col1, col2, col3 = st.columns(3)

    with col1:
        target_categories = st.multiselect(
            "혐오·반론 대상",
            options=['SB (Sexual Behavior)', 'ID (Individual Identity)', 'MC (Moral Character)',
                    'SI (Social Influence)', 'EX (Existential Disgust)']
        )

    with col2:
        justification_categories = st.multiselect(
            "정당화 논리",
            options=['MAU (Moral Authority)', 'PCN (Protective Concern)',
                    'BIO (Biological Essentialism)', 'SOC (Social Functionality)']
        )

    with col3:
        norm_categories = st.multiselect(
            "규범·가치 프레임",
            options=['TFM (Traditional Family)', 'REM (Religious-Moral)',
                    'SOR (Social Order)', 'NAT (Natural Order)']
        )

    # 선택된 카테고리의 댓글 표시
    selected_categories = target_categories + justification_categories + norm_categories
    display_comment_details(filtered_classified_df, selected_categories)

    # 통계 요약
    st.header("📈 분석 요약")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("주요 발견사항")
        st.write("🎯 **가장 빈번한 혐오 대상:** 사회적 영향 우려 (SI)")
        st.write("💭 **주요 정당화 논리:** 생물학적 본질주의 (BIO)")
        st.write("🌡️ **지배적 감정 강도:** 강한 혐오감 (SDG)")
        st.write("📏 **핵심 규범 프레임:** 종교-도덕적 규범 (REM)")

    with col2:
        st.subheader("정량적 인사이트")
        st.write(f"• **반대 의견 비율:** {anti_ratio:.1f}%")
        st.write(f"• **전체 감정 강도:** {avg_intensity:.2f}/5 ({'높음' if avg_intensity > 3 else '중간' if avg_intensity > 2 else '낮음'})")
        avg_sophistication = filtered_df['moral_sophistication'].mean()
        st.write(f"• **도덕적 정교함:** {avg_sophistication:.2f}/5 ({'높음' if avg_sophistication > 3 else '중간' if avg_sophistication > 2 else '낮음'})")

    # 데이터 다운로드 섹션
    st.header("💾 데이터 다운로드")

    col1, col2 = st.columns(2)

    with col1:
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📁 필터링된 데이터 CSV 다운로드",
            data=csv_data,
            file_name='filtered_polyamory_analysis.csv',
            mime='text/csv'
        )

    with col2:
        json_data = filtered_classified_df.to_json(orient='records', force_ascii=False).encode('utf-8')
        st.download_button(
            label="📁 프레임워크 분류 결과 JSON 다운로드",
            data=json_data,
            file_name='framework_classification.json',
            mime='application/json'
        )

if __name__ == "__main__":
    main()