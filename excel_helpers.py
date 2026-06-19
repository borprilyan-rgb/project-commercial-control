"""Excel export helpers for the Project Commercial Control System."""

from __future__ import annotations

from io import BytesIO

import pandas as pd

from cost_helpers import (
    calculate_package_metrics,
    prepare_package_register,
    prepare_summary_dataframe,
    normalize_vo_data,
)


def create_excel_report(
    project_metadata: dict,
    package_frame: pd.DataFrame,
    vo_frame: pd.DataFrame | None = None,
) -> bytes:
    """Create an in-memory Excel report with summary and package detail sheets."""
    output = BytesIO()
    package_details = calculate_package_metrics(package_frame, vo_frame)
    package_register = prepare_package_register(package_frame, vo_frame)
    variation_register = normalize_vo_data(vo_frame)
    summary_metrics = prepare_summary_dataframe(package_frame, vo_frame)

    summary_rows = [
        {"Item": "Project Name", "Value": project_metadata["name"]},
        {"Item": "Project Type", "Value": project_metadata["type"]},
        {"Item": "Location", "Value": project_metadata["location"]},
        {"Item": "Client Type", "Value": project_metadata["client_type"]},
        {"Item": "Currency", "Value": project_metadata["currency"]},
        {"Item": "", "Value": ""},
    ]
    summary_rows.extend(
        summary_metrics.rename(columns={"Metric": "Item"}).to_dict("records")
    )
    summary_frame = pd.DataFrame(summary_rows, columns=["Item", "Value"])

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        summary_frame.to_excel(writer, sheet_name="Summary", index=False)
        package_details.to_excel(writer, sheet_name="Package Details", index=False)
        package_register.to_excel(writer, sheet_name="Package Register", index=False)
        variation_register.to_excel(writer, sheet_name="Variation Register", index=False)

        workbook = writer.book
        money_format = workbook.add_format({"num_format": '"Rp" #,##0'})
        percent_format = workbook.add_format({"num_format": "0.0%"})
        header_format = workbook.add_format(
            {"bold": True, "bg_color": "#EAF2F8", "border": 1}
        )

        for sheet_name, frame in {
            "Summary": summary_frame,
            "Package Details": package_details,
            "Package Register": package_register,
            "Variation Register": variation_register,
        }.items():
            worksheet = writer.sheets[sheet_name]
            for column_index, column_name in enumerate(frame.columns):
                worksheet.write(0, column_index, column_name, header_format)
                width = max(16, min(32, len(str(column_name)) + 4))
                worksheet.set_column(column_index, column_index, width)

        summary_sheet = writer.sheets["Summary"]
        summary_sheet.set_column("B:B", 24, money_format)

        details_sheet = writer.sheets["Package Details"]
        money_columns = [
            package_details.columns.get_loc(column)
            for column in package_details.columns
            if column not in {"package", "status", "risk_level", "certified_percent"}
        ]
        for column_index in money_columns:
            details_sheet.set_column(column_index, column_index, 20, money_format)

        percent_column = package_details.columns.get_loc("certified_percent")
        details_sheet.set_column(percent_column, percent_column, 18, percent_format)

        variation_sheet = writer.sheets["Variation Register"]
        variation_money_columns = [
            variation_register.columns.get_loc(column)
            for column in ["submitted_amount", "approved_amount", "pending_amount"]
        ]
        for column_index in variation_money_columns:
            variation_sheet.set_column(column_index, column_index, 20, money_format)

    output.seek(0)
    return output.getvalue()
