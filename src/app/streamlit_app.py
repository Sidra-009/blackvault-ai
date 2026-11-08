"""BlackVault AI - ScamShield: bilingual text scam screening UI (demo).
Run: streamlit run src/app/streamlit_app.py"""
import html
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis import (  # noqa: E402
    analyze_url, extract_entities, extract_urls, final_verdict, find_flags, scam_types,
)
from i18n import TXT  # noqa: E402
from model import predict_text  # noqa: E402
from theme import CSS, flag_html, logo, step_html, tiles_html  # noqa: E402

st.set_page_config(page_title="BlackVault AI", layout="wide", initial_sidebar_state="expanded")

st.markdown(CSS, unsafe_allow_html=True)

EXAMPLES = {
    "bank": ("Bank alert (Roman Urdu)", "Bank alert (Roman Urdu)",
             "Aapka bank account aaj raat band ho jaye ga. Foran is link par click kar ke apna PIN aur OTP bhejein: http://bank-verify.example"),
    "prize": ("Prize message (English)", "Inami message (English)",
              "Congratulations! You won a cash prize. Send your CNIC number and pay a small fee today to claim it."),
    "parcel": ("Courier fee (English)", "Courier fee (English)",
               "Your parcel is on hold. Pay Rs 150 delivery fee at http://track-parcel.example or it will be returned."),
    "normal": ("Normal message", "Aam message",
               "Kal meeting 3 baje hai, agenda mail kar diya hai. Please check kar lena."),
}

@st.cache_data(show_spinner=False)
def analyze(text):
    res = predict_text(text)
    risk = float(res["risk"])
    words = re.findall(r"\S+", text)
    impacts = None
    if len(words) <= 80:
        impacts = []
        for i in range(len(words)):
            rest = " ".join(words[:i] + words[i + 1:]).strip()
            impacts.append(0.0 if not rest else risk - float(predict_text(rest)["risk"]))
    return risk, str(res.get("language_hint", "english")), words, impacts


def full_check(text):
    """Everything about one message that does not need word-level impacts."""
    risk = float(predict_text(text)["risk"])
    flags = find_flags(text)
    urls = [analyze_url(u) for u in extract_urls(text)]
    color, vkey, basis = final_verdict(risk, flags, urls)
    return risk, flags, urls, color, vkey, basis


def highlight(words, impacts):
    out = []
    for w, d in zip(words, impacts):
        safe = html.escape(w)
        if d >= 0.03:
            alpha = min(0.85, 0.25 + d * 3)
            out.append(f'<mark style="background: rgba(217,48,37,{alpha:.2f});">{safe}</mark>')
        else:
            out.append(safe)
    return " ".join(out)


def build_report(T, text, risk, title, basis_text, flags, urls):
    lines = [
        T["report_title"],
        "=" * len(T["report_title"]),
        f"{T['r_time']}: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"{T['r_verdict']}: {title}",
        f"{T['r_score']}: {risk * 100:.0f}%",
        f"{T['r_basis']}: {basis_text}",
        f"{T['r_signs']}: " + (", ".join(T["flags"][k] for k in flags) if flags else T["r_none"]),
        f"{T['r_links']}: " + (", ".join(u["url"] for u in urls) if urls else T["r_none"]),
        "",
        f"{T['r_msg']}:",
        text,
        "",
        T["r_note"],
    ]
    return "\n".join(lines)


def on_example():
    # The browser can re-fire this callback after a language switch; only act on a real change to a real example.
    key = st.session_state.get("ex_key", "-")
    if key == st.session_state.get("last_ex", "-"):
        return
    st.session_state["last_ex"] = key
    if key in EXAMPLES:
        st.session_state["msg"] = EXAMPLES[key][2]
        st.session_state["run"] = False


def on_clear():
    st.session_state["msg"] = ""
    st.session_state["ex_key"] = "-"
    st.session_state["last_ex"] = "-"
    st.session_state["run"] = False


def on_batch():
    st.session_state["batch_run"] = True


st.session_state.setdefault("msg", "")
st.session_state.setdefault("run", False)
st.session_state.setdefault("ex_key", "-")
st.session_state.setdefault("batch_msg", "")
st.session_state.setdefault("batch_run", False)
st.session_state.setdefault("history", [])

