import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
import math

# Page config
st.set_page_config(page_title="Reno Cost Tracker", layout="wide", page_icon="🏠")

# Data files
PROJECTS_FILE = "reno_projects.json"
EXPENSES_FILE = "reno_expenses.csv"

# Cost estimation constants (€/sqm for NRW suburbs)
COST_RANGES = {
    "good": {"low": 80, "avg": 110, "high": 140},
    "average": {"low": 110, "avg": 150, "high": 190},
    "poor": {"low": 150, "avg": 200, "high": 260}
}

# Fixed costs for major items (€)
ITEM_COSTS = {
    "kitchen": {"low": 10000, "avg": 15000, "high": 22000},
    "bathroom": {"low": 8000, "avg": 13000, "high": 18000},
    "roof": {"low": 15000, "avg": 22000, "high": 35000},
    "energy": {"low": 25000, "avg": 40000, "high": 65000},
    "flooring": {"low": 5000, "avg": 8000, "high": 12000},
    "windows": {"low": 10000, "avg": 16000, "high": 22000},
    "heating": {"low": 12000, "avg": 20000, "high": 28000},
    "electrical": {"low": 6000, "avg": 10000, "high": 15000}
}

# Standard contingency reserve for planning.
CONTINGENCY_RATE = 0.20

# Final KfW grants 2026 - balanced, realistic, size- and condition-aware
KFW_GRANTS = {
    "energy_efficiency": {
        "description": "Energieeffiziente Sanierung (Daemmung, Fenster etc.)",
        "base_cost_per_sqm": 195,
        "max_rate": 0.20,
        "max_amount": 30000,
        "requirements": ["energy"],
    },
    "roof_insulation": {
        "description": "Dachsanierung / Daemmung",
        "base_cost_per_sqm": 135,
        "max_rate": 0.20,
        "max_amount": 18000,
        "requirements": ["roof"],
    },
    "heat_pump": {
        "description": "Waermepumpe / Heizungstausch",
        "base_cost_per_sqm": 155,
        "max_rate": 0.30,
        "max_amount": 21000,
        "requirements": ["heating"],
    }
}

KFW_CONDITION_MULTIPLIER = {
    "good": 1.0,
    "average": 1.2,
    "poor": 1.45,
}

KFW_SIZE_REFERENCE_SQM = 120
KFW_SYNERGY_BONUS = 1.18
KFW_MIN_MEANINGFUL_GRANT = 750

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
    
    subtotal_low = base_low + item_low
    subtotal_avg = base_avg + item_avg
    subtotal_high = base_high + item_high

    contingency_low = subtotal_low * CONTINGENCY_RATE
    contingency_avg = subtotal_avg * CONTINGENCY_RATE
    contingency_high = subtotal_high * CONTINGENCY_RATE

    return {
        "low": subtotal_low + contingency_low,
        "avg": subtotal_avg + contingency_avg,
        "high": subtotal_high + contingency_high,
        "breakdown": {
            "base": {"low": base_low, "avg": base_avg, "high": base_high},
            "items": {item: ITEM_COSTS[item] for item in items},
            "subtotal": {"low": subtotal_low, "avg": subtotal_avg, "high": subtotal_high},
            "contingency": {"low": contingency_low, "avg": contingency_avg, "high": contingency_high}
        }
    }

def calculate_kfw_grants(items, sqm, condition):
    grants = []
    total_grant = 0
    condition_mult = KFW_CONDITION_MULTIPLIER.get(condition, 1.0)
    size_factor = sqm / KFW_SIZE_REFERENCE_SQM
    synergy_active = "roof" in items and "energy" in items

    for grant_name, grant_info in KFW_GRANTS.items():
        if not any(req in items for req in grant_info["requirements"]):
            continue

        eligible_cost = grant_info["base_cost_per_sqm"] * sqm * condition_mult * size_factor
        if grant_name == "energy_efficiency" and synergy_active:
            eligible_cost *= KFW_SYNERGY_BONUS

        raw_grant = eligible_cost * grant_info["max_rate"]
        grant_amount = min(raw_grant, grant_info["max_amount"])

        if grant_amount > KFW_MIN_MEANINGFUL_GRANT:
            grants.append({
                "key": grant_name,
                "name": grant_info["description"],
                "amount": round(grant_amount),
                "rate": grant_info["max_rate"],
                "base_cost_per_sqm": grant_info["base_cost_per_sqm"],
                "eligible_cost": round(eligible_cost),
                "synergy_applied": grant_name == "energy_efficiency" and synergy_active,
                "capped": raw_grant > grant_info["max_amount"],
                "max_amount": grant_info["max_amount"],
                "condition_mult": condition_mult,
                "size_factor": size_factor,
            })
            total_grant += grant_amount

    return grants, total_grant, synergy_active

