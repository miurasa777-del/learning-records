import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="GSIS学びの実践記録",
    page_icon="📚"
)

st.title("📚 GSIS学びの実践記録")
st.write("GSISで学んだことと、授業や業務での実践を記録します。")


@st.cache_resource
def connect_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = connect_supabase()

# 新しい記録の入力
st.subheader("新しい記録")

with st.form("learning_form", clear_on_submit=True):
    subject = st.text_input(
        "科目名",
        placeholder="例：ラーニングテクノロジーⅠ"
    )

    learning = st.text_area(
        "学んだこと",
        placeholder="授業で学んだ理論や技術を入力してください。"
    )

    application = st.text_area(
        "授業や業務への活用方法",
        placeholder="学んだことをどのように活用するか入力してください。"
    )

    result_improvement = st.text_area(
        "実践結果・改善点",
        placeholder="実践した結果と今後の改善点を入力してください。"
    )

    submitted = st.form_submit_button("記録する")

if submitted:
    if not subject.strip():
        st.warning("科目名を入力してください。")

    elif not learning.strip():
        st.warning("「学んだこと」を入力してください。")

    else:
        try:
            supabase.table("learning_records").insert(
                {
                    "subject": subject.strip(),
                    "learning": learning.strip(),
                    "application": application.strip(),
                    "result_improvement": result_improvement.strip()
                }
            ).execute()

            st.success("学習記録を保存しました。")

        except Exception as e:
            st.error(f"保存できませんでした：{e}")

# Supabaseから記録を取得
st.divider()
st.subheader("これまでの記録")

try:
    response = (
        supabase.table("learning_records")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    records = response.data or []

except Exception as e:
    st.error(f"記録を取得できませんでした：{e}")
    records = []

# 改良1：保存件数を表示
st.metric("保存されている記録", f"{len(records)}件")

if records:
    # 改良2：科目名で絞り込み
    subjects = sorted(
        {
            record["subject"]
            for record in records
            if record.get("subject")
        }
    )

    selected_subject = st.selectbox(
        "科目名で絞り込む",
        ["すべて"] + subjects
    )

    # 改良3：キーワード検索
    keyword = st.text_input(
        "キーワードで検索",
        placeholder="学んだ内容や活用方法を検索できます。"
    )

    filtered_records = []

    for record in records:
        subject_match = (
            selected_subject == "すべて"
            or record.get("subject") == selected_subject
        )

        search_text = " ".join(
            [
                str(record.get("subject") or ""),
                str(record.get("learning") or ""),
                str(record.get("application") or ""),
                str(record.get("result_improvement") or "")
            ]
        )

        keyword_match = (
            not keyword.strip()
            or keyword.lower() in search_text.lower()
        )

        if subject_match and keyword_match:
            filtered_records.append(record)

    st.caption(f"{len(filtered_records)}件の記録を表示しています。")

    if filtered_records:
        for record in filtered_records:
            created_date = str(
                record.get("created_at") or ""
            )[:10]

            title = record.get("subject") or "科目名なし"

            with st.expander(
                f"{title}（{created_date}）"
            ):
                st.markdown("#### 学んだこと")
                st.write(
                    record.get("learning")
                    or "記録されていません。"
                )

                st.markdown("#### 授業や業務への活用方法")
                st.write(
                    record.get("application")
                    or "まだ記録されていません。"
                )

                st.markdown("#### 実践結果・改善点")
                st.write(
                    record.get("result_improvement")
                    or "まだ記録されていません。"
                )

                st.caption(
                    f"登録日時：{record.get('created_at', '')}"
                )
    else:
        st.info("条件に一致する記録はありません。")

else:
    st.info("まだ学習記録がありません。")
