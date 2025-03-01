import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

def calculate_growth(params):
    """
    Calculate portfolio growth based on provided parameters
    
    Args:
        params: Dictionary containing all calculation parameters
    
    Returns:
        DataFrame with yearly portfolio projections
    """
    # Extract parameters
    nominal_rate = params['nominal_return'] / 100
    inflation_rate = params['inflation'] / 100
    real_withdrawal_growth_rate = params['withdrawal_increase'] / 100
    withdrawal_lakhs = params['initial_withdrawal']
    real_portfolio_value = params['initial_portfolio']
    projection_years = params['projection_years']
    big_withdrawal_time = params['big_withdrawal_time']
    big_withdrawal_amt = params['big_withdrawal_amt']
    big_withdrawal_start_yr = params['big_withdrawal_start_yr']
    withdrawal_start_yr = params['withdrawal_start_yr']
    generational_halving = params['generational_halving']
    halving_years = params['halving_years']
    inheritance_tax = params['inheritance_tax']
    tax_on_withdrawals = params['tax_on_withdrawals']
    
    # Calculate real rate of return (after inflation)
    real_rate = (1 + nominal_rate) / (1 + inflation_rate) - 1
    
    # Initialize data structure
    annual_withdrawal = withdrawal_lakhs / 100  # Convert lakhs to crores
    big_withdrawal = big_withdrawal_amt
    
    data = [{
        'year': 0,
        'year_display': datetime.now().year,
        'real_portfolio_value': real_portfolio_value,
        'annual_withdrawal': 0,
        'big_withdrawal': 0,
        'total_withdrawal': 0,
        'cumulative_withdrawals': 0,
        'withdrawal_events': '',
        'withdrawal_tax_paid': 0,
        'cumulative_withdrawal_tax_paid': 0,
        'inheritance_tax_paid': 0,
        'cumulative_inheritance_tax_paid': 0,
        'total_tax_paid': 0,
        'cumulative_total_tax_paid': 0,
    }]
    
    cumulative_withdrawals = 0
    cumulative_withdrawal_tax_paid = 0
    cumulative_inheritance_tax_paid = 0
    cumulative_total_tax_paid = 0
    
    for year in range(1, projection_years + 1):
        current_year = datetime.now().year + year
        
        # Apply return for this period
        real_portfolio_value = max(0, real_portfolio_value * (1 + real_rate))
        
        # Update withdrawal amounts with growth rate
        annual_withdrawal *= (1 + real_withdrawal_growth_rate)
        big_withdrawal *= (1 + real_withdrawal_growth_rate)

        # Track withdrawals
        withdrawal_amt = 0
        events = []
        
        annual_withdrawal_tax = 0
        big_withdrawal_tax = 0
        # Regular annual withdrawal
        annual_withdrawal_done = 0 
        if year >= withdrawal_start_yr:
            withdrawal_amt += annual_withdrawal
            annual_withdrawal_done = annual_withdrawal
            annual_withdrawal_tax = annual_withdrawal * tax_on_withdrawals / 100
            events.append("Annual")
        
        # Periodic big withdrawal
        big_withdrawal_done = 0
        if (year % big_withdrawal_time == 0 and 
            year >= big_withdrawal_time and 
            year >= big_withdrawal_start_yr and 
            year >= withdrawal_start_yr):
            withdrawal_amt += big_withdrawal
            big_withdrawal_done = big_withdrawal
            big_withdrawal_tax = big_withdrawal * tax_on_withdrawals / 100
            events.append("Big")
        
        # Apply withdrawals
        real_portfolio_value -= (withdrawal_amt + annual_withdrawal_tax + big_withdrawal_tax) 
        
        # Track cumulative withdrawals
        cumulative_withdrawals += withdrawal_amt
        
        # Apply generational wealth halving if enabled
        inheritance_tax_paid = 0
        if generational_halving and year > 0 and year % halving_years == 0:
            real_portfolio_value /= 2
            inheritance_tax_paid = real_portfolio_value * inheritance_tax / 100
            real_portfolio_value -= inheritance_tax_paid
            events.append("Generational Halving")

        # Calculate cumulative tax paid
        withdrawal_tax_paid = annual_withdrawal_tax + big_withdrawal_tax
        total_tax_paid = withdrawal_tax_paid + inheritance_tax_paid
        cumulative_withdrawal_tax_paid += withdrawal_tax_paid
        cumulative_inheritance_tax_paid += inheritance_tax_paid
        cumulative_total_tax_paid += total_tax_paid
        
        # Add data for this year
        data.append({
            'year': year,
            'year_display': current_year,
            'real_portfolio_value': max(0, real_portfolio_value),
            'annual_withdrawal': annual_withdrawal_done,
            'big_withdrawal': big_withdrawal_done,
            'total_withdrawal': withdrawal_amt * 100,  # Convert to lakhs
            'cumulative_withdrawals': cumulative_withdrawals,
            'withdrawal_events': ", ".join(events),
            'withdrawal_tax_paid': withdrawal_tax_paid,
            'cumulative_withdrawal_tax_paid': cumulative_withdrawal_tax_paid,
            'inheritance_tax_paid': inheritance_tax_paid,
            'cumulative_inheritance_tax_paid': cumulative_inheritance_tax_paid,
            'total_tax_paid': total_tax_paid,
            'cumulative_total_tax_paid': cumulative_total_tax_paid,
        })
        
        # Break if portfolio is depleted
        if real_portfolio_value <= 0:
            break
            
    return pd.DataFrame(data)

