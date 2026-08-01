import streamlit as st
from supabase import create_client


# ページの設定
st.set_page_config(
    page_title="GSIS学びの実践記録",
    page_icon="📚"
)

st.title("📚 GSIS学びの実践記録")
st.write(
    "GSISで学んだことと、"
    "授業や業務での実践を記録します。"
)


# Supabaseに接続する
@st.cache_resource
def connect_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = connect_supabase()


# 入力内容を箇条書きに変換する
def make_bullets(text):
    if not text:
        return "まだ記録されていません。"

    # 「・」が入力されている場合も改行に変換する
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("・", "\n")

    lines = text.splitlines()

    items = [
        line.strip().lstrip("-● ")
        for line in lines
        if line.strip()
    ]

    return "\n".join(
        f"- {item}" for item in items
    )


# 新しい記録の入力
st.subheader("新しい記録")

with st.form(
    "learning_form",
    clear_on_submit=True
):
    subject = st.text_input(
        "科目名",
        placeholder="例：教育ビジネス経営論"
    )

    learning = st.text_area(
        "学んだこと",
        placeholder=(
            "1項目ずつ改行して入力してください。\n"
            "例：出口目標を明確にする\n"
            "出口から逆算して教材を設計する"
        ),
        height=150
    )

    application = st.text_area(
        "授業や業務への活用方法",
        placeholder=(
            "1項目ずつ改行して入力してください。\n"
            "例：授業前に出口目標を設定する\n"
            "学習結果を基に教材を改善する"
        ),
        height=150
    )

    result_improvement = st.text_area(
        "実践結果・改善点",
        placeholder=(
            "1項目ずつ改行して入力してください。\n"
            "例：学生が目標を意識できた\n"
            "次回は評価基準も提示する"
        ),
        height=150
    )

    submitted = st.form_submit_button(
        "記録する"
    )


# 入力内容をSupabaseに保存する
if submitted:
    if not subject.strip():
        st.warning(
            "科目名を入力してください。"
        )

    elif not learning.strip():
        st.warning(
            "「学んだこと」を入力してください。"
        )

    else:
        try:
            supabase.table(
                "learning_records"
            ).insert(
                {
                    "subject": subject.strip(),
                    "learning": learning.strip(),
                    "application": application.strip(),
                    "result_improvement":
                        result_improvement.strip()
                }
            ).execute()

            st.success(
                "学習記録を保存しました。"
            )

        except Exception as e:
            st.error(
                f"保存できませんでした：{e}"
            )


# Supabaseから保存済みの記録を取得する
st.divider()
st.subheader("これまでの記録")

try:
    response = (
        supabase.table("learning_records")
        .select("*")
        .order(
            "created_at",
            desc=True
        )
        .execute()
    )

    records = response.data or []

except Exception as e:
    st.error(
        f"記録を取得できませんでした：{e}"
    )
    records = []


# 保存されている記録数を表示する
st.metric(
    "保存されている記録",
    f"{len(records)}件"
)


if records:
    # 科目名の一覧を作成する
    subjects = sorted(
        {
            record["subject"]
            for record in records
            if record.get("subject")
        }
    )

    filter_column, search_column = (
        st.columns(2)
    )

    # 科目名による絞り込み
    with filter_column:
        selected_subject = st.selectbox(
            "科目名で絞り込む",
            ["すべて"] + subjects
        )

    # キーワード検索
    with search_column:
        keyword = st.text_input(
            "キーワードで検索",
            placeholder="例：出口目標"
        )

    filtered_records = []

    # 絞り込みと検索を行う
    for record in records:
        subject_match = (
            selected_subject == "すべて"
            or record.get("subject")
            == selected_subject
        )

        search_text = " ".join(
            [
                str(
                    record.get("subject")
                    or ""
                ),
                str(
                    record.get("learning")
                    or ""
                ),
                str(
                    record.get("application")
                    or ""
                ),
                str(
                    record.get(
                        "result_improvement"
                    )
                    or ""
                )
            ]
        )

        keyword_match = (
            not keyword.strip()
            or keyword.lower()
            in search_text.lower()
        )

        if (
            subject_match
            and keyword_match
        ):
            filtered_records.append(
                record
            )

    st.caption(
        f"{len(filtered_records)}件の"
        "記録を表示しています。"
    )

    # 検索結果を表示する
    if filtered_records:
        for record in filtered_records:
            created_date = str(
                record.get("created_at")
                or ""
            )[:10]

            title = (
                record.get("subject")
                or "科目名なし"
            )

            with st.expander(
                f"{title}（{created_date}）"
            ):
                st.markdown(
                    "#### 学んだこと"
                )
                st.markdown(
                    make_bullets(
                        record.get("learning")
                    )
                )

                st.markdown(
                    "#### 授業や業務への活用方法"
                )
                st.markdown(
                    make_bullets(
                        record.get("application")
                    )
                )

                st.markdown(
                    "#### 実践結果・改善点"
                )
                st.markdown(
                    make_bullets(
                        record.get(
                            "result_improvement"
                        )
                    )
                )

                st.caption(
                    "登録日時："
                    f"{record.get('created_at', '')}"
                )

    else:
        st.info(
            "条件に一致する記録はありません。"
        )

else:
    st.info(
        "まだ学習記録がありません。"
    )
