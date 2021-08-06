# Copyright (c) 2013, Eskill Trading and contributors
# For license information, please see license.txt

from datetime import date

import frappe
from frappe import _


def execute(filters=None):
    "Main function."

    columns = []
    columns.extend(get_columns(filters))

    data = []
    data.extend(get_data(filters, columns))

    for index, record in enumerate(data):
        for col in columns:
            if col['fieldname'] not in record:
                data[index][col['fieldname']] = ""

    chart = get_chart_data(filters, data, columns)

    return columns, data, None, chart


def get_columns(filters: 'dict[str, ]'):
    "Returns a list of columns."

    columns = [
        {
            'fieldname': "posting_date",
            'label': _("Posting Date"),
            'fieldtype': "Date",
            'width': 105
        },
        {
            'fieldname': "due_date",
            'label': _("Due Date"),
            'fieldtype': "Date",
            'width': 105,
            'hidden': 0 if "show_due_date" in filters else 1
        },
        {
            'fieldname': "customer",
            'label': _("Customer"),
            'fieldtype': "Link",
            'options': "Customer",
            'width': 300
        },
        {
            'fieldname': "customer_code",
            'label': _("Customer Code"),
            'fieldtype': "Text",
            'width': 115
        },
        {
            'fieldname': "currency",
            'label': _("Account Currency"),
            'fieldtype': "Link",
            'options': "Currency"
        },
        {
            'fieldname': "voucher_type",
            'label': _("Voucher Type"),
            'fieldtype': "Data",
        },
        {
            'fieldname': "voucher_no",
            'label': _("Voucher No"),
            'fieldtype': "Dynamic Link",
            'options': "voucher_type",
            'width': 120
        },
        {
            'fieldname': 'cost_center',
            'label': _("Cost Center"),
            'fieldtype': "Link",
            'options': "Cost Center",
            'hidden': 0 if "show_cost_center" in filters else 1
        },
        {
            'fieldname': 'customer_group',
            'label': _("Customer Group"),
            'fieldtype': "Link",
            'options': "Customer Group",
            'hidden': 0 if "show_customer_group" in filters else 1
        },
        {
            'fieldname': 'sales_person',
            'label': _("Sales Person"),
            'fieldtype': "Link",
            'options': "Sales Person",
            'hidden': 0 if "show_sales_person" in filters else 1
        },
        {
            'fieldname': "age",
            'label': _("Age (Days)"),
            'fieldtype': "Data",
            'width': 95
        },
        {
            'fieldname': "total_debt",
            'label': _("Total Debt (Base)"),
            'fieldtype': "Currency",
            'options': "Company:company:default_currency",
            'default': 0
        },
        {
            'fieldname': "total_debt_account",
            'label': _("Total Debt (Account)"),
            'fieldtype': "Currency",
            'options': "currency",
            'default': 0
        },
        {
            'fieldname': "range1_base",
            'label': _(f"0-{filters['range1']} Base"),
            'fieldtype': "Currency",
            'options': "Company:company:default_currency",
            'default': 0,
            'urgency': 1
        },
        {
            'fieldname': "range1_account",
            'label': _(f"0-{filters['range1']} Account"),
            'fieldtype': "Currency",
            'options': "currency",
            'default': 0,
            'urgency': 1
        },
        {
            'fieldname': "range2_base",
            'label': _(f"{filters['range1'] + 1}-{filters['range2']} Base"),
            'fieldtype': "Currency",
            'options': "Company:company:default_currency",
            'default': 0,
            'urgency': 2
        },
        {
            'fieldname': "range2_account",
            'label': _(f"{filters['range1'] + 1}-{filters['range2']} Account"),
            'fieldtype': "Currency",
            'options': "currency",
            'default': 0,
            'urgency': 2
        },
        {
            'fieldname': "range3_base",
            'label': _(f"{filters['range2'] + 1}-{filters['range3']} Base"),
            'fieldtype': "Currency",
            'options': "Company:company:default_currency",
            'default': 0,
            'urgency': 3
        },
        {
            'fieldname': "range3_account",
            'label': _(f"{filters['range2'] + 1}-{filters['range3']} Account"),
            'fieldtype': "Currency",
            'options': "currency",
            'default': 0,
            'urgency': 3
        },
        {
            'fieldname': "range4_base",
            'label': _(f"{filters['range3'] + 1}-{filters['range4']} Base"),
            'fieldtype': "Currency",
            'options': "Company:company:default_currency",
            'default': 0,
            'urgency': 4
        },
        {
            'fieldname': "range4_account",
            'label': _(f"{filters['range3'] + 1}-{filters['range4']} Account"),
            'fieldtype': "Currency",
            'options': "currency",
            'default': 0,
            'urgency': 4
        },
        {
            'fieldname': "range5_base",
            'label': _(f"{filters['range4'] + 1}-Above Base"),
            'fieldtype': "Currency",
            'options': "Company:company:default_currency",
            'default': 0,
            'urgency': 5
        },
        {
            'fieldname': "range5_account",
            'label': _(f"{filters['range4'] + 1}-Above Account"),
            'fieldtype': "Currency",
            'options': "currency",
            'default': 0,
            'urgency': 5
        },
    ]

    return columns


