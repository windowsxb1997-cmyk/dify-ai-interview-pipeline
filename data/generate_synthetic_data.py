# -*- coding: utf-8 -*-
"""生成合成问卷数据（模拟 500 人预设池提交+AI 初筛后的问卷池状态）"""
import csv
import random
from datetime import datetime, timedelta

random.seed(42)

FIRST = ["James","Emma","Liam","Olivia","Noah","Ava","Ethan","Sophia","Mason","Isabella",
         "Lucas","Mia","Logan","Charlotte","Jackson","Amelia","Aiden","Harper","Elijah","Evelyn",
         "Jordan","Taylor","Casey","Riley","Alex","Marcus","Jasmine","Diego","Priya","Kevin",
         "Chen","Yuki","Carlos","Fatima","Andre","Nina","Omar","Grace","Tyler","Megan"]
LAST = ["Smith","Johnson","Brown","Garcia","Miller","Davis","Martinez","Lopez","Wilson","Anderson",
        "Thomas","Moore","Martin","Lee","Thompson","White","Harris","Clark","Lewis","Young",
        "Kim","Patel","Nguyen","Chen","Rivera","Brooks","Bennett","Reed","Coleman","Vargas"]
CITIES = ["Austin, TX","Seattle, WA","Boston, MA","Denver, CO","Chicago, IL","San Diego, CA",
          "Atlanta, GA","Toronto, ON","Vancouver, BC","New York, NY","Los Angeles, CA",
          "Durham, NC","Ann Arbor, MI","Madison, WI","Portland, OR","Miami, FL","Dallas, TX",
          "Philadelphia, PA","Phoenix, AZ","Montreal, QC"]
OCCUPATIONS = ["Grad student","Software engineer","Nurse","Teacher","Accountant","Product designer",
               "Sales rep","PhD candidate","Personal trainer","Marketing specialist","Data analyst",
               "Barista","Lawyer","Architect","Physical therapist","Financial analyst","Student (undergrad)",
               "Project manager","UX researcher","Electrician"]
GYM_TYPES = ["University / campus gym","Corporate / office gym",
             "Commercial gym (e.g. Planet Fitness, LA Fitness, Equinox, YMCA)",
             "Apartment gym","Other"]
FREQS = ["Less than once","1-2 times","2-3 times","4-5 times","6+ times"]
PRICE_BANDS = ["Under $100","$100 - $199","$200 - $299","$300 or above"]
WEAR_FREQ = ["Every session","Often (more than half)","Sometimes","Rarely","Never"]
MODELS_BY_PRICE = {
    "Under $100": ["Anker Soundcore Life Q20","JLab Studio Pro","Sony WH-CH520","generic Amazon brand"],
    "$100 - $199": ["Beats Solo 3","Soundcore Space One","JBL Live 660NC","Sony WH-CH720N"],
    "$200 - $299": ["Sony WH-1000XM4","Beats Studio Pro","Bose QC45","Sennheiser Accentum"],
    "$300 or above": ["AirPods Max","Sony WH-1000XM5","Bose QC Ultra","Sennheiser Momentum 4","Bowers & Wilkins Px7 S2e"],
}
TRAIN_POOL = ["strength training","powerlifting","bodybuilding","cardio","HIIT","CrossFit",
              "group classes","running","cycling","rowing","yoga","basketball"]

PAIN_POOL = {
    "heat": ["They get really hot and sweaty after an hour, the pads feel damp",
             "My ears overheat during long sessions, especially in summer",
             "The ear cups trap heat; I have to take them off between sets to air out"],
    "slip": ["They slide forward when I lie down for bench press",
             "The headband shifts during incline press and I have to readjust",
             "Any lying-down exercise makes them slip off position"],
    "weight": ["A bit heavy, my neck feels it after 90 minutes",
               "The clamping force gives me a headache on long sessions"],
    "clean": ["Sweat soaks into the pads and they start to smell; wiping never feels enough",
              "The fabric pads absorb sweat and are hard to clean"],
    "carry": ["Too bulky for my gym bag, takes half the space",
              "They don't fold flat so carrying them is annoying"],
    "noise_ok": ["Honestly no major complaints, ANC blocks the gym music and that's all I need",
                 "Not really, they do the job"],
    "social": ["Sometimes I worry I look unapproachable with big headphones on"],
}
ARCHETYPES = [
    # (name, weight) 达标: strong 25%, borderline 15%; 不达标: price 15%, freq 10%, nowear 20%, noown 15%
    ("qualified_strong", 0.25),
    ("qualified_borderline", 0.15),
    ("fail_price", 0.15),
    ("fail_freq", 0.10),
    ("fail_nowear", 0.20),
    ("fail_noown", 0.15),
]

def pick_archetype():
    r = random.random()
    acc = 0
    for name, w in ARCHETYPES:
        acc += w
        if r <= acc:
            return name
    return ARCHETYPES[-1][0]

