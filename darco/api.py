import frappe
from frappe import _


def change_delivery_status_in_si(self,method):
    si_found = False
    if len(self.items)>0:
        for row in self.items:
            if row.against_sales_invoice:
                si_found = True
                frappe.db.set_value("Sales Invoice",row.against_sales_invoice,"custom_delivery_status","Yes")
        
    if si_found == True:
        frappe.msgprint(_("Delivery Status in connected sales invoice is updated"),alert=True)

def validate_qty_against_available_qty(self, method):
    check_available_qty = frappe.db.get_single_value("Darco Settings","check_available_qty")
    if check_available_qty == 1:
        if len(self.items)>0:
            for row in self.items:
                maintain_stock = frappe.db.get_value("Item",row.item_code,"is_stock_item")
                if maintain_stock == 1:
                    if row.qty > row.actual_qty:
                        frappe.throw(_("#Row {0} : Qty cannot be greater than available qty {1}".format(row.idx,row.actual_qty)))

def set_payment_amount(self, method):
    print("Before Validate of ours")
    if self.is_return == 1 :
        if self.total:
            if len(self.payments)>0:
                for row in self.payments:
                    if  row.amount == 0:
                        row.amount = self.total
            self.run_method("before_save")
        
def validate_mop_amount(self,method):
    total_mop_amount = 0
    if len(self.payments)>0:
        for row in self.payments:
            total_mop_amount = total_mop_amount + row.amount
        
    if self.total:
        if self.is_return == 0:
            if self.total < total_mop_amount:
                frappe.throw(_("Total of Mode of Payment amount cannot be greater than {0}".format(self.total)))