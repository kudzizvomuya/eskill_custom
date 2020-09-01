from __future__ import unicode_literals
from frappe import _

def get_data():

    return [
        {
            "label": _("Dashboards"),
            "icon": "octicon octicon-briefcase",
            "items": [
				{
					"type": "page",
					"name": "gross-profit",
					"label": _("Gross Profit"),
					"icon": "fa fa-bar-chart",
					"onboard": 1,
				},
				{
					"type": "page",
					"name": "sales-dashboard",
					"label": _("Sales"),
					"icon": "fa fa-bar-chart",
					"onboard": 1,
				},
				{
					"type": "page",
					"name": "support-dashboard",
					"label": _("Support"),
					"icon": "fa fa-bar-chart",
					"onboard": 1,
				},
            ]
        }
    ]