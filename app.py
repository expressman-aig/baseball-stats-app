import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ページ設定
st.set_page_config(
    page_title="野球OPS分析・ランキングシステム", 
    page_icon="⚾️",
    layout="wide"
)

st.title("⚾️ 野球OPS分析・ランキングシステム")

# 2. サイドバー
st.sidebar.header("データ連携設定")
sheet_url = st.sidebar.text_input(
    "GoogleスプレッドシートのURLを貼り付けてください",
    placeholder="https://docs.google.com/spreadsheets/d/..."
)

# 3. メイン処理
if sheet_url:
    try:
        csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
        if '/edit' in csv_url and '/export' not in csv_url:
            csv_url = csv_url.split('/edit')[0] + '/export?format=csv'
        
        df = pd.read_csv(csv_url)

        # --- ここから計算処理 ---
        # 単打の算出
        df['単打'] = df['安打'] - (df['二塁打'] + df['三塁打'] + df['本塁打'])
        
        # 打率の計算（新規追加：これでエラーを回避！）
        df['打率'] = (df['安打'] / df['打数']).round(3)
        
        # 出塁率の計算
        obp_numerator = df['安打'] + df['四死球']
        obp_denominator = df['打数'] + df['四死球'] + df['犠飛']
        df['出塁率'] = (obp_numerator / obp_denominator).round(3)
        
        # 長打率の計算
        slg_numerator = df['単打'] + (df['二塁打'] * 2) + (df['三塁打'] * 3) + (df['本塁打'] * 4)
        df['長打率'] = (slg_numerator / df['打数']).round(3)
        
        # OPSの計算
        df['OPS'] = (df['出塁率'] + df['長打率']).round(3)
        # --- ここまで ---

        st.subheader("🏆 打撃成績ランキング（OPS順）")
        ranking_df = df[['名前', 'OPS', '打率', '出塁率', '長打率', '本塁打']].sort_values(by='OPS', ascending=False).reset_index(drop=True)
        st.dataframe(ranking_df, use_container_width=True)

        st.subheader("📊 選手別OPS可視化")
        fig = px.bar(ranking_df, x='名前', y='OPS', color='OPS', text='OPS',
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"データの読み込みに失敗しました。URLとシートの共有設定を確認してください。 エラー: {e}")
else:
    st.info("左側のサイドバーにスプレッドシートのURLを入力して、分析を開始してください。")
