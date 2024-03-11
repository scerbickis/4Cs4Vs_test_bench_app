import decimal

decimal.getcontext().rounding = decimal.ROUND_HALF_DOWN

entry = 2.5
# M = float(entry)/50*190
M = round(decimal.Decimal(entry),0)

print(M)
# print(M.to_bytes(2).hex(' '))
