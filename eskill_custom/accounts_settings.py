"Collection of methods to be used in the Accounts Settings document."

from __future__ import unicode_literals

from re import search

import frappe
from frappe import _

@frappe.whitelist()
def set_customer_debtors(company: str):
    "Sets debtors' control account for customers."

    customers_without_account = frappe.db.sql(
        f"""select
            name
        from
            `tabCustomer`
        where
            name not in (
                select
                    parent
                from
                    `tabParty Account`
                where
                    company = '{company}'
                    and parenttype = 'Customer'
            );"""
    )
    customers_without_account = [customer[0] for customer in customers_without_account]

    debtors_accounts = frappe.db.sql(
        f"""select
            name,
            account_currency currency
        from
            tabAccount
        where
            not disabled
            and company = '{company}'
            and debtors_account;""",
        as_dict=True
    )
    debtors_accounts = {account['currency']: account['name'] for account in debtors_accounts}

    failed_customers = list()

    for customer_name in customers_without_account:
        customer = frappe.get_doc("Customer", customer_name)
        if customer.default_currency in debtors_accounts:
            customer.append("accounts", {
                'account': debtors_accounts[customer.default_currency],
                'company': company
            })
            customer.save(ignore_permissions=True)
        else:
            failed_customers.append("<li>{}: {} | {}</li>".format(
                customer.name,
                customer.customer_name,
                customer.default_currency
            ))

    if len(failed_customers) > 0:
        message = (
            "The following customers could not have their account "
            "set as there are no debtors' accounts with their currency:<br>"
        )
        for customer in failed_customers:
            message += customer
        frappe.msgprint(_(message))
    else:
        frappe.msgprint(_("All customers have a debtors' control account set."))


@frappe.whitelist()
def create_secondary_customers(base_currency: str, currency: str):
    "Creates secondary custoer accounts based on the selected currency."

    def set_contact_details(doctype: str, previous_customer: str, customer: str):
        documents = frappe.get_all(
            "Dynamic Link",
            filters={
                'link_name': previous_customer,
                'parenttype': doctype
            },
            pluck="parent"
        )
        for document in documents:
            current_document = frappe.get_doc(doctype, document)
            current_document.append("links", {
                'link_doctype': "Customer",
                'link_name': customer
            })
            current_document.save(
                ignore_permissions=True
            )


    main_customers = frappe.get_all(
        "Customer",
        filters={
            'default_currency': base_currency,
            'disabled': 0
        },
        pluck="name"
    )

    customers_already_provisioned = frappe.get_all(
        "Customer",
        filters={
            'default_currency': currency,
            'disabled': 0
        },
        pluck="main_account"
    )

    try:
        debtors_account = frappe.db.sql(f"""
        select
            name
        from
            tabAccount
        where
            account_currency = '{currency}'
            and debtors_account is true
        limit 1;""")[0][0]
    except IndexError:
        frappe.throw(_(
            "Please configure a debtors control account for "
            "the selected currency before creating customers."
        ))

    meta = frappe.get_meta("Customer")
    fields = [
        field.fieldname
        for field in meta.fields
        if field.fieldtype not in (
            "Column Break",
            "Section Break",
            "Table"
        )
    ]


    rename_list = []
    for customer in main_customers:
        if customer in customers_already_provisioned:
            continue
        old_customer = frappe.get_doc("Customer", customer)
        new_customer = frappe.new_doc("Customer")
        for field in fields:
            if hasattr(old_customer, field):
                setattr(new_customer, field, getattr(old_customer, field))
        new_customer.main_account = customer
        new_customer.default_currency = currency
        for account in old_customer.accounts:
            new_customer.append("accounts", {
                'account': debtors_account,
                'company': account.company
            })

        if search(r"^[A-Z]{3}-\d{3}-[A-Z]{2}$", old_customer.name):
            new_name = old_customer.name.split("-")[:2]
            new_name = "-".join(new_name) + "-" + currency[:2]
            rename_list.append((new_customer.name, new_name))
            new_customer.insert(
                ignore_permissions=True,
                ignore_if_duplicate=True,
                set_name=new_name
            )
            new_customer = frappe.get_doc("Customer", new_name)
        else:
            new_customer.insert(
                ignore_permissions=True,
                ignore_if_duplicate=True
            )

        for doc in ("Address", "Contact"):
            set_contact_details(doc, old_customer.name, new_customer.name)
