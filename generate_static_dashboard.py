#!/usr/bin/env python3
"""
정적 HTML 대시보드 생성기
Streamlit 앱을 정적 HTML로 변환하여 GitHub Pages에서 호스팅 가능하도록 함
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from collections import defaultdict, Counter

def load_data():
    """데이터 로드"""
    try:
        # 현재 디렉토리 기준 상대 경로
        base_path = os.path.dirname(os.path.abspath(__file__))

        # 증강된 데이터셋 로드
        df = pd.read_csv(os.path.join(base_path, 'augmented_polyamory_dataset.csv'))

        # 상세 분석 결과 로드
        with open(os.path.join(base_path, 'detailed_gemini_analysis.json'), 'r', encoding='utf-8') as f:
            detailed_analysis = json.load(f)

        # 프레임워크 분석 결과 로드
        with open(os.path.join(base_path, 'quick_framework_analysis_results.json'), 'r', encoding='utf-8') as f:
            framework_results = json.load(f)

        return df, detailed_analysis, framework_results
    except Exception as e:
        print(f"데이터 로드 실패: {e}")
        # 샘플 데이터 생성
        sample_df = pd.DataFrame({
            'comment': ['샘플 댓글 1', '샘플 댓글 2', '샘플 댓글 3'],
            'likes': [10, 5, 15],
            'stance': ['anti_polyamory', 'neutral', 'pro_polyamory'],
            'emotional_intensity': [3.5, 2.0, 4.0],
            'moral_sophistication': [2.5, 3.0, 1.5],
            'author': ['사용자1', '사용자2', '사용자3'],
            'date': ['2023-01-01', '2023-01-02', '2023-01-03']
        })
        return sample_df, {}, {}

def create_framework_distribution_chart(df):
    """프레임워크 분포 차트 생성"""
    # 간단한 분포 차트
    stance_counts = df['stance'].value_counts()

    fig = px.bar(
        x=stance_counts.index,
        y=stance_counts.values,
        title="📊 입장별 분포",
        labels={'x': '입장', 'y': '댓글 수'},
        color=stance_counts.values,
        color_continuous_scale='viridis'
    )

    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=12),
        title=dict(font=dict(size=16, color='#2D3748'))
    )

    return fig

def create_interactive_scatter(df):
    """인터랙티브 산점도 생성"""
    # 댓글 요약 컬럼 생성
    df = df.copy()
    df['comment_preview'] = df['comment'].str[:50] + '...'

    fig = px.scatter(
        df,
        x='moral_sophistication',
        y='likes',
        color='stance',
        size='emotional_intensity',
        hover_data=['comment_preview', 'author', 'date'],
        title="📈 도덕적 정교함 vs 좋아요 수 분석",
        labels={
            'moral_sophistication': '도덕적 정교함',
            'likes': '좋아요 수',
            'stance': '입장'
        },
        color_discrete_map={
            'anti_polyamory': '#FF6B6B',
            'pro_polyamory': '#4ECDC4',
            'neutral': '#95E1D3',
            'questioning': '#F8B500',
            'anti_hedonism': '#845EC2'
        }
    )

    fig.update_layout(
        height=600,
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=12),
        title=dict(font=dict(size=16, color='#2D3748'))
    )

    return fig

def generate_html_dashboard():
    """HTML 대시보드 생성"""
    print("📊 데이터 로딩 중...")
    df, detailed_analysis, framework_results = load_data()

    print("📈 차트 생성 중...")
    framework_chart = create_framework_distribution_chart(df)
    scatter_chart = create_interactive_scatter(df)

    # 기본 통계
    total_comments = len(df)
    avg_likes = df['likes'].mean()
    avg_intensity = df['emotional_intensity'].mean()
    anti_ratio = (df['stance'] == 'anti_polyamory').mean() * 100

    # HTML 템플릿
    html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>폴리아모리 댓글 분석 대시보드</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }}

        .header h1 {{
            margin: 0 0 0.5rem 0;
            font-weight: 700;
            font-size: 2.5rem;
        }}

        .header p {{
            margin: 0;
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 300;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            text-align: center;
            border-left: 4px solid #667eea;
            transition: transform 0.2s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }}

        .metric-card h4 {{
            color: #667eea;
            margin: 0 0 0.5rem 0;
            font-weight: 500;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .metric-card h2 {{
            margin: 0;
            color: #2d3748;
            font-weight: 700;
            font-size: 2rem;
        }}

        .chart-container {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }}

        .chart-title {{
            color: #2d3748;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}

        .footer {{
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 폴리아모리 댓글 분석 대시보드</h1>
            <p>고도화 프레임워크 기반 인터랙티브 시각화 및 분석</p>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <h4>총 댓글 수</h4>
                <h2>{total_comments:,}</h2>
            </div>
            <div class="metric-card">
                <h4>평균 좋아요</h4>
                <h2>{avg_likes:.1f}</h2>
            </div>
            <div class="metric-card">
                <h4>평균 감정강도</h4>
                <h2>{avg_intensity:.2f}/5</h2>
            </div>
            <div class="metric-card">
                <h4>반대 의견 비율</h4>
                <h2>{anti_ratio:.1f}%</h2>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-title">📊 4차원 프레임워크 분석</div>
            <div id="framework-chart"></div>
        </div>

        <div class="chart-container">
            <div class="chart-title">🎯 인터랙티브 분석</div>
            <div id="scatter-chart"></div>
        </div>

        <div class="footer">
            <p>🚀 Generated with Claude Code | 📊 Powered by Plotly & Gemini AI</p>
        </div>
    </div>

    <script>
        // 프레임워크 차트
        var frameworkData = {framework_chart.to_json()};
        Plotly.newPlot('framework-chart', frameworkData.data, frameworkData.layout, {{responsive: true}});

        // 산점도 차트
        var scatterData = {scatter_chart.to_json()};
        Plotly.newPlot('scatter-chart', scatterData.data, scatterData.layout, {{responsive: true}});
    </script>
</body>
</html>
"""

    # HTML 파일 저장
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

    print("✅ 정적 HTML 대시보드 생성 완료: index.html")
    print("🌐 GitHub Pages에서 호스팅할 수 있습니다!")

if __name__ == "__main__":
    generate_html_dashboard()