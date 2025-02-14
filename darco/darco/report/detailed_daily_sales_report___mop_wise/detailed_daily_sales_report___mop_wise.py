# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	# print(report, '----------report---------------')
	if not filters: filters = {}
	columns, data = [], []

	mop = frappe.db.sql_list("select name from `tabMode of Payment` order by name asc")
	print(mop, "====mop")
	columns = get_columns(mop)
	data = get_data(filters, mop, columns)
	
	if not data:
		frappe.msgprint(_("No records found"))
		return columns,data
	
	return columns, data

# a = execute()
# print(a, "=============================aaaaaa")


def get_columns(mop):
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
			# {
			# 	"fieldname": "mode_of_payment",
			# 	"label":_("Mode of Payment"),
			# 	"fieldtype": "Data",
			# 	"width":'350'
			# },
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
			},
			{
				"fieldname": "outstanding_amount",
				"label":_("Outstanding Amount"),
				"fieldtype": "Currency",
				"width":'100'
			}
		]
	
	# for col in mop:
	# 	columns.append(
	# 			{
	# 			"fieldname": _(col),
	# 			"label":_(col),
	# 			"fieldtype": "Currency",
	# 			"width":'160'
	# 		})
	
	return columns


def get_data(filters, mop, columns):
	# print(columns, '------columns-----------')
	conditions = get_conditions(filters)
	data = frappe.db.sql("""
				SELECT
			si.posting_date as date,
			si.name as sales_invoice_no,
			si.outstanding_amount,
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
			si.docstatus!=2 and sii.idx = 1 and {conditions}
	""".format(conditions=conditions), as_dict=1)

	mop_data = frappe.db.sql("""SELECT
					sip.mode_of_payment ,
					sip.amount as mod_amout,
					sip.parent as sales_invoice_no
				FROM
					`tabSales Invoice` si
			inner join `tabSales Invoice Item` as sii on
				si.name = sii.parent						  
				inner join `tabSales Invoice Payment` sip on
					si.name = sip.parent
				where {0} and sip.amount != 0 and si.docstatus!=2 and sii.idx=1 """.format(conditions), filters, as_dict=1, debug=1)
	
	print('conditions',conditions)
	mop_list = frappe.db.sql("""SELECT
				sip.mode_of_payment
			FROM
				`tabSales Invoice` si
			inner join `tabSales Invoice Item` as sii on
				si.name = sii.parent						  
			inner join `tabSales Invoice Payment` sip on
				si.name = sip.parent
			where {0} and sip.amount != 0 and si.docstatus!=2 and sii.idx=1 
			group by sip.mode_of_payment""".format(conditions), filters, as_dict=1, debug=0)
	

	print(mop_list, "=======mop_list")
	
	for mop_1 in mop_list:
		mop_type = mop_1.get('mode_of_payment') 
		columns.append(
						{
						"fieldname": _(mop_type),
						"label":_(mop_type),
						"fieldtype": "Currency",
						"width":'160'
					})
	my_mop_value=0
	for main_row in data:
		for mop_row in mop_data:
			for mop_type in mop_list:
				mop_col =  mop_type.get('mode_of_payment')
				if mop_row.get('mode_of_payment') == mop_col and mop_row.get('sales_invoice_no') == main_row.get('sales_invoice_no'):
					main_row.update({_(mop_col): mop_row['mod_amout']})
					if mop_row.get('mode_of_payment') == 'شبكه بنك الراجحي الرئيسي':
						my_mop_value += mop_row['mod_amout']
	print(my_mop_value, "=======my_mop_value")
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

	if filters.si_type == "Only Return":
		conditions += " and si.is_return = 1"
	elif filters.si_type == "Only Sales invoice":
		conditions += " and si.is_return = 0"
	else:
		conditions += " and si.is_return in (0,1)"

	return conditions