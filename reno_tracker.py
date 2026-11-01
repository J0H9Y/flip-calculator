import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Page config
st.set_page_config(page_title="Reno Cost Tracker", layout="wide", page_icon="🏠")

# Data files
PROJECTS_FILE = "reno_projects.json"
EXPENSES_FILE = "reno_expenses.csv"

# Cost estimation constants (€/sqm for NRW suburbs)
COST_RANGES = {
    "good": {"low": 30, "avg": 45, "high": 60},
    "average": {"low": 50, "avg": 65, "high": 80},
    "poor": {"low": 70, "avg": 90, "high": 110}
}

# Fixed costs for major items (€)
ITEM_COSTS = {
    "kitchen": {"low": 8000, "avg": 12000, "high": 18000},
    "bathroom": {"low": 6000, "avg": 10000, "high": 15000},
    "roof": {"low": 10000, "avg": 15000, "high": 25000},
    "energy": {"low": 15000, "avg": 25000, "high": 40000},
    "flooring": {"low": 3000, "avg": 5000, "high": 8000},
    "windows": {"low": 8000, "avg": 12000, "high": 18000},
    "heating": {"low": 7000, "avg": 12000, "high": 18000},
    "electrical": {"low": 4000, "avg": 6000, "high": 9000}
}

# Timeline estimates (months)
TIMELINE_BASE = {
    "good": {"min": 3, "avg": 4, "max": 6},
    "average": {"min": 5, "avg": 7, "max": 9},
    "poor": {"min": 8, "avg": 10, "max": 12}
}

# KfW grant estimates (2026 basic rules)
KFW_GRANTS = {
    "energy_efficiency": {
        "description": "Energy efficient renovation",
        "max_rate": 0.20,  # 20% of eligible costs
        "max_amount": 12000,
        "requirements": ["energy"]
    },
    "renewable_heating": {
        "description": "Renewable heating system",
        "max_rate": 0.30,
        "max_amount": 9000,
        "requirements": ["heating", "energy"]
    }
}

def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_projects(projects):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f, indent=2)

def load_expenses():
    if os.path.exists(EXPENSES_FILE):
        return pd.read_csv(EXPENSES_FILE)
    return pd.DataFrame(columns=['project_id', 'date', 'category', 'description', 'amount'])

def save_expenses(df):
    df.to_csv(EXPENSES_FILE, index=False)

def calculate_costs(sqm, condition, items):
    # Base renovation cost
    base = COST_RANGES[condition]
    base_low = sqm * base["low"]
    base_avg = sqm * base["avg"]
    base_high = sqm * base["high"]
    
    # Add specific items
    item_low = sum(ITEM_COSTS[item]["low"] for item in items)
    item_avg = sum(ITEM_COSTS[item]["avg"] for item in items)
    item_high = sum(ITEM_COSTS[item]["high"] for item in items)
    
    return {
        "low": base_low + item_low,
        "avg": base_avg + item_avg,
        "high": base_high + item_high,
        "breakdown": {
            "base": {"low": base_low, "avg": base_avg, "high": base_high},
            "items": {item: ITEM_COSTS[item] for item in items}
        }
    }

def calculate_kfw_grants(items, costs):
    grants = []
    total_grant = 0
    
    for grant_name, grant_info in KFW_GRANTS.items():
        if all(req in items for req in grant_info["requirements"]):
            eligible_cost = sum(costs["breakdown"]["items"][item]["avg"] 
                              for item in grant_info["requirements"] if item in costs["breakdown"]["items"])
            grant_amount = min(eligible_cost * grant_info["max_rate"], grant_info["max_amount"])
            grants.append({
                "name": grant_info["description"],
                "amount": grant_amount
            })
            total_grant += grant_amount
    
    return grants, total_grant

def calculate_timeline(condition, items):
    base = TIMELINE_BASE[condition]
    item_months = len(items) * 0.5  # Each major item adds 0.5 months
    
    return {
        "min": max(1, int(base["min"] + item_months * 0.5)),
        "avg": int(base["avg"] + item_months),
        "max": int(base["max"] + item_months * 1.5)
    }

# Initialize session state
if 'current_project' not in st.session_state:
    st.session_state.current_project = None

