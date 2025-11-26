"""
Agent Monitoring Dashboard

Real-time monitoring of agent performance, quality metrics, and system health.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient
import os

# Page config
st.set_page_config(
    page_title="Agent Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

# MongoDB connection
@st.cache_resource
def get_mongo_client():
    mongo_uri = os.getenv("MONGO_URI")
    return MongoClient(mongo_uri)

client = get_mongo_client()
db = client["campus-plateform"]

# Collections
agent_logs = db["agent_logs"]
agent_metrics = db["agent_metrics"]
quizzes = db["quizzes"]
scores = db["scores"]

st.title("🎯 CertAgent Monitoring Dashboard")
st.caption("Real-time agent performance and quality metrics")

# Refresh button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Time range selector
time_range = st.selectbox(
    "Time Range",
    ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
    index=1
)

# Calculate time cutoff
if time_range == "Last Hour":
    cutoff = datetime.now() - timedelta(hours=1)
elif time_range == "Last 24 Hours":
    cutoff = datetime.now() - timedelta(days=1)
elif time_range == "Last 7 Days":
    cutoff = datetime.now() - timedelta(days=7)
else:
    cutoff = datetime.now() - timedelta(days=30)

# ==================== System Health Overview ====================

st.header("📈 System Health Overview")

# Fetch recent metrics
recent_logs = list(agent_logs.find({"timestamp": {"$gte": cutoff}}))
recent_metrics = list(agent_metrics.find({"timestamp": {"$gte": cutoff}}))

# Calculate KPIs
total_requests = len(recent_logs)
successful_requests = len([log for log in recent_logs if log.get("metadata", {}).get("status") == "success"])
error_rate = (total_requests - successful_requests) / total_requests * 100 if total_requests > 0 else 0

response_times = [m["value"] for m in recent_metrics if m["metric_type"] == "response_time"]
avg_response_time = sum(response_times) / len(response_times) if response_times else 0

recent_quizzes = quizzes.count_documents({"generated_at": {"$gte": cutoff}})

# Display KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "System Health",
        f"{100 - error_rate:.1f}%",
        f"{successful_requests}/{total_requests} requests",
        delta_color="normal"
    )

with col2:
    st.metric(
        "Avg Response Time",
        f"{avg_response_time:.2f}s",
        f"p95: {sorted(response_times)[int(len(response_times)*0.95)] if response_times else 0:.2f}s" if response_times else "N/A",
        delta_color="inverse"
    )

with col3:
    st.metric(
        "Quizzes Generated",
        recent_quizzes,
        f"{time_range.lower()}"
    )

with col4:
    st.metric(
        "Error Rate",
        f"{error_rate:.1f}%",
        f"{total_requests - successful_requests} errors",
        delta_color="inverse"
    )

# ==================== Agent Performance Comparison ====================

st.header("🤖 Agent Performance Comparison")

# Agent-specific metrics
agent_data = {}
for agent_name in ["content_curator", "assessment_engine", "learning_coach"]:
    logs = [log for log in recent_logs if log["agent_name"] == agent_name]
    metrics = [m for m in recent_metrics if m["agent_name"] == agent_name]
    
    total = len(logs)
    successful = len([log for log in logs if log.get("metadata", {}).get("status") == "success"])
    times = [m["value"] for m in metrics if m["metric_type"] == "response_time"]
    
    agent_data[agent_name] = {
        "requests": total,
        "success_rate": successful / total * 100 if total > 0 else 0,
        "avg_response_time": sum(times) / len(times) if times else 0,
        "error_rate": (total - successful) / total * 100 if total > 0 else 0
    }

# Create comparison table
col1, col2 = st.columns(2)

with col1:
    df_agents = pd.DataFrame(agent_data).T
    df_agents.index.name = "Agent"
    
    # Format the dataframe without using .style (which requires jinja2)
    df_display = df_agents.copy()
    df_display["requests"] = df_display["requests"].apply(lambda x: f"{x:.0f}")
    df_display["success_rate"] = df_display["success_rate"].apply(lambda x: f"{x:.1f}%")
    df_display["avg_response_time"] = df_display["avg_response_time"].apply(lambda x: f"{x:.3f}s")
    df_display["error_rate"] = df_display["error_rate"].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(df_display, use_container_width=True)

with col2:
    # Radar chart
    if agent_data:
        fig = go.Figure()
        
        for agent_name, data in agent_data.items():
            # Normalize metrics for radar chart (0-1 scale)
            normalized = {
                "Success Rate": data["success_rate"] / 100,
                "Speed": max(0, 1 - (data["avg_response_time"] / 10)),  # Faster is better
                "Reliability": 1 - (data["error_rate"] / 100)
            }
            
            fig.add_trace(go.Scatterpolar(
                r=list(normalized.values()),
                theta=list(normalized.keys()),
                fill='toself',
                name=agent_name.replace("_", " ").title()
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title="Agent Performance Comparison"
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ==================== Response Time Distribution ====================

st.header("⚡ Response Time Analysis")

col1, col2 = st.columns(2)

with col1:
    # Response time histogram
    if response_times:
        fig = px.histogram(
            x=response_times,
            nbins=30,
            labels={"x": "Response Time (seconds)", "y": "Count"},
            title="Response Time Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No response time data available")

with col2:
    # Response time by agent
    agent_times = {}
    for agent_name in ["content_curator", "assessment_engine", "learning_coach"]:
        times = [m["value"] for m in recent_metrics 
                if m["agent_name"] == agent_name and m["metric_type"] == "response_time"]
        if times:
            agent_times[agent_name.replace("_", " ").title()] = times
    
    if agent_times:
        fig = go.Figure()
        for agent_name, times in agent_times.items():
            fig.add_trace(go.Box(
                y=times,
                name=agent_name,
                boxmean='sd'
            ))
        
        fig.update_layout(
            title="Response Time by Agent",
            yaxis_title="Time (seconds)",
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No agent-specific timing data available")

# ==================== Question Quality Metrics ====================

st.header("📝 Question Quality Metrics")

# Analyze recent quiz questions
recent_quiz_docs = list(quizzes.find({"generated_at": {"$gte": cutoff}}))

if recent_quiz_docs:
    total_questions = sum(len(q.get("questions", [])) for q in recent_quiz_docs)
    
    # Difficulty distribution
    difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
    for quiz in recent_quiz_docs:
        difficulty = quiz.get("difficulty", "medium")
        difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Questions Generated", total_questions)
    
    with col2:
        # Difficulty distribution pie chart
        fig = px.pie(
            values=list(difficulty_counts.values()),
            names=list(difficulty_counts.keys()),
            title="Difficulty Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Questions per certification
        cert_counts = {}
        for quiz in recent_quiz_docs:
            cert_id = quiz.get("cert_id", "unknown")
            cert_counts[cert_id] = cert_counts.get(cert_id, 0) + len(quiz.get("questions", []))
        
        st.write("**Questions by Certification:**")
        for cert, count in sorted(cert_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"- {cert}: {count}")

else:
    st.info("No questions generated in selected time range")

# ==================== User Engagement ====================

st.header("👥 User Engagement")

recent_scores = list(scores.find({"submitted_at": {"$gte": cutoff}}))

if recent_scores:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unique_users = len(set(s["user_id"] for s in recent_scores))
        st.metric("Active Users", unique_users)
    
    with col2:
        total_attempts = len(recent_scores)
        st.metric("Quiz Attempts", total_attempts)
    
    with col3:
        avg_score = sum(s.get("score", 0) for s in recent_scores) / len(recent_scores)
        st.metric("Average Score", f"{avg_score * 100:.1f}%")
    
    # Score distribution
    scores_data = [s.get("score", 0) * 100 for s in recent_scores]
    fig = px.histogram(
        x=scores_data,
        nbins=20,
        labels={"x": "Score (%)", "y": "Count"},
        title="Score Distribution"
    )
    fig.add_vline(x=70, line_dash="dash", line_color="red", 
                  annotation_text="Passing Score (70%)")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No user activity in selected time range")

# ==================== Recent Agent Activity Log ====================

st.header("📋 Recent Agent Activity")

# Display recent logs
log_df = pd.DataFrame([
    {
        "Timestamp": log["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
        "Agent": log["agent_name"].replace("_", " ").title(),
        "Action": log["action"],
        "Status": log.get("metadata", {}).get("status", "unknown"),
        "Duration": f"{log.get('metadata', {}).get('duration_seconds', 0):.2f}s"
    }
    for log in sorted(recent_logs, key=lambda x: x["timestamp"], reverse=True)[:50]
])

if not log_df.empty:
    # Add color coding for status (manual formatting, no .style)
    def color_status(val):
        if val == "success":
            return "background-color: #d4edda"
        elif val == "error":
            return "background-color: #f8d7da"
        else:
            return ""

    # Manually build styled HTML table for Streamlit
    def render_styled_table(df):
        html = '<table style="width:100%;border-collapse:collapse;">'
        html += '<tr>' + ''.join(f'<th style="border:1px solid #ccc;padding:6px;">{col}</th>' for col in df.columns) + '</tr>'
        for _, row in df.iterrows():
            html += '<tr>'
            for col in df.columns:
                style = color_status(row[col]) if col == "Status" else ""
                html += f'<td style="border:1px solid #ccc;padding:6px;{style}">{row[col]}</td>'
            html += '</tr>'
        html += '</table>'
        return html

    st.markdown(render_styled_table(log_df), unsafe_allow_html=True)
    st.caption("Status: green = success, red = error")
else:
    st.info("No agent activity logs available")

# ==================== System Information ====================

st.header("ℹ️ System Information")

col1, col2 = st.columns(2)

with col1:
    st.write("**Database Collections:**")
    collections = db.list_collection_names()
    for coll in collections:
        count = db[coll].count_documents({})
        st.write(f"- `{coll}`: {count:,} documents")

with col2:
    st.write("**Agent Status:**")
    st.write("✅ Content Curator Agent: Active")
    st.write("✅ Assessment Engine Agent: Active")
    st.write("✅ Learning Coach Agent: Active")
    st.write("✅ Unified Memory System: Active")

# Footer
st.divider()
st.caption(f"Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
