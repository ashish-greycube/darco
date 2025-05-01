# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters: filters = {}

	columns, data = [], []

	warehouse = frappe.db.sql_list("SELECT tw.name FROM `tabWarehouse` tw")

	columns = get_columns(warehouse)
	data = get_data(filters, warehouse)
	
	if not data:
		frappe.msgprint(_("No records found"))
		return columns,data
	
	return columns, data

def get_columns(warehouse):
	columns = [
		{
			"fieldname": "item_code",
			"label":_("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width":'150'
		},
		{
			"fieldname": "item_name",
			"label":_("Item Name"),
			"fieldtype": "Data",
			"width":'150'
		},
		{
			"fieldname": "item_group",
			"label":_("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"width":'150'
		},
	]

	for col in warehouse:
		columns.append(
				{
				"fieldname": _(col),
				"label":_(col),
				"fieldtype": "Float",
				"width":'150',
				'precision': 2
			})

	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get('item_code'):
		conditions += " and ti.item_code = '{0}'".format(filters.get('item_code'))

	if filters.get('item_group'):
		conditions += " and ti.item_group = '{0}'".format(filters.get('item_group'))

	return conditions

def get_data(filters, warehouse):
	data = []

	conditions = get_conditions(filters)

	data = frappe.db.sql(""" SELECT 
					   ti.item_code, ti.item_name , ti.item_group  
					   FROM  `tabItem` ti 
					   WHERE ti.is_stock_item = 1 {0}
					""".format(conditions), filters, as_dict=1,)
	
	for row in data:
		item_details = frappe.db.get_all( "Bin",
				fields=[
					"item_code",
					"warehouse",
					"actual_qty",
				],
				filters={
					'item_code': row.item_code
				},
			)

		if len(item_details) > 0:
			for detail in item_details:
				for col in warehouse:
					if _(col) == detail.warehouse:
						row.update({_(col): detail.get('actual_qty')})
	return data