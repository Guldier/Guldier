from datetime import date


def calculate_discounts(promotions):
    """Crate discounts for given promotion, only first promotion which is set to ON is taken under consideration"""
    values_discounts = []
    date_today = date.today()
    for promotion in promotions:
        if promotion.is_on and promotion.start_date <= date_today <= promotion.end_date:
            for value in promotion.discounts.all().order_by('top_up_value'):
                price_value = value.top_up_value, value.top_up_value
                if value.discount > 0:
                    price_value = (value.top_up_value,
                                   str(value.top_up_value) +
                                   f' for {value.top_up_value - float(value.top_up_value * (value.discount / 100)):.2f}'
                                   )

                values_discounts.append(price_value)

            return values_discounts, promotion.id
    return values_discounts, None


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
