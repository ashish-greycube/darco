// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Detailed Daily Sales Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label":__("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.add_days(frappe.datetime.nowdate(), -30)
		},
		{
			"fieldname": "to_date",
			"label":__("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.nowdate()
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			// "reqd": 1,
			"options": "Warehouse",
		},
		{
			"fieldname": "sales_partner",
			"label":__("Sales Partner"),
			"fieldtype": "Link",
			"options": "Sales Partner"
		},
		{
			"fieldname": "hide_return",
			"label":__("Hide Return"),
			"fieldtype": "Check"
		}
	]
};
