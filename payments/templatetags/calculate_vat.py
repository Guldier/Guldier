from django import template

register = template.Library()


@register.simple_tag()
def return_nett(amount, vat):
    """Calculates nett amount
    [amount]: gross amount
    [vat]: VAT rate"""

    return f'{int(float(amount)) - (int(float(amount)) * (vat / 100)):.2f}'


@register.simple_tag()
def return_vat_amount(amount, vat):
    """Returns vat amount
        [amount]: gross amount
        [vat]: VAT rate"""
    return f'{int(float(amount)) * (vat / 100):.2f}'
