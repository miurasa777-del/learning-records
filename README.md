# GSIS学びの実践記録

GSISで学んだ内容と、その活用・実践結果を継続的に記録するStreamlitアプリです。

## アプリの概要

次の項目を入力し、学習記録として保存できます。

- 科目名
- 学んだこと
- 授業や業務への活用方法
- 実践結果・改善点

記録したデータはSupabaseに保存されるため、Streamlitアプリが休止しても保持されます。

## 主な機能

- 新しい学習記録の登録
- 入力内容の箇条書き表示
- 科目名による絞り込み
- キーワード検索
- 保存件数の表示
- 登録日時順での一覧表示

## アプリを試す

[GSIS学びの実践記録を開く](https://miurasa777-del-learning-records-streamlit-app-cgqsok.streamlit.app/)

## 使用技術

- Python
- Streamlit
- Supabase
- Streamlit Community Cloud

## 利用方法

1. 科目名と学習内容を入力します。
2. 「記録する」を押します。
3. 保存された記録を画面下部で確認します。
4. 科目名やキーワードで記録を検索できます。
