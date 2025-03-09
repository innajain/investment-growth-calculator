import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Perpetual Financial Planning Dashboard",
    page_icon="💰",
    layout="wide"
)

# CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 1rem;
    }
    .result-box {
        background-color: #F1F5F9;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .highlight {
        color: #1E40AF;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">Perpetual Financial Planning Dashboard</p>', unsafe_allow_html=True)

# Core functions from the original code
def get_final_corpus_val(amt, annual_withdrawal, decadal_withdrawal, withdrawal_increment, withdrawal_tax, annual_return, inflation, years, fees, new_generation_time, kids, withdrawal_start_yr, india_maturity_yr, mature_returns, mature_inflation):
    corpus_history = [amt]
    
    for i in range(years):
        if (i+1) == india_maturity_yr:
            annual_return = mature_returns
            inflation = mature_inflation

        amt = amt * (1 + annual_return / 100)
        amt *= 1 - fees / 100

        amt /= 1 + inflation / 100

        if (i+1) >= withdrawal_start_yr:
            amt -= annual_withdrawal * (1 + withdrawal_tax / 100)
            if (i + 1) % 10 == 0:
                amt -= decadal_withdrawal * (1 + withdrawal_tax / 100)

        annual_withdrawal *= (1 + withdrawal_increment / 100)
        decadal_withdrawal *= (1 + withdrawal_increment / 100)

        if (i + 1) % new_generation_time == 0:
            amt /= kids
        
        corpus_history.append(amt)
        
        # Stop if corpus becomes negative
        if amt <= 0:
            break
            
    return amt, corpus_history

def find_req_amt(annual_withdrawal, decadal_withdrawal, withdrawal_increment, withdrawal_tax, annual_return, inflation, fees, new_generation_time, kids, withdrawal_start_yr, india_maturity_yr, mature_returns, mature_inflation):
    low, high = 0, 1e10
    tolerance = 1e-6
    iteration = 0

    while high - low > tolerance and iteration < 1000:
        iteration += 1
        if iteration > 1000:
            return None, []
        
        mid_amt = (low + high) / 2
        output, corpus_history = get_final_corpus_val(
            amt=mid_amt,
            annual_withdrawal=annual_withdrawal,
            decadal_withdrawal=decadal_withdrawal,
            withdrawal_increment=withdrawal_increment,
            withdrawal_tax=withdrawal_tax,
            annual_return=annual_return,
            inflation=inflation,
            years=1000,
            fees=fees,
            new_generation_time=new_generation_time,
            kids=kids,
            withdrawal_start_yr=withdrawal_start_yr,
            india_maturity_yr=india_maturity_yr,
            mature_returns=mature_returns,
            mature_inflation=mature_inflation,
        )

        if output > mid_amt * 1.00001:
            high = mid_amt
        elif output < mid_amt * 0.99999:
            low = mid_amt
        else:
            break
    
    # Calculate the final corpus history with the found amount
    _, corpus_history = get_final_corpus_val(
        amt=mid_amt,
        annual_withdrawal=annual_withdrawal,
        decadal_withdrawal=decadal_withdrawal,
        withdrawal_increment=withdrawal_increment,
        withdrawal_tax=withdrawal_tax,
        annual_return=annual_return,
        inflation=inflation,
        years=1000,
        fees=fees,
        new_generation_time=new_generation_time,
        kids=kids,
        withdrawal_start_yr=withdrawal_start_yr,
        india_maturity_yr=india_maturity_yr,
        mature_returns=mature_returns,
        mature_inflation=mature_inflation,
    )
    
    return mid_amt, corpus_history

def get_final_sip_corpus(sip, sip_increment, annual_return, inflation, years):
    corpus = 0
    sip_history = []
    corpus_history = [0]
    
    for i in range(years):
        corpus += sip
        sip_history.append(sip)
        corpus *= 1 + annual_return / 100
        corpus_history.append(corpus)
        sip *= (1 + sip_increment / 100)
        
    real_corpus = corpus / ((1 + inflation / 100) ** years)
    
    return real_corpus, corpus_history, sip_history

def get_req_sip(amt, sip_increment, annual_return, inflation, years):
    amt_for_unit_sip, _, _ = get_final_sip_corpus(
        sip=1,
        sip_increment=sip_increment,
        annual_return=annual_return,
        inflation=inflation,
        years=years
    )

    required_sip = amt / amt_for_unit_sip
    
    _, corpus_history, sip_history = get_final_sip_corpus(
        sip=required_sip,
        sip_increment=sip_increment,
        annual_return=annual_return,
        inflation=inflation,
        years=years
    )
    
    return required_sip, corpus_history, sip_history

# Create sidebar for inputs
st.sidebar.markdown("## Investment Parameters")

# Input parameters with default values
with st.sidebar.expander("Withdrawal Parameters", expanded=True):
    annual_withdrawal = st.number_input("Annual Withdrawal (₹ crores)", value=0.3, min_value=0.0, step=0.1, format="%.2f")
    decadal_withdrawal = st.number_input("Decadal Withdrawal (₹ crores)", value=6.0, min_value=0.0, step=0.5, format="%.2f")
    withdrawal_increment = st.number_input("Withdrawal Increment (%)", value=0.0, min_value=0.0, step=0.5, format="%.2f")
    withdrawal_tax = st.number_input("Withdrawal Tax (%)", value=15.0, min_value=0.0, step=1.0, format="%.2f")
    withdrawal_start_yr = st.number_input("Withdrawal Start Year", value=0, min_value=0, step=1)

with st.sidebar.expander("Investment Parameters", expanded=True):
    annual_return = st.number_input("Annual Return (%)", value=14.0, min_value=0.0, step=0.5, format="%.2f")
    inflation = st.number_input("Inflation (%)", value=7.0, min_value=0.0, step=0.5, format="%.2f")
    fees = st.number_input("Fees (%)", value=1.0, min_value=0.0, step=0.1, format="%.2f")
    
    st.markdown("### Mature Market Parameters")
    india_maturity_yr = st.number_input("India Maturity Year", value=50, min_value=0, step=1)
    mature_returns = st.number_input("Mature Market Returns (%)", value=10.0, min_value=0.0, step=0.5, format="%.2f")
    mature_inflation = st.number_input("Mature Market Inflation (%)", value=5.0, min_value=0.0, step=0.5, format="%.2f")

with st.sidebar.expander("SIP Parameters", expanded=True):
    sip_increment = st.number_input("SIP Annual Increment (%)", value=5.0, min_value=0.0, step=0.5, format="%.2f")
    years_for_investment = st.number_input("Years for Investment", value=31, min_value=1, step=1)

with st.sidebar.expander("Generational Parameters", expanded=True):
    new_generation_time = st.number_input("New Generation Time (years)", value=27, min_value=1, step=1)
    kids = st.number_input("Number of Kids", value=2, min_value=1, step=1)

display_years = 200

# Auto-calculate on load and when parameters change
# Calculate required amount
amt, corpus_history = find_req_amt(
    annual_withdrawal=annual_withdrawal,
    decadal_withdrawal=decadal_withdrawal,
    withdrawal_increment=withdrawal_increment,
    withdrawal_tax=withdrawal_tax,
    annual_return=annual_return,
    inflation=inflation,
    fees=fees,
    new_generation_time=new_generation_time,
    kids=kids,
    withdrawal_start_yr=withdrawal_start_yr,
    india_maturity_yr=india_maturity_yr,
    mature_returns=mature_returns,
    mature_inflation=mature_inflation,
)

# Calculate required SIP
sip, sip_corpus_history, sip_history = get_req_sip(
    amt=amt,
    sip_increment=sip_increment,
    annual_return=annual_return,
    inflation=inflation,
    years=years_for_investment
)

# Calculate withdrawal ratio
withdrawal_ratio = (annual_withdrawal + decadal_withdrawal/10) / amt

# Results
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="section-header">Required Corpus</p>', unsafe_allow_html=True)
    st.markdown(f"<span class='highlight'>Initial Corpus Required:</span> ₹{amt:.2f} crores", unsafe_allow_html=True)
    st.markdown(f"<span class='highlight'>Withdrawal Ratio:</span> {withdrawal_ratio:.2%}", unsafe_allow_html=True)
    
with col2:
    st.markdown('<p class="section-header">SIP Plan</p>', unsafe_allow_html=True)
    st.markdown(f"<span class='highlight'>Initial SIP Required:</span> ₹{(sip*100):.2f} lakhs/year", unsafe_allow_html=True)
    st.markdown(f"<span class='highlight'>SIP Increment:</span> {sip_increment:.2f}% per year", unsafe_allow_html=True)
    st.markdown(f"<span class='highlight'>Investment Period:</span> {years_for_investment} years", unsafe_allow_html=True)

# Visualizations
st.markdown('<p class="section-header">Corpus Projection Over Time</p>', unsafe_allow_html=True)

# Plot corpus history with Plotly
corpus_df = pd.DataFrame({
    'Year': range(min(display_years+1, len(corpus_history))),
    'Corpus Value (₹ crores)': corpus_history[:display_years+1]
})

# Create annotations for generations and maturity year
annotations = []
shapes = []

# Add vertical line for maturity year
if india_maturity_yr <= display_years:
    shapes.append(dict(
        type="line",
        xref="x", yref="paper",
        x0=india_maturity_yr, y0=0, 
        x1=india_maturity_yr, y1=1,
        line=dict(color="red", width=2, dash="dash")
    ))
    
    annotations.append(dict(
        x=india_maturity_yr,
        y=max(corpus_history[:display_years+1]) * 0.95,
        xref="x", yref="y",
        text=f"Market Maturity<br>(Year {india_maturity_yr})",
        showarrow=True,
        arrowhead=1,
        ax=40,
        ay=-40,
        font=dict(color="red", size=12)
    ))

# Add generation lines
for gen in range(1, display_years // new_generation_time + 1):
    gen_year = gen * new_generation_time
    if gen_year <= display_years:
        shapes.append(dict(
            type="line",
            xref="x", yref="paper",
            x0=gen_year, y0=0, 
            x1=gen_year, y1=1,
            line=dict(color="green", width=1.5, dash="dot")
        ))
        
        annotations.append(dict(
            x=gen_year,
            y=max(corpus_history[:display_years+1]) * (0.85 - 0.05 * (gen % 3)),
            xref="x", yref="y",
            text=f"Generation {gen+1}",
            showarrow=True,
            arrowhead=1,
            ax=30,
            ay=-30,
            font=dict(color="green", size=12)
        ))

# Create the plot
fig = px.line(corpus_df, x='Year', y='Corpus Value (₹ crores)', 
              title='Corpus Value Projection Over Time (Inflation Adjusted)')

fig.update_traces(line=dict(width=3, color='#2563EB'))
fig.update_layout(
    shapes=shapes,
    annotations=annotations,
    hovermode="x unified",
    hoverlabel=dict(bgcolor="rgba(0,0,0,0.8)", font_size=14),
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(
        title="Year",
        gridcolor='rgba(0,0,0,0.1)',
        showgrid=True
    ),
    yaxis=dict(
        title="Corpus Value (₹ crores)",
        gridcolor='rgba(0,0,0,0.1)',
        showgrid=True
    ),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# SIP Plan visualization
st.markdown('<p class="section-header">SIP Growth Plan</p>', unsafe_allow_html=True)

sip_df = pd.DataFrame({
    'Year': range(1, years_for_investment + 1),
    'Annual SIP (₹ lakhs)': [s * 100 for s in sip_history],
    'Accumulated Corpus (₹ crores)': sip_corpus_history[1:]
})

# Create subplot with 2 y-axes
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    vertical_spacing=0.1,
                    subplot_titles=("Annual SIP Amount Over Time", 
                                   "SIP Corpus Growth Over Time (Nominal Value)"),
                    row_heights=[0.3, 0.7])

# Add SIP amount trace
fig.add_trace(
    go.Scatter(x=sip_df['Year'], y=sip_df['Annual SIP (₹ lakhs)'], 
               name='Annual SIP', line=dict(color='#10B981', width=3)),
    row=1, col=1
)

# Add accumulated corpus trace
fig.add_trace(
    go.Scatter(x=sip_df['Year'], y=sip_df['Accumulated Corpus (₹ crores)'], 
               name='Accumulated Corpus', line=dict(color='#6366F1', width=3)),
    row=2, col=1
)

# Add target corpus line
fig.add_trace(
    go.Scatter(x=[1, years_for_investment], y=[amt, amt], 
               name='Target Corpus', line=dict(color='red', width=2, dash='dash')),
    row=2, col=1
)

# Update layout
fig.update_layout(
    hovermode="x unified",
    hoverlabel=dict(bgcolor="rgba(0,0,0,0.8)", font_size=14),
    plot_bgcolor="rgba(0,0,0,0)",
    height=700,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

# Update axes
fig.update_xaxes(title_text="Year", row=2, col=1, gridcolor='rgba(0,0,0,0.1)')
fig.update_yaxes(title_text="Annual SIP (₹ lakhs)", row=1, col=1, gridcolor='rgba(0,0,0,0.1)')
fig.update_yaxes(title_text="Corpus (₹ crores)", row=2, col=1, gridcolor='rgba(0,0,0,0.1)')

# Add annotation for target corpus
fig.add_annotation(
    x=years_for_investment * 0.1,
    y=amt * 1.05,
    text=f"Target Corpus: ₹{amt:.2f} crores",
    showarrow=False,
    font=dict(size=12, color="red"),
    row=2, col=1
)

st.plotly_chart(fig, use_container_width=True)

# Sensitivity Analysis
st.markdown('<p class="section-header">Sensitivity Analysis</p>', unsafe_allow_html=True)

# Create tabs for sensitivity analysis
sensitivity_tabs = st.tabs(["Returns Sensitivity", "Inflation Sensitivity"])

with sensitivity_tabs[0]:
    # Effect of annual return
    returns_range = np.linspace(max(annual_return - 5, 1), annual_return + 5, 11)
    corpus_values = []
    
    for ret in returns_range:
        amt_temp, _ = find_req_amt(
            annual_withdrawal=annual_withdrawal,
            decadal_withdrawal=decadal_withdrawal,
            withdrawal_increment=withdrawal_increment,
            withdrawal_tax=withdrawal_tax,
            annual_return=ret,
            inflation=inflation,
            fees=fees,
            new_generation_time=new_generation_time,
            kids=kids,
            withdrawal_start_yr=withdrawal_start_yr,
            india_maturity_yr=india_maturity_yr,
            mature_returns=mature_returns,
            mature_inflation=mature_inflation,
        )
        corpus_values.append(amt_temp)
    
    sensitivity_df = pd.DataFrame({
        'Annual Return (%)': returns_range,
        'Required Corpus (₹ crores)': corpus_values
    })
    
    fig = px.line(sensitivity_df, x='Annual Return (%)', y='Required Corpus (₹ crores)',
                  title='Effect of Annual Return on Required Corpus',
                  markers=True)
    
    fig.update_traces(line=dict(width=3, color='#F59E0B'), marker=dict(size=10))
    fig.update_layout(
        hovermode="x unified",
        hoverlabel=dict(bgcolor="rgba(0,0,0,0.8)", font_size=14),
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Annual Return (%)",
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title="Required Corpus (₹ crores)",
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True
        ),
        height=500
    )
    
    # Add a vertical line at the current annual return
    fig.add_vline(x=annual_return, line_width=2, line_dash="dash", line_color="green",
                  annotation_text=f"Current: {annual_return}%",
                  annotation_position="top right")
    
    st.plotly_chart(fig, use_container_width=True)
    
with sensitivity_tabs[1]:
    # Effect of inflation
    inflation_range = np.linspace(max(inflation - 3, 1), inflation + 3, 11)
    corpus_values = []
    
    for inf in inflation_range:
        amt_temp, _ = find_req_amt(
            annual_withdrawal=annual_withdrawal,
            decadal_withdrawal=decadal_withdrawal,
            withdrawal_increment=withdrawal_increment,
            withdrawal_tax=withdrawal_tax,
            annual_return=annual_return,
            inflation=inf,
            fees=fees,
            new_generation_time=new_generation_time,
            kids=kids,
            withdrawal_start_yr=withdrawal_start_yr,
            india_maturity_yr=india_maturity_yr,
            mature_returns=mature_returns,
            mature_inflation=mature_inflation,
        )
        corpus_values.append(amt_temp)
    
    sensitivity_df = pd.DataFrame({
        'Inflation (%)': inflation_range,
        'Required Corpus (₹ crores)': corpus_values
    })
    
    fig = px.line(sensitivity_df, x='Inflation (%)', y='Required Corpus (₹ crores)',
                  title='Effect of Inflation on Required Corpus',
                  markers=True)
    
    fig.update_traces(line=dict(width=3, color='#EF4444'), marker=dict(size=10))
    fig.update_layout(
        hovermode="x unified",
        hoverlabel=dict(bgcolor="rgba(0,0,0,0.8)", font_size=14),
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Inflation (%)",
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title="Required Corpus (₹ crores)",
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True
        ),
        height=500
    )
    
    # Add a vertical line at the current inflation
    fig.add_vline(x=inflation, line_width=2, line_dash="dash", line_color="green",
                  annotation_text=f"Current: {inflation}%",
                  annotation_position="top right")
    
    st.plotly_chart(fig, use_container_width=True)