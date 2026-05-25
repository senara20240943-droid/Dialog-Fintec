"""FinSight Lanka — Analytics Dashboard | Dialog Finance PLC"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="FinSight Lanka", page_icon="💰", layout="wide")

# ── Theme ─────────────────────────────────────────────────────────────────────
NAVY, BLUE, GREEN, AMBER, RED = "#1B4F72", "#2E86C1", "#27AE60", "#E67E22", "#C0392B"
SEG_CLR = {"Premium": NAVY, "Regular": BLUE, "Starter": AMBER, "Unknown": "#95A5A6"}

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0A0A0A; }
[data-testid="stMain"]             { background: #0A0A0A; }
[data-testid="stSidebar"]          { background: #111111; border-right: 1px solid #222; }
[data-testid="stSidebar"] *        { color: #E0E0E0 !important; }
[data-testid="metric-container"] {
    background: #1A1A1A; border-radius: 10px;
    padding: 14px 18px; border-left: 4px solid #2E86C1;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.5rem; font-weight: 700; color: #2E86C1;
}
[data-testid="metric-container"] label { color: #AAAAAA !important; }
p, li, span, div { color: #DDDDDD; }
h1, h2, h3       { color: #FFFFFF !important; }
.sh {
    background: linear-gradient(90deg,#1B4F72,#2980B9);
    color: white; border-radius: 8px;
    padding: 8px 16px; margin: 12px 0;
    font-size: 1rem; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

def sh(t): st.markdown(f'<div class="sh">{t}</div>', unsafe_allow_html=True)
def pct(n, d): return 0 if d == 0 else round(100 * n / d, 1)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    df = pd.read_csv("finsight_clean.csv", parse_dates=["Date_of_Birth","Account_Open_Date",
                                                          "Loan_Start_Date","Last_Login_Date","KYC_Last_Updated"])
    df["Age_Band"] = pd.Categorical(df["Age_Band"],
        categories=["18-24","25-34","35-44","45-54","55-64","65+"], ordered=True)
    return df

df = get_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 FinSight Lanka")
    st.markdown("*Dialog Finance PLC*")
    st.markdown("---")
    seg  = st.multiselect("Segment",      sorted(df["Customer_Segment"].dropna().unique()), default=sorted(df["Customer_Segment"].dropna().unique()))
    prov = st.multiselect("Province",     sorted(df["Province"].dropna().unique()),         default=sorted(df["Province"].dropna().unique()))
    ur   = st.multiselect("Urban / Rural",sorted(df["Urban_Rural"].dropna().unique()),      default=sorted(df["Urban_Rural"].dropna().unique()))
    st.markdown("---")
    st.caption(f"📊 **{len(df):,}** clean records")

dff        = df[df["Customer_Segment"].isin(seg) & df["Province"].isin(prov) & df["Urban_Rural"].isin(ur)].copy()
loan_df    = dff[dff["Has_Loan"] == "Yes"].copy()
loan_valid = loan_df[loan_df["Loan_Repayment_Status"].notna()]

# ── Tabs ──────────────────────────────────────────────────────────────────────
t0, t1 = st.tabs(["🏠 Overview", "📊 KPIs"])


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with t0:
    st.title("FinSight Lanka — Customer Analytics")
    st.caption("Analytics Trainee Assessment | Dialog Finance PLC")
    st.divider()

    c1, c2, c3 = st.columns(3)
    c1.metric("👥 Customers",        f"{len(dff):,}")
    c2.metric("💰 Total Savings",    f"LKR {dff['Savings_Balance'].sum():,.0f}")
    c3.metric("🏦 Loan Penetration", f"{pct((dff['Has_Loan']=='Yes').sum(), len(dff))}%")
    c4, c5, c6 = st.columns(3)
    c4.metric("📱 App Adoption",     f"{pct((dff['Mobile_App_User']=='Yes').sum(), len(dff))}%")
    c5.metric("📈 Savings Growing",  f"{pct((dff['Net_Monthly_Flow']>0).sum(), len(dff))}%")
    c6.metric("⚠️ Default Rate",     f"{pct((loan_valid['Loan_Repayment_Status']=='Defaulted').sum(), len(loan_valid))}%")

    st.divider()

    fig = px.pie(dff["Customer_Segment"].value_counts().reset_index(),
                 names="Customer_Segment", values="count",
                 color="Customer_Segment", color_discrete_map=SEG_CLR,
                 hole=0.5, title="Segment Mix")
    fig.update_layout(height=320, margin=dict(t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

    d = dff["Province"].value_counts().reset_index().sort_values("count")
    fig = px.bar(d, x="count", y="Province", orientation="h",
                 color="count", color_continuous_scale="Blues",
                 text="count", title="Customers by Province")
    fig.update_layout(height=350, margin=dict(t=40,b=0), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(dff["Acquisition_Channel"].value_counts().reset_index(),
                 x="Acquisition_Channel", y="count", text="count",
                 color_discrete_sequence=[BLUE], title="Acquisition Channel")
    fig.update_layout(height=300, margin=dict(t=40,b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.pie(dff["KYC_Status"].value_counts().reset_index(),
                 names="KYC_Status", values="count", hole=0.5,
                 color="KYC_Status",
                 color_discrete_map={"Verified":GREEN,"Expired":AMBER,"Pending":BLUE,"Unknown":"#95A5A6"},
                 title="KYC Status")
    fig.update_layout(height=320, margin=dict(t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    st.header("Q4 — KPI Dashboard")
    st.caption("5 KPIs spanning Risk · Growth · Engagement · Compliance · Retention")
    st.divider()

    kpis = [
        {
            "area":    "RISK",
            "name":    "Loan Default Rate",
            "defn":    "This measures the percentage of loan customers who failed to repay their loans on time and are now marked as defaulted.",
            "formula": "Count(Loan_Repayment_Status = 'Defaulted') ÷ Count(Has_Loan = 'Yes') × 100",
            "val":     pct((loan_valid["Loan_Repayment_Status"]=="Defaulted").sum(), len(loan_valid)),
            "target":  5,
            "dir":     "lower",
            "why":     "A high default rate means the bank is at greater financial risk and may be giving loans to customers who struggle to repay. It also increases losses and affects the bank’s overall financial health.",
            "bench":   "The industry target is to keep the default rate below 5%, but the current rate is 10.1%. This means the bank is 5.1 percentage points above the ideal level and may need stricter credit checks or better risk monitoring.",
        },
        {
            "area":    "GROWTH",
            "name":    "Cross-Sell Gap",
            "defn":    "% of customers who hold savings but have NO Fixed Deposit and NO Insurance",
            "formula": "Count(Savings_Balance > 0 & Has_Fixed_Deposit='No' & Has_Insurance='No') ÷ Total × 100",
            "val":     pct(dff["CrossSell_Opportunity"].sum(), len(dff)),
            "target":  40,
            "dir":     "lower",
            "why":     "These customers are missed business opportunities for the bank. Selling them more products can increase revenue and customer loyalty.",
            "bench":   "The target is below 40%, but the current rate is 50.2%, meaning many customers still use only basic banking products.",
        },
        {
            "area":    "ENGAGEMENT",
            "name":    "App Adoption",
            "defn":    "% of customers actively using the mobile app (Mobile_App_User = 'Yes')",
            "formula": "Count(Mobile_App_User = 'Yes') ÷ Total Customers × 100",
            "val":     pct((dff["Mobile_App_User"]=="Yes").sum(), len(dff)),
            "target":  65,
            "dir":     "higher",
            "why":     "More app users mean lower servicing costs and better digital communication with customers. It also reduces pressure on branches and agents.",
            "bench":   "The target was 65%, and the current rate is 66.7%, meaning the bank has successfully achieved its digital adoption goal.",
        },
        {
            "area":    "COMPLIANCE",
            "name":    "KYC Verified",
            "defn":    "This shows the percentage of customers whose identity details have been fully verified according to banking regulations.",
            "formula": "Count(KYC_Status = 'Verified') ÷ Total Customers × 100",
            "val":     pct((dff["KYC_Status"]=="Verified").sum(), len(dff)),
            "target":  95,
            "dir":     "higher",
            "why":     "Customers without KYC verification create compliance and security risks for the bank. They may also be restricted from using certain financial products.",
            "bench":   "The target is 95%, but the current rate is only 70.5%, showing a large gap that needs urgent attention.",
        },
        {
            "area":    "RETENTION",
            "name":    "Savings Growing",
            "defn":    "% of customers whose monthly deposits exceed withdrawals (Net_Monthly_Flow > 0)",
            "formula": "Count(Net_Monthly_Flow > 0) ÷ Total Customers × 100",
            "val":     pct((dff["Net_Monthly_Flow"]>0).sum(), len(dff)),
            "target":  70,
            "dir":     "higher",
            "why":     "Customers with positive savings flow are more financially stable and less likely to leave the bank. A lower percentage could be an early warning sign of customer stress or future churn.",
            "bench":   "The target was 70%, and the current rate is 99%, showing a very strong and healthy savings customer base.",
        },
    ]

    def make_gauge_card(k):
        import math
        val    = k["val"]
        target = k["target"]
        area   = k["area"]
        name   = k["name"]
        dir_   = k["dir"]
        met    = val <= target if dir_ == "lower" else val >= target

        on_color  = "#22c55e"
        off_color = "#ef4444"
        arc_color = on_color if met else off_color
        status_label = "On Track" if met else "Needs Action"
        pill_bg   = "rgba(34,197,94,0.15)"  if met else "rgba(239,68,68,0.15)"

        tgt_sign = "<" if dir_ == "lower" else ">"
        tgt_text = f"Target:  {tgt_sign} {target}%"

        # Arc from top (270°), clockwise, sweep = val% of full circle
        # SVG: rotate(-90) so 0° is at top; stroke-dasharray on r=54 circle
        # circumference = 2 * pi * 54 = 339.29
        R    = 54
        CX, CY = 70, 70
        CIRC = round(2 * math.pi * R, 2)   # 339.29
        fill_frac = min(val / 100.0, 1.0)
        arc_len   = round(fill_frac * CIRC, 2)
        gap_len   = round(CIRC - arc_len, 2)
        # offset = CIRC * 0.25 so arc starts at top (12 o'clock)
        offset = round(CIRC * 0.25, 2)

        card_html = f"""
