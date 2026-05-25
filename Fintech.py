import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="FinSight Lanka", page_icon="💰", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f0f0f; }
[data-testid="stSidebar"]          { background: #141414; }
[data-testid="stSidebar"] *        { color: #ccc !important; }
[data-testid="metric-container"]   {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 10px; padding: 16px;
}
div[data-testid="stMetricValue"]   { font-size: 2rem; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv("finsight_clean.csv")
    df["Age_Band"] = pd.Categorical(df["Age_Band"],
        categories=["18-24","25-34","35-44","45-54","55-64","65+"], ordered=True)
    return df

df = load()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💰 FinSight Lanka")
    st.caption("Dialog Finance PLC · Analytics")
    st.divider()

    seg = st.multiselect("Segment",
        df["Customer_Segment"].unique(), default=list(df["Customer_Segment"].unique()))

    prov = st.multiselect("Province",
        sorted(df["Province"].unique()), default=list(df["Province"].unique()))

    channel = st.multiselect("Acquisition Channel",
        df["Acquisition_Channel"].unique(), default=list(df["Acquisition_Channel"].unique()))

    urban = st.multiselect("Urban / Rural",
        df["Urban_Rural"].unique(), default=list(df["Urban_Rural"].unique()))

    st.divider()
    st.caption(f"Raw records: 508 → Clean: {len(df):,}")

# ── Filter ────────────────────────────────────────────────────────────────────
dff = df[
    df["Customer_Segment"].isin(seg) &
    df["Province"].isin(prov) &
    df["Acquisition_Channel"].isin(channel) &
    df["Urban_Rural"].isin(urban)
].copy()

# ── Computed values ───────────────────────────────────────────────────────────
loan_holders  = dff[dff["Has_Loan"] == "Yes"]
loan_valid    = loan_holders[loan_holders["Loan_Repayment_Status"].notna()]
n             = len(dff)

default_rate  = round(100 * (loan_valid["Loan_Repayment_Status"] == "Defaulted").sum() / len(loan_valid), 1) if len(loan_valid) else 0
crosssell_pct = round(100 * dff["CrossSell_Opportunity"].sum() / n, 1) if n else 0
app_pct       = round(100 * (dff["Mobile_App_User"] == "Yes").sum() / n, 1) if n else 0
kyc_pct       = round(100 * (dff["KYC_Status"] == "Verified").sum() / n, 1) if n else 0
growing_pct   = round(100 * (dff["Net_Monthly_Flow"] > 0).sum() / n, 1) if n else 0
loan_pen      = round(100 * (dff["Has_Loan"] == "Yes").sum() / n, 1) if n else 0

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 KPI Overview", "💰 Savings", "🏦 Loans & Risk", "📱 Digital & Products"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — KPI OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## KPI Dashboard")
    st.caption(f"Showing **{n:,}** customers after filters")

    kpis = [
        ("🔴 Loan Default Rate",  f"{default_rate}%",  "Target < 5%",
         default_rate,   5,   True,  f"{default_rate - 5:+.1f}% vs target"),
        ("🟡 Cross-Sell Gap",     f"{crosssell_pct}%", "Target < 40%",
         crosssell_pct,  40,  True,  f"{crosssell_pct - 40:+.1f}% vs target"),
        ("📱 App Adoption",       f"{app_pct}%",       "Target > 65%",
         app_pct,        65,  False, f"{app_pct - 65:+.1f}% vs target"),
        ("⚖️ KYC Verified",       f"{kyc_pct}%",       "Target > 95%",
         kyc_pct,        95,  False, f"{kyc_pct - 95:+.1f}% vs target"),
        ("🟢 Savings Growing",    f"{growing_pct}%",   "Target > 70%",
         growing_pct,    70,  False, f"{growing_pct - 70:+.1f}% vs target"),
    ]

    cols = st.columns(5)
    for col, (name, val, caption, num, target, lower_better, delta) in zip(cols, kpis):
        on_track = num <= target if lower_better else num >= target
        col.metric(name, val, delta=delta,
                   delta_color="inverse" if lower_better else "normal",
                   help=caption)

    st.divider()

    # Gauge charts row
    st.markdown("### KPI Gauges")
    gcols = st.columns(5)
    gauge_data = [
        ("Loan Default Rate", default_rate,  5,   True),
        ("Cross-Sell Gap",    crosssell_pct, 40,  True),
        ("App Adoption",      app_pct,       65,  False),
        ("KYC Verified",      kyc_pct,       95,  False),
        ("Savings Growing",   growing_pct,   70,  False),
    ]

    for gcol, (name, val, target, lower_better) in zip(gcols, gauge_data):
        on_track = val <= target if lower_better else val >= target
        color = "#2ECC71" if on_track else "#E74C3C"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={"suffix": "%", "font": {"size": 28, "color": color}},
            title={"text": name, "font": {"size": 12, "color": "#aaa"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#444", "tickfont": {"color": "#666"}},
                "bar":  {"color": color, "thickness": 0.25},
                "bgcolor": "#1a1a1a",
                "bordercolor": "#2a2a2a",
                "steps": [{"range": [0, 100], "color": "#1a1a1a"}],
                "threshold": {
                    "line": {"color": "#F39C12", "width": 3},
                    "thickness": 0.75,
                    "value": target,
                },
            },
        ))
        fig.update_layout(height=220, margin=dict(t=60, b=10, l=20, r=20),
                          paper_bgcolor="#0f0f0f", font_color="#ccc")
        gcol.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Summary table
    st.markdown("### All KPIs at a Glance")
    kpi_df = pd.DataFrame([
        {"KPI": "Loan Default Rate",  "Area": "Risk",       "Current": f"{default_rate}%",  "Target": "< 5%",  "Status": "✅ On Track" if default_rate <= 5  else "❌ Needs Action"},
        {"KPI": "Cross-Sell Gap",     "Area": "Growth",     "Current": f"{crosssell_pct}%", "Target": "< 40%", "Status": "✅ On Track" if crosssell_pct <= 40 else "❌ Needs Action"},
        {"KPI": "App Adoption",       "Area": "Engagement", "Current": f"{app_pct}%",       "Target": "> 65%", "Status": "✅ On Track" if app_pct >= 65       else "❌ Needs Action"},
        {"KPI": "KYC Verified",       "Area": "Compliance", "Current": f"{kyc_pct}%",       "Target": "> 95%", "Status": "✅ On Track" if kyc_pct >= 95       else "❌ Needs Action"},
        {"KPI": "Savings Growing",    "Area": "Retention",  "Current": f"{growing_pct}%",   "Target": "> 70%", "Status": "✅ On Track" if growing_pct >= 70   else "❌ Needs Action"},
    ])
    st.dataframe(kpi_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SAVINGS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## Savings Analysis")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Savings",    f"LKR {dff['Savings_Balance'].sum()/1e6:.1f}M")
    m2.metric("Avg Savings",      f"LKR {dff['Savings_Balance'].mean()/1e3:.0f}K")
    m3.metric("Median Savings",   f"LKR {dff['Savings_Balance'].median()/1e3:.0f}K")
    m4.metric("Customers",        f"{n:,}")

    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### By Segment")
        seg_s = dff.groupby("Customer_Segment")["Savings_Balance"].agg(
            Mean="mean", Median="median").reset_index()
        fig = px.bar(seg_s.melt("Customer_Segment"), x="Customer_Segment", y="value",
                     color="variable", barmode="group",
                     color_discrete_map={"Mean": "#2E86C1", "Median": "#D4861A"},
                     labels={"value": "LKR", "variable": ""})
        fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                          font_color="#ccc", height=320)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### By Province (Median)")
        prov_s = dff.groupby("Province")["Savings_Balance"].median().sort_values().reset_index()
        fig = px.bar(prov_s, x="Savings_Balance", y="Province", orientation="h",
                     color="Savings_Balance", color_continuous_scale="Blues")
        fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                          font_color="#ccc", height=320, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### By Urban / Rural")
        ur_s = dff.groupby("Urban_Rural")["Savings_Balance"].agg(
            Mean="mean", Median="median").reset_index()
        fig = px.bar(ur_s.melt("Urban_Rural"), x="Urban_Rural", y="value",
                     color="variable", barmode="group",
                     color_discrete_map={"Mean": "#1B4F72", "Median": "#D4861A"},
                     labels={"value": "LKR", "variable": ""})
        fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                          font_color="#ccc", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown("#### By Age Band (Total Savings)")
        df_no_out = dff[dff["Savings_Balance"] < 999_000_000]
        age_s = df_no_out.groupby("Age_Band", observed=True)["Savings_Balance"].sum().reset_index()
        age_s["Age_Band"] = age_s["Age_Band"].astype(str)
        winner = age_s.loc[age_s["Savings_Balance"].idxmax(), "Age_Band"]
        age_s["color"] = age_s["Age_Band"].apply(lambda x: "#E74C3C" if x == winner else "#2E86C1")
        fig = px.bar(age_s, x="Age_Band", y="Savings_Balance",
                     color="Age_Band",
                     color_discrete_sequence=["#E74C3C" if b == winner else "#2E86C1" for b in age_s["Age_Band"]],
                     labels={"Savings_Balance": "Total Savings (LKR)"})
        fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                          font_color="#ccc", height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Savings Flow — Growing vs Draining")
    growing_n  = (dff["Net_Monthly_Flow"] > 0).sum()
    draining_n = (dff["Net_Monthly_Flow"] <= 0).sum()
    f1, f2 = st.columns([1, 2])
    with f1:
        fig = px.pie(values=[growing_n, draining_n],
                     names=[f"Growing ({growing_n})", f"Draining ({draining_n})"],
                     color_discrete_sequence=["#2ECC71", "#E74C3C"], hole=0.5)
        fig.update_layout(paper_bgcolor="#0f0f0f", font_color="#ccc", height=280)
        st.plotly_chart(fig, use_container_width=True)
    with f2:
        flow_seg = dff.groupby(["Customer_Segment"]).apply(
            lambda x: pd.Series({
                "Growing":  (x["Net_Monthly_Flow"] > 0).sum(),
                "Draining": (x["Net_Monthly_Flow"] <= 0).sum()
            })).reset_index()
        fig = px.bar(flow_seg.melt("Customer_Segment"), x="Customer_Segment", y="value",
                     color="variable", barmode="group",
                     color_discrete_map={"Growing": "#2ECC71", "Draining": "#E74C3C"},
                     labels={"value": "Customers", "variable": ""})
        fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                          font_color="#ccc", height=280)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — LOANS & RISK
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## Loan Portfolio & Risk")

    l1, l2, l3, l4 = st.columns(4)
    l1.metric("Loan Penetration",    f"{loan_pen}%")
    l2.metric("Total Borrowers",     f"{len(loan_holders):,}")
    l3.metric("Avg Loan Amount",     f"LKR {loan_holders['Loan_Amount'].mean()/1e3:.0f}K")
    l4.metric("Default Rate",        f"{default_rate}%",
              delta=f"{default_rate - 5:+.1f}% vs 5% target", delta_color="inverse")

    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Loan Penetration by Segment")
        sp = dff.groupby("Customer_Segment").apply(
            lambda x: round(100*(x["Has_Loan"]=="Yes").sum()/len(x), 1)).reset_index()
        sp.columns = ["Segment", "Penetration_%"]
        fig = px.bar(sp.sort_values("Penetration_%", ascending=False),
                     x="Segment", y="Penetration_%",
                     color="Penetration_%", color_continuous_scale="Blues",
                     labels={"Penetration_%": "Penetration (%)"}, text="Penetration_%")
        fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                          font_color="#ccc", height=320, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Default Rate by Segment")
        if len(loan_valid):
            dr = loan_valid.groupby("Customer_Segment").apply(
                lambda x: round(100*(x["Loan_Repayment_Status"]=="Defaulted").sum()/len(x), 1)
            ).reset_index()
            dr.columns = ["Segment", "Default_%"]
            fig = px.bar(dr.sort_values("Default_%", ascending=False),
                         x="Segment", y="Default_%",
                         color="Default_%",
                         color_continuous_scale=[[0,"#2ECC71"],[0.5,"#F39C12"],[1,"#E74C3C"]],
                         text="Default_%", labels={"Default_%": "Default Rate (%)"})
            fig.add_hline(y=5, line_dash="dash", line_color="#F39C12",
                          annotation_text="5% target")
            fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                              font_color="#ccc", height=320, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### Default Rate by Loan Type")
        if len(loan_valid):
            lt = (loan_valid[loan_valid["Loan_Type"].notna()]
                  .groupby("Loan_Type").apply(
                      lambda x: round(100*(x["Loan_Repayment_Status"]=="Defaulted").sum()/len(x),1))
                  .reset_index())
            lt.columns = ["Loan_Type", "Default_%"]
            fig = px.bar(lt.sort_values("Default_%", ascending=False),
                         x="Loan_Type", y="Default_%",
                         color="Default_%",
                         color_continuous_scale=[[0,"#2ECC71"],[0.5,"#F39C12"],[1,"#E74C3C"]],
                         text="Default_%")
            fig.add_hline(y=5, line_dash="dash", line_color="#F39C12")
            fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                              font_color="#ccc", height=300, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown("#### Debt-to-Savings Ratio Distribution")
        dts = loan_holders[loan_holders["Debt_to_Savings"].notna()]["Debt_to_Savings"]
        if len(dts):
            exceed = (dts > 1.0).sum()
            st.caption(f"**{exceed}** borrowers have D:S > 1.0 ({round(100*exceed/len(dts),1)}%)")
            fig = px.histogram(dts.clip(0, 10), nbins=40,
                               labels={"value": "D:S Ratio"},
                               color_discrete_sequence=["#2E86C1"])
            fig.add_vline(x=1.0, line_dash="dash", line_color="#E74C3C",
                          annotation_text="Risk = 1.0")
            fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                              font_color="#ccc", height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Repayment Status Breakdown")
    if len(loan_valid):
        status = loan_valid["Loan_Repayment_Status"].value_counts().reset_index()
        status.columns = ["Status", "Count"]
        fig = px.pie(status, names="Status", values="Count", hole=0.5,
                     color="Status",
                     color_discrete_map={"On-Time": "#2ECC71", "Delayed": "#F39C12", "Defaulted": "#E74C3C"})
        fig.update_layout(paper_bgcolor="#0f0f0f", font_color="#ccc", height=300)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DIGITAL & PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## Digital Engagement & Products")

    xsell = dff[dff["CrossSell_Opportunity"]]
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("App Users",           f"{(dff['Mobile_App_User']=='Yes').sum():,}")
    d2.metric("App Adoption Rate",   f"{app_pct}%")
    d3.metric("Cross-Sell Pool",     f"{len(xsell):,} customers")
    d4.metric("Cross-Sell Savings",  f"LKR {xsell['Savings_Balance'].sum()/1e6:.1f}M")

    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### App Users vs Non-App: Avg Savings")
        app_sav = dff.groupby("Mobile_App_User")["Savings_Balance"].agg(
            Mean="mean", Median="median").reset_index()
        fig = px.bar(app_sav.melt("Mobile_App_User"), x="Mobile_App_User", y="value",
                     color="variable", barmode="group",
                     color_discrete_map={"Mean": "#2E86C1", "Median": "#D4861A"},
                     labels={"value": "LKR", "Mobile_App_User": "App User", "variable": ""},
                     title="Note: median diff is small — mean is inflated by outliers")
        fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                          font_color="#ccc", height=320)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Cross-Sell Candidates by Segment")
        xs_seg = xsell.groupby("Customer_Segment").agg(
            Count=("Customer_ID","count"),
            Savings=("Savings_Balance","sum")).reset_index()
        fig = px.bar(xs_seg, x="Customer_Segment", y="Count",
                     color="Customer_Segment",
                     color_discrete_map={"Premium":"#1B4F72","Regular":"#2E86C1","Starter":"#D4861A"},
                     text="Count",
                     labels={"Count": "Customers", "Customer_Segment": "Segment"})
        fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                          font_color="#ccc", height=320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### Acquisition Channel Quality")
        ch_sav = dff.groupby("Acquisition_Channel")["Savings_Balance"].mean().reset_index()
        ch_def = (loan_valid.groupby("Acquisition_Channel").apply(
            lambda x: round(100*(x["Loan_Repayment_Status"]=="Defaulted").sum()/len(x),1))
            .reset_index() if len(loan_valid) else pd.DataFrame())
        if len(ch_def):
            ch_def.columns = ["Acquisition_Channel", "Default_%"]
            ch = ch_sav.merge(ch_def, on="Acquisition_Channel")
            ch["Count"] = dff.groupby("Acquisition_Channel").size().values
            fig = px.scatter(ch, x="Default_%", y="Savings_Balance",
                             size="Count", color="Acquisition_Channel",
                             text="Acquisition_Channel",
                             labels={"Default_%": "Default Rate (%)",
                                     "Savings_Balance": "Avg Savings (LKR)"})
            fig.update_traces(textposition="top center")
            fig.add_vline(x=ch["Default_%"].mean(), line_dash="dot", line_color="#555")
            fig.add_hline(y=ch["Savings_Balance"].mean(), line_dash="dot", line_color="#555")
            fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                              font_color="#ccc", height=320)
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown("#### Product Holdings Rate (%)")
        products = {"Loan": "Has_Loan", "Fixed Deposit": "Has_Fixed_Deposit",
                    "Insurance": "Has_Insurance", "Mobile Wallet": "Has_Mobile_Wallet"}
        prod_data = []
        for seg_name in ["Premium", "Regular", "Starter"]:
            sub = dff[dff["Customer_Segment"] == seg_name]
            for prod_label, col in products.items():
                r = round(100*(sub[col]=="Yes").sum()/len(sub),1) if len(sub) else 0
                prod_data.append({"Segment": seg_name, "Product": prod_label, "Rate": r})
        prod_df = pd.DataFrame(prod_data)
        fig = px.bar(prod_df, x="Product", y="Rate", color="Segment",
                     barmode="group",
                     color_discrete_map={"Premium":"#1B4F72","Regular":"#2E86C1","Starter":"#D4861A"},
                     labels={"Rate": "% Holding"},
                     text="Rate")
        fig.update_layout(paper_bgcolor="#0f0f0f", plot_bgcolor="#1a1a1a",
                          font_color="#ccc", height=320)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### KYC Status Breakdown")
    kyc_data = dff["KYC_Status"].value_counts().reset_index()
    kyc_data.columns = ["Status", "Count"]
    fig = px.pie(kyc_data, names="Status", values="Count", hole=0.5,
                 color="Status",
                 color_discrete_map={"Verified":"#2ECC71","Expired":"#F39C12",
                                     "Pending":"#2E86C1","Unknown":"#555"})
    fig.update_layout(paper_bgcolor="#0f0f0f", font_color="#ccc", height=300)
    st.plotly_chart(fig, use_container_width=True)