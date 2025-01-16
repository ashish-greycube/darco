# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters: filters = {}
	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)
	
	if not data:
		frappe.msgprint(_("No records found"))
		return columns,data
	
	return columns, data

def get_columns():
	columns = [
			{
				"fieldname": "date",
				"label":_("Date"),
				"fieldtype": "Date",
				"width":'150'
			},
			{
				"fieldname": "sales_invoice_no",
				"label":_("Sales Invoice No"),
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width":'150'
			},
			{
				"fieldname": "customer_name",
				"label":_("Customer Name"),
				"fieldtype": "Link",
				"options": "Customer",
				"width":'200'
			},
			{
				"fieldname": "grand_total",
				"label":_("Grand Total"),
				"fieldtype": "Currency",
				"width":'100'
			},
			{
				"fieldname": "sales_partner",
				"label":_("Sales Partner"),
				"fieldtype": "Link",
				"options": "Sales Partner",
				"width":'200'
			},
			{
				"fieldname": "mode_of_payment",
				"label":_("Mode of Payment"),
				"fieldtype": "Data",
				"width":'350'
			},
			{
				"fieldname": "warehouse",
				"label":_("Warehouse"),
				"fieldtype": "Link",
				"options": "Warehouse",
				"width":'150'
			},
			{
				"fieldname": "is_return",
				"label":_("Is Return"),
				"fieldtype": "Select",
				"options": "Yes\nNo",
				"width":'100'
			}
		]
	
	return columns

def get_data(filters):
	conditions = get_conditions(filters)
	data = frappe.db.sql("""
				SELECT
			si.posting_date as date,
			si.name as sales_invoice_no,
			si.customer_name ,
			si.grand_total ,
			si.sales_partner,
			sii.warehouse ,
			si.is_return
		FROM
			`tabSales Invoice` as si
		left outer join `tabSales Invoice Item` as sii on
			si.name = sii.parent
		where
			sii.idx = 1 and {conditions}
	""".format(conditions=conditions), as_dict=1)

	if len(data) > 0:
		for row in data:
			mode_of_payment_list = frappe.get_list("Sales Invoice Payment", filters={"parent": row.sales_invoice_no}, fields=["mode_of_payment"])
			if len(mode_of_payment_list) > 0:
				row["mode_of_payment"] = " , ".join((ele.mode_of_payment if ele.mode_of_payment!=None else '') for ele in mode_of_payment_list)

	return data

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "si.posting_date between {0} and {1}".format(
				frappe.db.escape(filters.get("from_date")),
				frappe.db.escape(filters.get("to_date")))
		else:
			frappe.throw(_("To Date should be greater then From Date"))

	if filters.warehouse:
		conditions += " and sii.warehouse = '{0}'".format(filters.warehouse)

	if filters.sales_partner:
		conditions += " and si.sales_partner = '{0}'".format(filters.sales_partner)
		
	if filters.hide_return == 1:
		conditions += " and si.is_return = 0"

	return conditions