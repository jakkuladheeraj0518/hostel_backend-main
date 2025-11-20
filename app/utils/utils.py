import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
from openpyxl import Workbook

def generate_pdf_report(data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)

    y = 750
    c.drawString(50, y, f"Report: {data.get('name', 'Unnamed')}")
    y -= 30

    result_data = data.get("result_data", {})

    # Summary section
    summary = result_data.get("summary", {})
    c.drawString(50, y, "Summary:")
    y -= 20
    for k, v in summary.items():
        c.drawString(60, y, f"{k}: {v}")
        y -= 18

    # Add some spacing before next section
    y -= 20

    # By Hostel section
    by_hostel = result_data.get("by_hostel", [])
    if by_hostel:
        c.drawString(50, y, "By Hostel:")
        y -= 20
        headers = list(by_hostel[0].keys())
        header_line = " | ".join(headers)
        c.drawString(60, y, header_line)
        y -= 18

        for row in by_hostel:
            line = " | ".join(str(row.get(h, "")) for h in headers)
            c.drawString(60, y, line[:100])  # limit line width
            y -= 18
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = 750

    c.save()
    buffer.seek(0)
    return buffer


def generate_csv_report(data: dict) -> io.BytesIO:
    summary = data.get("result_data", {}).get("summary", {})
    by_hostel = data.get("result_data", {}).get("by_hostel", [])

    csv_buffer = io.StringIO()

    # Write summary as key-value pairs
    if summary:
        df_summary = pd.DataFrame([summary])
        df_summary = df_summary.melt(var_name="Key", value_name="Value")  # reshape to two columns
        df_summary.to_csv(csv_buffer, index=False)
        csv_buffer.write("\n")  # blank line between tables

    # Write by_hostel table
    if by_hostel:
        df_hostel = pd.DataFrame(by_hostel)
        df_hostel.to_csv(csv_buffer, index=False)

    bytes_buffer = io.BytesIO(csv_buffer.getvalue().encode("utf-8"))
    bytes_buffer.seek(0)
    return bytes_buffer


def generate_excel_report(data: dict) -> io.BytesIO:
    wb = Workbook()
    
    # Summary sheet
    ws_summary = wb.active
    ws_summary.title = "Summary"
    summary = data.get("result_data", {}).get("summary", {})
    ws_summary.append(["Key", "Value"])
    for k, v in summary.items():
        ws_summary.append([k, v])

    # By Hostel sheet
    by_hostel = data.get("result_data", {}).get("by_hostel", [])
    ws_hostel = wb.create_sheet(title="By Hostel")
    if by_hostel:
        headers = list(by_hostel[0].keys())
        ws_hostel.append(headers)
        for row in by_hostel:
            ws_hostel.append([row.get(h, "") for h in headers])
    else:
        ws_hostel.append(["No data available"])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