def calculate_timeline(condition, items, sqm):
    base = {"good": 4, "average": 7, "poor": 10}
    item_months = len(items) * 1.1
    size_factor = (sqm / 100) * 0.8

    # Use ceiling so nearby sqm values do not collapse to the same month count.
    min_months = max(3, math.ceil(base[condition] + item_months * 0.7 + size_factor * 0.6))
    avg_months = math.ceil(base[condition] + item_months + size_factor)
    max_months = min(24, math.ceil(base[condition] + item_months * 1.4 + size_factor * 1.4))
    avg_months = min(max(avg_months, min_months), max_months)

    return {
        "min": min_months,
        "avg": avg_months,
        "max": max_months
    }

# Initialize session state
if 'current_project' not in st.session_state:
    st.session_state.current_project = None

# Language support (German default)
TRANSLATIONS = {
    "de": {
        "app_title": "🏠 Renovierungs- & Zeitplan-Tracker",
        "app_subtitle": "**Renovierungs-Tool fuer NRW Haus-Flips**",
        "lang_label": "Sprache / Language",
        "projects": "Projekte",
        "new_project_btn": "➕ Neues Projekt",
        "select_project": "Projekt auswaehlen",
        "new_project_opt": "Neues Projekt",
        "new_project_header": "📊 Neue Projektkalkulation",
        "basic_inputs": "Grunddaten",
        "project_name": "Projektname",
        "project_name_ph": "z. B. Essen Ruettenscheid Haus",
        "house_size": "Hausgroesse (qm)",
        "condition": "Zustand",
        "major_items": "Groessere Renovierungspositionen",
        "kitchen": "🍳 Kuechensanierung",
        "bathroom": "🚿 Badsanierung",
        "roof": "🏠 Dachreparatur/-tausch",
        "energy": "⚡ Energieeffizienz-Upgrade",
        "flooring": "🪵 Bodenbelaege",
        "windows": "🪟 Fenster",
        "heating": "🔥 Heizsystem",
        "electrical": "💡 Elektrik",
        "calc_btn": "📈 Berechnungen starten",
        "cost_header": "💰 Kostenschaetzung",
        "low_est": "Niedrige Schaetzung",
        "avg_est": "Durchschnitt",
        "high_est": "Hohe Schaetzung",
        "kfw_grants": "KfW-Zuschuesse",
        "breakdown": "📋 Kostenaufschluesselung",
        "base_reno": "**Basisrenovierung**",
        "subtotal": "**Zwischensumme (vor Reserve)**",
        "contingency": "**Reserve (+20%)**",
        "major_items_label": "**Grosse Positionen**",
        "kfw_potential": "🎁 KfW-Foerderpotenzial (2026)",
        "no_grants": "Keine passenden KfW-Foerderungen fuer die gewaehlten Positionen.",
        "synergy_text": (
            "**KfW-Synergie-Effekt aktiv**  \n"
            "Dachsanierung + Energieeffizienz-Massnahmen kombiniert  \n"
            "→ **+18% hoehere Foerderung** fuer Energieeffizienz  \n"
            "(Realistischer Bonus fuer kombinierte Sanierungen)"
        ),
        "net_after_grants": "**Nettokosten nach Zuschuss:**",
        "kfw_expander_title": "✅ {name} ({rate:.0f}%): €{amount:,}",
        "kfw_eligible_cost": "• Foerderfaehige Kosten: €{amount:,}",
        "kfw_calc_basis": (
            "• Berechnungsgrundlage: {base} €/m² × {sqm} m² × {mult} (Zustand: {condition}) "
            "× {size:.2f} (Groessenfaktor)"
        ),
        "kfw_grant_rate": "• Foerdersatz: {rate:.0f}%",
        "kfw_synergy_applied": "• Synergiebonus (+18%) auf Energiefoerderung angewendet",
        "kfw_capped": "• Hinweis: Betrag durch Programm-Obergrenze von €{max:,} begrenzt",
        "kfw_details": {
            "energy_efficiency": {
                "measures": ["• Daemmung, Fenster, etc."],
                "note": "Hinweis: Erfordert meist Energieberater-Bestaetigung",
            },
            "roof_insulation": {
                "measures": ["• Dachreparatur + Daemmung"],
                "note": "Hinweis: Kombiniert mit Energie-Massnahmen erhoeht die Gesamtfoerderung",
            },
            "heat_pump": {
                "measures": ["• Waermepumpe oder erneuerbare Heizung"],
                "note": "Hinweis: Antrag vor Beginn der Massnahmen erforderlich",
            },
        },
        "condition_labels": {"good": "Gut", "average": "Mittel", "poor": "Schlecht"},
        "expense_categories": [
            "Kueche", "Bad", "Dach", "Energie", "Boden",
            "Fenster", "Heizung", "Elektrik", "Sonstiges"
        ],
        "low_label": "Niedrig",
        "avg_label": "Durchschnitt",
        "high_label": "Hoch",
        "months_suffix": "Monate",
        "item_names": {
            "kitchen": "Kueche",
            "bathroom": "Bad",
            "roof": "Dach",
            "energy": "Energie",
            "flooring": "Boden",
            "windows": "Fenster",
            "heating": "Heizung",
            "electrical": "Elektrik",
        },
        "timeline_header": "⏱️ Zeitplan",
        "timeline_note": (
            "Zeitplan bezieht sich auf die eigentliche Renovierung "
            "(ohne Planung & Genehmigungen)."
        ),
        "disclaimer": (
            "Dies ist eine Schätzung basierend auf typischen 2026 KfW/BAFA-Sätzen. "
            "Die tatsächliche Förderung hängt von Energieberater-Gutachten, "
            "genauen Maßnahmen und Antragszeitpunkt ab."
        ),
        "optimistic": "Optimistisch",
        "realistic": "Realistisch",
        "conservative": "Konservativ",
        "save_btn": "💾 Projekt speichern",
        "saved_ok": "✓ Projekt '{name}' gespeichert!",
        "budget_before": "Budget (vor Zuschuss)",
        "budget_after": "Budget (nach Zuschuss)",
        "size": "Flaeche",
        "timeline": "Zeitplan",
        "expense_header": "💸 Ausgaben-Tracker",
        "add_expense": "➕ Ausgabe erfassen",
        "date": "Datum",
        "category": "Kategorie",
        "description": "Beschreibung",
        "desc_ph": "z. B. Kuechenmontage",
        "amount": "Betrag (€)",
        "add_expense_btn": "Ausgabe hinzufuegen",
        "expense_added": "✓ Ausgabe gespeichert!",
        "total_spent": "Bisher ausgegeben",
        "remaining": "Verbleibend",
        "overrun": "⚠️ Ueberschreitung",
        "status_ok": "✓ Status",
        "on_track": "Im Plan",
        "critical_overrun": "Kritisch",
        "warning": "Warnung",
        "spent_of_budget": "% des Nettobudgets",
        "status_critical_msg": "Status: Kritische Ueberschreitung (>10% ueber Budget).",
        "status_over_msg": "Status: Ueber Budget. Umfang pruefen oder Kosten nachverhandeln.",
        "status_almost_msg": "Status: Budget fast ausgeschoepft (>90%).",
        "status_good_msg": "Status: Im Plan.",
        "progress": "Fortschritt:",
        "recent_expenses": "Letzte Ausgaben",
        "spending_by_cat": "Ausgaben nach Kategorie",
        "no_expenses": "Noch keine Ausgaben erfasst. Fuege die erste Ausgabe hinzu.",
        "delete_btn": "🗑️ Projekt loeschen",
    },
    "en": {
        "app_title": "🏠 Reno Cost & Timeline Tracker",
        "app_subtitle": "**Bilingual renovation tracker for NRW house flips**",
        "lang_label": "Language / Sprache",
        "projects": "Projects",
        "new_project_btn": "➕ New Project",
        "select_project": "Select Project",
        "new_project_opt": "New Project",
        "new_project_header": "📊 New Project Estimation",
        "basic_inputs": "Basic Inputs",
        "project_name": "Project Name",
        "project_name_ph": "e.g., Essen Ruettenscheid House",
        "house_size": "House Size (sqm)",
        "condition": "Condition",
        "major_items": "Major Renovation Items",
        "kitchen": "🍳 Kitchen Renovation",
        "bathroom": "🚿 Bathroom Renovation",
        "roof": "🏠 Roof Repair/Replace",
        "energy": "⚡ Energy Efficiency Upgrade",
        "flooring": "🪵 Flooring",
        "windows": "🪟 Windows",
        "heating": "🔥 Heating System",
        "electrical": "💡 Electrical",
        "calc_btn": "📈 Calculate Estimates",
        "cost_header": "💰 Cost Estimates",
        "low_est": "Low Estimate",
        "avg_est": "Average Estimate",
        "high_est": "High Estimate",
        "kfw_grants": "KfW Grants",
        "breakdown": "📋 Cost Breakdown",
        "base_reno": "**Base Renovation**",
        "subtotal": "**Subtotal (before contingency)**",
        "contingency": "**Contingency (+20%)**",
        "major_items_label": "**Major Items**",
        "kfw_potential": "🎁 KfW Grant Potential (2026)",
        "no_grants": "No matching KfW grants for the selected items.",
        "synergy_text": (
            "**KfW synergy effect active**  \n"
            "Roof renovation + energy efficiency measures combined  \n"
            "→ **+18% higher grant** for energy efficiency  \n"
            "(Realistic bonus for combined renovations)"
        ),
        "net_after_grants": "**Net Cost After Grants:**",
        "kfw_expander_title": "✅ {name} ({rate:.0f}%): €{amount:,}",
        "kfw_eligible_cost": "• Eligible costs: €{amount:,}",
        "kfw_calc_basis": (
            "• Calculation basis: {base} €/sqm × {sqm} sqm × {mult} (condition: {condition}) "
            "× {size:.2f} (size factor)"
        ),
        "kfw_grant_rate": "• Grant rate: {rate:.0f}%",
        "kfw_synergy_applied": "• Synergy bonus (+18%) applied to energy grant",
        "kfw_capped": "• Note: Amount capped at program maximum of €{max:,}",
        "kfw_details": {
            "energy_efficiency": {
                "measures": ["• Insulation, windows, etc."],
                "note": "Note: Usually requires energy advisor confirmation",
            },
            "roof_insulation": {
                "measures": ["• Roof repair + insulation"],
                "note": "Note: Combining with energy measures increases total funding",
            },
            "heat_pump": {
                "measures": ["• Heat pump or renewable heating system"],
                "note": "Note: Application required before starting work",
            },
        },
        "condition_labels": {"good": "Good", "average": "Average", "poor": "Poor"},
        "expense_categories": [
            "Kitchen", "Bathroom", "Roof", "Energy", "Flooring",
            "Windows", "Heating", "Electrical", "Other"
        ],
        "low_label": "Low",
        "avg_label": "Average",
        "high_label": "High",
        "months_suffix": "months",
        "item_names": {
            "kitchen": "Kitchen",
            "bathroom": "Bathroom",
            "roof": "Roof",
            "energy": "Energy",
            "flooring": "Flooring",
            "windows": "Windows",
            "heating": "Heating",
            "electrical": "Electrical",
        },
        "timeline_header": "⏱️ Timeline Estimate",
        "timeline_note": (
            "Timeline refers to the actual renovation period only "
            "(excluding planning and permits)."
        ),
        "disclaimer": (
            "This is an estimate based on typical 2026 KfW/BAFA rates. "
            "Actual funding depends on energy advisor assessments, exact measures, "
            "and application timing."
        ),
        "optimistic": "Optimistic",
        "realistic": "Realistic",
        "conservative": "Conservative",
        "save_btn": "💾 Save Project",
        "saved_ok": "✓ Project '{name}' saved!",
        "budget_before": "Budget (Before Grants)",
        "budget_after": "Budget (After Grants)",
        "size": "Size",
        "timeline": "Timeline",
        "expense_header": "💸 Expense Tracker",
        "add_expense": "➕ Add New Expense",
        "date": "Date",
        "category": "Category",
        "description": "Description",
        "desc_ph": "e.g., Cabinet installation",
        "amount": "Amount (€)",
        "add_expense_btn": "Add Expense",
        "expense_added": "✓ Expense added!",
        "total_spent": "Total Spent",
        "remaining": "Remaining",
        "overrun": "⚠️ Overrun",
        "status_ok": "✓ Status",
        "on_track": "On Track",
        "critical_overrun": "CRITICAL",
        "warning": "Warning",
        "spent_of_budget": "% of net budget",
        "status_critical_msg": "Status: Critical overrun (>10% over budget).",
        "status_over_msg": "Status: Over budget. Review scope or renegotiate costs.",
        "status_almost_msg": "Status: Budget almost fully used (>90%).",
        "status_good_msg": "Status: On track.",
        "progress": "Progress:",
        "recent_expenses": "Recent Expenses",
        "spending_by_cat": "Spending by Category",
        "no_expenses": "No expenses recorded yet. Add your first expense above!",
        "delete_btn": "🗑️ Delete Project",
    },
}

