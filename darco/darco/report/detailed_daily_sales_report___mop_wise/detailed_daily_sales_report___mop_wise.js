// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Detailed Daily Sales Report - MOP Wise"] = {
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
			"fieldname": "si_type",
			"label":__("SI Type"),
			"fieldtype": "Select",
			"options": "Both\nOnly Return\nOnly Sales invoice",
			"default": "Both"
		},
	]
};
