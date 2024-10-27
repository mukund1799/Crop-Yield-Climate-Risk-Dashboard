import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np 
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Add company logo at the top
logo_path = "C:/Users/feby4/Downloads/Business Case Study and Report.png"  # Replace with the actual path to the logo
st.image(logo_path, width=400) 

# # Add company name at the top
# st.markdown("<h1 style='text-align: center; color: green;'>CropCast</h1>", unsafe_allow_html=True)
# Load data
file_path = "C:/Users/feby4/Downloads/1/GygaAustralia.xlsx"  # Path to your dataset
gyga_data = {
    'Country Year': pd.read_excel(file_path, sheet_name='Country Year'),
    'Climate Zone Year': pd.read_excel(file_path, sheet_name='Climate Zone Year'),
    'Climate Zone': pd.read_excel(file_path, sheet_name='Climate zone')
}


# Adding Overview Pop-up using st.expander
with st.sidebar.expander("Overview", expanded=False):
    st.write("""
    **Yield Over Time**: This section shows how crop yields have changed over the years for different crops.

    **Temperature Impact on Yield**: This section simulates how changes in temperature could affect the crop yield. Farmers can understand how increasing or decreasing temperature will impact their crops.

    **Climate Zone Risk Level**: This shows how different climate zones affect the potential yield of crops. It helps farmers see which zones are riskier or more stable for crop production.

    **Recommendations**: Based on temperature changes, this section gives farmers recommendations for their crops, such as switching to heat-tolerant crops or improving irrigation.

    **Correlation Analysis**: This section shows how different factors (like water productivity, temperature, and climate zones) are related to crop yield.

    **Water Productivity Analysis**: This shows how efficiently water is being used to produce crops. It can help farmers understand how to optimize water usage.

    **Crop vs Climate Zone**: This cross-tab analysis shows which crops perform best in different climate zones.

    **Yield Forecasting**: Using historical yield data, this section provides a short-term forecast of crop yield, helping farmers anticipate future trends.

    **Moving Average Yield Forecasting**: This method smooths out yield data over time to reveal long-term trends and predict future yields.
    """)


# Sidebar for user input
st.sidebar.header("Filter Options")
crop_type = st.sidebar.selectbox("Select Crop Type", gyga_data['Country Year']['CROP'].unique())
year_range = st.sidebar.slider("Select Year Range", 
                                int(gyga_data['Country Year']['HARVESTYEAR'].min()), 
                                int(gyga_data['Country Year']['HARVESTYEAR'].max()), 
                                (int(gyga_data['Country Year']['HARVESTYEAR'].min()), int(gyga_data['Country Year']['HARVESTYEAR'].max())))

# Filter data based on user input
country_year_data = gyga_data['Country Year']
filtered_data = country_year_data[(country_year_data['CROP'] == crop_type) & 
                                  (country_year_data['HARVESTYEAR'] >= year_range[0]) & 
                                  (country_year_data['HARVESTYEAR'] <= year_range[1])]

# Allow the user to select which yield type (YP, YA, YW) they want to visualize
yield_type = st.sidebar.selectbox("Select Yield Type", ['YP', 'YA', 'YW'])

# Correlation Analysis
numeric_data = filtered_data.select_dtypes(include=[np.number])

# Compute correlation matrix
correlation_matrix = numeric_data.corr()

# Prepare data for forecasting
historical_data = filtered_data[['HARVESTYEAR', yield_type]].dropna()
X = historical_data['HARVESTYEAR'].values.reshape(-1, 1)
y = historical_data[yield_type].values

# Split data for training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and fit the linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict future years (e.g., 5 years ahead)
future_years = np.array([year_range[1] + i for i in range(1, 6)]).reshape(-1, 1)
predicted_yields = model.predict(future_years)

# Combine historical and forecast data for visualization
forecast_data = pd.DataFrame({
    'HARVESTYEAR': future_years.flatten(),
    yield_type: predicted_yields
})

# Title of the dashboard
st.title("Crop Yield and Climate Risk Analysis Dashboard")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "Yield Over Time",
    "Temperature Impact on Yield",
    "Climate Zone Risk Level",
    "Recommendations",
    "Correlation Analysis",
    "Water Productivity Analysis",
    "Crop vs Climate Zone",
    "Yield Forecasting",
    "Moving Average Forecasting"
])