def get_data(filters: 'dict[str, ]', columns: 'list[dict]') -> list:
    "Get report data."

    total_columns = [col for col in columns[-10:]]

    data = initialise_data(filters, columns)

    values = get_debts(filters)
    if values:
        for value in values:
            if value['against_voucher']:
                try:
                    index = next(i for i, record in enumerate(data) if record['voucher_no'] == value['against_voucher'] and record['customer'] == value['customer'])
                except StopIteration:
                    index = next(i for i, record in enumerate(data) if record['voucher_no'] == value['voucher_no'] and record['customer'] == value['customer'])
            else:
                index = next(i for i, record in enumerate(data) if record['voucher_no'] == value['voucher_no'] and record['customer'] == value['customer'])
            data[index]['total_debt'] += value['main']
            data[index]['total_debt_account'] += value['account']

    data = [record for record in data if record['total_debt'] or record['total_debt_account']]

    if "cost_center" in filters:
        data = [record for record in data if record['cost_center'] == filters['cost_center']]
    if "customer" in filters:
        data = [record for record in data if record['customer'] == filters['customer']]
    if "customer_group" in filters:
        data = [record for record in data if record['customer_group'] == filters['customer_group']]
    if "sales_person" in filters:
        data = [record for record in data if record['sales_person'] == filters['sales_person']]

    for index, record in enumerate(data):
        if record['age'] <= filters['range1']:
            age_range = 0
        elif record['age'] <= filters['range2']:
            age_range = 2
        elif record['age'] <= filters['range3']:
            age_range = 4
        elif record['age'] <= filters['range4']:
            age_range = 6
        else:
            age_range = 8
        
        data[index][total_columns[age_range]['fieldname']] = record['total_debt']
        data[index][total_columns[age_range + 1]['fieldname']] = record['total_debt_account']

    if len(data):
        if 'group_by_party' in filters:
            old_data = data
            data = [old_data[0]]

            customer_total = {
                'currency': data[0]['currency'],
                'customer': data[0]['customer'],
                'customer_code': data[0]['customer_code'],
                'posting_date': data[0]['posting_date'],
                'total': 1,
                'total_debt': data[0]['total_debt'],
                'total_debt_account': data[0]['total_debt_account']
            }
            for col in total_columns:
                customer_total[col['fieldname']] = data[0][col['fieldname']]

            for index, record in enumerate(old_data[1:]):
                if customer_total['customer_code'] == record['customer_code']:
                    if record['posting_date'] > customer_total['posting_date']:
                        customer_total['posting_date'] = record['posting_date']
                    customer_total['total_debt'] += record['total_debt']
                    customer_total['total_debt_account'] += record['total_debt_account']
                    for col in total_columns:
                        customer_total[col['fieldname']] += record[col['fieldname']]
                else:
                    data.append(customer_total)
                    data.append({})
                    customer_total = {
                        'currency': record['currency'],
                        'customer': record['customer'],
                        'customer_code': record['customer_code'],
                        'posting_date': record['posting_date'],
                        'total': 1,
                        'total_debt': record['total_debt'],
                        'total_debt_account': record['total_debt_account']
                    }
                    for col in total_columns:
                        customer_total[col['fieldname']] = record[col['fieldname']]
                data.append(record)
            else:
                data.append(customer_total)

        data.extend([{}, add_total_row(data, columns)])
        data[-1][columns[0]['fieldname']] = date(*[int(i) for i in filters['report_date'].split("-")])
        data[-1]['customer'] = "Final Total"

    return data
    

