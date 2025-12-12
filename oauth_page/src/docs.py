# src/docs.py

from .templates import get_base_style  # Importa la función desde templates.py


def render_tools_docs_page() -> str:
    """Render the MCP Tools Documentation page"""
    html_content = (
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCP Tools Documentation</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        """
        + get_base_style()
        + """
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📘 Brief Tool Documentation – Zoho Books MCP Server</h1>
                <p style="color: #8b949e;">Focused purely on the output returned when each tool is invoked</p>
            </div>

            <div class="card">
                <h2>🧾 INVOICES</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_invoices</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns a list of invoices with pagination.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_invoice</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns full details of a specific invoice.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_invoice</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates an invoice and returns the new invoice ID + data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_invoice</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns the updated invoice data.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_invoice</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns confirmation of deletion.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>email_invoice</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms that the invoice email was sent.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_invoice_sent</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns invoice with status updated to "sent".</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_invoice_void</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns invoice with status "void".</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_invoice_payments</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns payments applied to an invoice.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>apply_credits_to_invoice</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns applied credits and remaining balance.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_invoice_attachment</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns the attachment file or its URL.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>add_invoice_attachment</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Uploads an attachment and returns confirmation.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>🧾 BILLS</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_bills</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of bills.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_bill</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns full bill details.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_bill</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates a bill and returns new ID + data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_bill</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns the updated bill.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_bill</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_bill_void</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Updates status to "void".</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_bill_open</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Updates status to "open".</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_bill_payments</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns payments applied to a bill.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>apply_credits_to_bill</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Applies credits and returns updated balance.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_bill_attachment</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns attachment or URL.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>add_bill_attachment</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Uploads attachment and confirms success.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>👥 CONTACTS</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_contacts</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of contacts.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_contact</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns full details of a contact.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_contact</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates a contact and returns ID + data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_contact</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated contact data.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_contact</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_contact_active</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Marks contact as active.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_contact_inactive</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Marks contact as inactive.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>add_contact_address</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns new address added.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_contact_address</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated address.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_contact_address</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>📦 ITEMS</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_items</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of items.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_item</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns item details.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_item</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates item and returns data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_item</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated item.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_item</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_item_details</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns extended item details.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_item_active</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Marks item as active.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_item_inactive</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Marks item as inactive.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>💸 EXPENSES</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_expenses</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of expenses.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns expense details.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates expense and returns data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated expense.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_expense_receipt</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns receipt file or URL.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_expense_receipt</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Uploads receipt and returns confirmation.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_expense_receipt</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Deletes receipt and returns confirmation.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>🔁 RECURRING EXPENSES</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_recurring_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates recurring expense and returns data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_recurring_expenses</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of recurring expenses.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_recurring_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns full recurring expense details.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_recurring_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated recurring expense.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_recurring_expense_using_custom_field</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated custom-field data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_recurring_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>stop_recurring_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Pauses recurrence.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>resume_recurring_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Resumes recurrence.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_child_expenses_of_recurring_expense</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns generated child expenses.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_recurring_expense_history</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns history of updates/changes.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>🧾 VENDOR PAYMENTS</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_vendor_payments</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of vendor payments.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_vendor_payment</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns vendor payment details.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_vendor_payment</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates payment and returns data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_vendor_payment</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated payment.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_vendor_payment</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>email_vendor_payment</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms email was sent.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>📄 ESTIMATES</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_estimates</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of estimates.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_estimate</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns full estimate details.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_estimate</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates estimate and returns data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_estimate</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated estimate.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_estimate</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_estimate_accepted</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Marks estimate as "accepted".</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>email_estimate</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms that email was sent.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>📦 SALES ORDERS</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_sales_orders</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of sales orders.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_sales_order</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns full sales order details.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_sales_order</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates order and returns data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_sales_order</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated order.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_sales_order</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_sales_order_as_void</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Marks as void.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>email_sales_order</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms email was sent.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>🛒 PURCHASE ORDERS</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_purchase_orders</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of purchase orders.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_purchase_order</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns purchase order details.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_purchase_order</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates order and returns data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_purchase_order</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated order.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_purchase_order</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_purchase_order_comments</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of comments.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>💳 CREDIT NOTES</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_credit_note</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates note and returns data.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_credit_notes</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of notes.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_credit_note</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns full details.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>update_credit_note</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns updated note.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>delete_credit_note</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms deletion.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>email_credit_note</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Confirms email sent.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_credit_note_void</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Marks as void.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_credit_note_draft</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Marks as draft.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>mark_credit_note_open</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Marks as open.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>submit_credit_note</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Submits for approval.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>approve_credit_note</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns approved status.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>👤 USERS</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_users</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of organization users.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_user</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns user details.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_current_user</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns authenticated user info.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>📁 PROJECTS</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_projects</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of projects.</td>
                        </tr>
                        <tr style="background-color: rgba(88, 166, 255, 0.05);">
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>get_project</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns project details.</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>create_project</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Creates project and returns data.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>📚 CHART OF ACCOUNTS</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #0d1117; color: #58a6ff;">
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Tool</th>
                            <th style="border: 1px solid #30363d; padding: 10px; text-align: left;">Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border: 1px solid #30363d; padding: 10px;"><code>list_chart_of_accounts</code></td>
                            <td style="border: 1px solid #30363d; padding: 10px;">Returns list of chart of accounts.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="btn btn-primary" style="font-size: 16px; padding: 12px 30px;">
                    ← Back to Dashboard
                </a>
            </div>

        </div>
    </body>
    </html>
    """
    )
    return html_content
