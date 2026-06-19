"""Streamlit app for a project commercial control dashboard."""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from cost_helpers import (
    calculate_dashboard_indicators,
    calculate_claim_indicators,
    calculate_package_status_indicators,
    calculate_project_totals,
    calculate_package_metrics,
    calculate_vo_indicators,
    format_idr,
    format_percent,
    prepare_package_register,
    prepare_package_summary,
    prepare_claim_register,
    prepare_summary_dataframe,
    prepare_variation_register,
)
from dummy_data import (
    PROJECT_METADATA,
    get_initial_claim_data,
    get_initial_package_data,
    get_initial_vo_data,
)
from excel_helpers import create_excel_report


st.set_page_config(
    page_title="Project Commercial Control System",
    layout="wide",
)


def inject_custom_css() -> None:
    """Add controlled, app-owned styling for portfolio presentation."""
    st.markdown(
        """
        <style>
        .app-header {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            padding: 1.2rem 1.35rem;
            margin: 0.25rem 0 1.15rem 0;
            background: #ffffff;
            color: #172033;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
        }
        .app-header__eyebrow {
            color: #536174;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }
        .app-header__title {
            font-size: 1.9rem;
            line-height: 1.15;
            font-weight: 750;
            margin: 0;
        }
        .app-header__meta {
            color: #536174;
            font-size: 0.95rem;
            margin-top: 0.4rem;
        }
        .section-heading {
            margin: 1.35rem 0 0.7rem 0;
            padding-bottom: 0.35rem;
            border-bottom: 1px solid #e3e8ef;
        }
        .section-heading__title {
            color: #172033;
            font-size: 1.05rem;
            font-weight: 750;
            margin: 0;
        }
        .section-heading__caption {
            color: #6b7280;
            font-size: 0.86rem;
            margin-top: 0.1rem;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.4rem 0 0.95rem 0;
        }
        .metric-grid--five {
            grid-template-columns: repeat(5, minmax(0, 1fr));
        }
        .metric-card {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            padding: 0.85rem 0.95rem;
            background: #ffffff;
            color: #172033;
            min-height: 5.1rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        .metric-card__label {
            color: #64748b;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }
        .metric-card__value {
            font-size: 1.18rem;
            font-weight: 760;
            line-height: 1.25;
            overflow-wrap: anywhere;
        }
        .metric-card--danger {
            border-left: 4px solid #c2410c;
        }
        .metric-card--good {
            border-left: 4px solid #15803d;
        }
        .metric-card--neutral {
            border-left: 4px solid #2563eb;
        }
        .badge {
            display: inline-block;
            border-radius: 999px;
            padding: 0.16rem 0.55rem;
            font-size: 0.75rem;
            font-weight: 700;
            white-space: nowrap;
            border: 1px solid transparent;
        }
        .badge-good {
            background: #dcfce7;
            color: #166534;
            border-color: #86efac;
        }
        .badge-warning {
            background: #fef3c7;
            color: #92400e;
            border-color: #fcd34d;
        }
        .badge-danger {
            background: #fee2e2;
            color: #991b1b;
            border-color: #fca5a5;
        }
        .badge-neutral {
            background: #e0f2fe;
            color: #075985;
            border-color: #7dd3fc;
        }
        .report-table {
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #d8dee8;
            border-radius: 8px;
            overflow: hidden;
            background: #ffffff;
            color: #172033;
            font-size: 0.86rem;
        }
        .report-table th {
            background: #f1f5f9;
            color: #334155;
            font-weight: 750;
            text-align: left;
            padding: 0.55rem 0.65rem;
            border-bottom: 1px solid #d8dee8;
        }
        .report-table td {
            padding: 0.52rem 0.65rem;
            border-bottom: 1px solid #edf2f7;
            vertical-align: top;
        }
        .report-table tr:last-child td {
            border-bottom: 0;
        }
        @media (max-width: 1100px) {
            .metric-grid,
            .metric-grid--five {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        @media (max-width: 720px) {
            .metric-grid,
            .metric-grid--five {
                grid-template-columns: 1fr;
            }
            .app-header__title {
                font-size: 1.45rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_css()


def init_state() -> None:
    """Initialize package data once per browser session."""
    if (
        "packages" not in st.session_state
        or st.session_state.packages is None
        or not isinstance(st.session_state.packages, pd.DataFrame)
    ):
        st.session_state.packages = pd.DataFrame(get_initial_package_data())
    if (
        "variations" not in st.session_state
        or st.session_state.variations is None
        or not isinstance(st.session_state.variations, pd.DataFrame)
    ):
        st.session_state.variations = pd.DataFrame(get_initial_vo_data())
    if (
        "claims" not in st.session_state
        or st.session_state.claims is None
        or not isinstance(st.session_state.claims, pd.DataFrame)
    ):
        st.session_state.claims = pd.DataFrame(get_initial_claim_data())

    metadata_defaults = {
        "contractor": "",
        "contract_number": "",
        "package_status": "Not Started",
        "procurement_status": "Budget Only",
        "remarks": "",
    }
    for column, default_value in metadata_defaults.items():
        if column not in st.session_state.packages:
            st.session_state.packages[column] = default_value

    variation_defaults = {
        "vo_no": "",
        "package": "",
        "description": "",
        "vo_status": "Draft",
        "submitted_amount": 0,
        "approved_amount": 0,
        "pending_amount": 0,
        "remarks": "",
    }
    for column, default_value in variation_defaults.items():
        if column not in st.session_state.variations:
            st.session_state.variations[column] = default_value

    claim_defaults = {
        "claim_no": "",
        "period": "",
        "package": "",
        "contractor": "",
        "claim_status": "Draft",
        "submitted_amount": 0,
        "certified_amount": 0,
        "payment_amount": 0,
        "remarks": "",
    }
    for column, default_value in claim_defaults.items():
        if column not in st.session_state.claims:
            st.session_state.claims[column] = default_value


def money_column(label: str) -> st.column_config.NumberColumn:
    """Consistent currency editor/display configuration."""
    return st.column_config.NumberColumn(
        label,
        min_value=0,
        step=100_000_000,
        format="Rp %d",
    )


PACKAGE_STATUS_OPTIONS = [
    "Not Started",
    "Tendering",
    "Awarded",
    "Ongoing",
    "Completed",
    "Closed",
]

PROCUREMENT_STATUS_OPTIONS = [
    "Budget Only",
    "Tender Preparation",
    "Tender Issued",
    "Under Evaluation",
    "Awarded",
    "Contract Signed",
]

VO_STATUS_OPTIONS = [
    "Draft",
    "Submitted",
    "Under Review",
    "Approved",
    "Rejected",
    "Pending",
]

CLAIM_STATUS_OPTIONS = [
    "Draft",
    "Submitted",
    "Under Review",
    "Certified",
    "Paid",
    "Rejected",
]


def badge_class(value: str) -> str:
    """Map report statuses to stable badge classes."""
    if value in {"Under Budget", "Low Risk", "Paid", "Certified", "Approved"}:
        return "badge-good"
    if value in {"On Budget", "Medium Risk", "Pending", "Under Review", "Submitted"}:
        return "badge-warning"
    if value in {"Over Budget", "High Risk", "Rejected"}:
        return "badge-danger"
    return "badge-neutral"


def render_badge(value: object) -> str:
    text = escape(str(value))
    return f'<span class="badge {badge_class(str(value))}">{text}</span>'


def render_section_heading(title: str, caption: str = "") -> None:
    caption_html = (
        f'<div class="section-heading__caption">{escape(caption)}</div>'
        if caption
        else ""
    )
    st.markdown(
        (
            '<div class="section-heading">'
            f'<div class="section-heading__title">{escape(title)}</div>'
            f"{caption_html}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_card_grid(
    cards: list[tuple[str, str | int | float]],
    columns: int = 4,
    accent_labels: set[str] | None = None,
) -> None:
    accent_labels = accent_labels or set()
    grid_class = "metric-grid metric-grid--five" if columns == 5 else "metric-grid"
    card_html = []

    for label, value in cards:
        accent_class = "metric-card--neutral"
        if label in accent_labels:
            value_text = str(value)
            accent_class = (
                "metric-card--danger"
                if value_text.startswith("-")
                else "metric-card--good"
            )
        card_html.append(
            (
                f'<div class="metric-card {accent_class}">'
                f'<div class="metric-card__label">{escape(label)}</div>'
                f'<div class="metric-card__value">{escape(str(value))}</div>'
                "</div>"
            )
        )

    st.markdown(
        f'<div class="{grid_class}">{"".join(card_html)}</div>',
        unsafe_allow_html=True,
    )


def render_report_table(frame: pd.DataFrame, badge_columns: set[str] | None = None) -> None:
    badge_columns = badge_columns or set()
    header_html = "".join(f"<th>{escape(str(column))}</th>" for column in frame.columns)
    row_html = []

    for _, row in frame.iterrows():
        cells = []
        for column in frame.columns:
            value = row[column]
            cell_html = render_badge(value) if column in badge_columns else escape(str(value))
            cells.append(f"<td>{cell_html}</td>")
        row_html.append(f"<tr>{''.join(cells)}</tr>")

    st.markdown(
        (
            '<table class="report-table">'
            f"<thead><tr>{header_html}</tr></thead>"
            f"<tbody>{''.join(row_html)}</tbody>"
            "</table>"
        ),
        unsafe_allow_html=True,
    )


def render_metric_grid(totals: dict[str, float]) -> None:
    cards = [
        ("Original Budget", format_idr(totals["original_budget"])),
        ("Contract Award", format_idr(totals["contract_award"])),
        ("Approved VO", format_idr(totals["approved_vo"])),
        ("Pending VO", format_idr(totals["pending_vo"])),
        ("Forecast Final Cost", format_idr(totals["forecast_final_cost"])),
        ("Budget Variance", format_idr(totals["budget_variance"])),
        ("Certified to Date", format_idr(totals["certified_payment"])),
        ("Remaining Contract Value", format_idr(totals["remaining_contract_value"])),
    ]
    render_card_grid(cards, accent_labels={"Budget Variance"})


def render_dashboard_indicators(indicators: dict[str, float]) -> None:
    render_card_grid(
        [
            ("Packages", int(indicators["package_count"])),
            ("Under Budget", int(indicators["under_budget_count"])),
            ("Over Budget", int(indicators["over_budget_count"])),
            ("High Risk", int(indicators["high_risk_count"])),
            ("Avg Certified %", format_percent(indicators["average_certified_percent"])),
        ],
        columns=5,
    )


def render_package_status_indicators(indicators: dict[str, int]) -> None:
    render_card_grid(
        [
            ("Awarded", indicators["awarded_count"]),
            ("Ongoing", indicators["ongoing_count"]),
            ("Completed / Closed", indicators["completed_closed_count"]),
            ("In Procurement", indicators["in_procurement_count"]),
        ]
    )


def render_vo_indicators(indicators: dict[str, float]) -> None:
    render_card_grid(
        [
            ("Submitted VO", format_idr(indicators["submitted_vo_total"])),
            ("Approved VO", format_idr(indicators["approved_vo_total"])),
            ("Pending VO", format_idr(indicators["pending_vo_total"])),
            ("Approved VOs", int(indicators["approved_vo_count"])),
            ("Pending / Review VOs", int(indicators["pending_review_vo_count"])),
        ],
        columns=5,
    )


def render_claim_indicators(indicators: dict[str, float]) -> None:
    render_card_grid(
        [
            ("Submitted Claims", format_idr(indicators["submitted_claim_total"])),
            ("Certified Claims", format_idr(indicators["certified_claim_total"])),
            ("Total Paid", format_idr(indicators["paid_total"])),
            ("Certified Claim Count", int(indicators["certified_claim_count"])),
            ("Under Review Claims", int(indicators["under_review_claim_count"])),
        ],
        columns=5,
    )


def render_dashboard_charts(details: pd.DataFrame) -> None:
    chart_data = details.set_index("package")

    chart_columns = st.columns(2)
    with chart_columns[0]:
        st.subheader("Budget Variance by Package")
        st.bar_chart(chart_data[["budget_variance"]])

    with chart_columns[1]:
        st.subheader("Certified Percentage by Package")
        certified_chart = chart_data[["certified_percent"]] * 100
        st.bar_chart(certified_chart)


def render_project_header() -> None:
    st.markdown(
        (
            '<div class="app-header">'
            '<div class="app-header__eyebrow">Project Commercial Control System</div>'
            f'<h1 class="app-header__title">{escape(PROJECT_METADATA["name"])}</h1>'
            '<div class="app-header__meta">'
            f'{escape(PROJECT_METADATA["type"])} | '
            f'{escape(PROJECT_METADATA["location"])} | '
            f'{escape(PROJECT_METADATA["client_type"])}'
            "</div></div>"
        ),
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    render_project_header()

    details = calculate_package_metrics(
        st.session_state.packages,
        st.session_state.variations,
        st.session_state.claims,
    )
    totals = calculate_project_totals(
        st.session_state.packages,
        st.session_state.variations,
        st.session_state.claims,
    )

    render_section_heading(
        "Commercial Overview",
        "Headline budget, award, variation, forecast, and payment position.",
    )
    render_metric_grid(totals)

    render_section_heading(
        "Package Risk Summary",
        "Budget status, risk exposure, and certified progress across packages.",
    )
    render_dashboard_indicators(
        calculate_dashboard_indicators(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        )
    )

    render_section_heading(
        "Package Status Summary",
        "Current procurement and execution status across the package register.",
    )
    render_package_status_indicators(
        calculate_package_status_indicators(st.session_state.packages)
    )

    render_section_heading(
        "Variation Order Summary",
        "Submitted, approved, and pending variation exposure from the VO register.",
    )
    render_vo_indicators(calculate_vo_indicators(st.session_state.variations))

    render_section_heading(
        "Progress Claim Summary",
        "Submitted, certified, paid, and review-stage progress claim position.",
    )
    render_claim_indicators(calculate_claim_indicators(st.session_state.claims))

    render_section_heading(
        "Commercial Trend Views",
        "Quick visual scan of variance and certification percentage by package.",
    )
    render_dashboard_charts(details)

    render_section_heading(
        "Package Commercial Summary",
        "Calculated package-level budget, forecast, payment, status, and risk.",
    )
    render_report_table(
        prepare_package_summary(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        ),
        badge_columns={"Status", "Risk Level"},
    )

    render_section_heading(
        "Package Register",
        "Contractor, contract reference, procurement status, package status, and risk.",
    )
    render_report_table(
        prepare_package_register(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        ),
        badge_columns={"Package Status", "Procurement Status", "Risk Level"},
    )


def render_package_register() -> None:
    st.title("Package Register")
    st.caption("Edit package metadata only. Commercial amounts remain on their own pages.")

    register_columns = [
        "package",
        "contractor",
        "contract_number",
        "package_status",
        "procurement_status",
        "remarks",
    ]
    editor_frame = st.session_state.packages[register_columns].copy()

    edited = st.data_editor(
        editor_frame,
        use_container_width=True,
        hide_index=True,
        column_config={
            "package": st.column_config.TextColumn("Package", required=True),
            "contractor": st.column_config.TextColumn("Contractor"),
            "contract_number": st.column_config.TextColumn("Contract Number"),
            "package_status": st.column_config.SelectboxColumn(
                "Package Status",
                options=PACKAGE_STATUS_OPTIONS,
                required=True,
            ),
            "procurement_status": st.column_config.SelectboxColumn(
                "Procurement Status",
                options=PROCUREMENT_STATUS_OPTIONS,
                required=True,
            ),
            "remarks": st.column_config.TextColumn("Remarks"),
        },
        key="editor_package_register",
    )
    if edited is None:
        edited = editor_frame

    for column in register_columns:
        st.session_state.packages[column] = edited[column].fillna("").astype(str)

    st.subheader("Updated Package Register")
    st.dataframe(
        prepare_package_register(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_edit_page(
    page_title: str,
    editable_columns: list[str],
    allow_package_edit: bool = False,
) -> None:
    st.title(page_title)
    st.caption("Changes are stored in memory for this session.")

    base_columns = ["package", *editable_columns]
    editor_frame = st.session_state.packages[base_columns].copy()

    column_config = {
        "package": st.column_config.TextColumn("Package", required=True),
    }
    column_config.update(
        {
            column: money_column(column.replace("_", " ").title())
            for column in editable_columns
        }
    )

    edited = st.data_editor(
        editor_frame,
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
        disabled=[] if allow_package_edit else ["package"],
        key=f"editor_{page_title.lower().replace(' ', '_')}",
    )
    if edited is None:
        edited = editor_frame

    if allow_package_edit:
        st.session_state.packages["package"] = edited["package"].fillna("").astype(str)
    for column in editable_columns:
        st.session_state.packages[column] = pd.to_numeric(
            edited[column], errors="coerce"
        ).fillna(0)

    st.subheader("Updated Package Summary")
    st.dataframe(
        prepare_package_summary(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_variation_orders() -> None:
    st.title("Variation Orders")
    st.caption("Edit detailed VO records. Package VO totals are aggregated from this register.")

    editor_columns = [
        "vo_no",
        "package",
        "description",
        "vo_status",
        "submitted_amount",
        "approved_amount",
        "pending_amount",
        "remarks",
    ]
    editor_frame = st.session_state.variations[editor_columns].copy()

    edited = st.data_editor(
        editor_frame,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "vo_no": st.column_config.TextColumn("VO No.", required=True),
            "package": st.column_config.SelectboxColumn(
                "Package",
                options=st.session_state.packages["package"].tolist(),
                required=True,
            ),
            "description": st.column_config.TextColumn("Description"),
            "vo_status": st.column_config.SelectboxColumn(
                "VO Status",
                options=VO_STATUS_OPTIONS,
                required=True,
            ),
            "submitted_amount": money_column("Submitted Amount"),
            "approved_amount": money_column("Approved Amount"),
            "pending_amount": money_column("Pending Amount"),
            "remarks": st.column_config.TextColumn("Remarks"),
        },
        key="editor_variation_orders",
    )
    if edited is None:
        edited = editor_frame

    for column in ["vo_no", "package", "description", "vo_status", "remarks"]:
        edited[column] = edited[column].fillna("").astype(str)
    for column in ["submitted_amount", "approved_amount", "pending_amount"]:
        edited[column] = pd.to_numeric(
            edited[column],
            errors="coerce",
        ).fillna(0)
    st.session_state.variations = edited[editor_columns]

    st.subheader("VO Summary")
    render_vo_indicators(calculate_vo_indicators(st.session_state.variations))

    st.subheader("Variation Register")
    st.dataframe(
        prepare_variation_register(st.session_state.variations),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Package Summary")
    st.dataframe(
        prepare_package_summary(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_progress_claims() -> None:
    st.title("Progress Claims")
    st.caption(
        "Edit detailed monthly claim records. Certified totals are aggregated from this register."
    )

    editor_columns = [
        "claim_no",
        "period",
        "package",
        "contractor",
        "claim_status",
        "submitted_amount",
        "certified_amount",
        "payment_amount",
        "remarks",
    ]
    editor_frame = st.session_state.claims[editor_columns].copy()

    edited = st.data_editor(
        editor_frame,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "claim_no": st.column_config.TextColumn("Claim No.", required=True),
            "period": st.column_config.TextColumn("Period"),
            "package": st.column_config.SelectboxColumn(
                "Package",
                options=st.session_state.packages["package"].tolist(),
                required=True,
            ),
            "contractor": st.column_config.TextColumn("Contractor"),
            "claim_status": st.column_config.SelectboxColumn(
                "Claim Status",
                options=CLAIM_STATUS_OPTIONS,
                required=True,
            ),
            "submitted_amount": money_column("Submitted Amount"),
            "certified_amount": money_column("Certified Amount"),
            "payment_amount": money_column("Payment Amount"),
            "remarks": st.column_config.TextColumn("Remarks"),
        },
        key="editor_progress_claims",
    )
    if edited is None:
        edited = editor_frame

    text_columns = [
        "claim_no",
        "period",
        "package",
        "contractor",
        "claim_status",
        "remarks",
    ]
    for column in text_columns:
        edited[column] = edited[column].fillna("").astype(str)
    for column in ["submitted_amount", "certified_amount", "payment_amount"]:
        edited[column] = pd.to_numeric(
            edited[column],
            errors="coerce",
        ).fillna(0)
    st.session_state.claims = edited[editor_columns]

    st.subheader("Claim Summary")
    render_claim_indicators(calculate_claim_indicators(st.session_state.claims))

    st.subheader("Progress Claim Register")
    st.dataframe(
        prepare_claim_register(st.session_state.claims),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Package Summary")
    st.dataframe(
        prepare_package_summary(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_export_report() -> None:
    st.title("Export Report")
    st.caption("Download an Excel report generated from the current in-memory data.")

    totals = calculate_project_totals(
        st.session_state.packages,
        st.session_state.variations,
        st.session_state.claims,
    )

    render_metric_grid(totals)
    st.subheader("Summary")
    st.dataframe(
        prepare_summary_dataframe(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.subheader("Export Preview")
    st.dataframe(
        prepare_package_summary(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        ),
        use_container_width=True,
        hide_index=True,
    )

    excel_bytes = create_excel_report(
        PROJECT_METADATA,
        st.session_state.packages,
        st.session_state.variations,
        st.session_state.claims,
    )
    st.download_button(
        "Download Excel Report",
        data=excel_bytes,
        file_name="project_commercial_control_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def main() -> None:
    init_state()

    st.sidebar.title("Project Commercial Control System")
    selected_page = st.sidebar.radio(
        "Pages",
        [
            "Dashboard",
            "Package Register",
            "Budget Packages",
            "Contract Awards",
            "Progress Claims",
            "Variation Orders",
            "Export Report",
        ],
    )

    if selected_page == "Dashboard":
        render_dashboard()
    elif selected_page == "Package Register":
        render_package_register()
    elif selected_page == "Budget Packages":
        render_edit_page("Budget Packages", ["original_budget"], allow_package_edit=True)
    elif selected_page == "Contract Awards":
        render_edit_page("Contract Awards", ["contract_award"])
    elif selected_page == "Progress Claims":
        render_progress_claims()
    elif selected_page == "Variation Orders":
        render_variation_orders()
    elif selected_page == "Export Report":
        render_export_report()


if __name__ == "__main__":
    main()
