import sqlite3


from filter import create_filter_sidebar, apply_filters

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def create_km_driven_boxplot(df):
    """
    Create a boxplot of kilometers driven.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.boxplot(df["kmdriven"], patch_artist=True)
    ax.set_title("Boxplot of Kilometers Driven", fontsize=16)
    ax.set_ylabel("Kilometers Driven", fontsize=12)

    #formatting y-axis to show numbers in readable format
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # Add grid for better readability
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    #adjusting the padding around plt
    plt.tight_layout()
    return fig


def create_heatmap(df):

    """
    Create a heatmap of correlations between features using Matplotlib.
    """
    #columns for correlation
    correlation_matrix = df[["relativeprice", "kmdriven", "age", "askprice"]].corr()

    #figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))

    #creating heatmap
    cax = ax.matshow(correlation_matrix, cmap="coolwarm")

    #adding color bar
    plt.colorbar(cax)

    # Set ticks and labels
    ax.set_xticks(np.arange(len(correlation_matrix.columns)))
    ax.set_yticks(np.arange(len(correlation_matrix.index)))
    ax.set_xticklabels(correlation_matrix.columns, rotation=45, ha="right")
    ax.set_yticklabels(correlation_matrix.index)

    # Add title
    ax.set_title("Correlation Heatmap", fontsize=16)

    # Display the correlation values on the heatmap
    for (i, j), val in np.ndenumerate(correlation_matrix):
        ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="black")

    plt.tight_layout()
    return fig


def create_histogram(df):
    """
    Create a histogram of relative prices
    """
    if df.empty:
        st.warning("No data available for histogram")
        return None

    #removing outliers
    lower_percentile = df["relativeprice"].quantile(0.05)
    upper_percentile = df["relativeprice"].quantile(0.95)

    filtered_data = df[
        (df["relativeprice"] >= lower_percentile) &
        (df["relativeprice"] <= upper_percentile)
        ]

    fig, ax = plt.subplots(figsize=(12, 6))

    #create histogram
    ax.hist(filtered_data["relativeprice"], bins=30, edgecolor="black")

    #customizing axis
    ax.set_title("Distribution of Relative Prices", fontsize=16)
    ax.set_xlabel("Relative Price", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)

    #marking average
    ax.axvline(x=1, color="r", linestyle="--", label="Average Price")

    ax.grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()
    return fig


def create_pie_chart(df):
    """
    Create a pie chart of price classifications
    """
    fig, ax = plt.subplots(figsize=(5, 3))

    # Count price classifications
    price_class_counts = df["priceclassification"].value_counts()

    # Create pie chart
    ax.pie(
        price_class_counts,
        labels=price_class_counts.index,
        autopct="%1.1f%%",
        colors=["green", "lightgreen", "blue", "orange", "red"]
    )

    plt.tight_layout()
    return fig

def load_data_from_db(db_path):
        """
        Load data from database car_view. (Should be in DatabaseLoadClass but issues with packages)

        :param db_path: Path to the SQLite database
        :return: DataFrame containing the data
        """
        try:
            conn = sqlite3.connect(db_path)
            query = "SELECT * FROM car_view"  # Adjust the query as needed
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df

        except Exception as e:

            print(f"Error loading data from database: {e}")
            return pd.DataFrame()  # Return an empty df if error


def main():
    # Set page configuration
    st.set_page_config(layout="wide")
    st.title("Car Deal Analysis")

    # Load data from the SQLite database
    db_path = "../../resources/used_cars.db"
    df = load_data_from_db(db_path)

    # Create sidebar with basic filters
    filters, intermediate_df = create_filter_sidebar(df)

    # Apply additional filters
    filtered_df, row_count = apply_filters(intermediate_df, filters)

    # Display warning if no data is available
    if row_count == 0:
        st.warning("No data available for the selected filters. Please adjust your selections.")
        return  # Exit early if no data

    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs([
        "Boxplot of Kilometers Driven",
        "Correlation Heatmap",
        "Relative Price Distribution Histogram",
        "Price Classification Distribution Pie Chart"
    ])

    with tab1:
        st.header("KmDriven Histogram")
        fig1 = create_km_driven_boxplot(filtered_df)
        st.pyplot(fig1)

    with tab2:
        st.header("Correlation Heatmap")
        fig2 = create_heatmap(filtered_df)
        st.pyplot(fig2)

        # Explanation of correlations
        st.write("""
            ### Correlation Coefficients:
            - **1**: Perfect positive correlation (as one variable increases, the other also increases).
            - **-1**: Perfect negative correlation (as one variable increases, the other decreases).
            - **0**: No correlation (the variables do not affect each other).
            """)

    with tab3:
        st.header("Relative Price Distribution")
        fig3 = create_histogram(filtered_df)
        st.pyplot(fig3)

    with tab4:
        st.header("Price Classification Distribution")
        fig4 = create_pie_chart(filtered_df)
        st.pyplot(fig4)

    #display summary statistics under every tab
    st.header("Summary Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Deals", len(filtered_df))
    with col2:
        st.metric("Avg Kilometers", f"{filtered_df['kmdriven'].mean():.0f}")

    #Display filtered df
    st.header("Filtered Car Deals")
    st.dataframe(filtered_df)


if __name__ == "__main__":
    main()