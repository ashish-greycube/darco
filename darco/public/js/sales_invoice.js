frappe.ui.form.on("Sales Invoice", {
    // validate(frm){
    //     console.log("111ON start CHANGE")
    //     return set_payment_amt(frm)
    //     console.log("444end CHANGE")

    // }
    onload(frm){
        if(frm.doc.is_return == 1 && frm.doc.docstatus == 0){
            frm.set_value("update_stock", 1)
        }
        else{
            frm.set_value("update_stock", 0)
        }
    },
    is_return (frm) {
        let is_return = frm.doc.is_return
        frm.set_value("update_stock", is_return)
    }
})


function set_payment_amt(frm) {
    return new Promise((resolve, reject) => {
        let total = frm.doc.total
        if (frm.doc.is_return == 1){

            console.log('222inside',total)
            frappe.model.set_value(frm.doc.payments[0].doctype, frm.doc.payments[0].name, "amount", total)
            resolve(1)
        } else{
            resolve(1)
        }
        console.log('333inside',total)
    })
  
}