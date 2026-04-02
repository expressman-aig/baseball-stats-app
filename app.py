import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ブラウザのタブ名やリンクカードのタイトルを設定（ここが「タイトル未設定」の解消ポイント）
st.set_page_config(
    page_title="野球OPS分析・ランキングシステム", 
    page_icon="⚾️",
    layout="wide"
)

# 2. アプリのメインタイトル（商品名）
st.title("⚾️ 野球OPS分析・ランキングシステム")

# 3. サイドバーでGoogleスプレッドシートのURLを入力
st.sidebar.header("データ連携設定")
sheet_url = st.sidebar.text_input(
    "GoogleスプレッドシートのURLを貼り付けてください",
    placeholder="https://docs.google.com/spreadsheets/d/..."
)

# 4. データ読み込みと計算の処理
if sheet_url:
    try:
        # スプレッドシートをCSV形式で読み込むためのURL変換
        csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
        if '/edit' in csv_url and '/export' not in csv_url:
            csv_url = csv_url.split('/edit')[0] + '/export?format=csv'
        
        df = pd.read_csv(csv_url)

        # OPSの計算（出塁率 + 長打率）
        # 出塁率 = (安打 + 四死球) / (打数 + 四死球 + 犠飛)
        # 長打率 = (単打 + 二塁打*2 + 三塁打*3 + 本塁打*4) / 打数
        # ※単打 = 安打 - (二塁打 + 三塁打 + 本塁打)
        
        df['単打'] = df['安打'] - (df['二塁打'] + df['三塁打'] + df['本塁打'])
        
        # 出塁率の計算
        obp_numerator = df['安打'] + df['四死球']
        obp_denominator = df['打数'] + df['四死球'] + df['犠飛']
        df['出塁率'] = (obp_numerator / obp_denominator).round(3)
        
        # 長打率の計算
        slg_numerator = df['単打'] + (df['二塁打'] * 2) + (df['三塁打'] * 3) + (df['本塁打'] * 4)
        df['長打率'] = (slg_numerator / df['打数']).round(3)
        
        # OPSの計算
        df['OPS'] = (df['出塁率'] + df['長打率']).round(3)

        # ランキング表示（OPSが高い順）
        st.subheader("🏆 打撃成績ランキング（OPS順）")
        ranking_df = df[['名前', 'OPS', '打率', '出塁率', '長打率', '本塁打']].sort_values(by='OPS', ascending=False).reset_index(drop=True)
        st.dataframe(ranking_df, use_container_width=True)

        # グラフ表示
        st.subheader("📊 選手別OPS可視化")
        fig = px.bar(ranking_df, x='名前', y='OPS', color='OPS', text='OPS',
                     color_continuous_scale='Blues', title="チーム内OPS比較")
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"データの読み込みに失敗しました。URLとシートの共有設定を確認してください。 エラー: {e}")
else:
    st.info("左側のサイドバーにスプレッドシートのURLを入力して、分析を開始してください。")
    st.image("https://images.unsplash.com/photo-1508344928928-71657ad7302c?auto=format&fit=crop&q=80&w=1000", caption="データで野球を科学する")

# フッター
st.markdown("---")
st.caption("© 2024 DX職人 | 現場の不便をITで解決する")
