import json
df = json.load(open('parag parikh flexi cap.json'))

import pandas as pd
df = pd.DataFrame(df)[["navDate","navValue"]]
df["navDate"] = pd.to_datetime(df["navDate"])
def show_plot(df):
    
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    line, = ax.plot(df["navValue"])
    ax.set_yscale('log')

    # Create the annotation object
    annot = ax.annotate("", xy=(0,0), xytext=(20,20),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        x, y = line.get_data()
        annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = f"{ind['ind'][0]} {df['navDate'][ind['ind'][0]]}: {y[ind['ind'][0]]:.2f}"
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = line.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()
# show_plot(df)

sip = 1000
sip_units_owned = 0
sip_held = 0    
for i in range(len(df)):
    current_nav = df["navValue"][i]
    current_date = df["navDate"][i]
    if (pd.to_datetime("2020-09-01") <= current_date <= pd.to_datetime("2021-09-01")): # boom
        extra_sip = min(3*sip, sip_held)
        sip_held -= extra_sip
        sip_units = (sip + extra_sip) / current_nav
        sip_units_owned += sip_units
    elif (pd.to_datetime("2022-02-22") <= current_date <= pd.to_datetime("2023-04-28")): # crash
        sip_held += sip / 2
        sip_units = sip / 2 / current_nav
        sip_units_owned += sip_units
    else:
        sip_units = sip / current_nav
        sip_units_owned += sip_units
final_value = sip_units_owned * df["navValue"].iloc[-1] + sip_held
cagr = (final_value / (sip * len(df))) ** (245 / len(df)) - 1
print(f"Annualized Return: {cagr:.2%}")