def initialise_data(filters: 'dict[str, ]', columns: 'list[dict]') -> list:
    "Initialise report data."

    age_query = f"datediff('{filters['report_date']}', GLE.posting_date)" if filters['aging_based_on'] == "Posting Date" else f"datediff('{filters['report_date']}', ifnull(GLE.due_date, GLE.posting_date))"

    data = frappe.db.sql(f"""\
        select
            {age_query} age,
            A.account_currency currency,
            GLE.cost_center,
            GLE.party customer,
            C.customer_code,
            C.customer_group,
            GLE.due_date,
            GLE.posting_date,
            tab1.sales_person,
            0 total,
            GLE.voucher_no,
            GLE.voucher_type
        from
            `tabGL Entry` GLE
        join
            tabAccount A on GLE.account = A.name
        join
            tabCustomer C on GLE.party = C.name
        left join (
            select
                SI.name invoice,
                ST.sales_person,
                max(ST.allocated_amount)
            from
                `tabSales Invoice` SI
            join
                `tabSales Team` ST on SI.name = ST.parent
            group by
                invoice
            ) tab1 on GLE.voucher_no = tab1.invoice
        where
            A.debtors_account and GLE.posting_date <= '{filters['report_date']}'
        group by
            GLE.party, GLE.voucher_no
        order by
            C.customer_code, GLE.posting_date, GLE.voucher_no;""", as_dict=1)

    for i in range(len(data)):
        for col in columns:
            if col['fieldname'] in data[i]:
                if not data[i][col['fieldname']]:
                    data[i][col['fieldname']] = 0
            else:
                data[i][col['fieldname']] = 0

    return data


def get_debts(filters: 'dict[str, ]'):
    "Return list of entry values."

    data = []

    data.extend(frappe.db.sql(f"""\
        select
            round(sum(GLE.debit_in_account_currency - GLE.credit_in_account_currency), 2) account,
            GLE.against_voucher,
            GLE.against_voucher_type,
            round(sum(GLE.debit - GLE.credit), 2) main,
            GLE.party customer,
            GLE.voucher_no
        from
            `tabGL Entry` GLE
        join
            tabAccount A on GLE.account = A.name
        where
            A.debtors_account and GLE.posting_date <= '{filters['report_date']}'
        group by
            GLE.party, GLE.voucher_no, GLE.against_voucher;""", as_dict=1))

    return data


def add_total_row(data: 'list[dict]', columns: 'list[dict]') -> 'dict[str, ]':
    "Returns grand total row."

    total_row = {}

    for col in columns:
        if col['fieldtype'] == "Currency":
            total_row[col['fieldname']] = 0
            for record in data:
                if 'total' in record:
                    if not record['total']:
                        total_row[col['fieldname']] += record[col['fieldname']]

    total_row['total'] = 1

    return total_row


def get_chart_data(filters: 'dict[str]', data: 'list[dict]', columns: 'list[dict]'):
    "Returns chart data for visualising debt age."
    
    chart = {}

    if "group_by_party" in filters:
        rows = []
        rows.append({
            'values': [record['total_debt'] for record in data[:-1] if "total" in record and record['total']]
        })
        column_labels = [record['customer_code'] for record in data if "total" in record and record['total']]

        chart = {
            'barOptions': {
                'spaceRatio': 0.2,
            },
            'colors': [
                "#00FF00"
            ],
            'data': {
                'labels': column_labels,
                'datasets': rows
            },
            'title': "Accounts Receivable",
            'type': "bar"
        }

    return chart