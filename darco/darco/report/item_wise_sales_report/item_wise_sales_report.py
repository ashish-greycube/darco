# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.report.item_wise_sales_register.item_wise_sales_register import execute as _execute

def execute(filters=None):
	sales_register_report = _execute(filters)
	columns = sales_register_report[0]
	data = sales_register_report[1]
	
	# Add new columns
	columns.insert(21, {
		"label": _("Valuation Rate"),
		"fieldname": "valuation_rate",
		"fieldtype": "Currency",
		"options": "currency",
		"width": 100
	})

	# Add valuation rate to each row
	for row in data:	
		valuation_rate = frappe.db.get_value("Item", row.get("item_code"), "valuation_rate")
		row.update({"valuation_rate": valuation_rate})
	return columns, data