<div style="background:#1c1c1c;border-radius:14px;padding:24px 16px 22px;
            display:flex;flex-direction:column;align-items:center;">
  <span style="font-size:.65rem;font-weight:700;letter-spacing:.14em;
               color:{arc_color};margin-bottom:16px;text-transform:uppercase;">{area}</span>
  <svg width="140" height="140" viewBox="0 0 140 140">
    <circle cx="{CX}" cy="{CY}" r="{R}"
            fill="none" stroke="#2e2e2e" stroke-width="14"/>
    <circle cx="{CX}" cy="{CY}" r="{R}"
            fill="none" stroke="{arc_color}" stroke-width="14"
            stroke-linecap="round"
            stroke-dasharray="{arc_len} {gap_len}"
            stroke-dashoffset="{offset}"
            transform="rotate(-90 {CX} {CY})"/>
    <text x="{CX}" y="{CY - 6}" text-anchor="middle"
          font-size="26" font-weight="700" fill="{arc_color}"
          font-family="Arial,sans-serif">{val}%</text>
    <text x="{CX}" y="{CY + 14}" text-anchor="middle"
          font-size="11" fill="#666"
          font-family="Arial,sans-serif">current</text>
  </svg>
  <p style="margin:14px 0 2px;font-size:1rem;font-weight:700;
            color:#ffffff;text-align:center;line-height:1.3;">{name}</p>
  <p style="margin:0 0 14px;font-size:.78rem;color:#555;text-align:center;">
    {tgt_text}</p>
  <span style="display:inline-block;padding:6px 22px;border-radius:999px;
               background:{pill_bg};border:1.5px solid {arc_color};
               color:{arc_color};font-size:.75rem;font-weight:700;
               letter-spacing:.05em;">
    {status_label}
  </span>
