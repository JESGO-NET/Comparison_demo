import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="ESGメトリクスダッシュボード",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to improve the design
st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 0;
    }
    
    /* Header styling */
    .header-container {
        padding: 1rem;
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Card styling */
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 4px;
        padding: 8px 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Table styling */
    .dataframe {
        font-size: 12px;
    }
    
    /* Plot styling */
    .stPlotlyChart {
        background-color: white;
        border-radius: 5px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Streamlit elements override */
    div[data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0);
    }
    
    .stSelectbox label {
        font-size: 0.9rem !important;
        color: #2c3e50 !important;
    }
    
    .stTitle {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Color scheme
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#2ecc71',
    'background': '#f8f9fa',
    'text': '#2c3e50'
}

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    return df

@st.cache_data
def calculate_statistics(df):
    stats = {}
    score_columns = ['総合スコア', '環境スコア', '社会スコア', 'ガバナンススコア']
    
    for col in score_columns:
        stats[f'{col}_avg'] = df[col].mean()
        stats[f'{col}_median'] = df[col].median()
        stats[f'{col}_top'] = df.nlargest(3, col)['会社名'].tolist()
    
    return stats

def main():
    # Load data
    try:
        df = load_data()
        stats = calculate_statistics(df)
    except FileNotFoundError:
        st.error("エラー：data.csvファイルが見つかりません。")
        return

    # Header
    with st.container():
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if os.path.exists("logo.png"):
                st.image("logo.png", use_container_width=True)
            else:
                st.info("ロゴを表示するには、'logo.png'をアプリケーションのディレクトリに配置してください。")
        
        with col2:
            st.title("ESGメトリクスダッシュボード")

    # Overview metrics
    st.markdown("### 主要指標")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>総合スコア平均</h3>
            <div class="metric-value">{:.1f}</div>
        </div>
        """.format(stats['総合スコア_avg']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>環境スコア平均</h3>
            <div class="metric-value">{:.1f}</div>
        </div>
        """.format(stats['環境スコア_avg']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>社会スコア平均</h3>
            <div class="metric-value">{:.1f}</div>
        </div>
        """.format(stats['社会スコア_avg']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>ガバナンススコア平均</h3>
            <div class="metric-value">{:.1f}</div>
        </div>
        """.format(stats['ガバナンススコア_avg']), unsafe_allow_html=True)

    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📊 分析", "📋 データテーブル", "ℹ️ 情報"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("ESGスコアランキング")
            score_options = {
                "総合スコア": "総合スコア",
                "環境スコア": "環境スコア",
                "社会スコア": "社会スコア",
                "ガバナンススコア": "ガバナンススコア"
            }
            selected_score_ranking = st.selectbox(
                "スコアの種類を選択",
                options=list(score_options.keys()),
                key="ranking_score"
            )
            
            # Ranking visualization
            sorted_data = df.sort_values(by=selected_score_ranking, ascending=True).tail(15)
            
            fig_ranking = go.Figure()
            fig_ranking.add_trace(go.Bar(
                x=sorted_data[selected_score_ranking],
                y=sorted_data['会社名'],
                orientation='h',
                marker_color=COLORS['primary']
            ))
            
            fig_ranking.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis_title=selected_score_ranking,
                yaxis_title=None,
                plot_bgcolor=COLORS['background'],
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", color=COLORS['text']),
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
                yaxis=dict(showgrid=False)
            )
            
            st.plotly_chart(fig_ranking, use_container_width=True)
        
        with col2:
            st.subheader("財務指標との相関")
            metric_col1, metric_col2 = st.columns(2)
            
            with metric_col1:
                selected_score_scatter = st.selectbox(
                    "ESGスコア",
                    options=list(score_options.keys()),
                    key="scatter_score"
                )
            
            with metric_col2:
                financial_metrics = {
                    "PER（TTM）": "PE Ratio (TTM)",
                    "PBR": "Price/Book",
                    "EV/EBITDA": "Enterprise Value/EBITDA"
                }
                selected_financial_display = st.selectbox(
                    "財務指標",
                    options=list(financial_metrics.keys()),
                    key="financial_metric"
                )
                selected_financial = financial_metrics[selected_financial_display]
            
            # Calculate correlation
            correlation = df[score_options[selected_score_scatter]].corr(df[selected_financial])
            
            # Scatter plot
            fig_scatter = px.scatter(
                df,
                x=score_options[selected_score_scatter],
                y=selected_financial,
                text='会社名',
                title=f"相関係数: {correlation:.2f}"
            )
            
            # Add trend line
            fig_scatter.add_trace(
                go.Scatter(
                    x=df[score_options[selected_score_scatter]],
                    y=np.poly1d(np.polyfit(df[score_options[selected_score_scatter]], df[selected_financial], 1))(df[score_options[selected_score_scatter]]),
                    mode='lines',
                    name='トレンド',
                    line=dict(color='red', dash='dash')
                )
            )
            
            fig_scatter.update_traces(
                textposition='top center',
                marker=dict(size=10, color=COLORS['secondary'])
            )
            
            fig_scatter.update_layout(
                height=400,
                plot_bgcolor=COLORS['background'],
                paper_bgcolor='white',
                margin=dict(l=0, r=0, t=40, b=0),
                font=dict(family="Arial, sans-serif", color=COLORS['text']),
                xaxis=dict(
                    title=selected_score_scatter,
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                yaxis=dict(
                    title=selected_financial_display,
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.1)'
                )
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)

    with tab2:
        st.subheader("データテーブル")
        
        # Search functionality
        search = st.text_input("企業名で検索", "")
        
        # Filter data based on search
        filtered_df = df[df['会社名'].str.contains(search, case=False)] if search else df
        
        # Display sortable table
        st.dataframe(
            filtered_df,
            hide_index=True,
            column_config={
                "会社名": "企業名",
                "総合スコア": st.column_config.NumberColumn("総合スコア", format="%.1f"),
                "環境スコア": st.column_config.NumberColumn("環境スコア", format="%.1f"),
                "社会スコア": st.column_config.NumberColumn("社会スコア", format="%.1f"),
                "ガバナンススコア": st.column_config.NumberColumn("ガバナンススコア", format="%.1f"),
                "PE Ratio (TTM)": st.column_config.NumberColumn("PER（TTM）", format="%.1f"),
                "Price/Book": st.column_config.NumberColumn("PBR", format="%.2f"),
                "Enterprise Value/EBITDA": st.column_config.NumberColumn("EV/EBITDA", format="%.1f")
            }
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "CSVをダウンロード",
            csv,
            "esg_data.csv",
            "text/csv",
            key='download-csv'
        )

    with tab3:
        st.subheader("データについて")
        st.markdown("""
        ### 指標の説明
        
        #### ESGスコア
        - **総合スコア**: 環境、社会、ガバナンスの総合評価
        - **環境スコア**: 環境への取り組みの評価
        - **社会スコア**: 社会的責任の評価
        - **ガバナンススコア**: 企業統治の評価
        
        #### 財務指標
        - **PER（TTM）**: 株価収益率（12ヶ月）
        - **PBR**: 株価純資産倍率
        - **EV/EBITDA**: 企業価値収益率
        
        ### 更新頻度
        データは四半期ごとに更新されます。
        
        ### データソース
        - ESGデータ: 各社のウェブサイトに公開されている情報に基づく
        - 財務データ: Yahoo Finance
        - ESGスコア: 自社独自の方法論で算出
        """)

if __name__ == "__main__":
    main()