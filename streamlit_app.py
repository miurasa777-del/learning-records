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
        placeholder="学んだことを、どのように活用するか入力してください。"
    )

    result_improvement = st.text_area(
        "実践結果・改善点",
        placeholder="実践した結果と、今後の改善点を入力してください。"
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

st.divider()
st.subheader("これまでの記録")

try:
    response = (
        supabase.table("learning_records")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    if response.data:
        for record in response.data:
            with st.expander(record["subject"]):
                st.markdown("#### 学んだこと")
                st.write(record["learning"])

                st.markdown("#### 授業や業務への活用方法")
                st.write(
                    record["application"]
                    or "まだ記録されていません。"
                )

                st.markdown("#### 実践結果・改善点")
                st.write(
                    record["result_improvement"]
                    or "まだ記録されていません。"
                )

                st.caption(
                    f"登録日時：{record['created_at']}"
                )
    else:
        st.info("まだ学習記録がありません。")

except Exception as e:
    st.error(f"記録を取得できませんでした：{e}")
