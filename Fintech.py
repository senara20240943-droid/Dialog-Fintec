"""
FinSight Lanka — Analytics Dashboard
Dialog Finance PLC
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="FinSight Lanka", page_icon="💰", layout="wide")

# ── Colours ───────────────────────────────────────────────────────────────────
NAVY  = "#1B4F72"
BLUE  = "#2E86C1"
GREEN = "#27AE60"
AMBER = "#E67E22"
RED   = "#C0392B"
SEG_CLR = {"Premium": NAVY, "Regular": BLUE, "Starter": AMBER, "Unknown": "#7F8C8D"}

# ── Helpers ───────────────────────────────────────────────────────────────────
def pct(n, d): return 0 if d == 0 else round(100 * n / d, 1)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data…")
def get_data():
    df = pd.read_csv("finsight_clean.csv", parse_dates=["Date_of_Birth", "Account_Open_Date",
                                                          "Loan_Start_Date", "Last_Login_Date",
                                                          "KYC_Last_Updated"])
    df["Age_Band"] = pd.Categorical(df["Age_Band"],
        categories=["18-24","25-34","35-44","45-54","55-64","65+"], ordered=True)
    return df

df = get_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💰 FinSight Lanka")
    st.markdown("---")
    seg  = st.multiselect("Segment",  sorted(df["Customer_Segment"].dropna().unique()), default=sorted(df["Customer_Segment"].dropna().unique()))
    prov = st.multiselect("Province", sorted(df["Province"].dropna().unique()),         default=sorted(df["Province"].dropna().unique()))
    st.markdown("---")
    st.caption(f"{len(df):,} clean records")

dff = df[df["Customer_Segment"].isin(seg) & df["Province"].isin(prov)].copy()
loan_df = dff[dff["Has_Loan"] == "Yes"].copy()
loan_valid = loan_df[loan_df["Loan_Repayment_Status"].notna()]

# ── Tabs ──────────────────────────────────────────────────────────────────────
t0, t1, t2, t3, t4, t5 = st.tabs([
    "🏠 Overview", "💰 Savings", "🏦 Loans & Risk",
    "📱 Digital", "📊 KPIs", "📋 Board Summary"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with t0:
    st.header("Customer Base Overview")

    c = st.columns(6)
    c[0].metric("Customers",       f"{len(dff):,}")
    c[1].metric("Total Savings",   f"LKR {dff['Savings_Balance'].sum()/1e6:.1f}M")
    c[2].metric("Loan Penetration",f"{pct((dff['Has_Loan']=='Yes').sum(), len(dff))}%")
    c[3].metric("App Adoption",    f"{pct((dff['Mobile_App_User']=='Yes').sum(), len(dff))}%")
    c[4].metric("Savings Growing", f"{pct((dff['Net_Monthly_Flow']>0).sum(), len(dff))}%")
    c[5].metric("Default Rate",    f"{pct((loan_valid['Loan_Repayment_Status']=='Defaulted').sum(), len(loan_valid))}%")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        fig = px.pie(dff["Customer_Segment"].value_counts().reset_index(),
                     names="Customer_Segment", values="count",
                     color="Customer_Segment", color_discrete_map=SEG_CLR,
                     hole=0.45, title="Customer Segment")
        fig.update_layout(height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        prov_cnt = dff["Province"].value_counts().reset_index()
        fig = px.bar(prov_cnt.sort_values("count"), x="count", y="Province",
                     orientation="h", color="count",
                     color_continuous_scale="Blues", text="count",
                     title="Customers by Province")
        fig.update_layout(height=300, margin=dict(t=40,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(dff["Acquisition_Channel"].value_counts().reset_index(),
                     x="Acquisition_Channel", y="count", text="count",
                     title="Acquisition Channel")
        fig.update_layout(height=280, margin=dict(t=40,b=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        kyc_clr = {"Verified": GREEN, "Expired": AMBER, "Pending": BLUE, "Unknown": "#7F8C8D"}
        kyc = dff["KYC_Status"].value_counts().reset_index()
        fig = px.pie(kyc, names="KYC_Status", values="count",
                     color="KYC_Status", color_discrete_map=kyc_clr,
                     hole=0.4, title="KYC Status")
        fig.update_layout(height=280, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SAVINGS
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    st.header("Q1 — Savings & Customer Behaviour")

    st.subheader("Average Savings by Group")
    c1, c2, c3 = st.columns(3)

    with c1:
        d = dff.groupby("Customer_Segment")["Savings_Balance"].mean().reset_index()
        fig = px.bar(d, x="Customer_Segment", y="Savings_Balance",
                     color="Customer_Segment", color_discrete_map=SEG_CLR,
                     text=d["Savings_Balance"].apply(lambda v: f"{v/1e3:.0f}K"),
                     title="By Segment")
        fig.update_layout(showlegend=False, height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        d = dff.groupby("Province")["Savings_Balance"].mean().reset_index().sort_values("Savings_Balance")
        fig = px.bar(d, x="Savings_Balance", y="Province", orientation="h",
                     text=d["Savings_Balance"].apply(lambda v: f"{v/1e3:.0f}K"),
                     title="By Province")
        fig.update_layout(height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        d = dff.groupby("Urban_Rural")["Savings_Balance"].mean().reset_index()
        fig = px.bar(d, x="Urban_Rural", y="Savings_Balance",
                     text=d["Savings_Balance"].apply(lambda v: f"{v/1e3:.0f}K"),
                     title="By Urban/Rural")
        fig.update_layout(height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Q1b — Savings by Age Band")
    age_sav = dff.groupby("Age_Band", observed=True)["Savings_Balance"].agg(Total="sum", Mean="mean", Count="count").reset_index()
    age_sav["Age_Band"] = age_sav["Age_Band"].astype(str)
    winner = age_sav.loc[age_sav["Total"].idxmax(), "Age_Band"]
    st.caption(f"✅ Highest total savings band: **{winner}**")

    fig = px.bar(age_sav, x="Age_Band", y="Total",
                 color=age_sav["Age_Band"].apply(lambda b: RED if b == winner else BLUE),
                 text=age_sav["Total"].apply(lambda v: f"{v/1e6:.1f}M"),
                 title="Total Savings by Age Band")
    fig.update_layout(showlegend=False, height=320, margin=dict(t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Q1c — Savings Flow: Growing vs Draining")
    dff["Flow"] = np.where(dff["Net_Monthly_Flow"] > 0, "Growing", "Draining")
    growing_n = (dff["Flow"] == "Growing").sum()

    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Growing",  f"{growing_n:,} ({pct(growing_n, len(dff))}%)")
        st.metric("Draining", f"{len(dff)-growing_n:,} ({pct(len(dff)-growing_n, len(dff))}%)")
    with c2:
        flow_seg = dff.groupby(["Customer_Segment","Flow"]).size().reset_index(name="Count")
        fig = px.bar(flow_seg, x="Customer_Segment", y="Count", color="Flow",
                     barmode="group", color_discrete_map={"Growing": GREEN, "Draining": RED})
        fig.update_layout(height=300, margin=dict(t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LOANS & RISK
# ══════════════════════════════════════════════════════════════════════════════
with t2:
    st.header("Q2 — Loan Portfolio & Risk")

    c = st.columns(5)
    c[0].metric("Borrowers",       f"{len(loan_df):,}")
    c[1].metric("Loan Penetration",f"{pct(len(loan_df), len(dff))}%")
    c[2].metric("Avg Loan",        f"LKR {loan_df['Loan_Amount'].mean():,.0f}")
    c[3].metric("Total Exposure",  f"LKR {loan_df['Outstanding_Loan_Balance'].sum()/1e6:.1f}M")
    c[4].metric("Default Rate",    f"{pct((loan_valid['Loan_Repayment_Status']=='Defaulted').sum(), len(loan_valid))}%")

    st.markdown("---")

    st.subheader("Q2a — Loan Penetration")
    c1, c2 = st.columns(2)
    with c1:
        d = dff.groupby("Customer_Segment")["Has_Loan"].apply(lambda x: pct((x=="Yes").sum(), len(x))).reset_index(name="%")
        fig = px.bar(d, x="Customer_Segment", y="%", color="Customer_Segment",
                     color_discrete_map=SEG_CLR, text=d["%"].apply(lambda v: f"{v}%"),
                     title="By Segment")
        fig.update_layout(showlegend=False, height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        d = dff.groupby("Acquisition_Channel")["Has_Loan"].apply(lambda x: pct((x=="Yes").sum(), len(x))).reset_index(name="%")
        fig = px.bar(d.sort_values("%", ascending=False), x="Acquisition_Channel", y="%",
                     text=d.sort_values("%", ascending=False)["%"].apply(lambda v: f"{v}%"),
                     title="By Channel")
        fig.update_layout(height=300, margin=dict(t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Q2b — Debt-to-Savings Ratio")
    dts = loan_df[loan_df["Debt_to_Savings"].notna()]
    exceed = dts[dts["Debt_to_Savings"] > 1.0]
    c1, c2, c3 = st.columns(3)
    c1.metric("D:S > 1.0",       f"{len(exceed):,}")
    c2.metric("% of borrowers",  f"{pct(len(exceed), len(dts))}%")
    c3.metric("Exposure",        f"LKR {exceed['Outstanding_Loan_Balance'].sum()/1e6:.1f}M")

    fig = px.histogram(dts, x="Debt_to_Savings", nbins=40, color_discrete_sequence=[BLUE],
                       title="Debt-to-Savings Distribution")
    fig.add_vline(x=1.0, line_dash="dash", line_color=RED, annotation_text="Risk = 1.0")
    fig.update_layout(height=300, margin=dict(t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Q2c — Default Rates")
    c1, c2 = st.columns(2)
    with c1:
        d = loan_valid.groupby("Customer_Segment")["Loan_Repayment_Status"].apply(
            lambda x: pct((x=="Defaulted").sum(), len(x))).reset_index(name="Default %")
        fig = px.bar(d.sort_values("Default %", ascending=False), x="Customer_Segment", y="Default %",
                     text=d.sort_values("Default %", ascending=False)["Default %"].apply(lambda v: f"{v}%"),
                     title="By Segment", color="Default %",
                     color_continuous_scale=["green","orange","red"])
        fig.add_hline(y=5, line_dash="dash", line_color=GREEN, annotation_text="5% target")
        fig.update_layout(height=300, margin=dict(t=40,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        d = loan_valid[loan_valid["Loan_Type"].notna()].groupby("Loan_Type")["Loan_Repayment_Status"].apply(
            lambda x: pct((x=="Defaulted").sum(), len(x))).reset_index(name="Default %")
        fig = px.bar(d.sort_values("Default %", ascending=False), x="Loan_Type", y="Default %",
                     text=d.sort_values("Default %", ascending=False)["Default %"].apply(lambda v: f"{v}%"),
                     title="By Loan Type", color="Default %",
                     color_continuous_scale=["green","orange","red"])
        fig.add_hline(y=5, line_dash="dash", line_color=GREEN, annotation_text="5% target")
        fig.update_layout(height=300, margin=dict(t=40,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DIGITAL
# ══════════════════════════════════════════════════════════════════════════════
with t3:
    st.header("Q3 — Digital Engagement & Products")

    st.subheader("Q3a — App Users vs Non-App Users")
    app = dff.groupby("Mobile_App_User")["Savings_Balance"].agg(["mean","median","count"]).reset_index()
    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(app.rename(columns={"Mobile_App_User":"App User","mean":"Avg","median":"Median","count":"Count"})
                     .style.format({"Avg":"{:,.0f}","Median":"{:,.0f}"}), use_container_width=True)
        st.info("Higher mean for app users may reflect selection bias — wealthier customers adopt apps more.")
    with c2:
        fig = px.box(dff, x="Mobile_App_User", y="Savings_Balance",
                     color="Mobile_App_User",
                     color_discrete_map={"Yes": GREEN, "No": RED},
                     title="Savings Balance: App vs Non-App")
        fig.update_layout(height=320, margin=dict(t=40,b=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Q3b — Cross-Sell Opportunity")
    xsell = dff[dff["CrossSell_Opportunity"]]
    c1, c2, c3 = st.columns(3)
    c1.metric("Cross-Sell Candidates", f"{len(xsell):,}")
    c2.metric("% of Base",             f"{pct(len(xsell), len(dff))}%")
    c3.metric("Savings Pool",          f"LKR {xsell['Savings_Balance'].sum()/1e6:.1f}M")

    fig = px.bar(xsell.groupby("Customer_Segment").size().reset_index(name="Count"),
                 x="Customer_Segment", y="Count", color="Customer_Segment",
                 color_discrete_map=SEG_CLR, text="Count",
                 title="Cross-Sell Candidates by Segment")
    fig.update_layout(showlegend=False, height=280, margin=dict(t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Q3c — Channel Quality")
    ch = dff.groupby("Acquisition_Channel")["Savings_Balance"].agg(Avg="mean", Count="count").reset_index()
    ch_def = loan_valid.groupby("Acquisition_Channel")["Loan_Repayment_Status"].apply(
        lambda x: pct((x=="Defaulted").sum(), len(x))).reset_index(name="Default %")
    ch = ch.merge(ch_def, on="Acquisition_Channel")
    st.dataframe(ch.style.format({"Avg":"LKR {:,.0f}","Default %":"{:.1f}%"}), use_container_width=True)
    st.caption("Best channel = highest avg savings + lowest default rate")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — KPIs
# ══════════════════════════════════════════════════════════════════════════════
with t4:
    st.header("Q4 — KPI Dashboard")

    kpis = [
        ("Loan Default Rate", pct((loan_valid["Loan_Repayment_Status"]=="Defaulted").sum(), len(loan_valid)), 5,  "lower"),
        ("Cross-Sell Gap",    pct(dff["CrossSell_Opportunity"].sum(), len(dff)),                              35, "lower"),
        ("App Adoption",      pct((dff["Mobile_App_User"]=="Yes").sum(), len(dff)),                           65, "higher"),
        ("KYC Verified",      pct((dff["KYC_Status"]=="Verified").sum(), len(dff)),                           95, "higher"),
        ("Savings Growing",   pct((dff["Net_Monthly_Flow"]>0).sum(), len(dff)),                               70, "higher"),
    ]

    cols = st.columns(5)
    for col, (name, val, target, direction) in zip(cols, kpis):
        col.metric(name, f"{val}%", delta=f"target {'<' if direction=='lower' else '>'}{target}%")

    st.markdown("---")

    fig = go.Figure()
    names   = [k[0] for k in kpis]
    values  = [k[1] for k in kpis]
    targets = [k[2] for k in kpis]
    colors  = [GREEN if (v<=t if d=="lower" else v>=t) else RED for _,v,t,d in kpis]

    fig.add_trace(go.Bar(x=names, y=values, marker_color=colors,
                         text=[f"{v}%" for v in values], textposition="outside", name="Current"))
    fig.add_trace(go.Scatter(x=names, y=targets, mode="markers",
                             marker=dict(symbol="line-ew", size=20, color=AMBER,
                                         line=dict(width=3, color=AMBER)),
                             name="Target"))
    fig.update_layout(height=380, margin=dict(t=10,b=80),
                      legend=dict(orientation="h", y=1.1), xaxis_tickangle=-10)
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — BOARD SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
with t5:
    st.header("Q5 & Q6 — Board Summary & Critique")

    st.subheader("Key Findings")
    findings = [
        ("📈", "Savings base healthy but concentrated",
         "35–44 age band and Premium segment hold the most savings. Western Province dominates. Concentration creates geographic and demographic risk."),
        ("⚠️", "Loan risk is uneven",
         "~44% of customers have loans. A significant share have Debt-to-Savings > 1.0. Default rates vary by segment and loan type."),
        ("📱", "Large cross-sell gap",
         f"~{pct(dff['CrossSell_Opportunity'].sum(), len(dff))}% of customers hold savings but no Fixed Deposit and no Insurance — a major untapped revenue opportunity."),
        ("⚖️", "KYC compliance gap",
         f"Only {pct((dff['KYC_Status']=='Verified').sum(), len(dff))}% KYC verified vs 95% regulatory target. Urgent remediation needed."),
    ]
    for icon, title, body in findings:
        st.markdown(f"**{icon} {title}**")
        st.caption(body)
        st.markdown("---")

    st.subheader("Recommendations")
    with st.expander("1. Launch FD & Insurance cross-sell campaign", expanded=True):
        st.markdown("**Evidence:** Large pool of savings-only customers with no FD or insurance.")
        st.markdown("**Action:** Target 35–54 age band via app for app users, agents for others.")
        st.markdown("**Outcome:** Higher product holdings per customer, more fee income, lower churn.")

    with st.expander("2. Risk-tiered loan underwriting", expanded=True):
        st.markdown("**Evidence:** Default rates differ significantly by segment and loan type.")
        st.markdown("**Action:** Cap loan amounts for Starter segment; flag D:S > 1.0 pre-disbursement.")
        st.markdown("**Outcome:** Default rate below 5% target within 12 months.")

    st.markdown("---")
    st.subheader("Q6 — Limitations")
    critiques = [
        ("🔴 High", "Segment median imputation may bias savings metrics",
         "If a whole segment is stressed, the median is biased. Obtain true values or exclude rather than impute."),
        ("🔴 High", "App–savings link is correlation, not causation",
         "Wealthier customers may adopt apps AND save more. Run a before/after study to isolate the app effect."),
        ("🟡 Medium", "Age band boundaries are arbitrary",
         "Different cuts produce different 'winners'. Apply Kruskal-Wallis test to confirm significance."),
        ("🟡 Medium", "District defaults are underpowered",
         "Some districts have <15 loan holders. Apply a minimum sample threshold before flagging regions."),
    ]
    for sev, title, body in critiques:
        st.markdown(f"**{sev} — {title}**")
        st.caption(body)
        st.markdown("---")