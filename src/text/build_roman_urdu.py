import random, pandas as pd
random.seed(42)

scam = [
 "Mubarak ho! Aap ka {amount} rupay ka inam nikla hai. Claim karne ke liye {link} par click karein.",
 "Aap ka {bank} account block ho jaye ga. Foran apna PIN {link} par update karein.",
 "BISP ki taraf se aap ke {amount} rupay approve hue hain. Registration ke liye {fee} rupay JazzCash karein.",
 "Aap ka parcel {courier} par ruka hua hai. Address confirm karne ke liye {link} kholein.",
 "Ghar baithe {amount} rupay mahana kamayein. Registration fee {fee} EasyPaisa karein.",
]
normal = [
 "Yaar kal shaam ko {place} chalte hain, {time} baje milte hain.",
 "Ammi ne kaha hai ke ghar aate waqt {item} le aana.",
 "Aap ke {bank} account se {amount} rupay {time} par debit hue. Shukriya.",
 "Kal {subject} ka test hai, notes bhej do please.",
 "Meeting {time} baje hai, please time par pohanch jana.",
]
fill = {
 "amount": ["10,000", "25,000", "50,000", "1 lakh"],
 "fee": ["200", "500", "1000"],
 "bank": ["HBL", "UBL", "Meezan", "Allied"],
 "courier": ["TCS", "Leopards", "M&P"],
 "link": ["http://claim-now.example/x1", "http://verify-acc.example/k9"],
 "place": ["Dolmen Mall", "Clifton", "chai wale"],
 "time": ["5", "6", "8", "11 baje"],
 "item": ["doodh", "roti", "sabzi"],
 "subject": ["Math", "Stats", "Physics"],
}

class SafeDict(dict):
    def __missing__(self, k): return "{" + k + "}"

rows = []
for label, templates in [(1, scam), (0, normal)]:
    for tid, t in enumerate(templates):
        for _ in range(12):
            vals = {k: random.choice(v) for k, v in fill.items()}
            rows.append({"text": t.format_map(SafeDict(vals)), "label": label,
                         "template_id": f"{label}_{tid}"})

df = pd.DataFrame(rows).drop_duplicates(subset="text")
df.to_csv("data/processed/roman_urdu.csv", index=False)
print(df.shape); print(df["label"].value_counts())
