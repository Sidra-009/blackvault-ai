"""Tests for the rule-based helpers. No model, no network."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "app"))

from analysis import analyze_url, extract_entities, extract_urls, final_verdict, find_flags, scam_types  # noqa: E402

BANK = "Aapka bank account aaj raat band ho jaye ga. Foran is link par click kar ke apna PIN aur OTP bhejein: http://bank-verify.example"
NORMAL = "Kal meeting 3 baje hai, agenda mail kar diya hai. Please check kar lena."


def test_flags_bank_message():
    flags = find_flags(BANK)
    assert {"urgency", "link", "cred", "org", "threat"} <= set(flags)


def test_flags_normal_message_empty():
    assert find_flags(NORMAL) == []


def test_extract_urls_strips_trailing_punctuation():
    urls = extract_urls("Click http://a-b.example/x, or www.test.com. Also bit.ly/abc!")
    assert urls == ["http://a-b.example/x", "www.test.com", "bit.ly/abc"]


def test_url_issues():
    r = analyze_url("http://bank-verify.example")
    assert "no_https" in r["issues"] and "lookalike" in r["issues"]
    assert "ip_host" in analyze_url("http://192.168.1.10/login")["issues"]
    assert "shortener" in analyze_url("bit.ly/abc")["issues"]
    assert "odd_tld" in analyze_url("https://prize-now.xyz/claim")["issues"]
    assert "at_sign" in analyze_url("http://hbl.com@evil.example/login")["issues"]
    assert analyze_url("https://www.google.com/search")["issues"] == []


def test_entities():
    e = extract_entities("Send Rs 1,500 to 0300-1234567 or +92 301 7654321 or 5000 rupees")
    assert len(e["phones"]) == 2
    assert len(e["amounts"]) == 2


def test_scam_types():
    assert "bank" in scam_types(BANK, find_flags(BANK))
    assert "parcel" in scam_types("Your parcel is held, pay fee", ["money"])
    assert scam_types(NORMAL, []) == []


def test_final_verdict_rules_override_low_model_score():
    flags = find_flags(BANK)
    urls = [analyze_url(u) for u in extract_urls(BANK)]
    color, key, basis = final_verdict(0.10, flags, urls)
    assert (color, key, basis) == ("red", "red_rules", "rules")


def test_final_verdict_plain_model_bands():
    assert final_verdict(0.9, [], [])[0] == "red"
    assert final_verdict(0.5, [], [])[0] == "amber"
    assert final_verdict(0.1, [], []) == ("green", "green", "model")
