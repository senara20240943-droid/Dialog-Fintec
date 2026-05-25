"""FinSight Lanka — Analytics Dashboard | Dialog Finance PLC"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
            "area":    "🔴 Risk",
            "name":    "Loan Default Rate",
            "defn":    "% of active loan customers whose repayment status is Defaulted",
            "formula": "Count(Loan_Repayment_Status = 'Defaulted') ÷ Count(Has_Loan = 'Yes') × 100",
            "val":     pct((loan_valid["Loan_Repayment_Status"]=="Defaulted").sum(), len(loan_valid)),
            "target":  5,
            "dir":     "lower",
            "why":     "Directly drives provisioning costs and regulatory capital requirements. An elevated rate signals underwriting failure or economic stress — informs credit policy decisions.",
            "bench":   "< 5% — industry benchmark for micro-finance institutions in emerging markets.",
        },
        {
            "area":    "🟡 Growth",
            "name":    "Cross-Sell Penetration Gap",
            "defn":    "% of customers who hold savings but have NO Fixed Deposit and NO Insurance",
            "formula": "Count(Savings_Balance > 0 & Has_Fixed_Deposit='No' & Has_Insurance='No') ÷ Total × 100",
            "val":     pct(dff["CrossSell_Opportunity"].sum(), len(dff)),
            "target":  40,
            "dir":     "lower",
            "why":     "Quantifies untapped fee income. Each converted customer adds recurring FD interest and insurance premium revenue while deepening product stickiness and reducing churn.",
            "bench":   "< 40% — reduce gap through targeted campaigns to the 35–54 age cohort.",
        },
        {
            "area":    "📱 Engagement",
            "name":    "Mobile App Adoption Rate",
            "defn":    "% of customers actively using the mobile app (Mobile_App_User = 'Yes')",
            "formula": "Count(Mobile_App_User = 'Yes') ÷ Total Customers × 100",
            "val":     pct((dff["Mobile_App_User"]=="Yes").sum(), len(dff)),
            "target":  65,
            "dir":     "higher",
            "why":     "App users are cheaper to service digitally and reachable via push notifications. Low adoption limits digital channel ROI and increases branch/agent servicing costs.",
            "bench":   "> 65% — digital-first strategy target aligned with regional fintech benchmarks.",
        },
        {
            "area":    "⚖️ Compliance",
            "name":    "KYC Verification Rate",
            "defn":    "% of customers with KYC_Status = 'Verified' per CBRSL regulatory requirements",
            "formula": "Count(KYC_Status = 'Verified') ÷ Total Customers × 100",
            "val":     pct((dff["KYC_Status"]=="Verified").sum(), len(dff)),
            "target":  95,
            "dir":     "higher",
            "why":     "Regulatory minimum. Unverified customers cannot access high-value products. Informs urgency of KYC refresh campaigns and risk of regulatory audit findings.",
            "bench":   "> 95% — CBRSL regulatory minimum; non-compliance risks fines and product restrictions.",
        },
        {
            "area":    "🟢 Retention",
            "name":    "Customer Savings Growth Rate",
            "defn":    "% of customers whose monthly deposits exceed withdrawals (Net_Monthly_Flow > 0)",
            "formula": "Count(Net_Monthly_Flow > 0) ÷ Total Customers × 100",
            "val":     pct((dff["Net_Monthly_Flow"]>0).sum(), len(dff)),
            "target":  70,
            "dir":     "higher",
            "why":     "A declining share of growing savers is an early churn warning — visible before account closures appear. Informs retention campaign triggers and financial wellness product targeting.",
            "bench":   "> 70% — healthy savings-led customer base; below 70% warrants proactive retention action.",
        },
    ]

    # ── Summary bar chart ──────────────────────────────────────────────────────
    colors_bar = [GREEN if (k["val"]<=k["target"] if k["dir"]=="lower" else k["val"]>=k["target"]) else RED for k in kpis]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[k["name"] for k in kpis], y=[k["val"] for k in kpis],
        marker_color=colors_bar, text=[f"{k['val']}%" for k in kpis],
        textposition="outside", name="Current Value",
    ))
    fig.add_trace(go.Scatter(
        x=[k["name"] for k in kpis], y=[k["target"] for k in kpis],
        mode="markers", name="Target",
        marker=dict(symbol="line-ew", size=24, color=AMBER, line=dict(width=3, color=AMBER)),
    ))
    fig.update_layout(
        height=400, margin=dict(t=30,b=80),
        plot_bgcolor="#111111", paper_bgcolor="#0A0A0A",
        font=dict(color="#DDDDDD"),
        legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(tickangle=-10, gridcolor="#222"),
        yaxis=dict(title="%", gridcolor="#222"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🟠 Line = target  |  🟢 Green bar = on track  |  🔴 Red bar = off target")

    st.divider()

    # ── Individual KPI cards ───────────────────────────────────────────────────
    for k in kpis:
        met    = k["val"] <= k["target"] if k["dir"] == "lower" else k["val"] >= k["target"]
        color  = GREEN if met else (AMBER if abs(k["val"] - k["target"]) < 15 else RED)
        status = "✅ On track" if met else "❌ Off target"
        gap    = k["target"] - k["val"] if k["dir"] == "higher" else k["val"] - k["target"]
        gap_txt= f"Gap: {abs(gap):.1f}pp to target" if not met else "Target met"

        st.markdown(f"""
        <div style="background:#1A1A1A;border-left:6px solid {color};border-radius:10px;
                    padding:16px 22px;margin-bottom:12px;box-shadow:0 3px 10px rgba(0,0,0,0.3)">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <span style="color:#7F8C8D;font-size:.8rem">{k["area"]}</span><br>
              <span style="color:#E0E0E0;font-size:1.1rem;font-weight:700">{k["name"]}</span>
            </div>
            <div style="text-align:right">
              <span style="font-size:2rem;font-weight:900;color:{color}">{k["val"]}%</span><br>
              <span style="background:{color};color:white;padding:2px 10px;border-radius:10px;font-size:.75rem">{status}</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Full definition — " + k['name']):
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown("**Definition**\n\n" + k['defn'])
            c2.markdown("**Formula**\n\n`" + k['formula'] + "`")
            c3.markdown("**Why it matters**\n\n" + k['why'])
            c4.markdown("**Target & Benchmark**\n\n" + k['bench'] + "\n\n*Current: " + str(k['val']) + "% | Gap: " + gap_txt + "*")