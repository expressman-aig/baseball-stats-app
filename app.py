import streamlit as st
import pandas as pd

# 1. 画面の基本設定（ブラウザのタブ名や横幅）
st.set_page_config(page_title="高校野球分析システム", layout="wide")
st.title("⚾️ OPS分析・ランキング表示ツール")
st.write("スプレッドシートのデータを読み込み、リアルタイムで指標を算出します。")

# 2. スプレッドシートURLの入力欄
sheet_url = st.text_input("GoogleスプレッドシートのURLを貼り付けてください", placeholder="https://docs.google.com/...")

if sheet_url:
    try:
        # URLをCSVエクスポート形式に変換して読み込む
        csv_url = sheet_url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        
        # --- データクレンジング（入力漏れ・エラー対策） ---
        required_cols = ['名前', '打数', '安打', '二塁打', '三塁打', '本塁打', '四死球', '犠飛']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0 # 項目がシートになければ0で作成
        
        df = df.fillna(0) # 空欄（NaN）をすべて0で埋める
        df = df[df['名前'] != 0] # 名前が入っていない行は除外

        # --- 計算ロジック（安全設計） ---
        
        # 打率 (AVG)
        df['打率'] = df.apply(lambda x: x['安打'] / x['打数'] if x['打数'] > 0 else 0, axis=1)
        
        # 出塁率 (OBP)
        df['出塁率'] = df.apply(lambda x: (x['安打'] + x['四死球']) / (x['打数'] + x['四死球'] + x['犠飛']) 
                            if (x['打数'] + x['四死球'] + x['犠飛']) > 0 else 0, axis=1)
        
        # 長打率 (SLG)
        def calc_slg(row):
            if row['打数'] == 0: return 0
            # 単打 = 安打 - (二塁打 + 三塁打 + 本塁打)
            single = row['安打'] - (row['二塁打'] + row['三塁打'] + row['本塁打'])
            # 塁打数 = 1*単打 + 2*二塁打 + 3*三塁打 + 4*本塁打
            total_bases = (single * 1) + (row['二塁打'] * 2) + (row['三塁打'] * 3) + (row['本塁打'] * 4)
            return total_bases / row['打数']
        
        df['長打率'] = df.apply(calc_slg, axis=1)
        
        # OPS = 出塁率 + 長打率
        df['OPS'] = df['出塁率'] + df['長打率']

        # --- 表示用データの整理 ---
        display_cols = ['名前', 'OPS', '打率', '出塁率', '長打率', '安打', '本塁打']
        res = df[display_cols].sort_values('OPS', ascending=False)
        
        # 順位を1から振り、インデックス（左端）に設定
        res['順位'] = range(1, len(res) + 1)
        res = res.set_index('順位')

        # --- 画面表示 ---
        st.success(f"現在 {len(df)} 名のデータを分析完了！")
        
        # 1位の選手をピックアップ
        top_player = res.iloc[0]
        st.info(f"🏆 チームOPSリーダー: {top_player['名前']} 選手 (OPS {top_player['OPS']:.3f})")

        # 成績テーブルの表示（★ここが修正ポイント：整数と小数を使い分け）
        st.dataframe(res.style.format({
            'OPS': '{:.3f}',    # 小数第3位まで
            '打率': '{:.3f}',   # 小数第3位まで
            '出塁率': '{:.3f}', # 小数第3位まで
            '長打率': '{:.3f}', # 小数第3位まで
            '安打': '{:.0f}',   # 整数（個数）
            '本塁打': '{:.0f}'  # 整数（個数）
        }), use_container_width=True)
        
        # 比較グラフの表示
        st.subheader("📊 選手別スタッツ比較 (OPS)")
        st.bar_chart(data=res.reset_index(), x="名前", y="OPS")

    except Exception as e:
        st.error("スプレッドシートの読み込みに失敗しました。")
        st.write("原因:", e)
else:
    st.info("スプレッドシートのURLを入力してください。チーム全員のランキングが生成されます。")
