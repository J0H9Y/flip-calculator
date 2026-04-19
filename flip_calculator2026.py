import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Page config
st.set_page_config(page_title="Flip-Rendite-Rechner (DE)", layout="wide", page_icon="💰")

# ──────────────────────────────────────────────
# TRANSLATIONS
# ──────────────────────────────────────────────
TRANSLATIONS = {
    "de": {
        # General
        "lang_label": "🌐 Sprache / Language",
        "page_title": "💰 Flip-Rendite- & Steuerrechner (DE)",
        "page_subtitle": "**Steuerkonformer Gewinnrechner für Immobilien-Flips in NRW (Steuerrecht 2026)**",
        # Sidebar
        "sidebar_header": "⚙️ Einstellungen",
        "annual_income_label": "Dein Jahreseinkommen (€)",
        "annual_income_help": "Für die progressive Steuerberechnung",
        # Section headers
        "deal_inputs_header": "📝 Eckdaten zum Deal",
        "purchase_subheader": "Kauf",
        "holding_subheader": "Haltedauer",
        "exit_subheader": "Exit-Strategie",
        # Input labels
        "buy_price_label": "Kaufpreis (€)",
        "reno_costs_label": "Renovierungskosten (€)",
        "vat_reclaim_header": "**Vorsteuerabzug**",
        "vat_reclaim_label": "Anrechenbarer Anteil der Renovierungskosten",
        "vat_reclaim_help": "Anteil mit ordnungsgemäßen Rechnungen inkl. MwSt. (19 % erstattungsfähig)",
        "hold_years_label": "Haltedauer (Jahre)",
        "holding_costs_label": "Monatliche Haltekosten (€)",
        "holding_costs_help": "Zinsen, Nebenkosten, Versicherung usw.",
        "strategy_label": "Strategie",
        "strategy_sell": "Verkauf",
        "strategy_rent": "Vermietung",
        "strategy_both": "Vergleich beider Varianten",
        "sell_price_label": "Verkaufspreis (€)",
        "makler_sell_label": "Verkäuferprovision zahlen (3,57 %)",
        "eigennutzung_label": "Eigennutzung (§ 23 EStG): Selbst bewohnt im Verkaufsjahr und den beiden Vorjahren",
        "eigennutzung_help": "Bei nachgewiesener Eigennutzung entfällt die Spekulationssteuer – auch bei Verkauf vor 10 Jahren.",
        "monthly_rent_label": "Monatliche Kaltmiete (€)",
        "vacancy_label": "Leerstandsquote (%)",
        "vacancy_help": "Erwarteter Anteil der Zeit ohne Mieter",
        # Calculate button
        "calc_button": "📊 Rendite berechnen",
        # Results
        "results_header": "📈 Ergebnisse",
        "sell_subheader": "💵 Verkaufsvariante",
        "rent_subheader": "🏠 Vermietungsvariante",
        "gross_profit": "Rohgewinn",
        "net_profit": "Nettogewinn",
        "speculation_tax": "Spekulationssteuer",
        "tax_free": "Steuerfrei!",
        "annual_roi": "Jähliche Rendite",
        "gross_yield": "Bruttomietrendite",
        "net_yield": "Nettomietrendite",
        "net_yield_help": "Nach allen Kosten & Einkommensteuer",
        "annual_cashflow": "Jählicher Cashflow",
        "total_cashflow_label": "Gesamtcashflow",
        # Expanders
        "sell_expander": "🔍 Detaillierte Aufschlüsselung (Verkauf)",
        "rent_expander": "🔍 Detaillierte Aufschlüsselung (Vermietung)",
        "acq_costs": "**Erwerbsnebenkosten**",
        "investment": "**Investition**",
        "exit_label": "**Verkauf**",
        "buy_price_line": "• Kaufpreis",
        "reno_line": "• Renovierung",
        "vat_line": "• Vorsteuererstattung",
        "holding_line": "• Haltekosten",
        "total_investment_line": "**Gesamtinvestition",
        "sell_price_line": "• Verkaufspreis",
        "selling_costs_line": "• Verkaufskosten",
        "gross_profit_line": "• Rohgewinn",
        "spec_tax_line": "• Spekulationssteuer",
        "net_profit_line": "**Nettogewinn",
        "tax_info": "**Steuerhinweis**",
        "spec_tax_warning": "⚠️ Verkauf innerhalb von 10 Jahren ({years:.1f} J.) – Spekulationssteuer fällig!",
        "spec_tax_rate_line": "Effektiver Steuersatz: {rate:.1f} %",
        "tax_free_success": "✓ Gehalten: {years:.1f} Jahre – steuerfrei!",
        "invest_same": "**Investition** (wie Verkaufsvariante)",
        "total_invest_line": "• Gesamtinvestition",
        "vat_reclaim_line": "• Vorsteuererstattung",
        "annual_income_section": "**Jährliche Einnahmen**",
        "gross_rent_line": "• Bruttomiete",
        "op_costs_line": "• Bewirtschaftungskosten (25 %)",
        "holding_costs_line2": "• Haltekosten",
        "net_rent_line": "• Nettomiete (vor Steuer)",
        "annual_tax_section": "**Steuern & Cashflow p.a.**",
        "income_tax_line": "• Einkommensteuer",
        "annual_cashflow_line": "**Jährlicher Cashflow",
        "total_over": "**Gesamt über {years:.1f} Jahre**",
        "total_cashflow_line": "• Gesamtcashflow",
        "yields_section": "**Renditen**",
        "gross_yield_line": "• Bruttomietrendite",
        "net_yield_line": "• Nettomietrendite",
        "breakeven_info": "💡 **Break-Even:** {months:.0f} Monate ({years:.1f} Jahre)",
        "no_breakeven": "⚠️ Monatliche Kosten übersteigen Mieteinnahmen – kein Break-Even möglich!",
        # Comparison
        "comparison_header": "⚖️ Vergleich: Verkauf vs. Vermietung",
        "chart_title": "Vergleich Verkauf / Vermietung ({years:.1f} Jahre)",
        "chart_x": "Kennzahl",
        "chart_y": "Betrag (€)",
        "sell_bar": "Verkauf",
        "rent_bar": "Vermietung",
        "bar_gross": "Rohgewinn",
        "bar_aftertax": "Nach Steuer",
        "bar_annual": "Jährl. Renditeäquivalent",
        "bar_total": "Gesamtmietertrag",
        "bar_cashflow": "Cashflow nach Steuer",
        "bar_annual_cf": "Jährl. Cashflow",
        "verdict_header": "### 🎯 Fazit auf einen Blick",
        "sell_better": "✓ **Verkauf ist rentabler**\n\nNettogewinn: €{profit:,.0f}",
        "sell_info": "**Verkauf:** €{profit:,.0f} Nettogewinn",
        "tax_free_sale": "✓ Steuerfreier Verkauf (≥ 10 Jahre Haltedauer)",
        "spec_tax_warn": "⚠️ Spekulationssteuer: €{tax:,.0f}",
        "rent_better": "✓ **Vermietung ist rentabler**\n\nGesamtcashflow: €{cf:,.0f}",
        "rent_info": "**Vermietung:** €{cf:,.0f} Gesamtcashflow",
        "net_yield_info": "Nettomietrendite: {yield_:.2f} %/Jahr",
        "strong_yield": "✓ Starke Mietrendite",
        "moderate_yield": "⚠️ Moderate Mietrendite",
        "low_yield": "❌ Schwache Mietrendite",
        # Save scenario
        "save_label": "Szenario speichern als:",
        "save_placeholder": "z. B. Essen Rüttenscheid Deal #1",
        "save_button": "💾 Szenario speichern",
        "save_success": "\u2713 Szenario \u201e{name}\u201c gespeichert!",
        # Saved scenarios
        "saved_header": "📚 Gespeicherte Szenarien",
        "col_name": "Name",
        "col_buy": "Kaufpreis",
        "col_sell": "Verkaufspreis",
        "col_rent": "Miete",
        "col_net_profit": "Nettogewinn (Verkauf)",
        "col_cashflow": "Cashflow (Miete)",
        "col_created": "Erstellt",
        "na": "k. A.",
        # Footer
        "footer": """
💡 **Steuerhinweise (Stand April 2026):**
- Grunderwerbsteuer: 6,5 % in NRW
- Spekulationssteuer: fällig bei Verkauf < 10 Jahre (progressiv bis 45 % + Soli)
- Eigennutzung-Ausnahme: Bei Selbstnutzung im Verkaufsjahr + den beiden Vorjahren ist der Verkauf steuerfrei (auch < 10 Jahre)
- Vorsteuerabzug: 19 % auf ordnungsgemäß fakturierte Renovierungskosten
- Mieteinkünfte: Werden dem Jahreseinkommen zugerechnet und progressiv besteuert

⚠️ Dies ist eine vereinfachte Berechnung. Für verbindliche Steuerplanung bitte einen Steuerberater konsultieren.

Alle Steuerangaben basieren auf 2026-Regeln und können sich ändern. Keine Haftung für Aktualität oder individuelle Fälle.
""",
    },
    "en": {
        # General
        "lang_label": "🌐 Sprache / Language",
        "page_title": "💰 Flip Profit & Tax Calculator (DE)",
        "page_subtitle": "**German tax-compliant profit calculator for NRW house flips (2026 rules)**",
        # Sidebar
        "sidebar_header": "⚙️ Settings",
        "annual_income_label": "Your Annual Income (€)",
        "annual_income_help": "For progressive tax calculation",
        # Section headers
        "deal_inputs_header": "📝 Deal Inputs",
        "purchase_subheader": "Purchase",
        "holding_subheader": "Holding Period",
        "exit_subheader": "Exit Strategy",
        # Input labels
        "buy_price_label": "Buy Price (€)",
        "reno_costs_label": "Renovation Costs (€)",
        "vat_reclaim_header": "**VAT Reclaim**",
        "vat_reclaim_label": "Eligible % of Reno Costs",
        "vat_reclaim_help": "% with proper VAT invoices (19% reclaimable)",
        "hold_years_label": "Hold Period (Years)",
        "holding_costs_label": "Monthly Holding Costs (€)",
        "holding_costs_help": "Interest, utilities, insurance, etc.",
        "strategy_label": "Strategy",
        "strategy_sell": "Sell",
        "strategy_rent": "Rent",
        "strategy_both": "Compare Both",
        "sell_price_label": "Sell Price (€)",
        "makler_sell_label": "Pay Sell-Side Makler (3.57%)",
        "eigennutzung_label": "Owner-occupied (§ 23 EStG): Self-used in year of sale and the two prior years",
        "eigennutzung_help": "If self-occupancy is proven, speculation tax is waived – even if sold before 10 years.",
        "monthly_rent_label": "Monthly Rent (€)",
        "vacancy_label": "Vacancy Rate (%)",
        "vacancy_help": "Expected % of time unrented",
        # Calculate button
        "calc_button": "📊 Calculate Profit",
        # Results
        "results_header": "📈 Results",
        "sell_subheader": "💵 Sell Scenario",
        "rent_subheader": "🏠 Rent Scenario",
        "gross_profit": "Gross Profit",
        "net_profit": "Net Profit",
        "speculation_tax": "Speculation Tax",
        "tax_free": "Tax-Free!",
        "annual_roi": "Annual ROI",
        "gross_yield": "Gross Yield",
        "net_yield": "Net Yield",
        "net_yield_help": "After all costs & income tax",
        "annual_cashflow": "Annual Cashflow",
        "total_cashflow_label": "Total Cashflow",
        # Expanders
        "sell_expander": "🔍 Detailed Breakdown (Sell)",
        "rent_expander": "🔍 Detailed Breakdown (Rent)",
        "acq_costs": "**Acquisition Costs**",
        "investment": "**Investment**",
        "exit_label": "**Exit**",
        "buy_price_line": "• Buy Price",
        "reno_line": "• Renovation",
        "vat_line": "• VAT Reclaim",
        "holding_line": "• Holding Costs",
        "total_investment_line": "**Total Investment",
        "sell_price_line": "• Sell Price",
        "selling_costs_line": "• Selling Costs",
        "gross_profit_line": "• Gross Profit",
        "spec_tax_line": "• Speculation Tax",
        "net_profit_line": "**Net Profit",
        "tax_info": "**Tax Info**",
        "spec_tax_warning": "⚠️ Sold within 10 years ({years:.1f}y) - speculation tax applies!",
        "spec_tax_rate_line": "Effective tax rate: {rate:.1f}%",
        "tax_free_success": "✓ Held {years:.1f} years - tax-free!",
        "invest_same": "**Investment** (Same as Sell)",
        "total_invest_line": "• Total Investment",
        "vat_reclaim_line": "• VAT Reclaim",
        "annual_income_section": "**Annual Income**",
        "gross_rent_line": "• Gross Rent",
        "op_costs_line": "• Operating Costs (25%)",
        "holding_costs_line2": "• Holding Costs",
        "net_rent_line": "• Net Rent (pre-tax)",
        "annual_tax_section": "**Annual Taxes & Cashflow**",
        "income_tax_line": "• Income Tax",
        "annual_cashflow_line": "**Annual Cashflow",
        "total_over": "**Total Over {years:.1f} Years**",
        "total_cashflow_line": "• Total Cashflow",
        "yields_section": "**Yields**",
        "gross_yield_line": "• Gross Yield",
        "net_yield_line": "• Net Yield",
        "breakeven_info": "💡 **Break-Even:** {months:.0f} months ({years:.1f} years)",
        "no_breakeven": "⚠️ Monthly costs exceed rental income - deal does not break even!",
        # Comparison
        "comparison_header": "⚖️ Sell vs. Rent Comparison",
        "chart_title": "Sell vs. Rent Profit Comparison ({years:.1f} Years)",
        "chart_x": "Metric",
        "chart_y": "Amount (€)",
        "sell_bar": "Sell",
        "rent_bar": "Rent",
        "bar_gross": "Total Profit",
        "bar_aftertax": "After Tax",
        "bar_annual": "Annual ROI Equiv.",
        "bar_total": "Total Return",
        "bar_cashflow": "After Tax Cashflow",
        "bar_annual_cf": "Annual Cashflow",
        "verdict_header": "### 🎯 Quick Verdict",
        "sell_better": "✓ **Selling is more profitable**\n\nNet profit: €{profit:,.0f}",
        "sell_info": "**Selling:** €{profit:,.0f} net profit",
        "tax_free_sale": "✓ Tax-free sale (held 10+ years)",
        "spec_tax_warn": "⚠️ Speculation tax: €{tax:,.0f}",
        "rent_better": "✓ **Renting is more profitable**\n\nTotal cashflow: €{cf:,.0f}",
        "rent_info": "**Renting:** €{cf:,.0f} total cashflow",
        "net_yield_info": "Net yield: {yield_:.2f}%/year",
        "strong_yield": "✓ Strong rental yield",
        "moderate_yield": "⚠️ Moderate rental yield",
        "low_yield": "❌ Low rental yield",
        # Save scenario
        "save_label": "Save Scenario As:",
        "save_placeholder": "e.g., Essen Rüttenscheid Deal #1",
        "save_button": "💾 Save Scenario",
        "save_success": "✓ Scenario '{name}' saved!",
        # Saved scenarios
        "saved_header": "📚 Saved Scenarios",
        "col_name": "Name",
        "col_buy": "Buy Price",
        "col_sell": "Sell Price",
        "col_rent": "Rent",
        "col_net_profit": "Net Profit (Sell)",
        "col_cashflow": "Cashflow (Rent)",
        "col_created": "Created",
        "na": "N/A",
        # Footer
        "footer": """
💡 **Tax Notes (as of April 2026):**
- Grunderwerbsteuer: 6.5% in NRW
- Speculation tax: due if sold <10 years (progressive up to 45% + Soli)
- Owner-occupancy exception: tax-free sale if self-used in year of sale + 2 prior years (even <10 years, per § 23 EStG)
- VAT reclaim: 19% on properly invoiced renovation costs
- Rental income: added to annual income and taxed progressively

⚠️ Simplified calculations. Consult a Steuerberater for binding tax advice.

All tax figures are based on 2026 rules and may change. No liability for accuracy or individual cases.
""",
    },
}

