from datetime import date
from html import escape

from playwright.sync_api import sync_playwright


def _money(value):
    return f"${value:,.2f}"


def _table_rows(rows):
    return "\n".join(
        f"""
        <tr>
          <td>{row["id"]}</td>
          <td>{escape(row["customer"])}</td>
          <td>{escape(row["product"])}</td>
          <td class="number">{_money(row["amount"])}</td>
          <td>{escape(row["created_at"])}</td>
        </tr>
        """
        for row in rows
    )


def _top_product_rows(rows):
    return "\n".join(
        f"""
        <tr>
          <td>{escape(row["product"])}</td>
          <td class="number">{row["order_count"]}</td>
          <td class="number">{_money(row["revenue"])}</td>
        </tr>
        """
        for row in rows
    )


def _daily_rows(rows):
    return "\n".join(
        f"""
        <tr>
          <td>{escape(row["day"])}</td>
          <td class="number">{row["order_count"]}</td>
          <td class="number">{_money(row["revenue"])}</td>
        </tr>
        """
        for row in rows
    )


def build_report_html(report_data):
    summary = report_data["summary"]

    return f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Sales Report</title>
        <style>
          @page {{
            size: A4;
            margin: 18mm 14mm;
          }}

          body {{
            color: #172026;
            font-family: Arial, sans-serif;
            font-size: 12px;
            line-height: 1.45;
          }}

          h1, h2 {{
            margin: 0;
          }}

          h1 {{
            font-size: 28px;
          }}

          h2 {{
            font-size: 16px;
            margin-top: 28px;
            margin-bottom: 10px;
          }}

          .muted {{
            color: #5d6b75;
          }}

          .summary {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 22px;
          }}

          .metric {{
            border: 1px solid #d7dde2;
            padding: 12px;
          }}

          .metric-label {{
            color: #5d6b75;
            font-size: 11px;
            text-transform: uppercase;
          }}

          .metric-value {{
            font-size: 22px;
            font-weight: 700;
            margin-top: 6px;
          }}

          table {{
            border-collapse: collapse;
            width: 100%;
          }}

          thead {{
            display: table-header-group;
          }}

          tr {{
            break-inside: avoid;
          }}

          th {{
            background: #eef2f4;
            color: #172026;
            font-weight: 700;
            text-align: left;
          }}

          th, td {{
            border: 1px solid #d7dde2;
            padding: 7px 8px;
          }}

          .number {{
            text-align: right;
          }}
        </style>
      </head>
      <body>
        <h1>Sales Report</h1>
        <p class="muted">Generated on {date.today().isoformat()}</p>

        <section class="summary">
          <div class="metric">
            <div class="metric-label">Total Orders</div>
            <div class="metric-value">{summary["total_orders"]}</div>
          </div>
          <div class="metric">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">{_money(summary["total_revenue"])}</div>
          </div>
          <div class="metric">
            <div class="metric-label">Average Order</div>
            <div class="metric-value">{_money(summary["average_order_value"])}</div>
          </div>
        </section>

        <h2>Top Products</h2>
        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th class="number">Orders</th>
              <th class="number">Revenue</th>
            </tr>
          </thead>
          <tbody>{_top_product_rows(report_data["top_products"])}</tbody>
        </table>

        <h2>Orders In The Last 7 Days</h2>
        <table>
          <thead>
            <tr>
              <th>Day</th>
              <th class="number">Orders</th>
              <th class="number">Revenue</th>
            </tr>
          </thead>
          <tbody>{_daily_rows(report_data["orders_by_day"])}</tbody>
        </table>

        <h2>All Orders</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Customer</th>
              <th>Product</th>
              <th class="number">Amount</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>{_table_rows(report_data["rows"])}</tbody>
        </table>
      </body>
    </html>
    """


def render_report_pdf(report_data, output_path):
    html = build_report_html(report_data)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(path=str(output_path), format="A4", print_background=True)
        browser.close()
