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
        "spec_tax_rate_note": "Berechnet progressiv auf Basis von Jahreseinkommen + Veräußerungsgewinn; weicht daher vom eingestellten Grenzsteuersatz ab.",
        "loss_restriction_note": "Kein steuerpflichtiger Gewinn — keine Spekulationssteuer fällig. Verlustverrechnung ist nach § 23 EStG nur mit anderen privaten Veräußerungsgewinnen möglich, nicht mit sonstigem Einkommen (hier nicht berücksichtigt).",
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
        # AfA Section
        "afa_header": "📉 AfA & Steuerliche Abschreibung",
        "afa_subheader": "Absetzung für Abnutzung (§ 7 EStG)",
        "construction_year_label": "Baujahr / Fertigstellungsjahr",
        "construction_year_help": "Jahr der Fertigstellung des Gebäudes (bestimmt den AfA-Satz)",
        "acquisition_year_label": "Kaufjahr",
        "acquisition_year_help": "Jahr des Erwerbs (für anteilige AfA im ersten Jahr)",
        "acquisition_month_label": "Kaufmonat",
        "acquisition_month_help": "Monat des Erwerbs (für präzise anteilige AfA-Berechnung)",
        "land_value_label": "Grundstückswert (€)",
        "land_value_help": "Wert des Grundstücks (nicht abschreibbar). Leer lassen für automatische Aufteilung (20 % Land / 80 % Gebäude)",
        "land_percentage_label": "Grundstück-Anteil (%)",
        "land_percentage_help": "Automatische Aufteilung: X % Land, (100-X) % Gebäude",
        "denkmal_costs_label": "Denkmal-AfA-fähige Sanierungskosten (€)",
        "denkmal_costs_help": "Zertifizierte Renovierungskosten für Denkmal-AfA (9% für 8 Jahre, dann 7% für 4 Jahre)",
        "custom_nutzungsdauer_label": "Individuelle Nutzungsdauer per Gutachten geltend machen (§ 7 Abs. 4 Satz 2 EStG)",
        "custom_nutzungsdauer_help": "Der Steuerpflichtige trägt die Nachweislast für eine kürzere tatsächliche Nutzungsdauer (BFH IX R 14/23). Das Finanzamt kann ein methodisch nachvollziehbares Gutachten nicht pauschal ablehnen, prüft aber im Einzelfall.",
        "gutachten_year_label": "Jahr der Gutachten-Anerkennung",
        "gutachten_year_help": "Jahr, in dem das Gutachten vom Finanzamt anerkannt wurde (muss ≥ Kaufjahr)",
        "gutachten_restnutzungsdauer_label": "Vom Gutachten festgestellte Restnutzungsdauer (Jahre)",
        "gutachten_restnutzungsdauer_help": "Restnutzungsdauer laut Gutachten, ab dem Anerkennungsjahr",
        "gutachten_year_error": "Fehler: Das Gutachten-Anerkennungsjahr muss ≥ Kaufjahr sein.",
        "gutachten_duration_error": "Fehler: Die Restnutzungsdauer muss > 0 Jahre betragen.",
        "afa_basis_standard": "Standard",
        "afa_basis_gutachten": "Gutachten",
        "custom_nutzungsdauer_summary": "AfA-Basis ab {year}: Restnutzungsdauer {duration} Jahre lt. Gutachten (statt {original} Jahre Standard).",
        "marginal_tax_rate_label": "Grenzsteuersatz (%)",
        "marginal_tax_rate_help": "Dein persönlicher Grenzsteuersatz für Steuerschild-Berechnung (Standard: 42% + Soli)",
        "use_afa_label": "AfA im Mietrendite-Cashflow anzeigen",
        "use_afa_help": "AfA wird im Mietrendite-Cashflow berücksichtigt (mindert das zu versteuernde Einkommen). Bei Verkauf wird AfA-Rückgängigmachung immer berechnet, wenn AfA aktiv ist.",
        "afa_rate_info": "AfA-Satz nach Baujahr: Vor 1925: 2,5 % | 1925-2022: 2 % | Ab 2023: 3 %",
        "denkmal_afa_info": "Denkmal-AfA: 9% p.a. für 8 Jahre, dann 7% für 4 Jahre auf zertifizierte Sanierungskosten",
        "annual_afa_table": "Jährliche AfA-Aufschlüsselung",
        "year_col": "Jahr",
        "normal_afa_col": "Normale AfA (€)",
        "denkmal_afa_col": "Denkmal-AfA (€)",
        "total_afa_col": "Gesamt AfA (€)",
        "cumulative_afa_col": "Kumulative AfA (€)",
        "tax_shield_col": "Steuerschild (€)",
        "book_value_col": "Restbuchwert (€)",
        "basis_col": "Basis",
        "total_afa_claimed": "Gesamt AfA geltend gemacht",
        "total_tax_shield": "Gesamter Steuervorteil",
        "remaining_book_value": "Verbleibender Buchwert",
        "afa_recapture": "AfA-Rückgängigmachung (bei Verkauf)",
        "afa_recapture_info": "Bei Verkauf: Alle bisherigen AfA-Beträge werden dem steuerpflichtigen Gewinn wieder hinzugerechnet",
        "gross_sale_profit": "Brutto-Verkaufsgewinn",
        "afa_recapture_amount": "+ AfA-Rückgängigmachung",
        "taxable_gain_after_recapture": "Steuerpflichtiger Gewinn nach Rückgängigmachung",
        "final_tax_on_sale": "Steuer auf Verkauf (inkl. AfA-Rückgängigmachung)",
        "building_value": "Gebäudewert",
        "total_normal_afa": "Gesamt Normale AfA",
        "total_denkmal_afa": "Gesamt Denkmal-AfA",
        "remaining_book_value_at_sale": "Restbuchwert bei Verkauf",
        "afa_benefit_rental": "AfA-Vorteil (Vermietung)",
        "annual_afa_tax_benefit": "Jährlicher AfA-Steuervorteil",
        "enhanced_cashflow": "Verbesserter Cashflow",
        "afa_disclaimer": "⚠️ Dies ist eine vereinfachte AfA-Berechnung nach § 7 EStG. Für verbindliche Aussagen bitte einen Steuerberater konsultieren.",
        # Compliance Section
        "properties_sold_label": "Anzahl verkaufter Immobilien in den letzten 5 Jahren (inkl. dieser)",
        "properties_sold_help": "Für Prüfung auf gewerblichen Grundstückshandel (Drei-Objekte-Grenze)",
        "vat_option_label": "Umsatzsteuer-Option aktiv (§ 9 UStG)",
        "vat_option_help": "Vorsteuerabzug nur bei Umsatzsteuer-Option möglich (z. B. gewerbliche Vermietung)",
        "vat_tooltip": "Vorsteuerabzug ist nur möglich, wenn Sie zur Umsatzsteuer optieren (§ 9 UStG) — z. B. bei gewerblicher/umsatzsteuerpflichtiger Vermietung. Bei einem privaten Verkauf oder normaler Wohnraumvermietung entfällt der Vorsteuerabzug in der Regel.",
        "soli_note": "Standardwert 42% + Soli entspricht dem oberen Steuerbereich. Solidaritätszuschlag fällt seit 2021 nur oberhalb einer bestimmten Einkommensgrenze an — bitte individuellen Satz prüfen.",
        "anschaffungsnahe_warning": "⚠️ Anschaffungsnahe Herstellungskosten: Renovierungskosten übersteigen 15% des Gebäudewerts innerhalb von 3 Jahren nach Kauf.",
        "anschaffungsnahe_info": "In diesem Fall müssen Renovierungskosten nicht als sofort abzugsfähige Werbungskosten behandelt werden, sondern in die Anschaffungskosten/Herstellungskosten kapitalisiert und über AfA abgeschrieben werden.",
        "anschaffungsnahe_percentage": "Renovierungskosten / Gebäudewert: {percentage:.1f}%",
        "gewerblich_warning": "⚠️ Risiko: Gewerblicher Grundstückshandel. Bei 3 oder mehr Objektverkäufen innerhalb von 5 Jahren kann das Finanzamt die Tätigkeit als gewerblich einstufen. Folge: Kein steuerfreier Verkauf nach 10 Jahren, zusätzlich Gewerbesteuer, laufende Buchführungspflicht.",
        "compliance_disclaimer": "Dies ist eine vereinfachte Berechnung ohne Berücksichtigung individueller Umstände (z. B. Gewerblicher Grundstückshandel, anschaffungsnahe Herstellungskosten, Kirchensteuer, Verlustverrechnung). Für verbindliche Aussagen einen Steuerberater konsultieren.",
        # Footer
        "footer": """
💡 **Steuerhinweise (Stand April 2026):**
- Grunderwerbsteuer: 6,5 % in NRW
- Spekulationssteuer: fällig bei Verkauf < 10 Jahre (progressiv bis 45 % + Soli)
- Eigennutzung-Ausnahme: Bei Selbstnutzung im Verkaufsjahr + den beiden Vorjahren ist der Verkauf steuerfrei (auch < 10 Jahre)
- Vorsteuerabzug: 19 % auf ordnungsgemäß fakturierte Renovierungskosten
- Mieteinkünfte: Werden dem Jahreseinkommen zugerechnet und progressiv besteuert
- AfA (Absetzung für Abnutzung): Lineare AfA nach Baujahr: Vor 1925: 2,5 % (40 Jahre), 1925-2022: 2 % (50 Jahre), Ab 2023: 3 % (≈33,3 Jahre)
- AfA-Rückgängigmachung: Bei Verkauf werden alle geltend gemachten AfA-Beträge dem steuerpflichtigen Gewinn wieder hinzugerechnet

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
        "spec_tax_rate_note": "Calculated progressively based on annual income + capital gain; therefore differs from the set marginal tax rate.",
        "loss_restriction_note": "No taxable profit — no speculation tax due. Loss offset is only possible with other private sales gains under § 23 EStG, not with other income (not considered here).",
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
        # AfA Section
        "afa_header": "📉 AfA & Tax Depreciation",
        "afa_subheader": "Depreciation Allowance (§ 7 EStG)",
        "construction_year_label": "Construction / Completion Year",
        "construction_year_help": "Year the building was completed (determines AfA rate)",
        "acquisition_year_label": "Acquisition Year",
        "acquisition_year_help": "Year of purchase (for pro-rata AfA in first year)",
        "acquisition_month_label": "Acquisition Month",
        "acquisition_month_help": "Month of purchase (for precise pro-rata AfA calculation)",
        "land_value_label": "Land Value (€)",
        "land_value_help": "Value of the land (not depreciable). Leave blank for automatic split (20% land / 80% building)",
        "land_percentage_label": "Land Percentage (%)",
        "land_percentage_help": "Automatic split: X% land, (100-X)% building",
        "denkmal_costs_label": "Denkmal-AfA Eligible Renovation Costs (€)",
        "denkmal_costs_help": "Certified renovation costs for Denkmal-AfA (9% for 8 years, then 7% for 4 years)",
        "custom_nutzungsdauer_label": "Claim individual useful life per expert appraisal (§ 7 Abs. 4 Satz 2 EStG)",
        "custom_nutzungsdauer_help": "The taxpayer bears the burden of proof for a shorter actual useful life (BFH IX R 14/23). The tax office cannot reject a methodologically comprehensible expert opinion outright, but examines it on a case-by-case basis.",
        "gutachten_year_label": "Year of Expert Appraisal Recognition",
        "gutachten_year_help": "Year when the expert appraisal was recognized by the tax office (must be ≥ acquisition year)",
        "gutachten_restnutzungsdauer_label": "Remaining useful life determined by expert appraisal (years)",
        "gutachten_restnutzungsdauer_help": "Remaining useful life per expert appraisal, from the recognition year",
        "gutachten_year_error": "Error: The expert appraisal recognition year must be ≥ acquisition year.",
        "gutachten_duration_error": "Error: The remaining useful life must be > 0 years.",
        "afa_basis_standard": "Standard",
        "afa_basis_gutachten": "Expert",
        "custom_nutzungsdauer_summary": "AfA basis from {year}: Remaining useful life {duration} years per expert appraisal (instead of {original} years standard).",
        "marginal_tax_rate_label": "Marginal Tax Rate (%)",
        "marginal_tax_rate_help": "Your personal marginal tax rate for tax shield calculation (default: 42% + Soli)",
        "use_afa_label": "Show AfA in rental cashflow",
        "use_afa_help": "AfA is factored into rental cashflow (reduces taxable income). AfA recapture on sale is always calculated when AfA is active.",
        "afa_rate_info": "AfA rate by construction year: Before 1925: 2.5% | 1925-2022: 2% | From 2023: 3%",
        "denkmal_afa_info": "Denkmal-AfA: 9% p.a. for 8 years, then 7% for 4 years on certified renovation costs",
        "annual_afa_table": "Annual AfA Breakdown",
        "year_col": "Year",
        "normal_afa_col": "Normal AfA (€)",
        "denkmal_afa_col": "Denkmal-AfA (€)",
        "total_afa_col": "Total AfA (€)",
        "cumulative_afa_col": "Cumulative AfA (€)",
        "tax_shield_col": "Tax Shield (€)",
        "book_value_col": "Remaining Book Value (€)",
        "basis_col": "Basis",
        "total_afa_claimed": "Total AfA Claimed",
        "total_tax_shield": "Total Tax Shield",
        "remaining_book_value": "Remaining Book Value",
        "afa_recapture": "AfA Recapture (on sale)",
        "afa_recapture_info": "On sale: All previously claimed AfA amounts are added back to taxable gain",
        "gross_sale_profit": "Gross Sale Profit",
        "afa_recapture_amount": "+ AfA Recapture",
        "taxable_gain_after_recapture": "Taxable Gain After Recapture",
        "final_tax_on_sale": "Tax on Sale (incl. AfA recapture)",
        "building_value": "Building Value",
        "total_normal_afa": "Total Normal AfA",
        "total_denkmal_afa": "Total Denkmal-AfA",
        "remaining_book_value_at_sale": "Remaining Book Value at Sale",
        "afa_benefit_rental": "AfA Benefit (Rental)",
        "annual_afa_tax_benefit": "Annual AfA Tax Benefit",
        "enhanced_cashflow": "Enhanced Cashflow",
        "afa_disclaimer": "⚠️ This is a simplified AfA calculation per § 7 EStG. Consult a tax advisor for binding advice.",
        # Compliance Section
        "properties_sold_label": "Number of properties sold in last 5 years (including this one)",
        "properties_sold_help": "For checking commercial property trading (three-object limit)",
        "vat_option_label": "VAT Option Active (§ 9 UStG)",
        "vat_option_help": "VAT deduction only possible with VAT option (e.g., commercial rental)",
        "vat_tooltip": "VAT deduction is only possible if you opt for VAT (§ 9 UStG) — e.g., for commercial/VAT-liable rental. For private sales or normal residential rental, VAT deduction generally does not apply.",
        "soli_note": "Default value 42% + Soli corresponds to the upper tax bracket. Solidarity surcharge only applies above a certain income threshold since 2021 — please check individual rate.",
        "anschaffungsnahe_warning": "⚠️ Acquisition-related production costs: Renovation costs exceed 15% of building value within 3 years of purchase.",
        "anschaffungsnahe_info": "In this case, renovation costs must not be treated as immediately deductible business expenses, but must be capitalized into acquisition/production costs and depreciated via AfA.",
        "anschaffungsnahe_percentage": "Renovation costs / Building value: {percentage:.1f}%",
        "gewerblich_warning": "⚠️ Risk: Commercial property trading. With 3 or more property sales within 5 years, the tax office may reclassify the activity as commercial. Consequence: No tax-free sale after 10 years, additional trade tax, ongoing bookkeeping requirement.",
        "compliance_disclaimer": "This is a simplified calculation without considering individual circumstances (e.g., commercial property trading, acquisition-related production costs, church tax, loss offset). Consult a tax advisor for binding advice.",
        # Footer
        "footer": """