</div>
"""
        return card_html

    # ── Row 1: 3 cards ─────────────────────────────────────────────────────────
    row1 = st.columns(3)
    for col, k in zip(row1, kpis[:3]):
        with col:
            st.markdown(make_gauge_card(k), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Row 2: 2 cards (centred) ───────────────────────────────────────────────
    _, c1, c2, _ = st.columns([0.5, 1, 1, 0.5])
    for col, k in zip([c1, c2], kpis[3:]):
        with col:
            st.markdown(make_gauge_card(k), unsafe_allow_html=True)

    st.divider()

    # ── Expandable detail cards ────────────────────────────────────────────────
    for k in kpis:
        met     = k["val"] <= k["target"] if k["dir"] == "lower" else k["val"] >= k["target"]
        gap     = k["target"] - k["val"] if k["dir"] == "higher" else k["val"] - k["target"]
        gap_txt = f"Gap: {abs(gap):.1f}pp to target" if not met else "Target met"
        with st.expander(f"{k['area']} — {k['name']} — Full definition"):
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown("**Definition**\n\n" + k['defn'])
            c2.markdown("**Formula**\n\n`" + k['formula'] + "`")
            c3.markdown("**Why it matters**\n\n" + k['why'])
            c4.markdown("**Target & Benchmark**\n\n" + k['bench'] + "\n\n*Current: " + str(k['val']) + "% | Gap: " + gap_txt + "*")