# Explanation Section for Farmers (Collapsible) - Yield Over Time
with tab1:
    st.header(f"Temporal Changes in Yield for {crop_type}")
    with st.expander("Explanation of Terms"):
        st.write("""
        - **YP (Potential Yield)**: This is the maximum yield you could achieve with the best possible growing conditions.
        - **YA (Actual Yield)**: This is the actual yield obtained from your fields, which is usually lower than YP due to environmental and management factors.
        - **YW (Water-limited Yield)**: This is the yield achievable under rainfed conditions where water is a limiting factor.
        """)

        st.write("""
        **How This Helps Farmers**: By looking at how yields change over time, farmers can see whether their productivity is increasing or decreasing. This information helps in making decisions on whether to adjust farming practices, try new crop varieties, or manage resources more efficiently.
        """)
    fig1 = px.line(filtered_data, x='HARVESTYEAR', y=['YA', 'YW', 'YP'], 
                   labels={'value': 'Yield (tons/ha)', 'HARVESTYEAR': 'Harvest Year'}, 
                   title=f'Temporal Changes in Yield for {crop_type}')
    st.plotly_chart(fig1)

# Temperature Impact Explanation
with tab2:
    st.header("Impact of Temperature Change on Yield")
    with st.expander("Explanation of Terms"):
        st.write("""
        **How This Helps Farmers**: This section simulates how changing temperatures might affect the yields. If temperatures are expected to rise, this tool shows how it will impact your crop productivity and can help in preparing for climate change.
        """)
    temperature_change = st.sidebar.slider("Select Temperature Change (°C)", 0.0, 5.0, 2.0)
    impact_data = filtered_data.copy()
    impact_data['Yield Under Temperature Change'] = impact_data['YP'] * (1 - temperature_change * 0.1)
    fig2 = px.line(impact_data, x='HARVESTYEAR', y='Yield Under Temperature Change',
                   labels={'Yield Under Temperature Change': 'Yield (tons/ha)', 'HARVESTYEAR': 'Harvest Year'},
                   title=f'Projected Yield Under Temperature Change of {temperature_change}°C')
    st.plotly_chart(fig2)

# Climate Zone Risk Level
with tab3:
    st.header("Climate Zone Risk Level Analysis")
    with st.expander("Explanation of Terms"):
        st.write("""
        **How This Helps Farmers**: Climate zones vary in their suitability for different crops. This section shows how risky it is to plant a specific crop in a particular climate zone, helping farmers make better land-use decisions.
        """)
    climate_zone_year_data = gyga_data['Climate Zone Year'][gyga_data['Climate Zone Year']['CROP'] == crop_type]
    fig3 = px.line(climate_zone_year_data, x='HARVESTYEAR', y='YP', color='CLIMATEZONE',
                   labels={'HARVESTYEAR': 'Year', 'YP': 'Potential Yield (tons/ha)', 'CLIMATEZONE': 'Climate Zone'},
                   title=f'Year-wise Potential Yield Trends at Climate Zone Level for {crop_type}')
    st.plotly_chart(fig3)

# Recommendations for Farmers
with tab4:
    st.header("Recommendations for Farmers")
    with st.expander("Explanation of Recommendations"):
        st.write("""
        **How This Helps Farmers**: Based on the temperature and climate data, the dashboard offers recommendations for managing crops under varying climate conditions. This helps farmers adapt to climate change and make informed decisions on farming practices.
        """)
    if temperature_change >= 3.0:
        st.warning(f"High temperature increase detected ({temperature_change}°C). Consider adopting heat-tolerant crop varieties, optimizing irrigation, and using soil moisture conservation practices.")
    else:
        st.success(f"Temperature is within a manageable range ({temperature_change}°C). Continue with regular practices but monitor soil moisture levels and use early warning systems.")

# Correlation Analysis Explanation
with tab5:
    st.header("Correlation Heatmap of Yield Factors")
    with st.expander("Explanation of Correlation"):
        st.write("""
        **How This Helps Farmers**: Correlation shows how different factors like water use, temperature, and yield are related. Farmers can understand which factors have the most significant impact on their crop productivity.
        """)
    heatmap_fig = px.imshow(correlation_matrix, text_auto=True, aspect="auto", 
                            color_continuous_scale='RdBu_r', title='Correlation Matrix of Variables')
    st.plotly_chart(heatmap_fig)

