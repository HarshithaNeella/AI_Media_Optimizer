import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Media Optimizer",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #020617;
    color: white;
}

.block-container {
    padding-top: 1.5rem;
    max-width: 1450px;
}

section[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
}

.stDataFrame {
    border-radius: 12px;
}

div[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1f2937;
    padding: 15px;
    border-radius: 16px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("⚡ Media Optimizer")

    uploaded_file = st.file_uploader(
        "📁 Upload Campaign CSV",
        type=["csv"]
    )

    analysis_type = st.selectbox(
        "📊 Analysis Type",
        [
            "Performance Analysis",
            "Budget Optimization",
            "Audience Optimization"
        ]
    )

    run_analysis = st.button(
        "🚀 Run AI Analysis",
        use_container_width=True
    )

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div style='padding:28px;border-radius:18px;
background:linear-gradient(90deg,#0f172a,#111827);
border:1px solid #1e293b;'>

<h1 style='color:white;font-size:42px;'>
🚀 AI Media Optimization Intelligence Dashboard
</h1>

<p style='color:#94a3b8;font-size:18px;'>
Enterprise-grade campaign analysis powered by Agentic AI workflows
</p>

</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# FILE VALIDATION
# =========================================================

if uploaded_file is not None:

    try:

        df = pd.read_csv(uploaded_file)
        # ============================================================
        # COLUMN STANDARDIZATION
        # ============================================================

        column_mapping = {

            "campaign_id": "ad_unit_id",
            "adid": "ad_unit_id",
            "ad_id": "ad_unit_id",

            "channel": "platform",
            "source": "platform",

            "ad_format": "ad_type",

            "views": "impressions",

            "spend": "revenue",
            "sales": "revenue",

            "position": "placement",

            "device_type": "device"
        }

        # normalize column names
        df.columns = [
            col.strip().lower()
            for col in df.columns
        ]

        # auto rename columns
        df.rename(
            columns=column_mapping,
            inplace=True
        )
        # =========================================================
        # SMART METRIC ENGINE
        # =========================================================

        # Convert numeric columns safely
        possible_numeric_cols = [
            "impressions",
            "clicks",
            "revenue",
            "spend"
        ]

        for col in possible_numeric_cols:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                ).fillna(0)

        # Safe default spend
        if "spend" not in df.columns:

            if "revenue" in df.columns:
                df["spend"] = df["revenue"] * 0.7
            else:
                df["spend"] = 1

        # Safe defaults
        if "impressions" not in df.columns:
            df["impressions"] = 1

        if "clicks" not in df.columns:
            df["clicks"] = 1

        # Prevent divide-by-zero
        df["impressions"] = df["impressions"].replace(0, 1)
        df["clicks"] = df["clicks"].replace(0, 1)
        df["spend"] = df["spend"].replace(0, 1)

        # CTR
        df["ctr"] = (
            df["clicks"] / df["impressions"]
        ) * 100

        # CPC
        df["cpc"] = (
            df["spend"] / df["clicks"]
        )

        # Conversion Rate
        if "revenue" in df.columns:

            df["conversion_rate"] = (
                df["revenue"] / df["clicks"]
            ) * 100

        else:

            df["conversion_rate"] = 0

        # ROAS
        if "revenue" in df.columns:

            df["roas"] = (
                df["revenue"] / df["spend"]
            )

        else:

            df["roas"] = 0
        # ============================================================
        # REQUIRED CORE COLUMNS
        # ============================================================

        required_core_columns = [
            "platform",
            "impressions",
            "clicks",
            "revenue"
        ]

        missing_core = [

            col for col in required_core_columns

            if col not in df.columns
        ]

        if missing_core:

            st.error(
                f"Missing required columns: {missing_core}"
            )

            st.stop()

        # ============================================================
        # OPTIONAL COLUMNS
        # ============================================================

        optional_defaults = {

            "date": "2025-01-01",
            "ad_unit_id": "UNKNOWN_AD",
            "ad_type": "banner",
            "placement": "feed",
            "device": "mobile"
        }

        for col, default in optional_defaults.items():

            if col not in df.columns:

                df[col] = default

        # ============================================================
        # KEEP ONLY REQUIRED SYSTEM COLUMNS
        # ============================================================

        final_columns = [

            "date",
            "platform",
            "ad_unit_id",
            "ad_type",
            "impressions",
            "clicks",
            "revenue",
            "placement",
            "device"
            
        ]

        df = df[final_columns]
        # ============================================================
        # DERIVED METRICS
        # ============================================================

        df["ctr"] = (
            df["clicks"] / df["impressions"]
        ) * 100

        df["ctr"] = df["ctr"].round(2)
        st.success("✅ CSV validated successfully")

        # =================================================
        # RUN ANALYSIS
        # =================================================

        if run_analysis:

            with st.spinner(
                "AI agents are analyzing campaign performance..."
            ):

                try:

                    backend_url = (
                        "https://aimediaoptimizer-production.up.railway.app/analyze"
                    )

                    payload = {
                            "summary_metrics": {

                                "avg_ctr": round(
                                    float(
                                        df.get("ctr", pd.Series([0])).mean()
                                    ),
                                    2
                                ),

                                "avg_cpc": round(
                                    float(
                                        df.get("cpc", pd.Series([0])).mean()
                                    ),
                                    2
                                ),

                                "avg_roas": round(
                                    float(
                                        df.get("roas", pd.Series([0])).mean()
                                    ),
                                    2
                                ),

                                "avg_conversion_rate": round(
                                    float(
                                        df.get("conversion_rate", pd.Series([0])).mean()
                                    ),
                                    2
                                ),

                                "total_revenue": round(
                                    float(
                                        df.get("revenue", pd.Series([0])).sum()
                                    ),
                                    2
                                ),

                                "total_spend": round(
                                    float(
                                        df.get("spend", pd.Series([0])).sum()
                                    ),
                                    2
                                )

                            },

                            "campaign_data": df.to_dict(
                                orient="records"
                            )
                    }

                    response = requests.post(
                        backend_url,
                        json=payload,
                        timeout=180
                    )

                    if response.status_code != 200:
                        st.error(f"Backend API Error: {response.status_code}")  
                        st.text(response.text)
                        st.stop()
                    result = response.json()

                    # =================================================
                    # FAILURE
                    # =================================================

                    if not result.get("success"):

                        st.error(
                            "Backend workflow failed"
                        )

                        st.json(result)

                    else:

                        # =================================================
                        # ANALYSIS DATA
                        # =================================================

                        analysis_data = result.get(
                            "analysis",
                            {}
                        )

                        campaign_summary = (
                            analysis_data.get(
                                "campaign_summary",
                                {}
                            )
                        )

                        issues_detected = (
                            analysis_data.get(
                                "issues_detected",
                                []
                            )
                        )

                        optimization_suggestions = (
                            analysis_data.get(
                                "optimization_suggestions",
                                []
                            )
                        )

                        action_plan = (
                            analysis_data.get(
                                "action_plan",
                                {}
                            )
                        )

                        # =================================================
                        # KPI CARDS
                        # =================================================

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric(
                                "Overall Status",
                                campaign_summary.get(
                                    "overall_status",
                                    "N/A"
                                )
                            )

                        with col2:
                            st.metric(
                                "Primary Issue",
                                campaign_summary.get(
                                    "primary_issue",
                                    "N/A"
                                )
                            )

                        with col3:
                            st.metric(
                                "Optimization Priority",
                                campaign_summary.get(
                                    "optimization_priority",
                                    "N/A"
                                )
                            )

                        with col4:
                            st.metric(
                                "AI Quality Score",
                                f"{result.get('quality_score','N/A')}/10"
                            )

                        st.markdown("<br>", unsafe_allow_html=True)

                        # =================================================
                        # EXECUTIVE SUMMARY
                        # =================================================

                        st.markdown(
                            "## 📌 Executive Summary"
                        )

                        st.markdown(f"""
                        <div style='padding:22px;
                        border-radius:16px;
                        background:#0f172a;
                        border-left:5px solid #38bdf8;'>

                        <p style='font-size:16px;
                        color:#e2e8f0;
                        line-height:1.8;'>

                        {analysis_data.get('executive_summary','No summary available')}

                        </p>

                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)

                        # =================================================
                        # CHARTS
                        # =================================================

                        col_chart1, col_chart2 = st.columns(2)

                        # -------------------------
                        # PIE CHART
                        # -------------------------

                        with col_chart1:

                            st.markdown(
                                "## 📊 Risk Distribution"
                            )

                            if issues_detected:

                                severity_data = {}

                                for issue in issues_detected:

                                    severity = issue.get(
                                        "severity",
                                        "UNKNOWN"
                                    )

                                    severity_data[severity] = (
                                        severity_data.get(
                                            severity,
                                            0
                                        ) + 1
                                    )

                                chart_df = pd.DataFrame({
                                    "Severity":
                                    list(
                                        severity_data.keys()
                                    ),

                                    "Count":
                                    list(
                                        severity_data.values()
                                    )
                                })

                                fig = px.pie(
                                    chart_df,
                                    names="Severity",
                                    values="Count",
                                    hole=0.6
                                )

                                fig.update_layout(
                                    height=360,
                                    paper_bgcolor="#020617",
                                    plot_bgcolor="#020617",
                                    font=dict(
                                        color="white"
                                    ),
                                    margin=dict(
                                        l=20,
                                        r=20,
                                        t=20,
                                        b=20
                                    )
                                )

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True,
                                    config={
                                        "displayModeBar": False
                                    }
                                )

                        # -------------------------
                        # BAR CHART
                        # -------------------------

                        with col_chart2:

                            st.markdown(
                                "## 📈 Priority Overview"
                            )

                            if optimization_suggestions:

                                priority_counts = {
                                    "HIGH": 0,
                                    "MEDIUM": 0,
                                    "LOW": 0
                                }

                                for item in optimization_suggestions:

                                    priority = item.get(
                                        "priority",
                                        "LOW"
                                    )

                                    if priority not in priority_counts:
                                        priority_counts[priority] = 0
                                    priority_counts[priority] += 1

                                priority_df = pd.DataFrame({
                                    "Priority":
                                    list(
                                        priority_counts.keys()
                                    ),

                                    "Count":
                                    list(
                                        priority_counts.values()
                                    )
                                })

                                fig2 = px.bar(
                                    priority_df,
                                    x="Priority",
                                    y="Count",
                                    text_auto=True
                                )

                                fig2.update_layout(
                                    height=360,
                                    paper_bgcolor="#020617",
                                    plot_bgcolor="#020617",
                                    font=dict(
                                        color="white"
                                    ),
                                    margin=dict(
                                        l=20,
                                        r=20,
                                        t=20,
                                        b=20
                                    )
                                )

                                st.plotly_chart(
                                    fig2,
                                    use_container_width=True,
                                    config={
                                        "displayModeBar": False
                                    }
                                )

                        st.markdown("<br>", unsafe_allow_html=True)

                        # =================================================
                        # CRITICAL ISSUES
                        # =================================================

                        st.markdown(
                            "## 🚨 Critical Issues"
                        )

                        for issue in issues_detected:

                            severity = issue.get(
                                "severity",
                                "LOW"
                            )

                            color = {
                                "HIGH":"#ef4444",
                                "MEDIUM":"#f59e0b",
                                "LOW":"#22c55e"
                            }.get(
                                severity,
                                "#38bdf8"
                            )

                            st.markdown(f"""
                            <div style='padding:18px;
                            margin-bottom:16px;
                            border-radius:16px;
                            background:#111827;
                            border-left:6px solid {color};'>

                            <h3 style='color:white;'>
                            ⚠️ {issue.get('issue')}
                            </h3>

                            <p style='color:#cbd5e1;'>
                            <b>Severity:</b>
                            {severity}
                            </p>

                            <p style='color:#cbd5e1;'>
                            <b>Affected Metric:</b>
                            {issue.get('affected_metric')}
                            </p>

                            <p style='color:#cbd5e1;'>
                            <b>Root Cause:</b>
                            {issue.get('root_cause')}
                            </p>

                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)

                        # =================================================
                        # RECOMMENDATIONS
                        # =================================================

                        st.markdown(
                            "## 💡 AI Recommendations"
                        )

                        col1, col2 = st.columns(2)

                        for idx, suggestion in enumerate(
                            optimization_suggestions
                        ):

                            target_col = (
                                col1 if idx % 2 == 0 else col2
                            )

                            with target_col:

                                priority = suggestion.get(
                                    "priority",
                                    "LOW"
                                )

                                color = {
                                    "HIGH":"#ef4444",
                                    "MEDIUM":"#f59e0b",
                                    "LOW":"#22c55e"
                                }.get(
                                    priority,
                                    "#38bdf8"
                                )

                                st.markdown(f"""
                                <div style='padding:18px;
                                margin-bottom:18px;
                                border-radius:18px;
                                background:#111827;
                                border:1px solid #1f2937;'>

                                <h3 style='color:white;'>
                                🎯 {suggestion.get('title')}
                                </h3>

                                <p style='color:#cbd5e1;'>
                                {suggestion.get('recommendation')}
                                </p>

                                <hr style='border:1px solid #1f2937;'>

                                <p style='color:#93c5fd;'>
                                <b>Expected Impact:</b><br>
                                {suggestion.get('expected_impact')}
                                </p>

                                <p style='color:#86efac;'>
                                <b>Business Value:</b><br>
                                {suggestion.get('business_value')}
                                </p>

                                <div style='display:flex;
                                gap:10px;
                                margin-top:15px;'>

                                <div style='padding:8px 14px;
                                border-radius:10px;
                                background:{color};
                                color:white;'>

                                {priority}

                                </div>

                                <div style='padding:8px 14px;
                                border-radius:10px;
                                background:#2563eb;
                                color:white;'>

                                {suggestion.get('implementation_time')}

                                </div>

                                </div>

                                </div>
                                """, unsafe_allow_html=True)
                        st.caption(
                                "Powered by Multi-Agent AI • Planner Agent • Analyzer Agent • Critic Agent"
                            )

                        st.markdown("<br>", unsafe_allow_html=True)

                        # =================================================
                        # ACTION PLAN
                        # =================================================

                        st.markdown(
                            "## 🛠 Strategic Action Plan"
                        )

                        a1, a2, a3 = st.columns(3)

                        with a1:

                            st.markdown(
                                "### ⚡ Immediate"
                            )

                            for item in action_plan.get(
                                "immediate_actions",
                                []
                            ):
                                st.success(item)

                        with a2:

                            st.markdown(
                                "### 📈 Mid-Term"
                            )

                            for item in action_plan.get(
                                "mid_term_actions",
                                []
                            ):
                                st.warning(item)

                        with a3:

                            st.markdown(
                                "### 🚀 Long-Term"
                            )

                            for item in action_plan.get(
                                "long_term_actions",
                                []
                            ):
                                st.info(item)

                        st.markdown("<br>", unsafe_allow_html=True)

                        # =================================================
                        # RECOMMENDATION TABLE
                        # =================================================

                        st.markdown(
                            "## 📋 Recommendation Matrix"
                        )

                        if optimization_suggestions:

                            table_df = pd.DataFrame([

                                {
                                    "Title":
                                    item.get("title"),

                                    "Priority":
                                    item.get("priority"),

                                    "Expected Impact":
                                    item.get("expected_impact"),

                                    "Timeline":
                                    item.get("implementation_time")
                                }

                                for item in optimization_suggestions

                            ])

                            st.dataframe(
                                table_df,
                                use_container_width=True,
                                hide_index=True
                            )

                        st.markdown("<br>", unsafe_allow_html=True)

                        # =================================================
                        # STATUS
                        # =================================================

                        st.markdown(
                            "## 🤖 AI Workflow Status"
                        )

                        s1, s2, s3 = st.columns(3)

                        with s1:
                            st.success(
                                f"Workflow: {result.get('status','completed')}"
                            )

                        with s2:
                            st.info(
                                f"Critic Verdict: {result.get('critic_verdict','PASS')}"
                            )

                        with s3:
                            st.warning(
                                f"Retry Count: {analysis_data.get('retry_iteration',0)}"
                            )

                except Exception as e:

                    st.error(
                        f"AI workflow failed. Please retry."
                    )
                    st.exception(e)

    except Exception as e:

        st.error(
            f"CSV Error: {str(e)}"
        )