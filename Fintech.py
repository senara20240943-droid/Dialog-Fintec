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
t0,t1,t2,t3,t4,t5 = st.tabs(["🏠 Overview","💰 Savings","🏦 Loans & Risk","📱 Digital","📊 KPIs","📋 Board Summary"])


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
# SAVINGS
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    st.header("Q1 — Savings & Customer Behaviour")

    sh("Average Savings Balance by Segment, Province & Location")
    c1, c2, c3 = st.columns(3)

    with c1:
        d = (dff[dff["Savings_Balance"] < 999_000_000]
             .groupby("Customer_Segment")["Savings_Balance"].median().reset_index()
             .sort_values("Savings_Balance", ascending=False))
        fig = px.bar(d, x="Customer_Segment", y="Savings_Balance",
                     color="Customer_Segment", color_discrete_map=SEG_CLR,
                     text=d["Savings_Balance"].apply(lambda v: f"{v/1e3:.0f}K"),
                     title="By Segment (median, outlier excluded)")
        fig.update_layout(showlegend=False, height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        d = (dff[dff["Savings_Balance"] < 999_000_000]
             .groupby("Province")["Savings_Balance"].median().reset_index()
             .sort_values("Savings_Balance"))
        fig = px.bar(d, x="Savings_Balance", y="Province", orientation="h",
                     color="Savings_Balance", color_continuous_scale="Blues",
                     text=d["Savings_Balance"].apply(lambda v: f"{v/1e3:.0f}K"),
                     title="By Province (median, outlier excluded)")
        fig.update_layout(height=300, margin=dict(t=40,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        d = (dff[dff["Savings_Balance"] < 999_000_000]
             .groupby("Urban_Rural")["Savings_Balance"].median().reset_index())
        fig = px.bar(d, x="Urban_Rural", y="Savings_Balance",
                     color="Urban_Rural", color_discrete_sequence=[NAVY, BLUE, AMBER],
                     text=d["Savings_Balance"].apply(lambda v: f"{v/1e3:.0f}K"),
                     title="By Urban/Rural (median, outlier excluded)")
        fig.update_layout(showlegend=False, height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    sh("Q1b — Total Savings by Age Band")
    age_sav = dff.groupby("Age_Band", observed=True)["Savings_Balance"].agg(Total="sum", Avg="mean", Count="count").reset_index()
    age_sav["Age_Band"] = age_sav["Age_Band"].astype(str)
    winner = age_sav.loc[age_sav["Total"].idxmax(), "Age_Band"]

    c1, c2 = st.columns([3, 1])
    with c1:
        fig = px.bar(age_sav, x="Age_Band", y="Total",
                     color=age_sav["Age_Band"].apply(lambda b: GREEN if b == winner else BLUE),
                     text=age_sav["Total"].apply(lambda v: f"{v/1e6:.1f}M"),
                     title="Total Savings by Age Band  (green = highest)")
        fig.update_layout(showlegend=False, height=320, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        top = age_sav.loc[age_sav["Total"].idxmax()]
        st.metric("🏆 Top Band",       str(top["Age_Band"]))
        st.metric("Total Savings",     f"LKR {top['Total']/1e6:.1f}M")
        st.metric("Avg Balance",       f"LKR {top['Avg']/1e3:.0f}K")
        st.metric("Customers in Band", f"{int(top['Count']):,}")

    st.divider()
    sh("Q1c — Savings Flow Health: Growing vs Draining")
    dff["Flow"] = np.where(dff["Net_Monthly_Flow"] > 0, "Growing", "Draining")
    growing_n = (dff["Flow"] == "Growing").sum()

    c1, c2 = st.columns([1, 3])
    with c1:
        st.metric("🟢 Growing",  f"{growing_n:,} ({pct(growing_n, len(dff))}%)")
        st.metric("🔴 Draining", f"{len(dff)-growing_n:,} ({pct(len(dff)-growing_n, len(dff))}%)")
        avg_grow  = dff.loc[dff["Net_Monthly_Flow"] > 0, "Net_Monthly_Flow"].mean()
        avg_drain = dff.loc[dff["Net_Monthly_Flow"] <= 0, "Net_Monthly_Flow"].mean()
        st.metric("Avg Gain (growers)",   f"LKR {avg_grow:,.0f}")
        st.metric("Avg Loss (drainers)",  f"LKR {avg_drain:,.0f}")
        st.info("Draining customers risk churn — target with financial wellness or retention products.")
    with c2:
        fig = px.bar(dff.groupby(["Customer_Segment","Flow"]).size().reset_index(name="Count"),
                     x="Customer_Segment", y="Count", color="Flow", barmode="group",
                     color_discrete_map={"Growing": GREEN, "Draining": RED},
                     text="Count", title="Growing vs Draining by Segment")
        fig.update_layout(height=320, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# LOANS & RISK
# ══════════════════════════════════════════════════════════════════════════════
with t2:
    st.header("Q2 — Loan Portfolio & Risk")

    c = st.columns(5)
    for col, label, val in zip(c, [
        "Borrowers", "Loan Penetration", "Avg Loan", "Total Exposure", "Default Rate"
    ], [
        f"{len(loan_df):,}",
        f"{pct(len(loan_df), len(dff))}%",
        f"LKR {loan_df['Loan_Amount'].mean():,.0f}",
        f"LKR {loan_df['Outstanding_Loan_Balance'].sum()/1e6:.1f}M",
        f"{pct((loan_valid['Loan_Repayment_Status']=='Defaulted').sum(), len(loan_valid))}%",
    ]):
        col.metric(label, val)

    st.divider()
    sh("Q2a — Loan Penetration by Segment & Channel")
    c1, c2 = st.columns(2)
    with c1:
        d = dff.groupby("Customer_Segment")["Has_Loan"].apply(lambda x: pct((x=="Yes").sum(), len(x))).reset_index(name="%")
        fig = px.bar(d.sort_values("%", ascending=False), x="Customer_Segment", y="%",
                     color="Customer_Segment", color_discrete_map=SEG_CLR,
                     text=d.sort_values("%", ascending=False)["%"].apply(lambda v: f"{v}%"),
                     title="By Segment (%)")
        fig.update_layout(showlegend=False, height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        d = dff.groupby("Acquisition_Channel")["Has_Loan"].apply(lambda x: pct((x=="Yes").sum(), len(x))).reset_index(name="%")
        fig = px.bar(d.sort_values("%", ascending=False), x="Acquisition_Channel", y="%",
                     color_discrete_sequence=[BLUE],
                     text=d.sort_values("%", ascending=False)["%"].apply(lambda v: f"{v}%"),
                     title="By Acquisition Channel (%)")
        fig.update_layout(height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    sh("Q2b — Debt-to-Savings Ratio (Outstanding Loan ÷ Savings Balance)")
    dts     = loan_df[loan_df["Debt_to_Savings"].notna()]
    exceed  = dts[dts["Debt_to_Savings"] > 1.0]
    c1, c2, c3 = st.columns(3)
    c1.metric("D:S > 1.0 (owe more than they save)", f"{len(exceed):,}")
    c2.metric("% of borrowers", f"{pct(len(exceed), len(dts))}%")
    c3.metric("Exposure (D:S > 1.0)", f"LKR {exceed['Outstanding_Loan_Balance'].sum()/1e6:.1f}M")

    c1, c2 = st.columns([2,1])
    with c1:
        fig = px.histogram(dts, x="Debt_to_Savings", nbins=40, color_discrete_sequence=[BLUE],
                           title="Distribution — values > 1.0 mean customer owes more than they save")
        fig.add_vline(x=1.0, line_dash="dash", line_color=RED, annotation_text="⚠️ Risk threshold = 1.0")
        fig.update_layout(height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        d = dts.groupby("Customer_Segment")["Debt_to_Savings"].mean().reset_index()
        fig = px.bar(d, x="Debt_to_Savings", y="Customer_Segment", orientation="h",
                     color="Debt_to_Savings", color_continuous_scale=["green","orange","red"],
                     text=d["Debt_to_Savings"].apply(lambda v: f"{v:.2f}"),
                     title="Avg D:S by Segment")
        fig.add_vline(x=1.0, line_dash="dash", line_color=RED)
        fig.update_layout(height=300, margin=dict(t=40,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    sh("Q2c — Default Rates by Segment & Loan Type")
    c1, c2 = st.columns(2)
    for col, grp in [(c1,"Customer_Segment"), (c2,"Loan_Type")]:
        with col:
            src = loan_valid if grp == "Customer_Segment" else loan_valid[loan_valid["Loan_Type"].notna()]
            d = src.groupby(grp)["Loan_Repayment_Status"].apply(
                lambda x: pct((x=="Defaulted").sum(), len(x))).reset_index(name="Default %")
            fig = px.bar(d.sort_values("Default %", ascending=False), x=grp, y="Default %",
                         color="Default %", color_continuous_scale=["green","orange","red"],
                         text=d.sort_values("Default %", ascending=False)["Default %"].apply(lambda v: f"{v}%"),
                         title=f"Default Rate by {grp.replace('_',' ')} (%)")
            fig.add_hline(y=5, line_dash="dash", line_color=GREEN, annotation_text="5% target")
            fig.update_layout(height=300, margin=dict(t=40,b=0), coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# DIGITAL
# ══════════════════════════════════════════════════════════════════════════════
with t3:
    st.header("Q3 — Digital Engagement & Products")

    sh("Q3a — Does mobile app use drive higher savings?")
    c1, c2 = st.columns([1, 2])
    with c1:
        app = dff.groupby("Mobile_App_User")["Savings_Balance"].agg(["mean","median","count"]).reset_index()
        yes = app[app["Mobile_App_User"]=="Yes"].iloc[0]
        no  = app[app["Mobile_App_User"]=="No"].iloc[0]
        st.metric("📱 App Users — Avg",    f"LKR {yes['mean']/1e3:.0f}K")
        st.metric("🚫 Non-App — Avg",      f"LKR {no['mean']/1e3:.0f}K")
        st.metric("App-User Premium",      f"+{pct(yes['mean']-no['mean'], no['mean'])}%")
        st.warning("⚠️ Means diverge but medians are similar — likely **selection bias** not causation. Wealthier customers both save more AND adopt apps.")
    with c2:
        fig = px.box(dff, x="Mobile_App_User", y="Savings_Balance",
                     color="Mobile_App_User",
                     color_discrete_map={"Yes": GREEN, "No": RED},
                     title="Savings Distribution: App vs Non-App Users")
        fig.update_layout(height=340, margin=dict(t=40,b=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    sh("Q3b — Cross-Sell Opportunity (savings only, no FD, no Insurance)")
    xsell = dff[dff["CrossSell_Opportunity"]]
    c1, c2, c3 = st.columns(3)
    c1.metric("Candidates",          f"{len(xsell):,}")
    c2.metric("% of customer base",  f"{pct(len(xsell), len(dff))}%")
    c3.metric("Savings held",        f"LKR {xsell['Savings_Balance'].sum()/1e6:.1f}M")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(xsell.groupby("Customer_Segment").size().reset_index(name="Count"),
                     x="Customer_Segment", y="Count", color="Customer_Segment",
                     color_discrete_map=SEG_CLR, text="Count",
                     title="Cross-Sell Candidates by Segment")
        fig.update_layout(showlegend=False, height=280, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(xsell.groupby("Province").size().reset_index(name="Count").sort_values("Count"),
                     x="Count", y="Province", orientation="h",
                     color="Count", color_continuous_scale="Blues", text="Count",
                     title="Cross-Sell Candidates by Province")
        fig.update_layout(height=280, margin=dict(t=40,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    sh("Q3c — Channel Quality: Which channel brings the best customers?")
    ch = dff.groupby("Acquisition_Channel")["Savings_Balance"].agg(Avg="mean", Count="count").reset_index()
    ch_def = loan_valid.groupby("Acquisition_Channel")["Loan_Repayment_Status"].apply(
        lambda x: pct((x=="Defaulted").sum(), len(x))).reset_index(name="Default %")
    ch = ch.merge(ch_def, on="Acquisition_Channel").sort_values("Avg", ascending=False)

    fig = px.scatter(ch, x="Default %", y="Avg", size="Count",
                     color="Acquisition_Channel", text="Acquisition_Channel",
                     color_discrete_sequence=px.colors.qualitative.Safe,
                     title="Top-left = BEST: high avg savings + low default rate")
    fig.add_vline(x=ch["Default %"].mean(), line_dash="dot", line_color="grey", annotation_text="Avg default")
    fig.add_hline(y=ch["Avg"].mean(),       line_dash="dot", line_color="grey", annotation_text="Avg savings")
    fig.update_traces(textposition="top center")
    fig.update_layout(height=380, margin=dict(t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

    best = ch.loc[ch["Default %"].idxmin(), "Acquisition_Channel"]
    st.success(f"✅ Best risk-adjusted channel: **{best}** (lowest default rate)")
    st.dataframe(ch.style.format({"Avg":"LKR {:,.0f}","Default %":"{:.1f}%","Count":"{:,}"}), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════════════════════
with t4:
    st.header("Q4 — KPI Dashboard")
    st.caption("5 KPIs spanning Risk · Growth · Engagement · Compliance · Retention")
    st.divider()

    kpis = [
        ("KPI 1 · Risk",        "Loan Default Rate",
         pct((loan_valid["Loan_Repayment_Status"]=="Defaulted").sum(), len(loan_valid)),
         5, "lower",
         "% of loan customers who have defaulted. Target < 5% industry benchmark.",
         "Drives provisioning and regulatory capital requirements."),
        ("KPI 2 · Growth",      "Cross-Sell Gap",
         pct(dff["CrossSell_Opportunity"].sum(), len(dff)),
         40, "lower",
         "% of customers with savings but no FD and no Insurance. Target < 40%.",
         "Quantifies untapped fee income. Each converted customer adds revenue and stickiness."),
        ("KPI 3 · Engagement",  "Mobile App Adoption",
         pct((dff["Mobile_App_User"]=="Yes").sum(), len(dff)),
         65, "higher",
         "% of customers using the mobile app. Target > 65%.",
         "Digital adoption reduces service cost and enables real-time push campaigns."),
        ("KPI 4 · Compliance",  "KYC Verification Rate",
         pct((dff["KYC_Status"]=="Verified").sum(), len(dff)),
         95, "higher",
         "% of customers with verified KYC. Target > 95% (regulatory minimum).",
         "Unverified accounts cannot access high-value products and create audit risk."),
        ("KPI 5 · Retention",   "Savings Growing",
         pct((dff["Net_Monthly_Flow"]>0).sum(), len(dff)),
         70, "higher",
         "% of customers with deposits > withdrawals. Target > 70%.",
         "A declining share of growing savers is an early warning of attrition."),
    ]

    for area, name, val, target, direction, defn, why in kpis:
        met   = val <= target if direction == "lower" else val >= target
        color = GREEN if met else (AMBER if abs(val - target) < 10 else RED)
        status= "✅ On track" if met else "❌ Off target"
        with st.container():
            st.markdown(f"""
            <div style="background:#1A1A1A;border-left:5px solid {color};border-radius:8px;
                        padding:14px 20px;margin-bottom:10px;box-shadow:0 2px 6px rgba(0,0,0,.07)">
              <small style="color:#7F8C8D">{area}</small><br>
              <strong style="color:#90CAF9;font-size:1.05rem">{name}</strong>
              &nbsp;&nbsp;
              <span style="font-size:1.7rem;font-weight:800;color:{color}">{val}%</span>
              <span style="float:right;background:{color};color:white;padding:3px 12px;
                           border-radius:12px;font-size:.8rem">{status} | target {'<' if direction=='lower' else '>'}{target}%</span>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("Definition & Why it matters"):
                st.markdown(f"**Definition:** {defn}")
                st.markdown(f"**Why it matters:** {why}")

    st.divider()
    fig = go.Figure()
    colors  = [GREEN if (v<=t if d=="lower" else v>=t) else RED for _,_,v,t,d,_,_ in kpis]
    fig.add_trace(go.Bar(x=[k[1] for k in kpis], y=[k[2] for k in kpis],
                         marker_color=colors, text=[f"{k[2]}%" for k in kpis],
                         textposition="outside", name="Current"))
    fig.add_trace(go.Scatter(x=[k[1] for k in kpis], y=[k[3] for k in kpis],
                             mode="markers", name="Target",
                             marker=dict(symbol="line-ew", size=22, color=AMBER,
                                         line=dict(width=3, color=AMBER))))
    fig.update_layout(height=380, margin=dict(t=20,b=80), plot_bgcolor="white",
                      legend=dict(orientation="h", y=1.1), xaxis_tickangle=-10, yaxis_title="%")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🟠 Line = target  |  🟢 Green = on track  |  🔴 Red = off target")


# ══════════════════════════════════════════════════════════════════════════════
# BOARD SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
with t5:
    st.header("Q5 — Board Summary & Recommendations")

    sh("Key Findings")
    for icon, title, body in [
        ("📈", "Savings base is healthy but concentrated",
         f"The 35–44 age band holds the largest share of total savings. Premium segment holds disproportionately high balances despite being a small minority. Western Province dominates in volume. Concentration means the portfolio is exposed to shocks affecting one demographic or geography."),
        ("⚠️", "Loan risk is uneven across segments and loan types",
         f"Loan penetration is ~{pct((dff['Has_Loan']=='Yes').sum(), len(dff))}%. A meaningful share of borrowers carry debt exceeding their savings (D:S > 1.0), representing significant LKR exposure. Default rates are not uniform — certain segment/loan-type combinations drive the bulk of defaults."),
        ("📱", "Large cross-sell revenue gap",
         f"~{pct(dff['CrossSell_Opportunity'].sum(), len(dff))}% of customers hold savings only — no FD, no Insurance. These customers collectively hold substantial savings and represent a major untapped fee income opportunity."),
        ("⚖️", "KYC compliance is a regulatory risk",
         f"Only {pct((dff['KYC_Status']=='Verified').sum(), len(dff))}% of customers are KYC-verified vs the 95% regulatory minimum. Unverified accounts restrict high-value product eligibility and expose the business to audit risk."),
    ]:
        st.markdown(f"""
        <div style="background:#1A1A1A;border-radius:8px;padding:14px 18px;
                    margin-bottom:8px;box-shadow:0 2px 6px rgba(0,0,0,.07)">
          <span style="font-size:1.2rem">{icon}</span>
          <strong style="color:#90CAF9"> {title}</strong><br>
          <span style="color:#CCCCCC;font-size:.9rem">{body}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    sh("Strategic Recommendations")
    c1, c2 = st.columns(2)

    with c1:
        with st.expander("1. Launch FD & Insurance cross-sell campaign", expanded=True):
            st.markdown("**📊 Evidence:** Large pool of savings-only customers with no FD or insurance.")
            st.markdown("**🎯 Action:** Segment by savings tier and age band. Route via app for digital users, agents for others. Target the 35–54 cohort — highest balances, most to gain.")
            st.markdown("**✅ Outcome:** More revenue per customer, deeper product stickiness, lower churn.")

    with c2:
        with st.expander("2. Risk-tiered loan underwriting", expanded=True):
            st.markdown("**📊 Evidence:** Default rates differ significantly by segment and loan type. D:S > 1.0 clusters in predictable groups.")
            st.markdown("**🎯 Action:** Introduce segment-aware loan limits. Flag any application where D:S would exceed 1.0 post-disbursement. Require minimum savings buffer for Starter customers.")
            st.markdown("**✅ Outcome:** Default rate below 5% target within 12 months.")

    st.divider()
    sh("Additional Data Sources We Would Want")
    for source, why in [
        ("CRIB (Credit Information Bureau) credit scores",
         "No external credit history in current data. CRIB scores would benchmark FinSight's internal D:S signals against a customer's full credit picture across all institutions — materially improving underwriting accuracy."),
        ("Transaction-level ledger data (monthly or daily)",
         "Current data only has monthly averages. Granular transactions would reveal salary credit dates, spending patterns, and early distress signals (declining credits before a default) — enabling behavioural scoring and churn prediction."),
    ]:
        st.markdown(f"""
        <div style="background:#111D2B;border-left:4px solid {BLUE};border-radius:6px;
                    padding:12px 16px;margin-bottom:8px">
          <strong style="color:#1B4F72">{source}</strong><br>
          <span style="color:#CCCCCC;font-size:.9rem">{why}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.header("Q6 — Analytical Limitations")

    for sev, color, title, limitation, impact, fix in [
        ("🔴 High", RED,
         "Savings imputation with segment median may mask true risk",
         "Negative and extreme savings values were replaced with segment medians. If a whole segment is stressed, the median itself is biased — imputations could understate risk.",
         "Average savings metrics per segment could be systematically wrong, making cross-sell opportunity look larger or smaller than reality.",
         "Obtain corrected values from source systems. Where impossible, exclude rather than impute for risk KPIs and report exclusion count explicitly."),
        ("🔴 High", RED,
         "App–savings link is correlation, not causation",
         "App users show higher savings, but higher-income customers may simply be more likely to both save more AND use apps.",
         "Investing in app campaigns to increase savings could produce no effect if the true driver is income or financial literacy.",
         "Run a difference-in-differences study: compare savings growth before vs after app adoption against a matched control group that did not adopt."),
        ("🟡 Medium", AMBER,
         "Age band boundaries are arbitrary",
         "The 35–44 band 'winning' is partly an artifact of the band width chosen. A 30–45 band would produce different results. No statistical test was applied.",
         "Product targeting decisions may be misdirected if the true inflection is at age 38 or 42.",
         "Apply Jenks natural breaks banding. Run a Kruskal-Wallis test to confirm band differences are statistically significant."),
        ("🟡 Medium", AMBER,
         "District default analysis is underpowered",
         "Some districts have fewer than 15 loan holders. A single default in a small district produces an inflated, statistically unreliable default rate.",
         "Flagging a district as 'high risk' based on 1–2 defaults could lead to unjustified credit restrictions.",
         "Apply a minimum threshold (≥ 30 loan holders) before reporting district rates. Use credible intervals rather than point estimates for small samples."),
        ("🟢 Low", GREEN,
         "Net Monthly Flow uses averages — not current-month actuals",
         "Monthly averages smooth volatility. A customer who recently lost income would still appear 'growing' if their historical average is positive.",
         "The '% growing' KPI may overstate current savings health in a volatile macroeconomic environment.",
         "Use the most recent 2–3 months of actual transaction data to compute a rolling flow metric with trend direction as a secondary flag."),
    ]:
        with st.expander(f"{sev} — {title}"):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**⚠️ Limitation**\n\n{limitation}")
            c2.markdown(f"**📉 Impact on Findings**\n\n{impact}")
            c3.markdown(f"**🔧 How to Fix**\n\n{fix}")