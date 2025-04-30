# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.report.item_wise_sales_register.item_wise_sales_register import execute as _execute
from erpnext.stock.report.stock_ledger.stock_ledger import get_stock_ledger_entries
from frappe.utils import cint, flt

def execute(filters=None):
	precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))
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
	print("="*10)
	print(filters)
	sl_filters=frappe._dict({"company":filters.get("company"),"from_date":filters.get("from_date"),"to_date":filters.get("to_date"),"valuation_field_type":"Currency"})
	for row in data:
		sl_filters["voucher_no"] = row.get("invoice")	
		items=row.get("item_code")
		valuation_rate = get_valuation_rate_for_si(sl_filters, [items],precision)
		row.update({"valuation_rate": valuation_rate})
	return columns, data

def get_valuation_rate_for_si(sl_filters,items,precision):
	valuation_rate=0
	
	sl_entries = get_stock_ledger_entries(sl_filters, items)
	for sle in sl_entries:
		if sle.actual_qty:
			valuation_rate = flt(sle.stock_value_difference / sle.actual_qty, precision)
		elif sle.voucher_type == "Stock Reconciliation":
			valuation_rate = sle.valuation_rate
	return valuation_rate