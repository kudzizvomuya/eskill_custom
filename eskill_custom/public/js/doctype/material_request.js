frappe.ui.form.on("Material Request", {
    after_cancel(frm) {
        if (frm.doc.service_order) {
            frappe.call({
                method: "eskill_custom.material_request.cancel_part_request",
                args: {
                    document: frm.doc.name
                }
            })
        }
    }
})