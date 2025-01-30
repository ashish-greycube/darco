# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.report.sales_register.sales_register import execute as sales_register_execute


def execute(filters=None):
	if not filters: filters = {}

	mop = frappe.db.sql_list("select name from `tabMode of Payment` order by name asc")
	columns, data = [], []

	columns = get_columns(mop)
	data = get_data(filters, mop, columns)
	
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
			},
			{
				"fieldname": "outstanding_amount",
				"label":_("Outstanding"),
				"fieldtype": "Currency",
				"width":'200'
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

def get_conditions(filters):
	conditions = ""

	if filters.get("from_date") and filters.get("to_date"):
		if filters.get("to_date") >= filters.get("from_date"):
			conditions += "DATE(si.posting_date) between {0} and {1}".format(
                frappe.db.escape(filters.get("from_date")),
                frappe.db.escape(filters.get("to_date")))       
		else:
			frappe.throw(_("To Date should be greater then From Date"))
	
	if filters.warehouse:
		conditions += " and sii.warehouse = '{0}'".format(filters.warehouse)

	# if filters.sales_partner:
	# 	conditions += " and si.sales_partner = '{0}'".format(filters.sales_partner)

	return conditions

def get_data(filters, mop, columns):
	print(filters, '===filters')
	conditions = get_conditions(filters)
	data = []
	report_filters = frappe._dict({
		"from_date": filters.get("from_date"),
		"to_date": filters.get("to_date"),
		"warehouse": filters.get("warehouse")
	})

	report = sales_register_execute(report_filters)
	print('report-----------------------',report)
	print(report[1], '===report_data', len(report[1]),type(report[1]))
	report_data = report[1]
	if len(report_data) == 0:
		return data
	invoice_list=[]
	for row in report_data:
		print(type(row), '===row',row)
		sales_partner = frappe.db.get_value("Sales Invoice", row.get('voucher_no'), "sales_partner")
		invoice_list.append(row.get('voucher_no'))
		row['sales_partner'] = sales_partner
		print(row, '===row')
	
	total_sales = 0
	total_return = 0
	total_outstanding_amount = 0
	for item in report_data:
		
		# print(item, '===item',type(item))
		if filters.get("sales_partner"):
			if item.get("sales_partner") == filters.get("sales_partner"):
				print(item.get('voucher_no'), '===voucher_no')
				if item.get("net_total") >=0 :
					total_sales += item.get("net_total")
				elif item.get("net_total") < 0:
					print(item.get("net_total"), '===',1)
					total_return += item.get("net_total")
					print(total_return)
		else:
			if item.get("net_total") >=0 :
					total_sales += item.get("net_total")
			elif item.get("net_total") < 0:
				print(item.get("net_total"), '===',1)
				total_return += item.get("net_total")
				print(total_return)
		total_outstanding_amount += item.get("outstanding_amount")

	net_sales = total_sales + total_return
	data.append({
		"warehouse": filters.get("warehouse"),
		"total_sales": total_sales,
		"total_return": total_return,
		"net_sales": net_sales,
		"outstanding_amount": total_outstanding_amount
	})

	mop_list = frappe.db.sql("""SELECT
					sip.mode_of_payment,sum(sip.amount) as mop_amount,count(si.name) as invoice_count
				FROM
					`tabSales Invoice` si
				inner join `tabSales Invoice Item` as sii on
					si.name = sii.parent						  
				inner join `tabSales Invoice Payment` sip on
					si.name = sip.parent
				where si.name in ({0}) and {1}
				and sip.amount != 0 and si.docstatus!=2 and sii.idx=1 and sip.mode_of_payment is not NULL
				group by
					sip.mode_of_payment""".format(",".join(["%s"] * len(invoice_list)),conditions),tuple(invoice_list),as_dict=True,debug=1)
	for main_row in data:
		for mop_type in mop_list:
			print(mop_type, '===mop_type')
			mop_type_value=mop_type.get('mode_of_payment')
			# print(mop_type, '===mop_type')
			# mop_report_filters = frappe._dict({
			# 	"from_date": filters.get("from_date"),
			# 	"to_date": filters.get("to_date"),
			# 	"warehouse": filters.get("warehouse"),
			# 	"mode_of_payment": mop_type_value
			# })
			# print(mop_report_filters, '===mop_report_filters')
			# mop_report_data = list(sales_register_execute(mop_report_filters))
			# total_mop_amount=0
			# if len(mop_report_data) > 0 and mop_report_data[1] and len(mop_report_data[1]) > 0:
			# 	for mop_report_row in mop_report_data[1]:
			# 		total_mop_amount += mop_report_row.get('grand_total')
			# 	if total_mop_amount>0:

			columns.append(
								{
								"fieldname": _(mop_type_value),
								"label":_(mop_type_value),
								"fieldtype": "Currency",
								"width":'160'
							})		
			main_row.update({_(mop_type_value): mop_type.get('mop_amount')})	

	return data