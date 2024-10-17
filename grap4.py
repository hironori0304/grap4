import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# アプリのレイアウト設定
st.set_page_config(layout="wide")
st.title("棒グラフ作成Webアプリ")

# フォントのパスを設定（GitHub にアップロードしたフォントファイルへのパス）
font_path = os.path.join(os.getcwd(), 'MSPGothic.ttf')  # フォントファイル名を適宜変更

# フォントを読み込む
plt.rcParams['font.family'] = 'MS Pゴシック'
plt.rcParams['axes.unicode_minus'] = False  # マイナス記号の表示を適切にする

# サイドバーでCSVファイルのアップロード
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロード", type=["csv"])

if uploaded_file:
    # CSVファイルの読み込み
    df = pd.read_csv(uploaded_file)
    st.write("アップロードされたデータ:")
    st.dataframe(df)

    # サイドバーでグループ列と項目列の選択（初期状態は未選択にする）
    group_column = st.sidebar.selectbox("グループ列を選択", ["--- 選択してください ---"] + list(df.columns))
    value_column = st.sidebar.selectbox("項目列を選択", ["--- 選択してください ---"] + list(df.columns))

    # グループと項目が未選択の場合にメイン画面に警告を表示
    if group_column == "--- 選択してください ---" or value_column == "--- 選択してください ---":
        st.warning("グループと項目を選択してください。")
    else:
        # サイドバーでグラフタイトル、縦軸ラベルの入力
        graph_title = st.sidebar.text_input("グラフのタイトルを入力", "グラフタイトル")
        y_label = st.sidebar.text_input("縦軸ラベルを入力", "縦軸ラベル")

        # グラフのフォントサイズを一括設定
        font_size = st.sidebar.slider("フォントサイズを選択", 8, 30, 12)
        plt.rcParams.update({'font.size': font_size})  # フォントサイズを一括設定

        # 縦横比のスライダー追加
        aspect_ratio = st.sidebar.slider("縦横比", 0.5, 2.0, 1.0)  # 縦横比の設定

        # グループごとに色を設定するためのサイドバー
        unique_groups = df[group_column].unique()
        group_colors = {}
        st.sidebar.markdown("### グループごとの棒グラフの色を設定")
        for group in unique_groups:
            group_colors[group] = st.sidebar.color_picker(f"{group}の色", "#4CAF50")

        # サイドバーでエラーバーの設定
        show_std_dev = st.sidebar.checkbox("標準偏差を表示")
        show_std_err = st.sidebar.checkbox("標準誤差を表示")
        show_individual_plot = st.sidebar.checkbox("個々のデータプロットを表示")

        # プロットの色設定
        scatter_color = st.sidebar.color_picker('プロットの色を選択してください', '#000000')  # プロットの色設定

        # プロットのサイズ設定
        scatter_size = st.sidebar.slider('プロットのサイズを選択してください', 10, 300, 50)

        # グループごとの平均値とエラーバーの計算
        grouped_data = df.groupby(group_column)[value_column].agg(['mean', 'std', 'sem']).reset_index()

        # 元のデータの順序に基づいてグループの順番を維持する
        ordered_groups = df[group_column].unique()  # 元のデータのグループ順を取得
        means = grouped_data.set_index(group_column).reindex(ordered_groups)['mean']
        stds = grouped_data.set_index(group_column).reindex(ordered_groups)['std']
        sems = grouped_data.set_index(group_column).reindex(ordered_groups)['sem']

        # 棒グラフの作成 (小さい固定サイズ)
        fig, ax = plt.subplots(figsize=(4 * aspect_ratio, 4))  # 縦横比を設定

        # 棒グラフの表示
        bar_width = 0.8  # 棒の幅
        for i, group in enumerate(ordered_groups):
            ax.bar(group, means[i], color=group_colors[group], edgecolor="black", width=bar_width)

            # エラーバーの表示
            if show_std_dev:
                ax.errorbar(group, means[i], yerr=stds[i], fmt='none', ecolor='black', capsize=5)
            if show_std_err:
                ax.errorbar(group, means[i], yerr=sems[i], fmt='none', ecolor='black', capsize=5)

        # 個々のデータプロットの表示
        if show_individual_plot:
            jitter_strength = st.sidebar.slider("ジッターの強さ", 0.0, 0.5, 0.1)
            for i, group in enumerate(ordered_groups):
                group_data = df[df[group_column] == group][value_column]
                jitter = np.random.normal(0, jitter_strength, size=len(group_data))
                ax.scatter([i + jitter_value for jitter_value in jitter], group_data, color=scatter_color, s=scatter_size)

        # グラフの装飾設定
        ax.set_title(graph_title)
        ax.set_ylabel(y_label)
        ax.set_xlabel(group_column)

        # グラフを画像として保存
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')  # bbox_inchesで余白を調整
        buf.seek(0)

        # 画像をStreamlitに表示
        st.image(buf)

        # プロットを閉じてメモリを解放
        plt.close(fig)

else:
    st.write("CSVファイルをアップロードしてください。")