💡 **Tax Notes (as of April 2026):**
- Grunderwerbsteuer: 6.5% in NRW
- Speculation tax: due if sold <10 years (progressive up to 45% + Soli)
- Owner-occupancy exception: tax-free sale if self-used in year of sale + 2 prior years (even <10 years, per § 23 EStG)
- VAT reclaim: 19% on properly invoiced renovation costs
- Rental income: added to annual income and taxed progressively
- AfA (Depreciation): Linear AfA by construction year: Before 1925: 2.5% (40 years), 1925-2022: 2% (50 years), From 2023: 3% (≈33.3 years)
- AfA Recapture: On sale, all claimed AfA amounts are added back to taxable gain

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
    if profit <= 0:
        # Losses can't offset ordinary income under § 23 EStG loss-restriction rules
        return 0, 0
    tax_without_profit = calculate_income_tax(annual_income)
    tax_with_profit = calculate_income_tax(annual_income + profit)
    speculation_tax = tax_with_profit - tax_without_profit
    # Effective rate is always based on a positive profit here, since losses are already handled above
    effective_rate = (speculation_tax / abs(profit) * 100) if profit != 0 else 0
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

def check_anschaffungsnahe_herstellungskosten(buy_price, land_value, land_percentage, 
                                              reno_costs, vat_option_active, vat_rate=0.19):
    """
    Check if renovation costs exceed 15% of building value within 3 years of purchase (§ 6 Abs. 1 Nr. 1a EStG).
    
    Returns:
        Dictionary with check results
    """
    # Calculate building value
    if land_value is not None and land_value > 0:
        building_value = buy_price - land_value
    else:
        land_value_final = buy_price * (land_percentage / 100)
        building_value = buy_price - land_value_final
    
    if building_value <= 0:
        return {
            "is_anschaffungsnahe": False,
            "percentage": 0,
            "threshold_exceeded": False,
            "building_value": 0,
            "reno_costs_net": 0
        }
    
    # Calculate renovation costs net of VAT
    if vat_option_active:
        reno_costs_net = reno_costs * (1 - vat_rate)
    else:
        reno_costs_net = reno_costs
    
    # Calculate percentage
    percentage = (reno_costs_net / building_value) * 100 if building_value > 0 else 0
    
    # Check if threshold exceeded (15%)
    threshold_exceeded = percentage > 15
    
    return {
        "is_anschaffungsnahe": threshold_exceeded,
        "percentage": percentage,
        "threshold_exceeded": threshold_exceeded,
        "building_value": building_value,
        "reno_costs_net": reno_costs_net,
        "threshold": 15
    }

