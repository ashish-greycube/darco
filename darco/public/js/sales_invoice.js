frappe.ui.form.on("Sales Invoice", {
    // validate(frm){
    //     console.log("111ON start CHANGE")
    //     return set_payment_amt(frm)
    //     console.log("444end CHANGE")

    // }
    onload(frm){
        if (frm.is_new() && frm.doc.docstatus == 0) {
            if(frm.doc.is_return == 1 ){
                frm.set_value("update_stock", 1)
            }
            else{
                frm.set_value("update_stock", 0)
            }        
        }

    },
    is_return (frm) {
        console.log("IS RETURN")
        empty_payment_table(frm)
    },

    is_pos (frm) {
        empty_payment_table(frm)
        
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

function empty_payment_table(frm){
    let is_pos = frm.doc.is_pos
    if (is_pos == 0){
        frm.set_value("payments",[])
    }
    let is_return = frm.doc.is_return
    frm.set_value("update_stock", is_return)
}

frappe.ui.form.on("Sales Invoice Item", {
    item_code(frm, cdt, cdn){
        set_amount_zero_in_payment(frm)
    },
    qty(frm, cdt, cdn){
        set_amount_zero_in_payment(frm)
    },
    rate(frm, cdt, cdn){
        set_amount_zero_in_payment(frm)
    },    
})

function set_amount_zero_in_payment(frm){
    setTimeout(() => {
        if (frm.is_new()){
            if (frm.doc.payments.length > 0){
                frappe.model.set_value(frm.doc.payments[0].doctype, frm.doc.payments[0].name, "amount", 0)
            }
        }
    }, 100);
    frappe.show_alert('Set amount in Payments table manually', 5);
}