"""Excel export helpers for the Project Commercial Control System."""

from __future__ import annotations

from io import BytesIO

import pandas as pd

from cost_helpers import calculate_package_metrics, prepare_summary_dataframe


def create_excel_report(project_metadata: dict, package_frame: pd.DataFrame) -> bytes:
    """Create an in-memory Excel report with summary and package detail sheets."""
    output = BytesIO()
    package_details = calculate_package_metrics(package_frame)
    summary_metrics = prepare_summary_dataframe(package_frame)

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

        workbook = writer.book
        money_format = workbook.add_format({"num_format": '"Rp" #,##0'})
        percent_format = workbook.add_format({"num_format": "0.0%"})
        header_format = workbook.add_format(
            {"bold": True, "bg_color": "#EAF2F8", "border": 1}
        )

        for sheet_name, frame in {
            "Summary": summary_frame,
            "Package Details": package_details,
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
            if column not in {"package", "status", "certified_percent"}
        ]
        for column_index in money_columns:
            details_sheet.set_column(column_index, column_index, 20, money_format)

        percent_column = package_details.columns.get_loc("certified_percent")
        details_sheet.set_column(percent_column, percent_column, 18, percent_format)

    output.seek(0)
    return output.getvalue()
