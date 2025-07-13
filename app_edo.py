import streamlit as st
import json
import re
import time

# JSON読み込み関数
def load_story(lang):
    filename = "story_sakamoto_en.json" if lang == "en" else "story_sakamoto_jp.json"
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# セッション初期化
def init_session():
    defaults = {
        "chapter": "start",
        "lp": 3,
        "selected": None,
        "show_result": False,
        "show_next": False,
        "show_story": False,
        "player_name": "",
        "lang": "ja",
        "show_choices": False,
        "lp_updated": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# プレイヤーネームを埋め込む
def personalize(text):
    name = st.session_state.get("player_name", "あなた")
    return re.sub(r"{player_name}", name, text)

# メイン処理
def main():
    st.set_page_config(page_title="坂本龍馬異聞録 / The Saga of Ryoma Sakamoto", layout="centered")
    init_session()

    # スタート画面
    if st.session_state.chapter == "start":
        lang_map = {"日本語": "ja", "English": "en"}
        lang_selection = st.radio("🌐 Language / 言語を選んでください：", ("日本語", "English"), index=0)
        st.session_state.lang = lang_map[lang_selection]
        lang = st.session_state.lang

        story = load_story(lang)
        st.image("assets/img_start.png", use_container_width=True)
        st.markdown("### 坂本龍馬異聞録 / The Saga of Ryoma Sakamoto")

        intro_text = story.get("intro_text" if lang == "en" else "intro_text", "")
        st.markdown(personalize(intro_text))

        name_input = st.text_input("あなたの名前を入力してください/Please input your name")
        if st.button("▶ ゲームを始める/Game start"):
            if not name_input.strip():
                st.warning("名前を入力してください/Please input your name")
            else:
                st.session_state.player_name = name_input
                st.session_state.chapter = "1"
                st.rerun()
        st.stop()

    # ストーリーデータ取得
    story = load_story(st.session_state.lang)
    chapter_key = st.session_state.chapter
    chapter = story["chapters"].get(chapter_key)
    if not chapter:
        st.error("この章のデータが見つかりません")
        return

    # ライフが0→ゲームオーバー
    if st.session_state.lp <= 0:
        st.markdown("### 💀 ゲームオーバー / Game Over")
        st.image("assets/img_gameover.png", use_container_width=True)
        if st.button("🔁 最初からやり直す / Restart"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        return

    # 結果表示フェーズ
    if st.session_state.show_result and st.session_state.selected is not None:
        choice = chapter["choices"][st.session_state.selected]
        result_data = choice["result"]
        result = personalize(result_data.get("text", ""))

        if not st.session_state.lp_updated:
            lp_diff = result_data.get("lp", 0)
            st.session_state.lp = max(0, min(3, st.session_state.lp + lp_diff))
            st.session_state.lp_updated = True

        st.markdown(f" {personalize(chapter['title'])}")

        # ✅ ここで画像を切り替える（result_image → choice_image → image）
        result_image = result_data.get("result_image", chapter.get("choice_image", chapter["image"]))
        st.image(f"assets/{result_image}", use_container_width=True)

        st.markdown("❤️ LP: " + str(st.session_state.lp))
        st.write(result)

        button_label_n = result_data.get("button_label_n", "▶ 次の章へ進む / Next Chapter")
        if st.button(personalize(button_label_n)):
            st.session_state.chapter = str(result_data.get("next", "end"))
            st.session_state.selected = None
            st.session_state.show_result = False
            st.session_state.show_story = False
            st.session_state.show_choices = False
            st.session_state.lp_updated = False
            st.rerun()
        return

    # ストーリー導入
    if not st.session_state.show_story:
        st.markdown(f" {personalize(chapter['title'])}")
        st.image(f"assets/{chapter['image']}", use_container_width=True)
        st.markdown("❤️ LP: " + str(st.session_state.lp))
        st.write(personalize(chapter.get("text", "")))

        # if st.button("▶ ストーリーを読む / Read Story"):
        button_label_r = chapter.get("button_label_r", "▶ 続きを読む")
        if st.button(personalize(button_label_r)):
            st.session_state.show_story = True
            st.rerun()
        return


    # 本文表示
    if not st.session_state.show_choices:
        st.markdown(f" {personalize(chapter['title'])}")
        st.image(f"assets/{chapter['image']}", use_container_width=True)
        st.markdown("❤️ LP: " + str(st.session_state.lp))
        st.write(personalize(chapter.get("story", "")))

        button_label_c = chapter.get("button_label_c", "▶ 選択してください / Please select.")
        if st.button(personalize(button_label_c)):
            st.session_state.show_choices = True
            st.rerun()
        return


    # 選択肢表示
    st.markdown(f" {personalize(chapter['title'])}")
    st.image(f"assets/{chapter.get('choice_image', chapter['image'])}", use_container_width=True)
    st.markdown("❤️ LP: " + str(st.session_state.lp))

    if not chapter.get("choices"):
        st.markdown("Thank you for playing!")

        if st.button("🔙 スタート画面に戻る/Back to start"):
            st.balloons()
            time.sleep(2)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        return

    # ✅ choicesがある場合の通常処理
    for i, choice in enumerate(chapter["choices"]):
        if st.button(personalize(choice["text"]), key=f"choice_{i}"):
            st.session_state.selected = i
            st.session_state.show_result = True
            st.session_state.lp_updated = False
            st.rerun()


if __name__ == "__main__":
    main()