# Header
st.title("🏠 Reno Cost & Timeline Tracker")
st.markdown("**Zero-cost renovation estimator and tracker for NRW house flips**")

# Sidebar for project selection
st.sidebar.header("Projects")
projects = load_projects()

if st.sidebar.button("➕ New Project"):
    st.session_state.current_project = None

if projects:
    project_names = list(projects.keys())
    selected = st.sidebar.selectbox("Select Project", ["New Project"] + project_names)
    if selected != "New Project":
        st.session_state.current_project = selected

# Main content
if st.session_state.current_project is None:
    # New project estimation
    st.header("📊 New Project Estimation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Inputs")
        project_name = st.text_input("Project Name", placeholder="e.g., Essen Rüttenscheid House")
        sqm = st.number_input("House Size (sqm)", min_value=50, max_value=500, value=120, step=10)
        condition = st.selectbox("Condition", ["good", "average", "poor"], 
                                format_func=lambda x: x.capitalize())
    
    with col2:
        st.subheader("Major Renovation Items")
        items = []
        if st.checkbox("🍳 Kitchen Renovation"): items.append("kitchen")
        if st.checkbox("🚿 Bathroom Renovation"): items.append("bathroom")
        if st.checkbox("🏠 Roof Repair/Replace"): items.append("roof")
        if st.checkbox("⚡ Energy Efficiency Upgrade"): items.append("energy")
        if st.checkbox("🪵 Flooring"): items.append("flooring")
        if st.checkbox("🪟 Windows"): items.append("windows")
        if st.checkbox("🔥 Heating System"): items.append("heating")
        if st.checkbox("💡 Electrical"): items.append("electrical")
    
    if st.button("📈 Calculate Estimates", type="primary"):
        costs = calculate_costs(sqm, condition, items)
        timeline = calculate_timeline(condition, items)
        grants, total_grant = calculate_kfw_grants(items, costs)
        
        # Display results
        st.markdown("---")
        st.header("💰 Cost Estimates")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Low Estimate", f"€{costs['low']:,.0f}")
        with col2:
            st.metric("Average Estimate", f"€{costs['avg']:,.0f}")
        with col3:
            st.metric("High Estimate", f"€{costs['high']:,.0f}")
        with col4:
            st.metric("KfW Grants", f"€{total_grant:,.0f}", delta=f"-{(total_grant/costs['avg']*100):.1f}%")
        
        st.markdown("---")
        st.subheader("📋 Cost Breakdown")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Base Renovation**")
            st.write(f"• Low: €{costs['breakdown']['base']['low']:,.0f}")
            st.write(f"• Average: €{costs['breakdown']['base']['avg']:,.0f}")
            st.write(f"• High: €{costs['breakdown']['base']['high']:,.0f}")
        
        with col2:
            st.markdown("**Major Items**")
            for item, cost in costs['breakdown']['items'].items():
                st.write(f"**{item.capitalize()}:** €{cost['low']:,.0f} - €{cost['high']:,.0f}")
        
        if grants:
            st.markdown("---")
            st.subheader("🎁 KfW Grant Potential (2026)")
            for grant in grants:
                st.success(f"✓ {grant['name']}: **€{grant['amount']:,.0f}**")
            st.info(f"**Net Cost After Grants:** €{costs['avg'] - total_grant:,.0f}")
        
        st.markdown("---")
        st.header("⏱️ Timeline Estimate")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Optimistic", f"{timeline['min']} months")
        with col2:
            st.metric("Realistic", f"{timeline['avg']} months")
        with col3:
            st.metric("Conservative", f"{timeline['max']} months")
        
        # Save project option
        st.markdown("---")
        if project_name and st.button("💾 Save Project"):
            projects[project_name] = {
                "sqm": sqm,
                "condition": condition,
                "items": items,
                "costs": costs,
                "timeline": timeline,
                "grants": grants,
                "total_grant": total_grant,
                "budget": costs['avg'],
                "created": datetime.now().isoformat()
            }
            save_projects(projects)
            st.success(f"✓ Project '{project_name}' saved!")
            st.session_state.current_project = project_name
            st.rerun()