if "lang" not in st.session_state:
    st.session_state.lang = "de"
selected_lang = st.sidebar.selectbox(
    "Sprache / Language",
    options=["Deutsch", "English"],
    index=0 if st.session_state.lang == "de" else 1,
)
st.session_state.lang = "de" if selected_lang == "Deutsch" else "en"
T = TRANSLATIONS[st.session_state.lang]

# Header
st.title(T["app_title"])
st.markdown(T["app_subtitle"])

# Sidebar for project selection
st.sidebar.header(T["projects"])
projects = load_projects()

if st.sidebar.button(T["new_project_btn"]):
    st.session_state.current_project = None

if projects:
    project_names = list(projects.keys())
    selected = st.sidebar.selectbox(T["select_project"], [T["new_project_opt"]] + project_names)
    if selected != T["new_project_opt"]:
        st.session_state.current_project = selected

# Main content
if st.session_state.current_project is None:
    # New project estimation
    st.header(T["new_project_header"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(T["basic_inputs"])
        project_name = st.text_input(T["project_name"], placeholder=T["project_name_ph"])
        sqm = st.number_input(T["house_size"], min_value=50, max_value=500, value=120, step=10)
        condition = st.selectbox(
            T["condition"],
            ["good", "average", "poor"],
            format_func=lambda x: T["condition_labels"][x],
        )
    
    with col2:
        st.subheader(T["major_items"])
        items = []
        if st.checkbox(T["kitchen"]): items.append("kitchen")
        if st.checkbox(T["bathroom"]): items.append("bathroom")
        if st.checkbox(T["roof"]): items.append("roof")
        if st.checkbox(T["energy"]): items.append("energy")
        if st.checkbox(T["flooring"]): items.append("flooring")
        if st.checkbox(T["windows"]): items.append("windows")
        if st.checkbox(T["heating"]): items.append("heating")
        if st.checkbox(T["electrical"]): items.append("electrical")
    
    if st.button(T["calc_btn"], type="primary"):
        costs = calculate_costs(sqm, condition, items)
        timeline = calculate_timeline(condition, items, sqm)
        grants, total_grant, synergy_active = calculate_kfw_grants(items, sqm, condition)
        
        # Display results
        st.markdown("---")
        st.header(T["cost_header"])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(T["low_est"], f"€{costs['low']:,.0f}")
        with col2:
            st.metric(T["avg_est"], f"€{costs['avg']:,.0f}")
        with col3:
            st.metric(T["high_est"], f"€{costs['high']:,.0f}")
        with col4:
            st.metric(T["kfw_grants"], f"€{total_grant:,.0f}", delta=f"-{(total_grant/costs['avg']*100):.1f}%")
        
        st.markdown("---")
        st.subheader(T["breakdown"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(T["base_reno"])
            st.write(f"• {T['low_label']}: €{costs['breakdown']['base']['low']:,.0f}")
            st.write(f"• {T['avg_label']}: €{costs['breakdown']['base']['avg']:,.0f}")
            st.write(f"• {T['high_label']}: €{costs['breakdown']['base']['high']:,.0f}")
            st.markdown(T["subtotal"])
            st.write(f"• {T['low_label']}: €{costs['breakdown']['subtotal']['low']:,.0f}")
            st.write(f"• {T['avg_label']}: €{costs['breakdown']['subtotal']['avg']:,.0f}")
            st.write(f"• {T['high_label']}: €{costs['breakdown']['subtotal']['high']:,.0f}")
            st.markdown(T["contingency"])
            st.write(f"• {T['low_label']}: €{costs['breakdown']['contingency']['low']:,.0f}")
            st.write(f"• {T['avg_label']}: €{costs['breakdown']['contingency']['avg']:,.0f}")
            st.write(f"• {T['high_label']}: €{costs['breakdown']['contingency']['high']:,.0f}")
        
        with col2:
            st.markdown(T["major_items_label"])
            for item, cost in costs['breakdown']['items'].items():
                item_label = T["item_names"].get(item, item.capitalize())
                st.write(f"**{item_label}:** €{cost['low']:,.0f} - €{cost['high']:,.0f}")
        
        st.markdown("---")
        st.subheader(T["kfw_potential"])
        if grants:
            if synergy_active:
                st.info(T["synergy_text"], icon="🔄")
            for grant in grants:
                expander_title = T["kfw_expander_title"].format(
                    name=grant["name"],
                    rate=grant["rate"] * 100,
                    amount=grant["amount"],
                )
                details = T["kfw_details"].get(grant["key"], {})
                with st.expander(expander_title, expanded=False):
                    for measure in details.get("measures", []):
                        st.write(measure)
                    st.write(
                        T["kfw_calc_basis"].format(
                            base=grant["base_cost_per_sqm"],
                            sqm=sqm,
                            mult=grant["condition_mult"],
                            condition=T["condition_labels"][condition],
                            size=grant["size_factor"],
                        )
                    )
                    st.write(
                        T["kfw_eligible_cost"].format(amount=grant["eligible_cost"])
                    )
                    st.write(
                        T["kfw_grant_rate"].format(rate=grant["rate"] * 100)
                    )
                    if grant["synergy_applied"]:
                        st.write(T["kfw_synergy_applied"])
                    if grant["capped"]:
                        st.write(
                            T["kfw_capped"].format(max=grant["max_amount"])
                        )
                    if details.get("note"):
                        st.caption(details["note"])
            st.info(
                f"{T['net_after_grants']} €{costs['avg'] - total_grant:,.0f}",
                icon="💰",
            )
        else:
            st.warning(T["no_grants"])
        
        st.markdown("---")
        st.header(T["timeline_header"])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(T["optimistic"], f"{timeline['min']} {T['months_suffix']}")
        with col2:
            st.metric(T["realistic"], f"{timeline['avg']} {T['months_suffix']}")
        with col3:
            st.metric(T["conservative"], f"{timeline['max']} {T['months_suffix']}")
        st.caption(T["timeline_note"])
        
        # Save project option
        st.markdown("---")
        if project_name and st.button(T["save_btn"]):
            projects[project_name] = {
                "sqm": sqm,
                "condition": condition,
                "items": items,
                "costs": costs,
                "timeline": timeline,
                "grants": grants,
                "total_grant": total_grant,
                "budget": costs['avg'],
                "budget_before_grants": costs['avg'],
                "budget_after_grants": max(0, costs['avg'] - total_grant),
                "created": datetime.now().isoformat()
            }
            save_projects(projects)
            st.success(T["saved_ok"].format(name=project_name))
            st.session_state.current_project = project_name
            st.rerun()

else:
    # Existing project tracking
    project = projects[st.session_state.current_project]
    
    st.header(f"📁 {st.session_state.current_project}")
    
    # Project summary
    col1, col2, col3, col4 = st.columns(4)
    budget_after_grants = project.get("budget_after_grants", project["budget"])
    with col1:
        st.metric(T["budget_before"], f"€{project['budget']:,.0f}")
    with col2:
        st.metric(T["size"], f"{project['sqm']} sqm")
    with col3:
        st.metric(T["timeline"], f"{project['timeline']['avg']} {T['months_suffix']}")
    with col4:
        st.metric(T["budget_after"], f"€{budget_after_grants:,.0f}")
    
    # Expense tracking
    st.markdown("---")
    st.header(T["expense_header"])
    
    expenses_df = load_expenses()
    project_expenses = expenses_df[expenses_df['project_id'] == st.session_state.current_project]
    
    # Add expense form
    with st.expander(T["add_expense"]):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            expense_date = st.date_input(T["date"], datetime.now())
        with col2:
            expense_category = st.selectbox(T["category"], T["expense_categories"])
        with col3:
            expense_desc = st.text_input(T["description"], placeholder=T["desc_ph"])
        with col4:
            expense_amount = st.number_input(T["amount"], min_value=0.0, step=100.0)
        
        if st.button(T["add_expense_btn"]):
            new_expense = pd.DataFrame([{
                'project_id': st.session_state.current_project,
                'date': expense_date.isoformat(),
                'category': expense_category,
                'description': expense_desc,
                'amount': expense_amount
            }])
            expenses_df = pd.concat([expenses_df, new_expense], ignore_index=True)
            save_expenses(expenses_df)
            st.success(T["expense_added"])
            st.rerun()
    
    # Display expenses and budget status
    if not project_expenses.empty:
        total_spent = project_expenses['amount'].sum()
        budget = budget_after_grants
        remaining = budget - total_spent
        overrun_pct = ((total_spent - budget) / budget * 100) if total_spent > budget else 0
        spent_pct = (total_spent / budget * 100) if budget else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(T["total_spent"], f"€{total_spent:,.0f}", 
                     delta=f"{spent_pct:.1f}{T['spent_of_budget']}")
        with col2:
            st.metric(T["remaining"], f"€{remaining:,.0f}",
                     delta=f"{((remaining/budget)*100 if budget else 0):.1f}%",
                     delta_color="normal" if remaining >= 0 else "inverse")
        with col3:
            if overrun_pct > 10:
                st.metric(T["overrun"], f"{overrun_pct:.1f}%", 
                         delta=T["critical_overrun"], delta_color="inverse")
            elif total_spent > budget:
                st.metric(T["overrun"], f"{overrun_pct:.1f}%", 
                         delta=T["warning"], delta_color="inverse")
            else:
                st.metric(T["status_ok"], T["on_track"], delta="Good")
        
        # Progress bar
        progress = min(total_spent / budget, 1.0) if budget else 0
        st.progress(progress)
        if total_spent > budget * 1.1:
            st.error(T["status_critical_msg"])
        elif total_spent > budget:
            st.warning(T["status_over_msg"])
        elif total_spent > budget * 0.9:
            st.warning(T["status_almost_msg"])
        else:
            st.success(T["status_good_msg"])
        st.caption(f"{T['progress']} {progress * 100:.1f}%")
        
        # Expenses table
        st.subheader(T["recent_expenses"])
        display_df = project_expenses[['date', 'category', 'description', 'amount']].copy()
        display_df['amount'] = display_df['amount'].apply(lambda x: f"€{x:,.2f}")
        display_df = display_df.sort_values('date', ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Category breakdown
        st.subheader(T["spending_by_cat"])
        category_totals = project_expenses.groupby('category')['amount'].sum().sort_values(ascending=False)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.bar_chart(category_totals)
        with col2:
            for cat, amt in category_totals.items():
                st.write(f"**{cat}:** €{amt:,.0f}")
    else:
        st.info(T["no_expenses"])
    
    # Delete project option
    st.markdown("---")
    if st.button(T["delete_btn"], type="secondary"):
        del projects[st.session_state.current_project]
        save_projects(projects)
        # Remove expenses
        expenses_df = expenses_df[expenses_df['project_id'] != st.session_state.current_project]
        save_expenses(expenses_df)
        st.session_state.current_project = None
        st.rerun()

# Footer
st.markdown("---")
st.caption(T["disclaimer"])