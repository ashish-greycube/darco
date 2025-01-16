# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if not filters: filters = {}

	mop = frappe.db.sql_list("select name from `tabMode of Payment` order by name asc")
	columns, data = [], []

	columns = get_columns(mop)
	data = get_data(filters, mop)
	
	if not data:
		frappe.msgprint(_("No records found"))
		return columns,data
	
	return columns, data

def get_columns(mop):
	columns = [
			{
				"fieldname": "warehouse",
				"label":_("Warehouse Name"),
				"fieldtype": "Link",
				"options": "Warehouse",
				"width":'350'
			},
			{
				"fieldname": "total_sales",
				"label":_("Total Sales"),
				"fieldtype": "Currency",
				"width":'200'
			},
			{
				"fieldname": "total_return",
				"label":_("Total Return"),
				"fieldtype": "Currency",
				"width":'200'
			},
			{
				"fieldname": "net_sales",
				"label":_("Net Sales"),
				"fieldtype": "Currency",
				"width":'200'
			}
		]
	
	for col in mop:
		columns.append(
				{
				"fieldname": _(col),
				"label":_(col),
				"fieldtype": "Currency",
				"width":'160'
			})

	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "DATE(si.creation) between {0} and {1}".format(
                frappe.db.escape(filters.get("from_date")),
                frappe.db.escape(filters.get("to_date")))       
		else:
			frappe.throw(_("To Date should be greater then From Date"))
	
	if filters.warehouse:
		conditions += " and sit.warehouse = '{0}'".format(filters.warehouse)

	if filters.sales_partner:
		conditions += " and si.sales_partner = '{0}'".format(filters.sales_partner)

	return conditions

def get_data(filters, mop):
	conditions = get_conditions(filters)
	data = []

	si = frappe.db.sql("""
			SELECT
				IFNULL(sit.warehouse ,'') as warehouse,
				sum(si.grand_total) as total_sales
			FROM
				`tabSales Invoice` si
			inner join `tabSales Invoice Item` sit on sit.parent = si.name 
			where
				{0} and si.is_return = 0 
			group by
				sit.warehouse 
		""".format(conditions), filters, as_dict=1)
	
	print(si, "=======si")
	
	return_si = frappe.db.sql("""
			SELECT
				IFNULL(sit.warehouse ,'') as warehouse,
				sum(si.grand_total) as total_return
			FROM
				`tabSales Invoice` si
			inner join `tabSales Invoice Item` sit on sit.parent = si.name 
			where
				{0} and si.is_return = 1
			group by
				sit.warehouse
		""".format(conditions), filters, as_dict=1)
	
	print(return_si, "===return_si")

	for row in si:
		return_si_found = False
		for credit in return_si:
			if row.warehouse == credit.warehouse:
				data.append({
					"warehouse": row.warehouse,
					"total_sales": row.total_sales,
					"total_return": credit.total_return,
					"net_sales": row.total_sales + credit.total_return
				})
				return_si_found = True
				break

		if return_si_found == False:
			data.append({
				"warehouse": row.warehouse,
				"total_sales": row.total_sales,
				"total_return": 0,
				"net_sales": row.total_sales
			})
	
	mop_data = frappe.db.sql("""SELECT
					IFNULL(sit.warehouse,'') as warehouse,
					sip.mode_of_payment ,
					sum(sip.amount) as mod_amout
				FROM
					`tabSales Invoice` si
				left outer join `tabSales Invoice Payment` sip on
					si.name = sip.parent
				inner join `tabSales Invoice Item` sit on sit.parent = si.name
				where {0}
				group by
					sit.warehouse,
					sip.mode_of_payment""".format(conditions), filters, as_dict=1)

	print(data, '========data')

	for main_row in data:
		for mop_row in mop_data:
			if main_row.get('warehouse') == mop_row.get('warehouse'):
				for mop_type in mop:
					if mop_row.get('mode_of_payment') == mop_type:
						# print(main_row,'mainrow')
						main_row.update({_(mop_type): mop_row['mod_amout']})

	return data