from payments import models as pay_models


def get_current_prices():
    return [(price.get_in_zl, f'{price.get_in_zl:.2f} za {price.get_discounted_price:.2f}')
            if price.promotion_id and price.promotion.active_dates.date_within_range
            and price.promotion.active else (price.get_in_zl, f'{price.get_in_zl:.2f}')
            for price in pay_models.Price.objects.all().order_by('amount')]
