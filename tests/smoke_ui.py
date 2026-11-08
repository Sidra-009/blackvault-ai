"""Headless UI smoke test with the real model. Run: python tests/smoke_ui.py"""
import os

from streamlit.testing.v1 import AppTest

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "app", "streamlit_app.py")
at = AppTest.from_file(APP, default_timeout=120).run()
assert not at.exception, at.exception
at.sidebar.selectbox[0].select("bank").run()
assert not at.exception, at.exception
[b for b in at.button if b.label == "Analyze message"][0].click().run()
assert not at.exception, at.exception
assert "AI SCAM SCORE" in " ".join(m.value for m in at.markdown).upper(), "result tiles missing"
at.sidebar.radio[0].set_value("Roman Urdu").run()
assert not at.exception, at.exception
assert "Nateeja" in " ".join(m.value for m in at.markdown), "Roman Urdu result missing"
print("ui smoke test passed")