with st.sidebar:
    st.markdown(f'<div class="hero sbrand">{logo(46)}<div><b style="font-size:1.25rem;">BlackVault AI</b></div></div>', unsafe_allow_html=True)
    lang = st.radio("Language / Zaban", ["English", "Roman Urdu"], horizontal=True)
    T = TXT[lang]
    idx = 0 if lang == "English" else 1
    st.markdown(f"**{T['example']}**")
    st.selectbox(
        "example", ["-"] + list(EXAMPLES), key="ex_key", on_change=on_example, label_visibility="collapsed",
        format_func=lambda k: T["no_example"] if k == "-" else EXAMPLES[k][idx],
    )
    st.markdown("---")
    hist_slot = st.container()  # filled at the end of the script so it shows the check that just ran
    st.markdown("---")
    st.markdown(f"**{T['about_h']}**")
    st.caption(T["about"])
    st.markdown(f"**{T['limits_h']}**")
    for item in T["limits"]:
        st.caption("- " + item)

T = TXT[lang]
st.markdown(
    f'<div class="hero">{logo(64)}<div><h1>BlackVault AI</h1><div class="sub">{T["brand_sub"]}</div></div></div>',
    unsafe_allow_html=True,
)
st.markdown(f'<p class="tag"><b>{T["tagline"]}</b><br>{T["intro"]}</p>', unsafe_allow_html=True)

tab_check, tab_batch, tab_guide = st.tabs(T["main_tabs"])

# ---------------------------------------------------------------- single message
with tab_check:
    # Widget label/placeholder must NOT change with the language, or Streamlit treats it as a new widget and clears the text.
    st.markdown(f"**{T['input']}**")
    text = st.text_area("message", key="msg", height=150, max_chars=5000,
                        label_visibility="collapsed", placeholder="Paste message here / Message yahan paste karo...")
    c1, c2, _ = st.columns([1.4, 0.9, 4])
    clicked = c1.button(T["analyze"], type="primary")
    c2.button(T["clear"], on_click=on_clear)
    if clicked:
        st.session_state["run"] = True

    if st.session_state["run"]:
        if not text.strip():
            st.warning(T["empty"])
        else:
            risk, lang_hint, words, impacts = analyze(text)
            flags = find_flags(text)
            url_reports = [analyze_url(u) for u in extract_urls(text)]
            color, vkey, basis = final_verdict(risk, flags, url_reports)
            title, sub = T["v"][vkey]
            basis_text = T["basis_rules"] if basis == "rules" else T["basis_model"]
            kinds = scam_types(text, flags)
            lang_name = T["l_roman_urdu"] if lang_hint == "roman_urdu" else T["l_english"]

            if clicked:
                st.session_state["history"].insert(
                    0, {"pct": f"{risk * 100:.0f}", "label": title, "snippet": text.strip()[:36].replace("\n", " ")}
                )
                st.session_state["history"] = st.session_state["history"][:10]

            st.markdown(tiles_html(T, title, sub, color, risk, lang_name), unsafe_allow_html=True)
            st.markdown(f'<div class="basis">{basis_text}</div>', unsafe_allow_html=True)
            if kinds:
                chips = "".join(f'<span class="chip">{T["types"][k]}</span>' for k in kinds)
                st.markdown(f'<div><b>{T["types_label"]}:</b> {chips}<div class="basis">{T["types_note"]}</div></div>',
                            unsafe_allow_html=True)

            t_why, t_signs, t_links, t_do, t_share = st.tabs(T["tabs"])

            with t_why:
                if impacts is None:
                    st.info(T["why_long"])
                elif max(impacts, default=0) < 0.03:
                    st.info(T["why_none"])
                    st.markdown(f'<div class="msgbox">{html.escape(text)}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="msgbox">{highlight(words, impacts)}</div>', unsafe_allow_html=True)
                    st.caption(T["why_cap"])

            with t_signs:
                if flags:
                    for i, k in enumerate(flags, 1):
                        st.markdown(flag_html(T["flags"][k], i), unsafe_allow_html=True)
                    st.caption(T["signs_cap"])
                else:
                    st.info(T["signs_none"])

            with t_links:
                st.markdown(f"**{T['links_h']}**")
                if url_reports:
                    for r in url_reports:
                        if r["issues"]:
                            items = "".join(f"<li>{T['url_issues'][i]}</li>" for i in r["issues"])
                        else:
                            items = f"<li>{T['link_ok']}</li>"
                        st.markdown(
                            f'<div class="urlbox"><code>{html.escape(r["url"])}</code><ul>{items}</ul></div>',
                            unsafe_allow_html=True,
                        )
                    st.caption(T["links_note"])
                else:
                    st.info(T["links_none"])
                ent = extract_entities(text)
                st.markdown(f"**{T['ent_h']}**")
                if ent["phones"] or ent["amounts"]:
                    if ent["phones"]:
                        st.write(f"{T['ent_phones']}: " + ", ".join(ent["phones"]))
                    if ent["amounts"]:
                        st.write(f"{T['ent_amounts']}: " + ", ".join(ent["amounts"]))
                else:
                    st.caption(T["ent_none"])

            with t_do:
                steps = T["do_ok"] if color == "green" else T["do_bad"]
                for n, step in enumerate(steps, 1):
                    st.markdown(step_html(n, step), unsafe_allow_html=True)

            with t_share:
                st.markdown(f"**{T['share_h']}**")
                kind = T["types"][kinds[0]].lower() if kinds else T["share_generic"]
                st.caption(T["share_cap"])
                st.code(T["share_tpl"].format(kind=kind), language=None)
                st.markdown(f"**{T['report_h']}**")
                st.download_button(
                    T["report_btn"],
                    data=build_report(T, text, risk, title, basis_text, flags, url_reports),
                    file_name="blackvault_report.txt",
                    mime="text/plain",
                )
                st.caption(T["report_cap"])

