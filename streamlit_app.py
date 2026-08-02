import html

import requests
import streamlit as st
from supabase import create_client


st.set_page_config(
    page_title="GSIS学びの実践記録",
    page_icon="📚",
    layout="wide",
)

st.title("📚 GSIS学びの実践記録")
st.write(
    "GSISで学んだことを授業や業務で実践し、結果と改善点まで記録します。"
    "記録したテーマに関連する文献も検索できます。"
)


@st.cache_resource
def connect_supabase():
    """StreamlitのSecretsを使ってSupabaseに接続する。"""
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


@st.cache_data(ttl=3600, show_spinner=False)
def search_crossref(keyword, rows=5):
    """Crossref REST APIからキーワードに関連する文献を取得する。"""
    response = requests.get(
        "https://api.crossref.org/works",
        params={
            "query.bibliographic": keyword,
            "rows": rows,
        },
        headers={"User-Agent": "GSIS-Learning-Records/1.0"},
        timeout=15,
    )
    response.raise_for_status()

    items = response.json().get("message", {}).get("items", [])
    results = []

    for item in items:
        titles = item.get("title") or []
        title = titles[0] if titles else "タイトル情報なし"

        author_names = []
        for author in item.get("author") or []:
            name = " ".join(
                part
                for part in [
                    author.get("given", ""),
                    author.get("family", ""),
                ]
                if part
            )
            if name:
                author_names.append(name)

        authors = ", ".join(author_names[:3]) or "著者情報なし"
        if len(author_names) > 3:
            authors += " ほか"

        date_parts = (
            item.get("published", {}).get("date-parts")
            or item.get("issued", {}).get("date-parts")
            or []
        )
        year = (
            str(date_parts[0][0])
            if date_parts and date_parts[0]
            else "年不明"
        )

        journal_names = item.get("container-title") or []
        journal = (
            journal_names[0]
            if journal_names
            else "掲載誌情報なし"
        )

        doi = item.get("DOI", "")
        url = (
            f"https://doi.org/{doi}"
            if doi
            else item.get("URL", "")
        )

        results.append(
            {
                "title": title,
                "authors": authors,
                "year": year,
                "journal": journal,
                "url": url,
            }
        )

    return results


def make_bullets(text):
    """複数行の入力をMarkdownの箇条書きに変換する。"""
    if not text:
        return "まだ記録されていません。"

    normalized = (
        text.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("・", "\n")
    )

    items = [
        line.strip().lstrip("-● ")
        for line in normalized.splitlines()
        if line.strip()
    ]

    return "\n".join(
        f"- {html.escape(item)}"
        for item in items
    )


try:
    supabase = connect_supabase()

except Exception as error:
    st.error(
        "Supabaseに接続できません。StreamlitのSecretsに"
        "SUPABASE_URLとSUPABASE_KEYが設定されているか"
        "確認してください。"
    )
    st.exception(error)
    st.stop()


if st.session_state.get("flash_message"):
    st.success(
        st.session_state.pop("flash_message")
    )


# ボタン操作後も指定したタブを表示する
def keep_tab_open(tab_label):
    st.session_state["main_navigation"] = tab_label


input_tab, records_tab, literature_tab = st.tabs(
    [
        "✍️ 新しい記録",
        "📖 これまでの記録",
        "🔎 関連文献を探す",
    ],
    key="main_navigation",
    on_change="rerun",
)


# 新しい記録
with input_tab:
    st.subheader("新しい記録")

    with st.form(
        "learning_form",
        clear_on_submit=True,
    ):
        subject = st.text_input(
            "科目名",
            placeholder="例：教育ビジネス経営論",
        )

        learning = st.text_area(
            "学んだこと",
            placeholder=(
                "1項目ずつ改行して入力してください。\n"
                "例：出口目標を明確にする\n"
                "出口から逆算して教材を設計する"
            ),
            height=150,
        )

        application = st.text_area(
            "授業や業務への活用方法",
            placeholder=(
                "1項目ずつ改行して入力してください。\n"
                "例：授業前に出口目標を設定する\n"
                "学習結果を基に教材を改善する"
            ),
            height=150,
        )

        result_improvement = st.text_area(
            "実践結果・改善点",
            placeholder=(
                "1項目ずつ改行して入力してください。\n"
                "例：学生が目標を意識できた\n"
                "次回は評価基準も提示する"
            ),
            height=150,
        )

        submitted = st.form_submit_button(
            "記録する",
            type="primary",
        )

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
                (
                    supabase
                    .table("learning_records")
                    .insert(
                        {
                            "subject": subject.strip(),
                            "learning": learning.strip(),
                            "application": application.strip(),
                            "result_improvement":
                                result_improvement.strip(),
                        }
                    )
                    .execute()
                )

                st.session_state.flash_message = (
                    "学習記録を保存しました。"
                )
                st.rerun()

            except Exception as error:
                st.error(
                    f"保存できませんでした：{error}"
                )


