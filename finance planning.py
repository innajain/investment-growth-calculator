def run_withdrawal_simulation(amt, annual_withdrawal, decadal_withdrawal, withdrawal_tax, annual_return, inflation, years, fees, new_generation_time, kids, withdrawal_start_yr):
    for i in range(years):
        amt = amt * (1 + annual_return / 100)
        amt *= 1 - fees / 100
        amt /= 1 + inflation / 100
        if (i+1) >= withdrawal_start_yr:
            amt -= annual_withdrawal * (1 + withdrawal_tax / 100)
            if (i + 1) % 10 == 0:
                amt -= decadal_withdrawal * (1 + withdrawal_tax / 100)
        if (i + 1) % new_generation_time == 0:
            amt /= kids
    return amt

def find_req_amt(annual_withdrawal, decadal_withdrawal, withdrawal_tax, annual_return, inflation, fees, new_generation_time, kids, withdrawal_start_yr):
    # Binary Search Approach
    low, high = 0, 1e10  # Start with a reasonable range
    tolerance = 1e-6
    iteration = 0

    while high - low > tolerance and iteration < 1000:
        iteration += 1
        amt = (low + high) / 2  # Middle point
        output = run_withdrawal_simulation(
            amt=amt,
            annual_withdrawal=annual_withdrawal,
            decadal_withdrawal=decadal_withdrawal,
            withdrawal_tax=withdrawal_tax,
            annual_return=annual_return,
            inflation=inflation,
            years=1000,
            fees=fees,
            new_generation_time=new_generation_time,
            kids=kids,
            withdrawal_start_yr=withdrawal_start_yr
        )

        if output > amt * 1.00001:
            high = amt
        elif output < amt * 0.99999:
            low = amt
        else:
            break
    
    return amt


amt = find_req_amt(annual_withdrawal=.3,
                   decadal_withdrawal=6,
                   withdrawal_tax=15,
                   annual_return=15,
                   inflation=6.5,
                   fees=0.7,
                   new_generation_time=25,
                   kids=2,
                   withdrawal_start_yr=0
                   )

print(f"Required Amount: ₹{amt:.2f} crores")