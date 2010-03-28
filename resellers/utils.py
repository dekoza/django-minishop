from resellers.models import PartnerHistory

def log_order(partner, order):
    calculated_income = partner.rate * order.price
    log = PartnerHistory(partner=partner, order=order, income=calculated_income)
    log.save()
