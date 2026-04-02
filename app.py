import streamlit as st
import pandas as pd

# 1. 画面の基本設定
st.set_page_config(page_title="高校野球分析システム", layout="wide")
st.title("⚾️ 高校野球 OPS & 打撃成績ランキング")
st.write("スプレッドシートと連動して、チームの打撃成績をリアルタイム分析します。")

# 2. スプレッドシートURLの入力
sheet_url = st.text_input("GoogleスプレッドシートのURLを貼り付けてください", placeholder="https://docs.google.com/...")

if sheet_url:
    try:
        # URLをCSVエクスポート形式に変換
        csv_url = sheet_url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        
        # --- データクレンジング（入力漏れ・エラー対策） ---
        required_cols = ['名前', '打数', '安打', '二塁打', '三塁打', '本塁打', '四死球', '犠飛']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0 # 項目がなければ0で作成
        
        df = df.fillna(0) # 空欄を0で埋める
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
            single = row['安打'] - (row['二塁打'] + row['三塁打'] + row['本塁打'])
            total_bases = (single * 1) + (row['二塁打'] * 2) + (row['三塁打'] * 3) + (row['本塁打'] * 4)
            return total_bases / row['打数']
        
        df['長打率'] = df.apply(calc_slg, axis=1)
        
        # OPS
        df['OPS'] = df['出塁率'] + df['長打率']

        # --- ランキングと表示用データの整理 ---
        display_cols = ['名前', 'OPS', '打率', '出塁率', '長打率', '安打', '本塁打']
        res = df[display_cols].sort_values('OPS', ascending=False)
        
        # 順位を1から振る
        res['順位'] = range(1, len(res) + 1)
        res = res.set_index('順位')

        # --- 画面表示 ---
        st.success(f"現在 {len(df)} 名のデータを分析中...")
        
        # リーダーの強調表示
        top_player = res.iloc[0]
        st.info(f"🏆 現在のチームOPSリーダー: {top_player['名前']} 選手 (OPS {top_player['OPS']:.3f})")

        # 成績テーブル（小数点3桁表示）
        st.dataframe(res.style.format({
            'OPS': '{:.3f}', '打率': '{:.3f}', '出塁率': '{:.3f}', '長打率': '{:.3f}'
        }), use_container_width=True)
        
        # 比較グラフ
        st.subheader("📊 選手別スタッツ比較 (OPS vs 打率)")
        st.bar_chart(data=res.reset_index(), x="名前", y=["OPS", "打率"])

    except Exception as e:
        st.error(f"読み込み中にエラーが発生しました。URLやシートの項目名を確認してください。")
        st.write("詳細なエラー:", e)
else:
    st.info("URLを入力してEnterを押してください。チームのランキングが表示されます。")
    