import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def render_metric_cards(spot, atm, pcr, max_pain, support, resistance):
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Spot Price", f"{spot:,.2f}")
    col2.metric("ATM Strike", f"{int(atm)}")
    col3.metric("PCR", f"{pcr:.2f}")
    col4.metric("Max Pain", f"{int(max_pain)}")
    col5.metric("Support", f"{int(support)}")
    col6.metric("Resistance", f"{int(resistance)}")

def render_option_chain_table(df, atm_strike):
    # Prepare table for display
    # CE on left, Strike in middle, PE on right
    display_df = pd.DataFrame(index=df.index)
    display_df['CE_Delta'] = df['CE_Delta']
    display_df['CE_IV'] = df['CE_IV']
    display_df['CE_OI'] = df['CE_OI'].astype(int)
    display_df['CE_CHG_OI'] = df['CE_CHG_OI'].astype(int)
    display_df['CE_LTP'] = df['CE_LTP'].round(2)
    display_df['Strike'] = df.index.astype(int)
    display_df['PE_LTP'] = df['PE_LTP'].round(2)
    display_df['PE_CHG_OI'] = df['PE_CHG_OI'].astype(int)
    display_df['PE_OI'] = df['PE_OI'].astype(int)
    display_df['PE_IV'] = df['PE_IV']
    display_df['PE_Delta'] = df['PE_Delta']
    
    # Reorder columns
    cols = ['CE_Delta', 'CE_IV', 'CE_OI', 'CE_CHG_OI', 'CE_LTP', 'Strike', 'PE_LTP', 'PE_CHG_OI', 'PE_OI', 'PE_IV', 'PE_Delta']
    display_df = display_df[cols]
    
    # Style: highlight ATM
    def highlight_atm(s):
        return ['background-color: #333333' if s.name == atm_strike else '' for _ in s]

    st.dataframe(display_df.style.apply(highlight_atm, axis=1), use_container_width=True, height=500)

def render_oi_charts(df):
    col1, col2 = st.columns(2)
    
    with col1:
        # OI vs Strike Bar Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.index, y=df['CE_OI'], name='Call OI', marker_color='red'))
        fig.add_trace(go.Bar(x=df.index, y=df['PE_OI'], name='Put OI', marker_color='green'))
        fig.update_layout(title="OI vs Strike", barmode='group', height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Change in OI vs Strike
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.index, y=df['CE_CHG_OI'], name='Call OI Chg', marker_color='darkred'))
        fig.add_trace(go.Bar(x=df.index, y=df['PE_CHG_OI'], name='Put OI Chg', marker_color='darkgreen'))
        fig.update_layout(title="Change in OI vs Strike", barmode='group', height=400)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # Total OI Pie Chart
        total_ce = df['CE_OI'].sum()
        total_pe = df['PE_OI'].sum()
        fig = px.pie(values=[total_ce, total_pe], names=['Total Call OI', 'Total Put OI'], 
                     color_discrete_sequence=['red', 'green'], title="OI Dominance")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        # Simple Intraday PCR Line (Mocking trend with random variations around current PCR)
        pcr = total_pe / total_ce if total_ce > 0 else 1
        pcr_trend = [pcr * (1 + (i-5)*0.01) for i in range(10)]
        fig = px.line(x=range(10), y=pcr_trend, title="Intraday PCR Trend (Simulated)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_oi_heatmap(df):
    # Simple heatmap of OI
    fig = px.imshow([df['CE_OI'].values, df['PE_OI'].values], 
                    labels=dict(x="Strike", y="Option Type", color="OI"),
                    x=df.index, y=['CE', 'PE'],
                    color_continuous_scale='RdYlGn',
                    title="OI Heatmap")
    st.plotly_chart(fig, use_container_width=True)
