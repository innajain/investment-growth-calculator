base_salary_lpa = 17

def calc_tax(salary):
    standard_deduction = .75
    salary -= standard_deduction
    tax = 0
    if salary >= 4:
        tax += min(4, salary - 4) * 0.05
    if salary >= 8:
        tax += min(4, salary - 8) * 0.1
    if salary >= 12:
        tax += min(4, salary - 12) * 0.15
    if salary >= 16:
        tax += min(4, salary - 16) * 0.2
    if salary >= 20:
        tax += min(4, salary - 20) * 0.25
    if salary >= 24:
        tax += (salary - 24) * 0.3

    cess = 4
    tax *= 1 + cess / 100
    return tax

tax = calc_tax(base_salary_lpa)
annual_inhand = round(base_salary_lpa - tax, 2)
print(f"Annual inhand salary: {annual_inhand} LPA")
monthly_inhand = round(annual_inhand / 12, 2)
print(f"Monthly inhand salary: {monthly_inhand} lakhs")


car_price = annual_inhand / 2
print(f"Car price: {car_price} lakhs")
car_downpayment = car_price * 0.2
print(f"Car downpayment: {car_downpayment} lakhs")

def calculate_emi(principal, annual_rate, tenure_months):
    monthly_rate = annual_rate / (12 * 100)  # Convert annual rate to monthly
    emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / ((1 + monthly_rate) ** tenure_months - 1)
    return round(emi, 2)

car_emi = calculate_emi(car_price - car_downpayment, 10, 4*12)
print(f"Car EMI: {car_emi} lakhs/month ({car_emi/monthly_inhand:.2%} of monthly inhand)")


house_price = round(annual_inhand * 4.5, 2)
print(f"House price: {house_price} lakhs")
house_downpayment = round(house_price * 0.4, 2)
print(f"House downpayment: {house_downpayment} lakhs")
house_emi = calculate_emi(house_price - house_downpayment, 9, 20*12)
print(f"House EMI: {house_emi} lakhs/month ({house_emi/monthly_inhand:.2%} of monthly inhand)")

term_insurance_cover = annual_inhand * 15 + 40
print(f"Term insurance cover: {term_insurance_cover/100} crores")
term_insurance_premium = round(0.35/12, 2)
print(f"Term insurance premium: {term_insurance_premium} lakhs/month ({term_insurance_premium/monthly_inhand:.2%} of monthly inhand)")

health_insurance_cover = 100
print(f"Health insurance cover: {health_insurance_cover/100} crores")
health_insurance_premium = round(0.3/12, 2)
print(f"Health insurance premium: {health_insurance_premium} lakhs/month ({health_insurance_premium/monthly_inhand:.2%} of monthly inhand)")

emergency_fund = annual_inhand / 2
print(f"Emergency fund: {emergency_fund} lakhs")