# ---------------------------------------------------------------- batch
with tab_batch:
    st.subheader(T["batch_h"])
    st.caption(T["batch_help"])
    st.markdown(f"**{T['batch_input']}**")
    st.text_area("batch messages", key="batch_msg", height=170, label_visibility="collapsed")
    st.button(T["batch_btn"], on_click=on_batch)
    if st.session_state["batch_run"]:
        msgs = [m.strip() for m in st.session_state["batch_msg"].splitlines() if m.strip()]
        if not msgs:
            st.warning(T["batch_empty"])
        else:
            if len(msgs) > 30:
                st.caption(T["batch_cut"])
                msgs = msgs[:30]
            rows = []
            for n, m in enumerate(msgs, 1):
                risk, flags, urls, color, vkey, basis = full_check(m)
                rows.append({
                    T["batch_cols"][0]: n,
                    T["batch_cols"][1]: T["v"][vkey][0],
                    T["batch_cols"][2]: round(risk * 100),
                    T["batch_cols"][3]: len(flags),
                    T["batch_cols"][4]: m[:90],
                })
            df = pd.DataFrame(rows).sort_values(T["batch_cols"][2], ascending=False)
            st.dataframe(df, hide_index=True)
            st.download_button(T["batch_csv"], data=df.to_csv(index=False), file_name="blackvault_batch.csv", mime="text/csv")

# ---------------------------------------------------------------- guide
with tab_guide:
    st.subheader(T["guide_h"])
    for gi, (key, (how, tip)) in enumerate(T["guide"].items(), 1):
        st.markdown(
            f'<div class="guide" style="--i:{gi}"><h4>{T["types"][key]}</h4>'
            f'<div><b>{T["guide_how"]}:</b> {how}</div><div><b>{T["guide_tip"]}:</b> {tip}</div></div>',
            unsafe_allow_html=True,
        )
    st.subheader(T["rules_h"])
    for n, r in enumerate(T["rules"], 1):
        st.markdown(step_html(n, r), unsafe_allow_html=True)

with hist_slot:
    st.markdown(f"**{T['hist_h']}**")
    if st.session_state["history"]:
        for h in st.session_state["history"][:5]:
            st.caption(f"{h['pct']}% - {h['label']} - {h['snippet']}")
    else:
        st.caption(T["hist_none"])

st.markdown(f'<div class="foot">{T["foot"]}</div>', unsafe_allow_html=True)
