# 📚 GSIS学びの実践記録

Streamlitを利用した、GSISでの学びを継続的に記録するためのWebアプリケーションです。「学んだこと」だけでなく、授業や業務への活用方法、実践結果・改善点まで記録できます。入力したデータはSupabaseに保存されます。

---

## URL

このURLから試すことができます（スリープ状態のときは、表示される起動ボタンを押してください）：  
https://miurasa777-del-learning-records-streamlit-app-cggsok.streamlit.app/

---

## 🌟 主な機能

* **学習記録の登録**: 科目名、学んだこと、授業や業務への活用方法、実践結果・改善点を登録できます。
* **箇条書き表示**: 1項目ずつ改行して入力した内容を、読みやすい箇条書きで表示します。
* **科目別の絞り込み**: 保存された記録を科目名で絞り込めます。
* **キーワード検索**: 学んだ内容や活用方法をキーワードで検索できます。
* **保存件数の表示**: Supabaseに保存されている記録数を確認できます。
* **データの継続保存**: Streamlitアプリが休止しても、登録したデータはSupabaseに保持されます。

---

## 🛠 セットアップ方法

### 1. 依存ライブラリのインストール

Python環境で、必要なライブラリをインストールします。

```bash
pip install streamlit supabase
```

### 2. Supabaseの準備

Supabaseに`learning_records`テーブルを作成し、次の列を設定します。

| 列名 | 内容 |
| :--- | :--- |
| id | 記録番号 |
| created_at | 登録日時 |
| subject | 科目名 |
| learning | 学んだこと |
| application | 授業や業務への活用方法 |
| result_improvement | 実践結果・改善点 |

### 3. Secretsの設定

Streamlit Community CloudのSecretsに、Supabaseの接続情報を登録します。

```toml
SUPABASE_URL = "SupabaseのProject URL"
SUPABASE_KEY = "SupabaseのPublishable key"
```

実際の接続情報は、GitHubのソースコードには記載しません。

### 4. アプリの起動

以下のコマンドでアプリを起動します。

```bash
streamlit run streamlit_app.py
```

---

## 📊 データの仕組み

このアプリは、SupabaseのPostgreSQLデータベースを使用して学習記録を管理しています。

* **learning_records**: 科目名、学習内容、活用方法、実践結果・改善点、登録日時を保存
* **SELECT Policy**: 保存された記録の読み取りを許可
* **INSERT Policy**: 新しい記録の追加を許可

---

## 💻 使用技術

* **Frontend/UI**: [Streamlit](https://streamlit.io/)
* **Database**: [Supabase](https://supabase.com/)
* **Language**: Python
* **Deployment**: Streamlit Community Cloud

---

## 💡 今後の改良案

* 登録した記録の編集・削除機能
* 日付による絞り込み機能
* CSV形式でのダウンロード機能
* ログイン機能の追加
