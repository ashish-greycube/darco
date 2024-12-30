# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import erpnext



def execute(filters=None):
	columns, data = [], []

	columns = get_columns()
	report_data= get_data(filters)
	
	if not report_data:
		frappe.msgprint(_("No records found"))
		return columns,report_data
	
	return columns, report_data


def get_columns():
	currency_symbol=' ('+erpnext.get_default_currency()+')'
	return [
		{
			"fieldname": "so_reference",
			"label":_("SO Reference"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width":'350'
		},
		{
			"fieldname": "date",
			"label":_("Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "total_amount",
			"label":_("Total Amount "+currency_symbol),
			"fieldtype": "Currency",
			"width":'200'
		},
		{
			"fieldname": "total_cost",
			"label":_("Total Cost"),
			"fieldtype": "Currency",
			"width":'200'
		},
		{
			"fieldname": "profit_amount",
			"label":_("Profit Amount"+currency_symbol),
			"fieldtype": "Data",
			"width":'200'
		},
		{
			"fieldname": "profit",
			"label":_("Profit %"),
			"fieldtype": "Percent",
			"width":'200'
		},
		{
			"fieldname": "sales_partner",
			"label":_("Sales Partner"),
			"fieldtype": "Link",
			"options": "Sales Partner"
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)
	so_data = frappe.db.sql("""
					SELECT
				name as so_reference,
				transaction_date as date,
				net_total as total_amount,
				sales_partner
			FROM
				`tabSales Order`
			Where {0}
		""".format(conditions),filters,as_dict=1,debug=1)
	print(so_data)

	if len(so_data)>0:
		for row in so_data:
			total_cost = 0
			connected_jv = frappe.db.get_all("Journal Entry",
									filters={"docstatus":1,"custom_so_reference":row.so_reference},
									fields=["sum(total_credit) as total_credit"],group_by="custom_so_reference")
			if len(connected_jv)>0:
				total_cost = total_cost + connected_jv[0].total_credit
			
			connected_expense_entry = frappe.db.get_all("Expense Entry",
											   filters={"docstatus":1,"so_reference":row.so_reference},
											   fields=["sum(total_amount) as total_amount"],group_by="so_reference")

			if len(connected_expense_entry)>0:
				total_cost = total_cost + connected_expense_entry[0].total_amount
			
			connected_purchase_invoice = frappe.db.get_all("Purchase Invoice",
												  filters={"docstatus":1,"custom_so_reference":row.so_reference},
												  fields=["sum(total) as total"],group_by="custom_so_reference")

			if len(connected_purchase_invoice)>0:
				total_cost = total_cost + connected_purchase_invoice[0].total

			row["total_cost"] = total_cost
			row["profit_amount"] = row.total_amount - total_cost
			row["profit"] = (row.profit_amount / row.total_amount) * 100

	return so_data

def get_conditions(filters):
	conditions =""

	if filters.from_date:
		conditions += " transaction_date >= %(from_date)s"

	if filters.to_date:
		conditions += " and transaction_date <= %(to_date)s"

	if filters.customer:
		conditions += " and customer = %(customer)s"
	
	if filters.sales_partner:
		conditions += " and sales_partner = %(sales_partner)s"
	
	return conditions