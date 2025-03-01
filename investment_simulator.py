annual_investment = 3.7
inflation = 0.07
annual_return = 0.12
corpus = 0
num_years = 27
for i in range(num_years):
    corpus += annual_investment
    corpus *= 1 + annual_return
    corpus /= 1 + inflation
print(corpus)