def format_currency(amount, currency="₹"):
    """Format currency values with appropriate units (Lakhs/Crores). Takes input in Lakhs"""
    if abs(amount) >= 100:
        return f"{currency}{amount/100:.2f} Cr"
    else:
        return f"{currency}{amount:.2f} L"

def main():
    st.set_page_config(
        page_title="Investment Growth Calculator",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    with st.sidebar:
        st.title("Investment Growth Calculator")
        st.markdown("### ⚙️ Simulation Parameters")
        
        tabs = st.tabs(["Basic", "Advanced", "Display Options"])
        
        with tabs[0]:  # Basic parameters
            initial_portfolio = st.number_input(
                "Initial Portfolio Value (Crores)", 
                min_value=0.0, 
                max_value=1000.0, 
                value=194.0, 
                step=1.0,
                help="Your current portfolio value in crores (1 crore = 10 million)"
            )
            
            nominal_return = st.slider(
                "Investment Returns (% per year)", 
                min_value=0.0, 
                max_value=20.0, 
                value=12.0, 
                step=0.5,
                help="Expected nominal return on investments before inflation"
            )
            
            inflation = st.slider(
                "Inflation Rate (% per year)", 
                min_value=0.0, 
                max_value=15.0, 
                value=7.0, 
                step=0.5,
                help="Expected annual inflation rate"
            )
            
            initial_withdrawal = st.slider(
                "Initial Annual Withdrawal (lakhs/year)", 
                min_value=0, 
                max_value=200, 
                value=200, 
                step=1,
                help="How much you plan to withdraw annually in lakhs (1 lakh = 100,000)"
            )
            
            withdrawal_start_yr = st.slider(
                "Withdrawal Start Year", 
                min_value=0, 
                max_value=50, 
                value=0, 
                step=1,
                help="Year to start regular withdrawals (0 = immediate)"
            )

            big_withdrawal_time = st.slider(
                "Big Withdrawal Every (Years)", 
                min_value=1, 
                max_value=50, 
                value=10, 
                step=1,
                help="Frequency of large periodic withdrawals"
            )
            
            big_withdrawal_amt = st.slider(
                "Big Withdrawal Amount (Crores)", 
                min_value=0.0, 
                max_value=100.0, 
                value=25.0, 
                step=1.0,
                help="Amount of each large periodic withdrawal in crores"
            )
            
            big_withdrawal_start_yr = st.slider(
                "Big Withdrawal Start Year", 
                min_value=0, 
                max_value=100, 
                value=0, 
                step=1,
                help="Year to start periodic big withdrawals (0 = immediate)"
            )
            
        with tabs[1]:  # Advanced parameters
            real_withdrawal_increase = st.slider(
                "Real Annual Withdrawal Increase (% per year)", 
                min_value=-2.0, 
                max_value=5.0, 
                value=0.0, 
                step=0.1,
                help="Annual increase in withdrawal amount above inflation"
            )
            
            projection_years = st.slider(
                "Projection Timeline (Years)", 
                min_value=10, 
                max_value=1000, 
                value=1000, 
                step=10,
                help="Number of years to project into the future"
            )
            
            generational_halving = st.checkbox(
                "Enable Generational Wealth Transfer", 
                value=True,
                help="Simulate wealth division across generations"
            )
            
            halving_years = st.slider(
                "Generational Transfer Period (Years)", 
                min_value=10, 
                max_value=50, 
                value=25, 
                step=5,
                disabled=not generational_halving,
                help="Years between generational wealth transfers"
            )
        
            inheritance_tax = st.slider(
                "Inheritance Tax Rate (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=0.0, 
                step=1.0,
                disabled=not generational_halving,
                help="Tax rate on inherited wealth"
            )
        
            tax_on_withdrawals = st.slider(
                "Withdrawal Tax Rate (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=15.0, 
                step=1.0,
                help="Tax rate on any withdrawals made"
            )

        with tabs[2]:  # Display options
            show_data_table = st.checkbox("Show Data Table", value=False)
            chart_years = st.slider(
                "Chart Display Years", 
                min_value=0, 
                max_value=min(1000, projection_years), 
                value=min(100, projection_years), 
                step=10,
                help="Number of years to show in the chart (zoom level)"
            )
            log_scale = st.checkbox("Use Logarithmic Scale", value=False)
    
    # Calculate real return after all factors
    real_return = ((1 + nominal_return/100) / (1 + inflation/100) - 1) * 100
    effective_real_return = real_return
    
    if generational_halving:
        # Factor in the generational halving effect on compound returns
        halving_factor = (0.5 ** (1/halving_years))
        effective_real_return = ((1 + real_return/100) * halving_factor - 1) * 100
        
    # Safe withdrawal rate calculation
    annual_withdrawal_cr = initial_withdrawal / 100  # Convert lakhs to crores
    swr = (annual_withdrawal_cr + big_withdrawal_amt/big_withdrawal_time) / initial_portfolio * 100
        
    # Prepare simulation parameters
    params = {
        'nominal_return': nominal_return,
        'inflation': inflation,
        'withdrawal_increase': real_withdrawal_increase,
        'initial_withdrawal': initial_withdrawal,
        'projection_years': projection_years,
        'initial_portfolio': initial_portfolio,
        'big_withdrawal_time': big_withdrawal_time,
        'big_withdrawal_amt': big_withdrawal_amt,
        'big_withdrawal_start_yr': big_withdrawal_start_yr,
        'withdrawal_start_yr': withdrawal_start_yr,
        'generational_halving': generational_halving,
        'halving_years': halving_years,
        'inheritance_tax': inheritance_tax,
        'tax_on_withdrawals': tax_on_withdrawals,
    }
    
    # Run simulation
    df = calculate_growth(params)
    
    # Main content area
    st.title("Portfolio Projection")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Effective Real Return", 
            f"{effective_real_return:.2f}%",
            delta=f"{effective_real_return - real_return:.2f}%" if generational_halving else None,
            delta_color="off" if generational_halving else "normal",
            help="Real return after inflation and generational effects (without considering withdrawals and taxes)"
        )
    
    with col2:
        st.metric(
            "Initial Withdrawal Rate", 
            f"{swr:.2f}%",
            help="Initial withdrawal as percentage of portfolio"
        )
    
    with col3:
        if df['real_portfolio_value'].iloc[-1] <= 0:
            depletion_year = df[df['real_portfolio_value'] <= 0]['year'].iloc[0]
            year_text = f"Year {depletion_year}"
            st.metric(
                "Portfolio Depletes", 
                year_text,
                delta=f"({datetime.now().year + depletion_year})",
                delta_color="off"
            )
        else:
            final_value = df['real_portfolio_value'].iloc[-1]
            growth_multiple = final_value / initial_portfolio
            st.metric(
                "Final Portfolio", 
                format_currency(final_value * 100),
                delta=f"{growth_multiple:.1f}x growth" if growth_multiple > 1 else f"{growth_multiple:.1f}x reduction",
                delta_color="normal" if growth_multiple >= 1 else "inverse"
            )
    
    with col4:
        total_withdrawn = df['cumulative_withdrawals'].iloc[-1]
        st.metric(
            "Total Withdrawals", 
            format_currency(total_withdrawn * 100),
            delta=f"{total_withdrawn/initial_portfolio:.1f}x initial",
            delta_color="off"
        )
    
    # Visualization
    st.subheader("Portfolio Projection Over Time")
    
    fig = go.Figure()
    
    # Limit visible range if needed
    visible_df = df[df['year'] <= chart_years]
    
    # Portfolio value
    fig.add_trace(go.Scatter(
        x=visible_df['year_display'], 
        y=visible_df['real_portfolio_value'], 
        name="Portfolio Value (Crores)", 
        line=dict(color="#2563eb", width=3)
    ))
    
    # Total withdrawals
    fig.add_trace(go.Scatter(
        x=visible_df['year_display'], 
        y=visible_df['total_withdrawal'] / 100,  # Convert lakhs to crores
        name="Total Withdrawal (Crores)", 
        line=dict(color="#16a34a", width=2, dash="dash")
    ))
    
    # For each generational halving point, add a vertical line
    if generational_halving:
        for year in range(halving_years, projection_years + 1, halving_years):
            if year <= chart_years:
                year_value = datetime.now().year + year
                fig.add_vline(
                    x=year_value, 
                    line_width=1, 
                    line_dash="dash", 
                    line_color="gray",
                    annotation_text="",
                    annotation_position="top right"
                )
    
    # Update layout
    fig.update_layout(
        title=f"Portfolio Value and Withdrawals Over Time (Next {chart_years} Years)",
        xaxis_title="Year",
        yaxis_title="Value (₹ Crores)",
        height=500,
        hovermode="x unified",
        yaxis_type="log" if log_scale else "linear",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add a horizontal line at portfolio = 0
    fig.add_hline(y=0, line_width=1, line_dash="solid", line_color="red")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Warning for portfolio depletion
    if any(df['real_portfolio_value'] <= 0):
        depletion_year = df[df['real_portfolio_value'] <= 0]['year'].iloc[0]
        depletion_calendar_year = datetime.now().year + depletion_year
        st.error(f"⚠️ Warning: Portfolio depletes in year {depletion_year} ({depletion_calendar_year}). Consider reducing withdrawal rate or adjusting other parameters.")

    # Show the scenario results
    st.subheader("Scenario Summary")
    
    # Portfolio sustainability information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if df['real_portfolio_value'].iloc[-1] <= 0:
            st.info("Portfolio depletion analysis:")
            depletion_year = df[df['real_portfolio_value'] <= 0]['year'].iloc[0]
            st.markdown(f"- Portfolio depletes after **{depletion_year}** years")
            st.markdown(f"- Calendar year of depletion: **{datetime.now().year + depletion_year}**")
            
            # Calculate withdrawal to avoid depletion
            sustainable_withdrawal = 0
            test_rates = np.linspace(0.1, initial_withdrawal, 20)
            
            for test_rate in test_rates:
                test_params = params.copy()
                test_params['initial_withdrawal'] = test_rate
                test_df = calculate_growth(test_params)
                if test_df['real_portfolio_value'].iloc[-1] > 0:
                    sustainable_withdrawal = test_rate
                    break
            
            if sustainable_withdrawal > 0:
                st.markdown(f"- Sustainable initial withdrawal: **{format_currency(sustainable_withdrawal)}** per year")
                st.markdown(f"- Sustainable withdrawal rate: **{(sustainable_withdrawal/100)/initial_portfolio*100:.2f}%**")
        else:
            st.success("Portfolio sustainability analysis:")
            final_year = df['year'].iloc[-1]
            st.markdown(f"- Portfolio remains positive after **{final_year}** years")
            final_value = df['real_portfolio_value'].iloc[-1]
            initial_value = df['real_portfolio_value'].iloc[0]
            st.markdown(f"- Final portfolio value: **{format_currency(final_value*100)}**")
            growth_multiple = final_value / initial_value
            st.markdown(f"- Growth multiple: **{growth_multiple:.2f}x** the initial portfolio")
            
            # Calculate maximum sustainable withdrawal
            max_withdrawal = initial_withdrawal
            test_rates = np.linspace(initial_withdrawal, initial_withdrawal*10, 20)
            
            for test_rate in test_rates:
                test_params = params.copy()
                test_params['initial_withdrawal'] = test_rate
                test_df = calculate_growth(test_params)
                if test_df['real_portfolio_value'].iloc[-1] > 0:
                    max_withdrawal = test_rate
                else:
                    break
            
            st.markdown(f"- Maximum sustainable initial withdrawal: **{format_currency(max_withdrawal)}** per year")
            st.markdown(f"- Maximum sustainable withdrawal rate: **{(max_withdrawal/100)/initial_portfolio*100:.2f}%**")
    
    with col2:
        # Withdrawal statistics
        st.info("Withdrawal statistics:")
        
        total_withdrawn = df['cumulative_withdrawals'].iloc[-1]
        st.markdown(f"- Total withdrawals: **{format_currency(total_withdrawn*100)}**")
        
        # Show the final annual withdrawal
        final_withdrawal_value = df[df['annual_withdrawal'] > 0]['annual_withdrawal'].iloc[-1] if not df[df['annual_withdrawal'] > 0].empty else 0
        final_withdrawal_year = df[df['annual_withdrawal'] > 0]['year_display'].iloc[-1] if not df[df['annual_withdrawal'] > 0].empty else "N/A"
        
        st.markdown(f"- Final annual withdrawal: **{format_currency(final_withdrawal_value*100)}** in year {final_withdrawal_year}")
        
        # Show the final big withdrawal
        final_big_withdrawal_value = df[df['big_withdrawal'] > 0]['big_withdrawal'].iloc[-1] if not df[df['big_withdrawal'] > 0].empty else 0
        final_big_withdrawal_year = df[df['big_withdrawal'] > 0]['year_display'].iloc[-1] if not df[df['big_withdrawal'] > 0].empty else "N/A"
        st.markdown(f"- Final big withdrawal: **{format_currency(final_big_withdrawal_value*100)}** in year {final_big_withdrawal_year}")
        
            
        # Show info about generational halving if enabled
        if generational_halving:
            halving_count = df['withdrawal_events'].str.contains('Generational').sum()
            st.markdown(f"- Generational wealth transfers: **{halving_count}** events")

    with col3:
        # Tax statistics
        st.info("Tax burden:")

        cumulative_withdrawal_tax_paid = df['cumulative_withdrawal_tax_paid'].iloc[-1]
        cumulative_inheritance_tax_paid = df['cumulative_inheritance_tax_paid'].iloc[-1]
        cumulative_total_tax_paid = df['cumulative_total_tax_paid'].iloc[-1]
        
        st.markdown(f"- Total withdrawal tax paid: **{format_currency(cumulative_withdrawal_tax_paid*100)}**")
        st.markdown(f"- Total inheritance tax paid: **{format_currency(cumulative_inheritance_tax_paid*100)}**")
        st.markdown(f"- Total tax paid: **{format_currency(cumulative_total_tax_paid*100)}**")
        
        # Tax as percentage of portfolio and withdrawals
        if total_withdrawn > 0:
            tax_to_withdrawal_ratio = cumulative_withdrawal_tax_paid / total_withdrawn * 100
            st.markdown(f"- Withdrawal tax as % of withdrawals: **{tax_to_withdrawal_ratio:.1f}%**")
        
        if initial_portfolio > 0:
            tax_to_portfolio_ratio = cumulative_total_tax_paid / initial_portfolio * 100
            st.markdown(f"- Total tax as % of initial portfolio: **{tax_to_portfolio_ratio:.1f}%**")
    
    # Show the data table if requested
    if show_data_table:
        st.subheader("Detailed Projection Data")
        display_df = df.copy()
        
        # Format the portfolio values, withdrawals, and taxes
        display_df['Portfolio (Cr)'] = display_df['real_portfolio_value'].apply(lambda x: f"₹{x:.2f} Cr")
        display_df['Withdrawal (L)'] = display_df['total_withdrawal'].apply(lambda x: f"₹{x:.2f} L")
        display_df['Cum. Withdrawals (Cr)'] = display_df['cumulative_withdrawals'].apply(lambda x: f"₹{x:.2f} Cr")
        display_df['Tax Paid (Cr)'] = display_df['total_tax_paid'].apply(lambda x: f"₹{x:.2f} Cr")
        display_df['Cum. Tax Paid (Cr)'] = display_df['cumulative_total_tax_paid'].apply(lambda x: f"₹{x:.2f} Cr")
        
        # Select and rename columns for display
        display_cols = ['year', 'year_display', 'Portfolio (Cr)', 'Withdrawal (L)', 'Cum. Withdrawals (Cr)', 
                       'Tax Paid (Cr)', 'Cum. Tax Paid (Cr)', 'withdrawal_events']
        display_df = display_df[display_cols].rename(columns={
            'year': 'Year',
            'year_display': 'Calendar Year',
            'withdrawal_events': 'Events'
        })
        
        st.dataframe(display_df, hide_index=True)

    # Add a section for exporting data
    st.subheader("Export Results")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export to CSV"):
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="portfolio_projection.csv",
                mime="text/csv"
            )
    
    with col2:
        # Save parameters as a preset
        if st.button("Save Parameters as JSON"):
            import json
            params_json = json.dumps(params, indent=2)
            st.download_button(
                label="Download Parameters",
                data=params_json,
                file_name="portfolio_parameters.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()