# これまでの記録
with records_tab:
    st.subheader("これまでの記録")

    try:
        response = (
            supabase
            .table("learning_records")
            .select("*")
            .order(
                "created_at",
                desc=True,
            )
            .execute()
        )

        records = response.data or []

    except Exception as error:
        st.error(
            f"記録を取得できませんでした：{error}"
        )
        records = []

    st.metric(
        "保存されている記録",
        f"{len(records)}件",
    )

    if records:
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

        with filter_column:
            selected_subject = st.selectbox(
                "科目名で絞り込む",
                ["すべて"] + subjects,
            )

        with search_column:
            keyword = st.text_input(
                "キーワードで検索",
                placeholder="例：出口目標",
            )

        filtered_records = []

        for record in records:
            subject_match = (
                selected_subject == "すべて"
                or record.get("subject")
                == selected_subject
            )

            search_text = " ".join(
                str(record.get(field) or "")
                for field in [
                    "subject",
                    "learning",
                    "application",
                    "result_improvement",
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
                filtered_records.append(record)

        st.caption(
            f"{len(filtered_records)}件の"
            "記録を表示しています。"
        )

        if filtered_records:
            for record in filtered_records:
                record_id = record["id"]

                created_date = str(
                    record.get("created_at") or ""
                )[:10]

                title = (
                    record.get("subject")
                    or "科目名なし"
                )

                is_editing = (
                    st.session_state.get(
                        "editing_record_id"
                    )
                    == record_id
                )

                is_deleting = (
                    st.session_state.get(
                        "deleting_record_id"
                    )
                    == record_id
                )

                with st.expander(
                    f"{title}（{created_date}）",
                    expanded=(
                        is_editing
                        or is_deleting
                    ),
                ):
                    # 編集画面
                    if is_editing:
                        st.markdown(
                            "#### 記録を編集"
                        )

                        with st.form(
                            f"edit_form_{record_id}"
                        ):
                            edited_subject = (
                                st.text_input(
                                    "科目名",
                                    value=(
                                        record.get(
                                            "subject"
                                        )
                                        or ""
                                    ),
                                )
                            )

                            edited_learning = (
                                st.text_area(
                                    "学んだこと",
                                    value=(
                                        record.get(
                                            "learning"
                                        )
                                        or ""
                                    ),
                                    height=140,
                                )
                            )

                            edited_application = (
                                st.text_area(
                                    "授業や業務への活用方法",
                                    value=(
                                        record.get(
                                            "application"
                                        )
                                        or ""
                                    ),
                                    height=140,
                                )
                            )

                            edited_result = (
                                st.text_area(
                                    "実践結果・改善点",
                                    value=(
                                        record.get(
                                            "result_improvement"
                                        )
                                        or ""
                                    ),
                                    height=140,
                                )
                            )

                            save_edit = (
                                st.form_submit_button(
                                    "変更を保存",
                                    type="primary",
                                    on_click=keep_tab_open,
                                    args=(
                                        "📖 これまでの記録",
                                    ),
                                )
                            )

                        if save_edit:
                            if not edited_subject.strip():
                                st.warning(
                                    "科目名を入力してください。"
                                )

                            elif not edited_learning.strip():
                                st.warning(
                                    "「学んだこと」を"
                                    "入力してください。"
                                )

                            else:
                                try:
                                    (
                                        supabase
                                        .table(
                                            "learning_records"
                                        )
                                        .update(
                                            {
                                                "subject":
                                                    edited_subject
                                                    .strip(),
                                                "learning":
                                                    edited_learning
                                                    .strip(),
                                                "application":
                                                    edited_application
                                                    .strip(),
                                                "result_improvement":
                                                    edited_result
                                                    .strip(),
                                            }
                                        )
                                        .eq(
                                            "id",
                                            record_id,
                                        )
                                        .execute()
                                    )

                                    st.session_state.pop(
                                        "editing_record_id",
                                        None,
                                    )

                                    st.session_state[
                                        "flash_message"
                                    ] = (
                                        "記録を更新しました。"
                                    )

                                    st.rerun()

                                except Exception as error:
                                    st.error(
                                        "更新できませんでした："
                                        f"{error}"
                                    )

                        if st.button(
                            "編集をキャンセル",
                            key=(
                                f"cancel_edit_{record_id}"
                            ),
                            on_click=keep_tab_open,
                            args=(
                                "📖 これまでの記録",
                            ),
                        ):
                            st.session_state.pop(
                                "editing_record_id",
                                None,
                            )
                            st.rerun()

                    # 通常表示
                    else:
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

                        edit_column, delete_column = (
                            st.columns(2)
                        )

                        with edit_column:
                            if st.button(
                                "編集する",
                                key=f"edit_{record_id}",
                                use_container_width=True,
                                on_click=keep_tab_open,
                                args=(
                                    "📖 これまでの記録",
                                ),
                            ):
                                (
                                    st.session_state[
                                        "editing_record_id"
                                    ]
                                ) = record_id

                                st.session_state.pop(
                                    "deleting_record_id",
                                    None,
                                )
                                st.rerun()

                        with delete_column:
                            if st.button(
                                "削除する",
                                key=f"delete_{record_id}",
                                use_container_width=True,
                                on_click=keep_tab_open,
                                args=(
                                    "📖 これまでの記録",
                                ),
                            ):
                                (
                                    st.session_state[
                                        "deleting_record_id"
                                    ]
                                ) = record_id

                                st.session_state.pop(
                                    "editing_record_id",
                                    None,
                                )
                                st.rerun()

                    # 削除確認画面
                    if is_deleting:
                        st.warning(
                            "この記録を削除しますか？"
                            "削除後は元に戻せません。"
                        )

                        (
                            confirm_column,
                            cancel_column,
                        ) = st.columns(2)

                        with confirm_column:
                            if st.button(
                                "削除を確定",
                                key=(
                                    "confirm_delete_"
                                    f"{record_id}"
                                ),
                                type="primary",
                                use_container_width=True,
                                on_click=keep_tab_open,
                                args=(
                                    "📖 これまでの記録",
                                ),
                            ):
                                try:
                                    (
                                        supabase
                                        .table(
                                            "learning_records"
                                        )
                                        .delete()
                                        .eq(
                                            "id",
                                            record_id,
                                        )
                                        .execute()
                                    )

                                    st.session_state.pop(
                                        "deleting_record_id",
                                        None,
                                    )

                                    st.session_state[
                                        "flash_message"
                                    ] = (
                                        "記録を削除しました。"
                                    )

                                    st.rerun()

                                except Exception as error:
                                    st.error(
                                        "削除できませんでした："
                                        f"{error}"
                                    )

                        with cancel_column:
                            if st.button(
                                "削除をキャンセル",
                                key=(
                                    "cancel_delete_"
                                    f"{record_id}"
                                ),
                                use_container_width=True,
                                on_click=keep_tab_open,
                                args=(
                                    "📖 これまでの記録",
                                ),
                            ):
                                st.session_state.pop(
                                    "deleting_record_id",
                                    None,
                                )
                                st.rerun()

        else:
            st.info(
                "条件に一致する記録はありません。"
            )

    else:
        st.info(
            "まだ学習記録がありません。"
        )


# 関連文献検索
with literature_tab:
    st.subheader(
        "学びに関連する文献を探す"
    )

    st.write(
        "CrossrefのWeb APIを使って、"
        "学習テーマに関連する論文などを検索します。"
        "APIキーは必要ありません。"
    )

    with st.form("literature_form"):
        literature_keyword = st.text_input(
            "検索キーワード",
            placeholder=(
                "例：instructional design、"
                "self-regulated learning"
            ),
        )

        result_count = st.slider(
            "表示件数",
            3,
            10,
            5,
        )

        search_submitted = (
            st.form_submit_button(
                "文献を検索する",
                type="primary",
                on_click=keep_tab_open,
                args=(
                    "🔎 関連文献を探す",
                ),
            )
        )

    if search_submitted:
        if not literature_keyword.strip():
            st.warning(
                "検索キーワードを入力してください。"
            )

        else:
            try:
                with st.spinner(
                    "文献を検索しています……"
                ):
                    (
                        st.session_state[
                            "literature_results"
                        ]
                    ) = search_crossref(
                        literature_keyword.strip(),
                        result_count,
                    )

                    (
                        st.session_state[
                            "literature_query"
                        ]
                    ) = literature_keyword.strip()

            except (
                requests.exceptions.RequestException
            ) as error:
                (
                    st.session_state[
                        "literature_results"
                    ]
                ) = []

                st.error(
                    "Crossrefからデータを"
                    "取得できませんでした。"
                    "時間を置いて、"
                    "もう一度お試しください。"
                )
                st.caption(str(error))

    literature_results = (
        st.session_state.get(
            "literature_results",
            [],
        )
    )

    literature_query = (
        st.session_state.get(
            "literature_query",
            "",
        )
    )

    if literature_results:
        st.success(
            f"「{literature_query}」に関連する文献を"
            f"{len(literature_results)}件取得しました。"
        )

        for index, work in enumerate(
            literature_results,
            start=1,
        ):
            st.markdown(
                f"### {index}. "
                f"{html.escape(work['title'])}"
            )

            st.write(
                f"著者：{work['authors']}"
            )

            st.write(
                f"発行年：{work['year']}　"
                f"掲載誌：{work['journal']}"
            )

            if work["url"]:
                st.link_button(
                    "文献情報を開く",
                    work["url"],
                )

            st.divider()

    st.caption(
        "文献情報はCrossrefに登録された"
        "メタデータに基づきます。"
        "検索結果の内容は、"
        "リンク先で確認してください。"
    )
