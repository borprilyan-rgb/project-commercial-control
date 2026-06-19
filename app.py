"""Phase 1 Streamlit app for a project commercial control dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from cost_helpers import (
    calculate_project_totals,
    calculate_package_metrics,
    format_idr,
    prepare_package_summary,
    prepare_summary_dataframe,
)
from dummy_data import PROJECT_METADATA, get_initial_package_data
from excel_helpers import create_excel_report


st.set_page_config(
    page_title="Project Commercial Control System",
    layout="wide",
)


def init_state() -> None:
    """Initialize package data once per browser session."""
    if "packages" not in st.session_state:
        st.session_state.packages = pd.DataFrame(get_initial_package_data())


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

    details = calculate_package_metrics(st.session_state.packages)
    totals = calculate_project_totals(st.session_state.packages)

    st.divider()
    render_metric_grid(totals)

    st.subheader("Package Summary")
    st.dataframe(
        prepare_package_summary(st.session_state.packages),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Package Status")
    st.dataframe(
        details[["package", "status"]].rename(
            columns={"package": "Package", "status": "Status"}
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

    if allow_package_edit:
        st.session_state.packages["package"] = edited["package"].fillna("").astype(str)
    for column in editable_columns:
        st.session_state.packages[column] = pd.to_numeric(
            edited[column], errors="coerce"
        ).fillna(0)

    st.subheader("Updated Package Summary")
    st.dataframe(
        prepare_package_summary(st.session_state.packages),
        use_container_width=True,
        hide_index=True,
    )


def render_export_report() -> None:
    st.title("Export Report")
    st.caption("Download an Excel report generated from the current in-memory data.")

    details = calculate_package_metrics(st.session_state.packages)
    totals = calculate_project_totals(st.session_state.packages)

    render_metric_grid(totals)
    st.subheader("Summary")
    st.dataframe(
        prepare_summary_dataframe(st.session_state.packages),
        use_container_width=True,
        hide_index=True,
    )
    st.subheader("Export Preview")
    st.dataframe(
        prepare_package_summary(st.session_state.packages),
        use_container_width=True,
        hide_index=True,
    )

    excel_bytes = create_excel_report(PROJECT_METADATA, st.session_state.packages)
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
        render_edit_page("Budget Packages", ["original_budget"], allow_package_edit=True)
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
