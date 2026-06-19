"""Streamlit demo QS cost-control dashboard for Aurora Residence."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from cost_helpers import (
    calculate_package_metrics,
    display_table,
    format_idr,
    summarize_totals,
)
from dummy_data import PACKAGE_DATA, PROJECT_METADATA
from excel_helpers import create_excel_report


st.set_page_config(
    page_title="Aurora Residence Cost Control",
    page_icon="AR",
    layout="wide",
)


def init_state() -> None:
    """Initialize package data once per browser session."""
    if "packages" not in st.session_state:
        st.session_state.packages = pd.DataFrame(PACKAGE_DATA)


def money_column(label: str) -> st.column_config.NumberColumn:
    """Consistent currency editor/display configuration."""
    return st.column_config.NumberColumn(
        label,
        min_value=0,
        step=100_000_000,
        format="Rp %d",
    )


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


def render_project_header() -> None:
    st.title(PROJECT_METADATA["name"])
    st.caption("QS Cost-Control Dashboard")

    meta_columns = st.columns(3)
    meta_columns[0].markdown(f"**Project Type:** {PROJECT_METADATA['type']}")
    meta_columns[1].markdown(f"**Location:** {PROJECT_METADATA['location']}")
    meta_columns[2].markdown("**Data Source:** In-memory dummy data")


def render_dashboard() -> None:
    render_project_header()

    details = calculate_package_metrics(st.session_state.packages)
    totals = summarize_totals(st.session_state.packages)

    st.divider()
    render_metric_grid(totals)

    st.subheader("Package Summary")
    st.dataframe(
        display_table(details),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Package Status")
    status_counts = details["status"].value_counts().rename_axis("Status").reset_index(
        name="Packages"
    )
    st.dataframe(status_counts, use_container_width=True, hide_index=True)


def render_edit_page(page_title: str, editable_columns: list[str]) -> None:
    st.title(page_title)
    st.caption("Changes are stored in memory for this session.")

    base_columns = ["package", *editable_columns]
    editor_frame = st.session_state.packages[base_columns].copy()

    column_config = {
        "package": st.column_config.TextColumn("Package", disabled=True),
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
        disabled=["package"],
        key=f"editor_{page_title.lower().replace(' ', '_')}",
    )

    for column in editable_columns:
        st.session_state.packages[column] = pd.to_numeric(
            edited[column], errors="coerce"
        ).fillna(0)

    details = calculate_package_metrics(st.session_state.packages)
    st.subheader("Updated Package Summary")
    st.dataframe(display_table(details), use_container_width=True, hide_index=True)


def render_export_report() -> None:
    st.title("Export Report")
    st.caption("Download an Excel report generated from the current in-memory data.")

    details = calculate_package_metrics(st.session_state.packages)
    totals = summarize_totals(st.session_state.packages)

    render_metric_grid(totals)
    st.subheader("Export Preview")
    st.dataframe(display_table(details), use_container_width=True, hide_index=True)

    excel_bytes = create_excel_report(PROJECT_METADATA, st.session_state.packages)
    st.download_button(
        "Download Excel Report",
        data=excel_bytes,
        file_name="aurora_residence_cost_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def main() -> None:
    init_state()

    st.sidebar.title("Aurora Residence")
    selected_page = st.sidebar.radio(
        "Pages",
        [
            "Dashboard",
            "Budget Packages",
            "Contract Awards",
            "Progress Claims",
            "Variation Orders",
            "Export Report",
        ],
    )

    if selected_page == "Dashboard":
        render_dashboard()
    elif selected_page == "Budget Packages":
        render_edit_page("Budget Packages", ["original_budget"])
    elif selected_page == "Contract Awards":
        render_edit_page("Contract Awards", ["contract_award"])
    elif selected_page == "Progress Claims":
        render_edit_page("Progress Claims", ["certified_payment"])
    elif selected_page == "Variation Orders":
        render_edit_page("Variation Orders", ["approved_vo", "pending_vo"])
    elif selected_page == "Export Report":
        render_export_report()


if __name__ == "__main__":
    main()