else:
    # Existing project tracking
    project = projects[st.session_state.current_project]
    
    st.header(f"📁 {st.session_state.current_project}")
    
    # Project summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Budget", f"€{project['budget']:,.0f}")
    with col2:
        st.metric("Size", f"{project['sqm']} sqm")
    with col3:
        st.metric("Timeline", f"{project['timeline']['avg']} months")
    with col4:
        st.metric("KfW Grants", f"€{project['total_grant']:,.0f}")
    
    # Expense tracking
    st.markdown("---")
    st.header("💸 Expense Tracker")
    
    expenses_df = load_expenses()
    project_expenses = expenses_df[expenses_df['project_id'] == st.session_state.current_project]
    
    # Add expense form
    with st.expander("➕ Add New Expense"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            expense_date = st.date_input("Date", datetime.now())
        with col2:
            expense_category = st.selectbox("Category", 
                ["Kitchen", "Bathroom", "Roof", "Energy", "Flooring", 
                 "Windows", "Heating", "Electrical", "Other"])
        with col3:
            expense_desc = st.text_input("Description", placeholder="e.g., Cabinet installation")
        with col4:
            expense_amount = st.number_input("Amount (€)", min_value=0.0, step=100.0)
        
        if st.button("Add Expense"):
            new_expense = pd.DataFrame([{
                'project_id': st.session_state.current_project,
                'date': expense_date.isoformat(),
                'category': expense_category,
                'description': expense_desc,
                'amount': expense_amount
            }])
            expenses_df = pd.concat([expenses_df, new_expense], ignore_index=True)
            save_expenses(expenses_df)
            st.success("✓ Expense added!")
            st.rerun()
    
    # Display expenses and budget status
    if not project_expenses.empty:
        total_spent = project_expenses['amount'].sum()
        budget = project['budget']
        remaining = budget - total_spent
        overrun_pct = ((total_spent - budget) / budget * 100) if total_spent > budget else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Spent", f"€{total_spent:,.0f}", 
                     delta=f"{(total_spent/budget*100):.1f}% of budget")
        with col2:
            st.metric("Remaining", f"€{remaining:,.0f}",
                     delta=f"{(remaining/budget*100):.1f}%",
                     delta_color="normal" if remaining >= 0 else "inverse")
        with col3:
            if overrun_pct > 10:
                st.metric("⚠️ Overrun", f"{overrun_pct:.1f}%", 
                         delta="CRITICAL", delta_color="inverse")
            elif total_spent > budget:
                st.metric("⚠️ Overrun", f"{overrun_pct:.1f}%", 
                         delta="Warning", delta_color="inverse")
            else:
                st.metric("✓ Status", "On Track", delta="Good")
        
        # Progress bar
        progress = min(total_spent / budget, 1.0)
        color = "red" if progress > 1.0 else "orange" if progress > 0.9 else "green"
        st.progress(progress)
        
        # Expenses table
        st.subheader("Recent Expenses")
        display_df = project_expenses[['date', 'category', 'description', 'amount']].copy()
        display_df['amount'] = display_df['amount'].apply(lambda x: f"€{x:,.2f}")
        display_df = display_df.sort_values('date', ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Category breakdown
        st.subheader("Spending by Category")
        category_totals = project_expenses.groupby('category')['amount'].sum().sort_values(ascending=False)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.bar_chart(category_totals)
        with col2:
            for cat, amt in category_totals.items():
                st.write(f"**{cat}:** €{amt:,.0f}")
    else:
        st.info("No expenses recorded yet. Add your first expense above!")
    
    # Delete project option
    st.markdown("---")
    if st.button("🗑️ Delete Project", type="secondary"):
        del projects[st.session_state.current_project]
        save_projects(projects)
        # Remove expenses
        expenses_df = expenses_df[expenses_df['project_id'] != st.session_state.current_project]
        save_expenses(expenses_df)
        st.session_state.current_project = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown("💡 **Pro Tips:** Update KfW grant rules annually • Track all expenses for tax purposes • Add 15-20% contingency buffer")
st.markdown("🔧 **Zero Cost Stack:** Python + Streamlit + Local CSV • No cloud fees • Run: `streamlit run app.py`")