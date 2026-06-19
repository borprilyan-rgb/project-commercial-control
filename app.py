"""Streamlit app for a project commercial control dashboard."""

from __future__ import annotations

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


def render_metric_grid(totals: dict[str, float]) -> None:
    metric_rows = [
        [
            ("Original Budget", totals["original_budget"]),
            ("Contract Award", totals["contract_award"]),
            ("Approved VO", totals["approved_vo"]),
            ("Pending VO", totals["pending_vo"]),
        ],
        [
            ("Forecast Final Cost", totals["forecast_final_cost"]),
            ("Budget Variance", totals["budget_variance"]),
            ("Certified to Date", totals["certified_payment"]),
            ("Remaining Contract Value", totals["remaining_contract_value"]),
        ],
    ]

    for row in metric_rows:
        columns = st.columns(4)
        for column, (label, value) in zip(columns, row):
            column.metric(label, format_idr(value))


def render_dashboard_indicators(indicators: dict[str, float]) -> None:
    columns = st.columns(5)
    columns[0].metric("Packages", int(indicators["package_count"]))
    columns[1].metric("Under Budget", int(indicators["under_budget_count"]))
    columns[2].metric("Over Budget", int(indicators["over_budget_count"]))
    columns[3].metric("High Risk", int(indicators["high_risk_count"]))
    columns[4].metric(
        "Avg Certified %",
        format_percent(indicators["average_certified_percent"]),
    )


def render_package_status_indicators(indicators: dict[str, int]) -> None:
    columns = st.columns(4)
    columns[0].metric("Awarded", indicators["awarded_count"])
    columns[1].metric("Ongoing", indicators["ongoing_count"])
    columns[2].metric("Completed / Closed", indicators["completed_closed_count"])
    columns[3].metric("In Procurement", indicators["in_procurement_count"])


def render_vo_indicators(indicators: dict[str, float]) -> None:
    columns = st.columns(5)
    columns[0].metric("Submitted VO", format_idr(indicators["submitted_vo_total"]))
    columns[1].metric("Approved VO", format_idr(indicators["approved_vo_total"]))
    columns[2].metric("Pending VO", format_idr(indicators["pending_vo_total"]))
    columns[3].metric("Approved VOs", int(indicators["approved_vo_count"]))
    columns[4].metric(
        "Pending / Review VOs",
        int(indicators["pending_review_vo_count"]),
    )


def render_claim_indicators(indicators: dict[str, float]) -> None:
    columns = st.columns(5)
    columns[0].metric(
        "Submitted Claims",
        format_idr(indicators["submitted_claim_total"]),
    )
    columns[1].metric(
        "Certified Claims",
        format_idr(indicators["certified_claim_total"]),
    )
    columns[2].metric("Total Paid", format_idr(indicators["paid_total"]))
    columns[3].metric("Certified Claims", int(indicators["certified_claim_count"]))
    columns[4].metric(
        "Under Review Claims",
        int(indicators["under_review_claim_count"]),
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
    st.title("Project Commercial Control System")
    st.subheader(PROJECT_METADATA["name"])

    meta_columns = st.columns(5)
    meta_columns[0].markdown(f"**Project Type:** {PROJECT_METADATA['type']}")
    meta_columns[1].markdown(f"**Location:** {PROJECT_METADATA['location']}")
    meta_columns[2].markdown(f"**Client Type:** {PROJECT_METADATA['client_type']}")
    meta_columns[3].markdown(f"**Currency:** {PROJECT_METADATA['currency']}")
    meta_columns[4].markdown("**Data Source:** Dummy in-memory data")



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

    st.divider()
    render_metric_grid(totals)

    st.subheader("Commercial Summary")
    render_dashboard_indicators(
        calculate_dashboard_indicators(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        )
    )

    st.subheader("Package Status Summary")
    render_package_status_indicators(
        calculate_package_status_indicators(st.session_state.packages)
    )

    st.subheader("Variation Order Summary")
    render_vo_indicators(calculate_vo_indicators(st.session_state.variations))

    st.subheader("Progress Claim Summary")
    render_claim_indicators(calculate_claim_indicators(st.session_state.claims))

    st.subheader("Charts")
    render_dashboard_charts(details)

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

    st.subheader("Package Register")
    st.dataframe(
        prepare_package_register(
            st.session_state.packages,
            st.session_state.variations,
            st.session_state.claims,
        ),
        use_container_width=True,
        hide_index=True,
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
