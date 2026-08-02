# 📚 GSIS学びの実践記録

Streamlitを利用した、GSISでの学びを継続的に記録するためのWebアプリケーションです。「学んだこと」だけでなく、授業や業務への活用方法、実践結果・改善点まで記録できます。登録した記録は後から編集・削除でき、学習テーマに関連する文献も検索できます。入力したデータはSupabaseに保存されます。

---

## URL

このURLから試すことができます（スリープ状態のときは、表示される起動ボタンを押してください）：  
https://miurasa777-del-learning-records-streamlit-app-cggsok.streamlit.app/

---

## 🌟 主な機能

* **学習記録の登録**: 科目名、学んだこと、授業や業務への活用方法、実践結果・改善点を登録できます。
* **記録の編集**: 登録済みの記録を開き、内容を修正して再保存できます。
* **記録の削除**: 確認画面を経て、不要な記録を削除できます。
* **箇条書き表示**: 1項目ずつ改行して入力した内容を、読みやすい箇条書きで表示します。
* **科目別の絞り込み**: 保存された記録を科目名で絞り込めます。
* **キーワード検索**: 学んだ内容や活用方法をキーワードで検索できます。
* **関連文献の検索**: 学習テーマを入力すると、Crossrefから関連する論文などを検索できます。
* **保存件数の表示**: Supabaseに保存されている記録数を確認できます。
* **データの継続保存**: Streamlitアプリが休止しても、登録したデータはSupabaseに保持されます。

---

## 🛠 セットアップ方法

### 1. 依存ライブラリのインストール

Python環境で、必要なライブラリをインストールします。

```bash
pip install streamlit supabase requests
```

または、次のコマンドで`requirements.txt`に記載されたライブラリをまとめてインストールできます。

```bash
pip install -r requirements.txt
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

編集・削除機能を利用するため、SupabaseのSQL Editorで`supabase_edit_delete.sql`を実行します。

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
* **UPDATE Policy**: 登録済み記録の編集を許可
* **DELETE Policy**: 登録済み記録の削除を許可

---

## 🌐 使用しているWeb API

関連文献の検索には、[Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)を使用しています。検索キーワードをWeb APIに送り、文献のタイトル、著者、発行年、掲載誌、DOIリンクなどをJSON形式で取得します。APIキーは必要ありません。

---

## 💻 使用技術

* **Frontend/UI**: [Streamlit](https://streamlit.io/)
* **Database**: [Supabase](https://supabase.com/)
* **Web API**: [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
* **HTTP通信**: Requests
* **Language**: Python
* **Deployment**: Streamlit Community Cloud

---

## ⚠️ 利用上の注意

このアプリにはログイン機能がないため、アプリにアクセスできる人は、保存済みの記録を閲覧・編集・削除できます。氏名、学生番号、成績などの個人情報や機密情報は入力しないでください。

---

## 💡 今後の改良案

* 日付による絞り込み機能
* CSV形式でのダウンロード機能
* ログイン機能の追加
