frappe.ui.form.on("Sales Invoice", {
    validate(frm){
        console.log("ON CHANGE")
        let total = frm.doc.total
        if (frm.doc.is_return == 1){
            console.log(total)
            frappe.model.set_value(frm.doc.payments[0].doctype, frm.doc.payments[0].name, "amount", total)
        }
    }
})