def check_gewerblicher_grundstueckshandel(properties_sold_5y, hold_years):
    """
    Check for commercial property trading risk (Drei-Objekte-Grenze).
    
    Returns:
        Dictionary with check results
    """
    is_gewerblich = properties_sold_5y >= 3 and hold_years <= 5
    
    return {
        "is_gewerblich": is_gewerblich,
        "properties_sold": properties_sold_5y,
        "hold_years": hold_years,
        "threshold": 3,
        "hold_threshold": 5
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
# AfA (DEPRECIATION) FUNCTIONS
# ──────────────────────────────────────────────
def get_afa_rate(construction_year):
    """
    Determine linear AfA rate based on construction year (§ 7 EStG 2026 rules)
    Returns: (rate as decimal, useful life in years, description)
    """
    if construction_year < 1925:
        return 0.025, 40, "2.5% (40 Jahre, vor 1925)"
    elif construction_year <= 2022:
        return 0.02, 50, "2% (50 Jahre, 1925-2022)"
    else:
        return 0.03, 33.33, "3% (≈33,3 Jahre, ab 2023)"

def calculate_afa_schedule(total_purchase_price, land_value, land_percentage,
                           construction_year, acquisition_year, acquisition_month,
                           denkmal_costs, marginal_tax_rate, hold_years,
                           annual_income, use_afa=True,
                           custom_nutzungsdauer_active=False,
                           gutachten_year=None,
                           gutachten_restnutzungsdauer=None):
    """
    Calculate annual AfA schedule with pro-rating for partial years.
    Handles both normal linear AfA and Denkmal-AfA separately.
    Supports custom useful life based on expert appraisal (§ 7 Abs. 4 Satz 2 EStG).
    
    Args:
        total_purchase_price: Total purchase price
        land_value: Explicit land value (or None for automatic split)
        land_percentage: Land percentage for automatic split (default 20%)
        construction_year: Year building was completed
        acquisition_year: Year of acquisition
        acquisition_month: Month of acquisition (1-12)
        denkmal_costs: Certified renovation costs for Denkmal-AfA
        marginal_tax_rate: User's marginal tax rate (as percentage)
        hold_years: Holding period in years
        annual_income: User's annual income for tax shield calculation
        use_afa: Whether to include AfA in calculations
        custom_nutzungsdauer_active: Whether to use custom useful life from expert appraisal
        gutachten_year: Year when expert appraisal was recognized
        gutachten_restnutzungsdauer: Remaining useful life per expert appraisal (years)
    
    Returns:
        Dictionary with AfA schedule and summary
    """
    if not use_afa:
        return {
            "use_afa": False,
            "annual_schedule": [],
            "total_normal_afa": 0,
            "total_denkmal_afa": 0,
            "total_afa_claimed": 0,
            "total_tax_shield": 0,
            "remaining_book_value": 0,
            "building_value": 0,
            "land_value": 0,
            "denkmal_value": 0,
            "afa_rate": 0,
            "afa_description": "AfA deaktiviert"
        }
    
    # Determine building value and land value
    if land_value is not None and land_value > 0:
        # Explicit land value provided
        building_value = total_purchase_price - land_value
        land_value_final = land_value
    else:
        # Automatic split based on percentage
        land_value_final = total_purchase_price * (land_percentage / 100)
        building_value = total_purchase_price - land_value_final
    
    # Get normal AfA rate
    afa_rate, useful_life, afa_description = get_afa_rate(construction_year)
    
    # Calculate annual normal AfA (full year)
    annual_normal_afa = building_value * afa_rate
    
    # Denkmal-AfA calculation (9% for 8 years, 7% for 4 years)
    denkmal_value = denkmal_costs
    annual_denkmal_afa_phase1 = denkmal_value * 0.09  # 9% for first 8 years
    annual_denkmal_afa_phase2 = denkmal_value * 0.07  # 7% for next 4 years
    
    # Calculate months in first year (acquisition year)
    months_first_year = 12 - acquisition_month + 1  # e.g., July = month 7, so 6 months (July-Dec)
    
    # Calculate months in last year (if holding period is not integer)
    months_last_year = ((hold_years - int(hold_years)) * 12)
    
    # Generate annual schedule
    schedule = []
    total_normal_afa = 0
    total_denkmal_afa = 0
    total_afa_claimed = 0
    remaining_book_value = building_value
    remaining_denkmal_value = denkmal_value
    cumulative_afa = 0
    
    # Convert marginal tax rate to decimal
    marginal_rate_decimal = marginal_tax_rate / 100 if marginal_tax_rate > 0 else 0.42
    
    # Custom useful life from expert appraisal
    custom_annual_afa = None
    custom_nutzungsdauer_active_year = None
    if custom_nutzungsdauer_active and gutachten_year is not None and gutachten_restnutzungsdauer is not None:
        if gutachten_year >= acquisition_year:
            custom_nutzungsdauer_active_year = gutachten_year - acquisition_year
    
    for year_offset in range(int(hold_years) + 1):
        year = acquisition_year + year_offset
        afa_basis = "Standard"
        
        # Check if we need to switch to custom useful life this year
        if custom_nutzungsdauer_active and year_offset == custom_nutzungsdauer_active_year:
            # Switch to custom useful life based on expert appraisal
            custom_annual_afa = remaining_book_value / gutachten_restnutzungsdauer
            afa_basis = "Gutachten"
        
        # Calculate normal AfA for this year
        if custom_nutzungsdauer_active and year_offset >= custom_nutzungsdauer_active_year and custom_annual_afa is not None:
            # Use custom annual AfA from expert appraisal
            if year_offset == custom_nutzungsdauer_active_year:
                # First year of custom AfA - pro-rate if needed
                normal_afa_this_year = custom_annual_afa * (months_first_year / 12) if year_offset == 0 else custom_annual_afa
            elif year_offset < hold_years:
                normal_afa_this_year = custom_annual_afa
            else:
                # Partial final year if holding period is not integer
                if months_last_year > 0:
                    normal_afa_this_year = custom_annual_afa * (months_last_year / 12)
                else:
                    normal_afa_this_year = 0
            afa_basis = "Gutachten"
        else:
            # Use standard AfA rate
            if year_offset == 0:
                # First year (acquisition year) - pro-rated by month
                normal_afa_this_year = annual_normal_afa * (months_first_year / 12)
            elif year_offset < hold_years:
                # Full years
                normal_afa_this_year = annual_normal_afa
            else:
                # Partial final year if holding period is not integer
                if months_last_year > 0:
                    normal_afa_this_year = annual_normal_afa * (months_last_year / 12)
                else:
                    normal_afa_this_year = 0
            afa_basis = "Standard"
        
        # Don't exceed remaining book value for normal AfA
        if normal_afa_this_year > remaining_book_value:
            normal_afa_this_year = remaining_book_value
        
        # Calculate Denkmal-AfA for this year
        denkmal_afa_this_year = 0
        if denkmal_value > 0 and year_offset <= 11:  # Max 12 years (8 + 4)
            if year_offset < 8:
                # Phase 1: 9% for first 8 years
                if year_offset == 0:
                    denkmal_afa_this_year = annual_denkmal_afa_phase1 * (months_first_year / 12)
                elif year_offset < hold_years:
                    denkmal_afa_this_year = annual_denkmal_afa_phase1
                else:
                    if months_last_year > 0:
                        denkmal_afa_this_year = annual_denkmal_afa_phase1 * (months_last_year / 12)
            elif year_offset < 12:
                # Phase 2: 7% for next 4 years
                if year_offset < hold_years:
                    denkmal_afa_this_year = annual_denkmal_afa_phase2
                else:
                    if months_last_year > 0:
                        denkmal_afa_this_year = annual_denkmal_afa_phase2 * (months_last_year / 12)
        
        # Don't exceed remaining Denkmal value
        if denkmal_afa_this_year > remaining_denkmal_value:
            denkmal_afa_this_year = remaining_denkmal_value
        
        # Total AfA for this year
        total_afa_this_year = normal_afa_this_year + denkmal_afa_this_year
        
        # Calculate tax shield using marginal tax rate
        tax_shield = total_afa_this_year * marginal_rate_decimal
        
        # Update book values
        remaining_book_value -= normal_afa_this_year
        if remaining_book_value < 0:
            remaining_book_value = 0
        
        remaining_denkmal_value -= denkmal_afa_this_year
        if remaining_denkmal_value < 0:
            remaining_denkmal_value = 0
        
        # Update cumulative totals
        total_normal_afa += normal_afa_this_year
        total_denkmal_afa += denkmal_afa_this_year
        total_afa_claimed += total_afa_this_year
        cumulative_afa += total_afa_this_year
        
        schedule.append({
            "year": year,
            "normal_afa": normal_afa_this_year,
            "denkmal_afa": denkmal_afa_this_year,
            "total_afa": total_afa_this_year,
            "cumulative_afa": cumulative_afa,
            "tax_shield": tax_shield,
            "book_value": remaining_book_value,
            "afa_basis": afa_basis
        })
    
    # Calculate total tax shield
    total_tax_shield = sum(item["tax_shield"] for item in schedule)
    
    return {
        "use_afa": True,
        "annual_schedule": schedule,
        "total_normal_afa": total_normal_afa,
        "total_denkmal_afa": total_denkmal_afa,
        "total_afa_claimed": total_afa_claimed,
        "total_tax_shield": total_tax_shield,
        "remaining_book_value": remaining_book_value,
        "building_value": building_value,
        "land_value": land_value_final,
        "denkmal_value": denkmal_value,
        "afa_rate": afa_rate,
        "afa_description": afa_description,
        "custom_nutzungsdauer_active": custom_nutzungsdauer_active,
        "gutachten_year": gutachten_year,
        "gutachten_restnutzungsdauer": gutachten_restnutzungsdauer,
        "useful_life_original": useful_life
    }

def calculate_sell_scenario_with_afa(buy_price, reno_costs, holding_costs_monthly, hold_months,
                                     sell_price, vat_reclaim_pct, annual_income, use_sell_makler,
                                     eigennutzung=False, afa_schedule=None):
    """
    Calculate sell scenario with AfA recapture integration.
    
    Args:
        afa_schedule: AfA schedule from calculate_afa_schedule (optional)
    
    Returns:
        Enhanced sell scenario results with AfA recapture
    """
    # Base calculation
    result = calculate_sell_scenario(
        buy_price, reno_costs, holding_costs_monthly, hold_months,
        sell_price, vat_reclaim_pct, annual_income, use_sell_makler,
        eigennutzung=eigennutzung
    )
    
    # Add AfA recapture if schedule provided
    if afa_schedule and afa_schedule["use_afa"]:
        total_afa_claimed = afa_schedule["total_afa_claimed"]
        total_normal_afa = afa_schedule["total_normal_afa"]
        total_denkmal_afa = afa_schedule["total_denkmal_afa"]
        
        # AfA recapture: add back all claimed AfA (normal + Denkmal) to taxable gain
        # This is done by adjusting the gross profit for tax calculation
        original_gross_profit = result["gross_profit"]
        
        # Taxable gain with AfA recapture
        taxable_gain_with_recapture = original_gross_profit + total_afa_claimed
        
        # Recalculate speculation tax with recapture
        hold_years = hold_months / 12
        if eigennutzung or hold_years >= 10:
            speculation_tax_with_recapture = 0
            spec_tax_rate_with_recapture = 0
        elif taxable_gain_with_recapture <= 0:
            # Losses can't offset ordinary income under § 23 EStG loss-restriction rules
            speculation_tax_with_recapture = 0
            spec_tax_rate_with_recapture = 0
        else:
            tax_without = calculate_income_tax(annual_income)
            tax_with = calculate_income_tax(annual_income + taxable_gain_with_recapture)
            speculation_tax_with_recapture = tax_with - tax_without
            # Effective rate is always based on a positive taxable gain here, since losses are already handled above
            spec_tax_rate_with_recapture = (speculation_tax_with_recapture / abs(taxable_gain_with_recapture) * 100) if taxable_gain_with_recapture != 0 else 0
        
        # Update result with AfA information
        result["afa"] = {
            "total_normal_afa": total_normal_afa,
            "total_denkmal_afa": total_denkmal_afa,
            "total_afa_claimed": total_afa_claimed,
            "afa_recapture_amount": total_afa_claimed,
            "original_gross_profit": original_gross_profit,
            "taxable_gain_with_recapture": taxable_gain_with_recapture,
            "speculation_tax_with_recapture": speculation_tax_with_recapture,
            "spec_tax_rate_with_recapture": spec_tax_rate_with_recapture,
            "net_profit_with_recapture": original_gross_profit - speculation_tax_with_recapture,
            "remaining_book_value": afa_schedule["remaining_book_value"]
        }
        
        # Update main profit figures to reflect AfA recapture
        result["speculation_tax"] = speculation_tax_with_recapture
        result["spec_tax_rate"] = spec_tax_rate_with_recapture
        result["net_profit"] = result["afa"]["net_profit_with_recapture"]
        result["roi"] = (result["net_profit"] / result["total_investment"] * 100) if result["total_investment"] > 0 else 0
        result["annual_roi"] = (result["roi"] / hold_years) if hold_years > 0 else 0
    else:
        result["afa"] = None
    
    return result

def calculate_rent_scenario_with_afa(buy_price, reno_costs, holding_costs_monthly, hold_months,
                                      monthly_rent, vacancy_rate, annual_income, vat_reclaim_pct,
                                      afa_schedule=None):
    """
    Calculate rent scenario with AfA tax shield integration.
    
    Args:
        afa_schedule: AfA schedule from calculate_afa_schedule (optional)
    
    Returns:
        Enhanced rent scenario results with AfA tax benefits
    """
    # Base calculation
    result = calculate_rent_scenario(
        buy_price, reno_costs, holding_costs_monthly, hold_months,
        monthly_rent, vacancy_rate, annual_income, vat_reclaim_pct
    )
    
    # Add AfA tax shield if schedule provided
    if afa_schedule and afa_schedule["use_afa"]:
        hold_years = hold_months / 12
        
        # Calculate annual AfA tax shield
        # For simplicity distribute total tax shield evenly over holding period
        total_tax_shield = afa_schedule["total_tax_shield"]
        annual_tax_shield = total_tax_shield / hold_years if hold_years > 0 else 0
        
        # Adjust annual cashflow with AfA tax shield
        original_annual_cashflow = result["annual_cashflow"]
        enhanced_annual_cashflow = original_annual_cashflow + annual_tax_shield
        
        # Recalculate totals
        enhanced_total_cashflow = enhanced_annual_cashflow * hold_years
        
        # Recalculate yields with enhanced cashflow
        enhanced_net_yield = (enhanced_annual_cashflow / result["total_investment"] * 100) if result["total_investment"] > 0 else 0
        
        # Update result with AfA information
        result["afa"] = {
            "total_normal_afa": afa_schedule["total_normal_afa"],
            "total_denkmal_afa": afa_schedule["total_denkmal_afa"],
            "total_afa_claimed": afa_schedule["total_afa_claimed"],
            "total_tax_shield": total_tax_shield,
            "annual_tax_shield": annual_tax_shield,
            "original_annual_cashflow": original_annual_cashflow,
            "enhanced_annual_cashflow": enhanced_annual_cashflow,
            "remaining_book_value": afa_schedule["remaining_book_value"],
            "building_value": afa_schedule["building_value"],
            "land_value": afa_schedule["land_value"],
            "denkmal_value": afa_schedule["denkmal_value"],
            "afa_rate": afa_schedule["afa_rate"],
            "afa_description": afa_schedule["afa_description"]
        }
        
        # Update main cashflow figures to reflect AfA benefits
        result["annual_cashflow"] = enhanced_annual_cashflow
        result["total_cashflow"] = enhanced_total_cashflow
        result["net_yield"] = enhanced_net_yield
    else:
        result["afa"] = None
    
    return result

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
    vat_option_active = st.checkbox(
        T["vat_option_label"], value=False,
        help=T["vat_option_help"]
    )
    if vat_option_active:
        vat_reclaim_pct = st.slider(
            T["vat_reclaim_label"], 0, 100, 70, 5,
            help=T["vat_tooltip"]
        ) / 100
    else:
        vat_reclaim_pct = 0
        st.info(T["vat_tooltip"])

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
# AfA INPUTS
# ──────────────────────────────────────────────
st.markdown("---")
st.header(T["afa_header"])
st.markdown(T["afa_subheader"])

col_afa1, col_afa2, col_afa3 = st.columns(3)

with col_afa1:
    construction_year = st.number_input(
        T["construction_year_label"],
        min_value=1800, max_value=2030, value=1990, step=1,
        help=T["construction_year_help"]
    )
    acquisition_year = st.number_input(
        T["acquisition_year_label"],
        min_value=2000, max_value=2030, value=2024, step=1,
        help=T["acquisition_year_help"]
    )
    acquisition_month = st.selectbox(
        T["acquisition_month_label"],
        options=list(range(1, 13)),
        index=6,  # July (month 7) as default
        help=T["acquisition_month_help"]
    )

with col_afa2:
    land_value = st.number_input(
        T["land_value_label"],
        min_value=0, max_value=1000000, value=0, step=5000,
        help=T["land_value_help"]
    )
    land_percentage = st.slider(
        T["land_percentage_label"], 0, 100, 20, 1,
        help=T["land_percentage_help"]
    )
    denkmal_costs = st.number_input(
        T["denkmal_costs_label"],
        min_value=0, max_value=500000, value=0, step=1000,
        help=T["denkmal_costs_help"]
    )
    custom_nutzungsdauer_active = st.checkbox(
        T["custom_nutzungsdauer_label"], value=False,
        help=T["custom_nutzungsdauer_help"]
    )
    gutachten_year = None
    gutachten_restnutzungsdauer = None
    if custom_nutzungsdauer_active:
        gutachten_year = st.number_input(
            T["gutachten_year_label"],
            min_value=2000, max_value=2050, value=acquisition_year, step=1,
            help=T["gutachten_year_help"]
        )
        gutachten_restnutzungsdauer = st.number_input(
            T["gutachten_restnutzungsdauer_label"],
            min_value=0.1, max_value=100.0, value=20.0, step=0.5,
            help=T["gutachten_restnutzungsdauer_help"]
        )
        # Validation
        if gutachten_year < acquisition_year:
            st.error(T["gutachten_year_error"])
        if gutachten_restnutzungsdauer <= 0:
            st.error(T["gutachten_duration_error"])

with col_afa3:
    marginal_tax_rate = st.slider(
        T["marginal_tax_rate_label"], 0, 50, 42, 1,
        help=T["marginal_tax_rate_help"]
    )
    st.caption(T["soli_note"])
    properties_sold_5y = st.number_input(
        T["properties_sold_label"], min_value=1, max_value=20, value=1, step=1,
        help=T["properties_sold_help"]
    )
    use_afa = st.checkbox(
        T["use_afa_label"], value=True,
        help=T["use_afa_help"]
    )

# Show AfA rate info
st.info(T["afa_rate_info"])
if denkmal_costs > 0:
    st.info(T["denkmal_afa_info"])

# ──────────────────────────────────────────────
# CALCULATE
# ──────────────────────────────────────────────
if st.button(T["calc_button"], type="primary"):

    results = {}

    # Calculate AfA schedule first
    afa_schedule = calculate_afa_schedule(
        total_purchase_price=buy_price,
        land_value=land_value if land_value > 0 else None,
        land_percentage=land_percentage,
        construction_year=construction_year,
        acquisition_year=acquisition_year,
        acquisition_month=acquisition_month,
        denkmal_costs=denkmal_costs,
        marginal_tax_rate=marginal_tax_rate,
        hold_years=hold_years_input,
        annual_income=annual_income,
        use_afa=use_afa,
        custom_nutzungsdauer_active=custom_nutzungsdauer_active,
        gutachten_year=gutachten_year,
        gutachten_restnutzungsdauer=gutachten_restnutzungsdauer
    )

    if scenario_type in ["Sell", "Compare Both"]:
        results["sell"] = calculate_sell_scenario_with_afa(
            buy_price, reno_costs, holding_costs_monthly, hold_months,
            sell_price, vat_reclaim_pct, annual_income, use_sell_makler,
            eigennutzung=eigennutzung,
            afa_schedule=afa_schedule
        )

    if scenario_type in ["Rent", "Compare Both"]:
        results["rent"] = calculate_rent_scenario_with_afa(
            buy_price, reno_costs, holding_costs_monthly, hold_months,
            monthly_rent, vacancy_rate, annual_income, vat_reclaim_pct,
            afa_schedule=afa_schedule if use_afa else None
        )
        results["breakeven_months"] = calculate_breakeven_hold_period(
            buy_price, reno_costs, holding_costs_monthly,
            monthly_rent, vacancy_rate, annual_income, vat_reclaim_pct
        )
    
    # Store AfA schedule in results for display
    results["afa"] = afa_schedule
    
    # Compliance checks
    compliance_checks = {}
    compliance_checks["anschaffungsnahe"] = check_anschaffungsnahe_herstellungskosten(
        buy_price, land_value if land_value > 0 else None, land_percentage,
        reno_costs, vat_option_active
    )
    compliance_checks["gewerblich"] = check_gewerblicher_grundstueckshandel(
        properties_sold_5y, hold_years_input
    )
    results["compliance"] = compliance_checks

    # ── Results header ──────────────────────────
    st.markdown("---")
    st.header(T["results_header"])
    
    # ── COMPLIANCE WARNINGS ─────────────────────
    if results.get("compliance"):
        compliance = results["compliance"]
        
        # Anschaffungsnahe Herstellungskosten warning
        if compliance["anschaffungsnahe"]["threshold_exceeded"]:
            st.error(T["anschaffungsnahe_warning"])
            st.info(T["anschaffungsnahe_info"])
            anschaffungsnahe = compliance["anschaffungsnahe"]
            st.info(T["anschaffungsnahe_percentage"].format(percentage=anschaffungsnahe["percentage"]))
        
        # Gewerblicher Grundstückshandel warning
        if compliance["gewerblich"]["is_gewerblich"]:
            st.warning(T["gewerblich_warning"])

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
                if sell['speculation_tax'] == 0 and sell['gross_profit'] <= 0:
                    st.metric(T["speculation_tax"], "€0", delta="Loss restriction", delta_color="normal")
                else:
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
                    if sell['speculation_tax'] == 0 and sell['gross_profit'] <= 0:
                        st.info(T["loss_restriction_note"])
                    else:
                        st.warning(T["spec_tax_warning"].format(years=sell['hold_years']))
                        st.write(T["spec_tax_rate_line"].format(rate=sell['spec_tax_rate']))
                        st.caption(T["spec_tax_rate_note"])
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

    # ── AfA RESULTS ──────────────────────────────
    if results.get("afa") and results["afa"]["use_afa"]:
        st.markdown("---")
        st.header(T["afa_header"])
        st.markdown(T["afa_subheader"])
        
        afa = results["afa"]
        
        # Summary metrics with breakdown
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric(T["total_normal_afa"], f"€{afa['total_normal_afa']:,.0f}")
        with c2:
            st.metric(T["total_denkmal_afa"], f"€{afa['total_denkmal_afa']:,.0f}")
        with c3:
            st.metric(T["total_afa_claimed"], f"€{afa['total_afa_claimed']:,.0f}")
        with c4:
            st.metric(T["total_tax_shield"], f"€{afa['total_tax_shield']:,.0f}")
        with c5:
            st.metric(T["remaining_book_value"], f"€{afa['remaining_book_value']:,.0f}")
        
        # Annual AfA table with separate columns
        st.markdown(f"**{T['annual_afa_table']}**")
        afa_df = pd.DataFrame(afa["annual_schedule"])
        afa_df.columns = [
            T["year_col"], 
            T["normal_afa_col"], 
            T["denkmal_afa_col"], 
            T["total_afa_col"], 
            T["cumulative_afa_col"], 
            T["tax_shield_col"], 
            T["book_value_col"],
            T["basis_col"]
        ]
        st.dataframe(afa_df, use_container_width=True, hide_index=True)
        
        # Custom useful life summary
        if afa.get("custom_nutzungsdauer_active") and afa.get("gutachten_year"):
            st.info(T["custom_nutzungsdauer_summary"].format(
                year=afa["gutachten_year"],
                duration=afa["gutachten_restnutzungsdauer"],
                original=afa["useful_life_original"]
            ))
        
        # AfA recapture info for sell scenario
        if "sell" in results and results["sell"].get("afa"):
            st.markdown("---")
            st.subheader(T["afa_recapture"])
            st.info(T["afa_recapture_info"])
            
            sell_afa = results["sell"]["afa"]
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric(T["gross_sale_profit"], f"€{sell_afa['original_gross_profit']:,.0f}")
            with c2:
                st.metric(f"{T['total_normal_afa']} (Rückgängig)", f"+€{sell_afa['total_normal_afa']:,.0f}")
            with c3:
                st.metric(f"{T['total_denkmal_afa']} (Rückgängig)", f"+€{sell_afa['total_denkmal_afa']:,.0f}")
            with c4:
                st.metric(T["taxable_gain_after_recapture"], f"€{sell_afa['taxable_gain_with_recapture']:,.0f}")
            
            st.metric(T["final_tax_on_sale"], f"€{sell_afa['speculation_tax_with_recapture']:,.0f}")
        
        # AfA benefit info for rent scenario
        if "rent" in results and results["rent"].get("afa"):
            st.markdown("---")
            st.subheader(T["afa_benefit_rental"])
            rent_afa = results["rent"]["afa"]
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(T["annual_afa_tax_benefit"], f"€{rent_afa['annual_tax_shield']:,.0f}")
            with c2:
                st.metric(T["enhanced_cashflow"], f"€{rent_afa['enhanced_annual_cashflow']:,.0f}")
            with c3:
                st.metric(T["remaining_book_value_at_sale"], f"€{rent_afa['remaining_book_value']:,.0f}")
        
        # Disclaimer
        st.warning(T["compliance_disclaimer"])

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
                "use_sell_makler": use_sell_makler if scenario_type in ["Sell", "Compare Both"] else False,
                "construction_year": construction_year,
                "acquisition_year": acquisition_year,
                "acquisition_month": acquisition_month,
                "land_value": land_value,
                "land_percentage": land_percentage,
                "denkmal_costs": denkmal_costs,
                "marginal_tax_rate": marginal_tax_rate,
                "use_afa": use_afa,
                "vat_option_active": vat_option_active,
                "properties_sold_5y": properties_sold_5y,
                "custom_nutzungsdauer_active": custom_nutzungsdauer_active,
                "gutachten_year": gutachten_year,
                "gutachten_restnutzungsdauer": gutachten_restnutzungsdauer
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