# ──────────────────────────────────────────────
# LANGUAGE SELECTOR (top of sidebar)
# ──────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "de"

lang_options = {"🇩🇪 Deutsch": "de", "🇬🇧 English": "en"}
selected_lang_label = st.sidebar.selectbox(
    "🌐 Sprache / Language",
    options=list(lang_options.keys()),
    index=0 if st.session_state.lang == "de" else 1,
)
st.session_state.lang = lang_options[selected_lang_label]
T = TRANSLATIONS[st.session_state.lang]

# ──────────────────────────────────────────────
# DATA FILE & TAX CONSTANTS
# ──────────────────────────────────────────────
SCENARIOS_FILE = "flip_scenarios.json"

TAX_RATES = {
    "grunderwerbsteuer_nrw": 0.065,
    "notar_grundbuch": 0.015,
    "makler_buy": 0.0357,
    "makler_sell": 0.0357,
    "vat_rate": 0.19,
    "income_tax_brackets": [
        (11604, 0.0),
        (17005, 0.14),
        (66760, 0.24),
        (277825, 0.42),
        (float('inf'), 0.45)
    ],
    "soli": 0.055,
    "soli_threshold": 20350,        # 2026 single person threshold
    "soli_threshold_joint": 40700   # 2026 for married/joint filing
}

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def load_scenarios():
    if os.path.exists(SCENARIOS_FILE):
        with open(SCENARIOS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_scenarios(scenarios):
    with open(SCENARIOS_FILE, 'w') as f:
        json.dump(scenarios, f, indent=2)

def calculate_income_tax(taxable_income):
    if taxable_income <= 0:
        return 0
    tax = 0
    prev_bracket = 0
    for bracket_limit, rate in TAX_RATES["income_tax_brackets"]:
        if taxable_income <= bracket_limit:
            tax += (taxable_income - prev_bracket) * rate
            break
        else:
            tax += (bracket_limit - prev_bracket) * rate
            prev_bracket = bracket_limit
    if tax > TAX_RATES["soli_threshold"]:
        tax += (tax - TAX_RATES["soli_threshold"]) * TAX_RATES["soli"]
    return tax

def calculate_speculation_tax(profit, hold_years, annual_income=50000):
    if hold_years >= 10:
        return 0, 0
    tax_without_profit = calculate_income_tax(annual_income)
    tax_with_profit = calculate_income_tax(annual_income + profit)
    speculation_tax = tax_with_profit - tax_without_profit
    effective_rate = (speculation_tax / profit * 100) if profit > 0 else 0
    return speculation_tax, effective_rate

def calculate_sell_scenario(buy_price, reno_costs, holding_costs_monthly, hold_months,
                            sell_price, vat_reclaim_pct, annual_income, use_sell_makler,
                            eigennutzung=False):
    grunderwerbsteuer = buy_price * TAX_RATES["grunderwerbsteuer_nrw"]
    notar_grundbuch = buy_price * TAX_RATES["notar_grundbuch"]
    makler_buy = buy_price * TAX_RATES["makler_buy"]
    acquisition_costs = grunderwerbsteuer + notar_grundbuch + makler_buy
    total_holding_costs = holding_costs_monthly * hold_months
    vat_reclaim = reno_costs * vat_reclaim_pct * TAX_RATES["vat_rate"]
    total_investment = buy_price + reno_costs + acquisition_costs + total_holding_costs - vat_reclaim
    makler_sell = sell_price * TAX_RATES["makler_sell"] if use_sell_makler else 0
    selling_costs = makler_sell
    gross_profit = sell_price - total_investment - selling_costs
    hold_years = hold_months / 12
    # § 23 EStG Eigennutzung-Ausnahme: steuerfrei bei Selbstnutzung im Verkaufsjahr + 2 Vorjahre
    if eigennutzung:
        speculation_tax, spec_tax_rate = 0, 0
    else:
        speculation_tax, spec_tax_rate = calculate_speculation_tax(gross_profit, hold_years, annual_income)
    net_profit = gross_profit - speculation_tax
    roi = (net_profit / total_investment * 100) if total_investment > 0 else 0
    annual_roi = (roi / hold_years) if hold_years > 0 else 0
    return {
        "acquisition": {
            "grunderwerbsteuer": grunderwerbsteuer,
            "notar_grundbuch": notar_grundbuch,
            "makler": makler_buy
        },
        "total_investment": total_investment,
        "vat_reclaim": vat_reclaim,
        "holding_costs": total_holding_costs,
        "selling_costs": selling_costs,
        "gross_profit": gross_profit,
        "speculation_tax": speculation_tax,
        "spec_tax_rate": spec_tax_rate,
        "net_profit": net_profit,
        "roi": roi,
        "annual_roi": annual_roi,
        "hold_years": hold_years
    }

def calculate_rent_scenario(buy_price, reno_costs, holding_costs_monthly, hold_months,
                            monthly_rent, vacancy_rate, annual_income, vat_reclaim_pct):
    grunderwerbsteuer = buy_price * TAX_RATES["grunderwerbsteuer_nrw"]
    notar_grundbuch = buy_price * TAX_RATES["notar_grundbuch"]
    makler_buy = buy_price * TAX_RATES["makler_buy"]
    acquisition_costs = grunderwerbsteuer + notar_grundbuch + makler_buy
    vat_reclaim = reno_costs * vat_reclaim_pct * TAX_RATES["vat_rate"]
    total_investment = buy_price + reno_costs + acquisition_costs - vat_reclaim
    hold_years = hold_months / 12
    annual_rent_gross = monthly_rent * 12 * (1 - vacancy_rate)
    total_rent_gross = annual_rent_gross * hold_years
    operating_cost_rate = 0.25
    annual_operating_costs = annual_rent_gross * operating_cost_rate
    total_operating_costs = annual_operating_costs * hold_years
    total_holding_costs = holding_costs_monthly * hold_months
    annual_rent_net = annual_rent_gross - annual_operating_costs - (holding_costs_monthly * 12)
    total_rent_net = annual_rent_net * hold_years
    annual_tax_on_rent = calculate_income_tax(annual_income + annual_rent_net) - calculate_income_tax(annual_income)
    total_tax_on_rent = annual_tax_on_rent * hold_years
    annual_cashflow = annual_rent_net - annual_tax_on_rent
    total_cashflow = annual_cashflow * hold_years
    gross_yield = (annual_rent_gross / total_investment * 100) if total_investment > 0 else 0
    net_yield = (annual_cashflow / total_investment * 100) if total_investment > 0 else 0
    return {
        "acquisition": {
            "grunderwerbsteuer": grunderwerbsteuer,
            "notar_grundbuch": notar_grundbuch,
            "makler": makler_buy
        },
        "total_investment": total_investment,
        "vat_reclaim": vat_reclaim,
        "annual_rent_gross": annual_rent_gross,
        "annual_operating_costs": annual_operating_costs,
        "annual_holding_costs": holding_costs_monthly * 12,
        "annual_rent_net": annual_rent_net,
        "annual_tax": annual_tax_on_rent,
        "annual_cashflow": annual_cashflow,
        "total_cashflow": total_cashflow,
        "gross_yield": gross_yield,
        "net_yield": net_yield,
        "hold_years": hold_years
    }

def calculate_breakeven_hold_period(buy_price, reno_costs, holding_costs_monthly,
                                    monthly_rent, vacancy_rate, annual_income, vat_reclaim_pct):
    grunderwerbsteuer = buy_price * TAX_RATES["grunderwerbsteuer_nrw"]
    notar_grundbuch = buy_price * TAX_RATES["notar_grundbuch"]
    makler_buy = buy_price * TAX_RATES["makler_buy"]
    vat_reclaim = reno_costs * vat_reclaim_pct * TAX_RATES["vat_rate"]
    total_investment = buy_price + reno_costs + grunderwerbsteuer + notar_grundbuch + makler_buy - vat_reclaim
    monthly_rent_gross = monthly_rent * (1 - vacancy_rate)
    monthly_operating_costs = monthly_rent_gross * 0.25
    monthly_net = monthly_rent_gross - monthly_operating_costs - holding_costs_monthly
    annual_rent_net = monthly_net * 12
    annual_tax = calculate_income_tax(annual_income + annual_rent_net) - calculate_income_tax(annual_income)
    monthly_tax = annual_tax / 12
    monthly_cashflow = monthly_net - monthly_tax
    if monthly_cashflow <= 0:
        return None
    return total_investment / monthly_cashflow

# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = load_scenarios()

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.title(T["page_title"])
st.markdown(T["page_subtitle"])

# ──────────────────────────────────────────────
# SIDEBAR – Settings
# ──────────────────────────────────────────────
st.sidebar.header(T["sidebar_header"])
annual_income = st.sidebar.number_input(
    T["annual_income_label"],
    min_value=0, max_value=500000, value=50000, step=5000,
    help=T["annual_income_help"]
)

# ──────────────────────────────────────────────
# MAIN INPUTS
# ──────────────────────────────────────────────
st.header(T["deal_inputs_header"])

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader(T["purchase_subheader"])
    buy_price = st.number_input(T["buy_price_label"], min_value=0, max_value=2000000,
                                value=250000, step=10000)
    reno_costs = st.number_input(T["reno_costs_label"], min_value=0, max_value=500000,
                                 value=50000, step=5000)
    st.markdown(T["vat_reclaim_header"])
    vat_reclaim_pct = st.slider(
        T["vat_reclaim_label"], 0, 100, 70, 5,
        help=T["vat_reclaim_help"]
    ) / 100

with col2:
    st.subheader(T["holding_subheader"])
    hold_years_input = st.number_input(T["hold_years_label"], min_value=0.0, max_value=30.0,
                                       value=5.0, step=0.5)
    hold_months = int(hold_years_input * 12)
    holding_costs_monthly = st.number_input(
        T["holding_costs_label"],
        min_value=0, max_value=10000, value=800, step=50,
        help=T["holding_costs_help"]
    )

with col3:
    st.subheader(T["exit_subheader"])
    strategy_options = [T["strategy_sell"], T["strategy_rent"], T["strategy_both"]]
    strategy_raw = st.radio(T["strategy_label"], strategy_options)

    # Map translated label back to internal key
    if strategy_raw == T["strategy_sell"]:
        scenario_type = "Sell"
    elif strategy_raw == T["strategy_rent"]:
        scenario_type = "Rent"
    else:
        scenario_type = "Compare Both"

    sell_price = 350000
    use_sell_makler = False
    eigennutzung = False
    monthly_rent = 1200
    vacancy_rate = 0.05

    if scenario_type in ["Sell", "Compare Both"]:
        sell_price = st.number_input(T["sell_price_label"], min_value=0, max_value=2000000,
                                     value=350000, step=10000)
        use_sell_makler = st.checkbox(T["makler_sell_label"], value=False)
        eigennutzung = st.checkbox(T["eigennutzung_label"], value=False,
                                   help=T["eigennutzung_help"])

    if scenario_type in ["Rent", "Compare Both"]:
        monthly_rent = st.number_input(T["monthly_rent_label"], min_value=0, max_value=20000,
                                       value=1200, step=50)
        vacancy_rate = st.slider(T["vacancy_label"], 0, 30, 5, 1,
                                 help=T["vacancy_help"]) / 100

# ──────────────────────────────────────────────
# CALCULATE
# ──────────────────────────────────────────────
if st.button(T["calc_button"], type="primary"):

    results = {}

    if scenario_type in ["Sell", "Compare Both"]:
        results["sell"] = calculate_sell_scenario(
            buy_price, reno_costs, holding_costs_monthly, hold_months,
            sell_price, vat_reclaim_pct, annual_income, use_sell_makler,
            eigennutzung=eigennutzung
        )

    if scenario_type in ["Rent", "Compare Both"]:
        results["rent"] = calculate_rent_scenario(
            buy_price, reno_costs, holding_costs_monthly, hold_months,
            monthly_rent, vacancy_rate, annual_income, vat_reclaim_pct
        )
        results["breakeven_months"] = calculate_breakeven_hold_period(
            buy_price, reno_costs, holding_costs_monthly,
            monthly_rent, vacancy_rate, annual_income, vat_reclaim_pct
        )

    # ── Results header ──────────────────────────
    st.markdown("---")
    st.header(T["results_header"])

    # ── SELL results ────────────────────────────
    if "sell" in results:
        st.subheader(T["sell_subheader"])
        sell = results["sell"]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric(T["gross_profit"], f"€{sell['gross_profit']:,.0f}")
        with c2:
            st.metric(T["net_profit"], f"€{sell['net_profit']:,.0f}",
                      delta=f"{sell['roi']:.1f}% ROI")
        with c3:
            if sell['hold_years'] < 10:
                st.metric(T["speculation_tax"], f"€{sell['speculation_tax']:,.0f}",
                          delta=f"{sell['spec_tax_rate']:.1f}%", delta_color="inverse")
            else:
                st.metric(T["speculation_tax"], "€0", delta=T["tax_free"], delta_color="normal")
        with c4:
            st.metric(T["annual_roi"], f"{sell['annual_roi']:.1f}%")

        with st.expander(T["sell_expander"]):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(T["acq_costs"])
                st.write(f"• Grunderwerbsteuer (6,5 %): €{sell['acquisition']['grunderwerbsteuer']:,.0f}")
                st.write(f"• Notar/Grundbuch (~1,5 %): €{sell['acquisition']['notar_grundbuch']:,.0f}")
                st.write(f"• Maklerprovision Kauf (3,57 %): €{sell['acquisition']['makler']:,.0f}")
                st.markdown(T["investment"])
                st.write(f"{T['buy_price_line']}: €{buy_price:,.0f}")
                st.write(f"{T['reno_line']}: €{reno_costs:,.0f}")
                st.write(f"{T['vat_line']}: -€{sell['vat_reclaim']:,.0f}")
                st.write(f"{T['holding_line']}: €{sell['holding_costs']:,.0f}")
                st.write(f"{T['total_investment_line']}: €{sell['total_investment']:,.0f}**")
            with c2:
                st.markdown(T["exit_label"])
                st.write(f"{T['sell_price_line']}: €{sell_price:,.0f}")
                st.write(f"{T['selling_costs_line']}: €{sell['selling_costs']:,.0f}")
                st.write(f"{T['gross_profit_line']}: €{sell['gross_profit']:,.0f}")
                st.write(f"{T['spec_tax_line']}: €{sell['speculation_tax']:,.0f}")
                st.write(f"{T['net_profit_line']}: €{sell['net_profit']:,.0f}**")

                st.markdown(T["tax_info"])
                if sell['hold_years'] < 10:
                    st.warning(T["spec_tax_warning"].format(years=sell['hold_years']))
                    st.write(T["spec_tax_rate_line"].format(rate=sell['spec_tax_rate']))
                else:
                    st.success(T["tax_free_success"].format(years=sell['hold_years']))

    # ── RENT results ────────────────────────────
    if "rent" in results:
        st.subheader(T["rent_subheader"])
        rent = results["rent"]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric(T["gross_yield"], f"{rent['gross_yield']:.2f}%")
        with c2:
            st.metric(T["net_yield"], f"{rent['net_yield']:.2f}%", help=T["net_yield_help"])
        with c3:
            st.metric(T["annual_cashflow"], f"€{rent['annual_cashflow']:,.0f}")
        with c4:
            st.metric(f"{T['total_cashflow_label']} ({rent['hold_years']:.1f}y)",
                      f"€{rent['total_cashflow']:,.0f}")

        if results.get("breakeven_months"):
            bm = results["breakeven_months"]
            st.info(T["breakeven_info"].format(months=bm, years=bm / 12))
        else:
            st.error(T["no_breakeven"])

        with st.expander(T["rent_expander"]):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(T["invest_same"])
                st.write(f"{T['total_invest_line']}: €{rent['total_investment']:,.0f}")
                st.write(f"{T['vat_reclaim_line']}: €{rent['vat_reclaim']:,.0f}")
                st.markdown(T["annual_income_section"])
                st.write(f"{T['gross_rent_line']}: €{rent['annual_rent_gross']:,.0f}")
                st.write(f"{T['op_costs_line']}: -€{rent['annual_operating_costs']:,.0f}")
                st.write(f"{T['holding_costs_line2']}: -€{rent['annual_holding_costs']:,.0f}")
                st.write(f"{T['net_rent_line']}: €{rent['annual_rent_net']:,.0f}")
            with c2:
                st.markdown(T["annual_tax_section"])
                st.write(f"{T['income_tax_line']}: -€{rent['annual_tax']:,.0f}")
                st.write(f"{T['annual_cashflow_line']}: €{rent['annual_cashflow']:,.0f}**")
                st.markdown(T["total_over"].format(years=rent['hold_years']))
                st.write(f"{T['total_cashflow_line']}: €{rent['total_cashflow']:,.0f}")
                st.markdown(T["yields_section"])
                st.write(f"{T['gross_yield_line']}: {rent['gross_yield']:.2f}%")
                st.write(f"{T['net_yield_line']}: {rent['net_yield']:.2f}%")

    # ── COMPARISON chart ────────────────────────
    if scenario_type == "Compare Both" and "sell" in results and "rent" in results:
        sell = results["sell"]
        rent = results["rent"]

        st.markdown("---")
        st.subheader(T["comparison_header"])

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name=T["sell_bar"],
            x=[T["bar_gross"], T["bar_aftertax"], T["bar_annual"]],
            y=[sell['gross_profit'], sell['net_profit'], sell['annual_roi'] * 10000],
            marker_color='rgb(55, 83, 109)'
        ))
        fig.add_trace(go.Bar(
            name=T["rent_bar"],
            x=[T["bar_total"], T["bar_cashflow"], T["bar_annual_cf"]],
            y=[rent['annual_rent_gross'] * rent['hold_years'],
               rent['total_cashflow'],
               rent['annual_cashflow']],
            marker_color='rgb(26, 118, 255)'
        ))
        fig.update_layout(
            title=T["chart_title"].format(years=hold_years_input),
            xaxis_title=T["chart_x"],
            yaxis_title=T["chart_y"],
            barmode='group',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # Quick verdict
        st.markdown(T["verdict_header"])
        c1, c2 = st.columns(2)
        with c1:
            if sell['net_profit'] > rent['total_cashflow']:
                st.success(T["sell_better"].format(profit=sell['net_profit']))
            else:
                st.info(T["sell_info"].format(profit=sell['net_profit']))
            if sell['hold_years'] >= 10:
                st.success(T["tax_free_sale"])
            else:
                st.warning(T["spec_tax_warn"].format(tax=sell['speculation_tax']))
        with c2:
            if rent['total_cashflow'] > sell['net_profit']:
                st.success(T["rent_better"].format(cf=rent['total_cashflow']))
            else:
                st.info(T["rent_info"].format(cf=rent['total_cashflow']))
            st.info(T["net_yield_info"].format(yield_=rent['net_yield']))
            if rent['net_yield'] >= 4:
                st.success(T["strong_yield"])
            elif rent['net_yield'] >= 2:
                st.warning(T["moderate_yield"])
            else:
                st.error(T["low_yield"])

    # ── Save scenario ────────────────────────────
    st.markdown("---")
    scenario_name = st.text_input(T["save_label"], placeholder=T["save_placeholder"])
    if scenario_name and st.button(T["save_button"]):
        st.session_state.scenarios[scenario_name] = {
            "inputs": {
                "buy_price": buy_price,
                "reno_costs": reno_costs,
                "holding_costs_monthly": holding_costs_monthly,
                "hold_months": hold_months,
                "sell_price": sell_price if scenario_type in ["Sell", "Compare Both"] else None,
                "monthly_rent": monthly_rent if scenario_type in ["Rent", "Compare Both"] else None,
                "vacancy_rate": vacancy_rate if scenario_type in ["Rent", "Compare Both"] else None,
                "vat_reclaim_pct": vat_reclaim_pct,
                "annual_income": annual_income,
                "use_sell_makler": use_sell_makler if scenario_type in ["Sell", "Compare Both"] else False
            },
            "results": results,
            "created": datetime.now().isoformat()
        }
        save_scenarios(st.session_state.scenarios)
        st.success(T["save_success"].format(name=scenario_name))

# ──────────────────────────────────────────────
# SAVED SCENARIOS TABLE
# ──────────────────────────────────────────────
if st.session_state.scenarios:
    st.markdown("---")
    st.header(T["saved_header"])

    scenarios_df = pd.DataFrame([
        {
            T["col_name"]: name,
            T["col_buy"]: f"€{data['inputs']['buy_price']:,.0f}",
            T["col_sell"]: f"€{data['inputs']['sell_price']:,.0f}" if data['inputs'].get('sell_price') else T["na"],
            T["col_rent"]: f"€{data['inputs']['monthly_rent']:,.0f}/mo" if data['inputs'].get('monthly_rent') else T["na"],
            T["col_net_profit"]: f"€{data['results']['sell']['net_profit']:,.0f}" if 'sell' in data['results'] else T["na"],
            T["col_cashflow"]: f"€{data['results']['rent']['annual_cashflow']:,.0f}/yr" if 'rent' in data['results'] else T["na"],
            T["col_created"]: data['created'][:10]
        }
        for name, data in st.session_state.scenarios.items()
    ])

    st.dataframe(scenarios_df, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(T["footer"])