def make_row(idx):
    arch = pick_archetype()
    first, last = random.choice(FIRST), random.choice(LAST)
    name = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}{random.randint(1,99)}@{random.choice(['gmail.com','outlook.com','icloud.com','yahoo.com'])}"
    age = random.choices(["18-24","25-34","35-44","45 or above"], weights=[35,40,18,7])[0]
    gender = random.choices(["Male","Female","Non-binary","Prefer not to say"], weights=[55,40,2,3])[0]
    loc = random.choice(CITIES)
    occ = random.choice(OCCUPATIONS)
    gym = random.choices(GYM_TYPES, weights=[30,15,40,10,5])[0]

    # 训练类型：达标类必含力量；fail_freq 可能不含力量
    trains = random.sample(TRAIN_POOL, k=random.randint(1, 3))
    if arch in ("qualified_strong", "qualified_borderline", "fail_price", "fail_nowear"):
        if not any(t in trains for t in ["strength training","powerlifting","bodybuilding"]):
            trains[0] = random.choice(["strength training","powerlifting","bodybuilding"])
    training_types = ", ".join(trains)

    if arch == "qualified_strong":
        freq = random.choice(["4-5 times","6+ times"])
        price = random.choice(["$200 - $299","$300 or above"])
        wear = random.choice(["Every session","Often (more than half)"])
        own = "Yes"
        score = random.randint(80, 96)
    elif arch == "qualified_borderline":
        freq = "2-3 times"
        price = "$200 - $299"
        wear = random.choice(["Sometimes","Often (more than half)"])
        own = "Yes"
        score = random.randint(60, 79)
    elif arch == "fail_price":
        freq = random.choice(["2-3 times","4-5 times"])
        price = random.choice(["Under $100","$100 - $199"])
        wear = random.choice(["Every session","Often (more than half)","Sometimes"])
        own = "Yes"
        score = random.randint(35, 55)
    elif arch == "fail_freq":
        freq = random.choice(["Less than once","1-2 times"])
        price = random.choice(["$200 - $299","$300 or above"])
        wear = random.choice(["Sometimes","Often (more than half)"])
        own = "Yes"
        score = random.randint(30, 50)
    elif arch == "fail_nowear":
        freq = random.choice(["2-3 times","4-5 times"])
        price = random.choice(["$200 - $299","$300 or above"])
        wear = random.choice(["Rarely","Never"])
        own = "Yes"
        score = random.randint(25, 45)
    else:  # fail_noown
        freq = random.choice(["2-3 times","4-5 times","6+ times"])
        price = random.choice(["Under $100","$100 - $199"])
        wear = random.choice(["Rarely","Never"])
        own = "No"
        score = random.randint(5, 25)

    qualified = arch.startswith("qualified")
    model = random.choice(MODELS_BY_PRICE[price]) if own == "Yes" else ""

    # 痛点自述
    if arch in ("qualified_strong", "qualified_borderline", "fail_nowear"):
        pains = random.sample(list(PAIN_POOL.keys()), k=random.randint(1, 2))
        pain_text = " ".join(random.choice(PAIN_POOL[p]) for p in pains)
    elif arch == "fail_price":
        pain_text = random.choice(PAIN_POOL["heat"] + PAIN_POOL["carry"])
    elif arch == "fail_noown":
        pain_text = ""
    else:
        pain_text = random.choice(random.choice([PAIN_POOL["noise_ok"], PAIN_POOL["social"]]))
        pain_text = random.choice(PAIN_POOL["noise_ok"]) if random.random() < 0.5 else pain_text

    # AI 字段
    tags = []
    if "University" in gym: tags.append("学校健身房")
    elif "Commercial" in gym: tags.append("商业健身房")
    elif "Corporate" in gym: tags.append("公司健身房")
    if any(t in training_types for t in ["powerlifting","bodybuilding","strength"]): tags.append("力量训练为主")
    if wear in ("Every session","Often (more than half)"): tags.append("高频佩戴")
    if pain_text and "hot" in pain_text or "sweat" in pain_text: tags.append("痛点明确")
    tags = tags[:4] if tags else ["信息有限"]

    if qualified:
        reason = f"每周训练{freq}，训练含力量项目，{price}价位耳机，健身房{wear}佩戴大耳罩，符合全部硬性筛选标准。"
        scene = "gym" if random.random() < 0.7 else "both"
    elif arch == "fail_price":
        reason = f"训练频率与佩戴习惯良好，但耳机价位为{price}，低于$200硬性门槛，不满足消费力筛选指标。"
        scene = "gym"
    elif arch == "fail_freq":
        reason = f"训练频率仅{freq}，低于每周2-3次的硬性标准，样本价值有限。"
        scene = "gym"
    elif arch == "fail_nowear":
        reason = f"训练习惯达标，但健身房佩戴频率为{wear}，不符合『确实在健身房佩戴大耳罩』的核心行为要求。"
        scene = "gym"
    else:
        reason = "未拥有大耳罩耳机，不属于目标人群。"
        scene = "gym"

    submit_time = (datetime.now() - timedelta(days=random.randint(0, 29), hours=random.randint(0,23), minutes=random.randint(0,59))).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "姓名": name, "邮箱": email, "年龄段": age, "性别": gender, "地区": loc, "职业": occ,
        "健身房类型": gym, "训练频率": freq, "训练类型": training_types, "是否有大耳罩": own,
        "耳机型号": model, "耳机价格段": price, "健身房佩戴频率": wear, "痛点自述": pain_text,
        "AI匹配分": score, "AI标签": "、".join(tags), "AI评估理由": reason, "AI关注场景": scene,
        "是否达标": "达标" if qualified else "不达标", "筛选状态": "待筛选", "邀请状态": "未邀请",
        "问卷提交时间": submit_time,
    }

FIELDS = ["姓名","邮箱","年龄段","性别","地区","职业","健身房类型","训练频率","训练类型","是否有大耳罩",
          "耳机型号","耳机价格段","健身房佩戴频率","痛点自述","AI匹配分","AI标签","AI评估理由",
          "AI关注场景","是否达标","筛选状态","邀请状态","问卷提交时间"]

def main(n=500):
    rows = [make_row(i) for i in range(n)]
    qualified = sum(1 for r in rows if r["是否达标"] == "达标")
    with open("synthetic_questionnaires_500.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    # 30 条快测版
    with open("synthetic_questionnaires_30.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows[:30])
    print(f"生成完成：500 份（达标 {qualified} 份，占 {qualified/5:.1f}%），另存 30 条快测版")

if __name__ == "__main__":
    main()