# Water Productivity Analysis
with tab6:
    st.header("Water Productivity Analysis")
    with st.expander("Explanation of Water Productivity"):
        st.write("""
        - **WPP (Water Productivity Potential)**: This measures how much yield you can get per unit of water.
        - **WPA (Water Productivity Actual)**: This is the actual yield obtained per unit of water.
        
        **How This Helps Farmers**: By understanding how much water your crops are using versus how much they should be using, you can optimize irrigation and conserve water, which is especially important in areas facing water shortages.
        """)
    fig4 = px.scatter(filtered_data, x='WPP', y='YA', color='CROP',
                      size='WPA', hover_data=['CROP', 'HARVESTYEAR', 'COUNTRY'],
                      labels={"WPP": "Water Productivity per mm water per hectare (kg/m³)", "YA": "Yield (tons/ha)"},
                      title=f"Water Productivity vs. Yield Analysis for {crop_type}")
    st.plotly_chart(fig4)

# Cross-tab Analysis of Crop Types and Climate Zones
with tab7:
    st.header("Cross-Tab Analysis: Crop Types vs. Climate Zones")
    with st.expander("Explanation of Cross-tab Analysis"):
        st.write("""
        **How This Helps Farmers**: This section compares how different crops perform in various climate zones. It helps farmers decide which crops to plant depending on the climate of their region, leading to better crop selection and increased yields.
        """)
    # Creating a pivot table to show mean yield by crop type and climate zone
    climate_zone_data = gyga_data['Climate Zone Year']
    pivot_data = climate_zone_data.pivot_table(values=yield_type, 
                                               index='CROP', 
                                               columns='CLIMATEZONE', 
                                               aggfunc='mean')

    # Display the pivot table as a heatmap
    fig5 = px.imshow(pivot_data, text_auto=True, aspect="auto", 
                     color_continuous_scale='Viridis', 
                     labels={'color': 'Value'},
                     title=f'{yield_type} by Crop Type and Climate Zone')
    st.plotly_chart(fig5)

# Yield Forecasting Explanation
with tab8:
    st.header(f"Yield Forecasting for {crop_type} ({yield_type})")
    with st.expander("Explanation of Yield Forecasting"):
        st.write("""
        **How This Helps Farmers**: Yield forecasting uses historical data to predict future crop yields. Farmers can use this information to plan their crop production, manage resources, and make strategic decisions about their future planting seasons.
        """)
    # Plot historical and forecast data
    combined_data = pd.concat([historical_data, forecast_data], ignore_index=True)
    fig8 = px.line(combined_data, x='HARVESTYEAR', y=yield_type, 
                   labels={'HARVESTYEAR': 'Year', yield_type: 'Yield (tons/ha)'}, 
                   title=f"Yield Forecast for {crop_type} ({yield_type})")
    fig8.add_scatter(x=future_years.flatten(), y=predicted_yields, mode='lines', name='Forecast')

    # Show the plot
    st.plotly_chart(fig8)

# Moving Average Forecasting
with tab9:
    st.header(f"Moving Average Yield Forecast for {crop_type} ({yield_type})")
    with st.expander("Explanation of Moving Average Forecasting"):
        st.write("""
        **How This Helps Farmers**: The moving average forecast smooths out the historical yield data to show trends and helps predict future yields. This technique is useful for understanding longer-term trends, reducing noise in the data, and making informed decisions about future crops.
        """)
    
    # Historical data for moving average
    historical_data = filtered_data[['HARVESTYEAR', yield_type]]

    # Sidebar: Allow user to select moving average window
    window_size = st.sidebar.slider("Select Moving Average Window", 1, 5, 3)
    
    # Calculate moving average
    filtered_data['Moving_Average'] = filtered_data[yield_type].rolling(window=window_size).mean()

    # Plot Moving Average
    fig7 = px.line(filtered_data, x='HARVESTYEAR', y='Moving_Average', 
                   labels={'HARVESTYEAR': 'Year', 'Moving_Average': f'Moving Average of {yield_type}'}, 
                   title=f'Moving Average of {yield_type} for {crop_type} with Window Size {window_size}')
    st.plotly_chart(fig7)

# Footer Information
st.sidebar.info("This dashboard provides insights into crop yield, climate-related risks, and potential yield trends across climate zones. Use the tabs to view different visualizations.")
