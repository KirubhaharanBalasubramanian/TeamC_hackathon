import streamlit as st
from upload_script import upload_drive
from get_contents import contents
from streamlit_lottie import st_lottie
import json
from datetime import datetime
import pandas as pd
import pandas as pd
import geopandas as gpd
from shapely import wkt
import matplotlib.pyplot as plt
from contents_csv import contents_from_CSV

df_paris = gpd.GeoDataFrame(pd.read_csv('/Users/kirubha/Documents/GitHub/TeamC_hackathon/csv/geo_paris.csv'))
df_paris['geometry'] = df_paris['geometry'].apply(wkt.loads)
df_paris = df_paris.set_geometry('geometry')
df_zips = gpd.GeoDataFrame(pd.read_csv('/Users/kirubha/Documents/GitHub/TeamC_hackathon/csv/geo_zips.csv'))
df_zips['geometry'] = df_zips['geometry'].apply(wkt.loads)
df_zips = df_zips.set_geometry('geometry')


def visualizer(df, list_visuals):
    if 'zip_code' in df.columns:
        df = df.merge(df_zips, how='left', on='zipcode')
        df = gpd.GeoDataFrame(df).set_geometry('geometry')
    for visio in list_visuals:
        if visio == 'visu_1':
            if ('latitude' in df.columns) and ('longitude' in df.columns):
                fig, ax = plt.subplots(figsize=(20, 20))
                df_paris.plot(alpha=0.2, ax=ax)
                df[['latitude', 'longitude']].plot(kind='scatter', x='longitude', y='latitude', ax=ax,
                                                   color='tab:orange')
                plt.savefig('output_visualize.png')


def save_question_to_file(question):
    current_date = datetime.now().strftime("%Y-%m-%d")
    with open("questions.txt", "a") as file:
        file.write(f"{current_date}: {question}\n")


def display_csv_contents():
    df = pd.read_csv("output.csv")
    st.write(df)


def main():
    st.title("EchoBase")

    # Define layout
    col1, col2 = st.columns([1, 3])

    # Left column for animations
    with col1:
        # Load Lottie animation
        with open("AI Animation.json", "r") as f:
            lottie_json = json.load(f)
        st_lottie(lottie_json)

    # Right column for contents
    with col2:
        user_input = st.text_area("Enter your prompt:")

        # Save to text file on button click
    if st.button("Generate"):
        upload_drive(user_input)

        with st.spinner("AI is computing..."):
            df = contents_from_CSV()
            st.table(df)
            st.write("DOWNLOADED CSV SUCCESS")
            st.write("CSV CONTENTS")
            # display_csv_contents()
            st.success("Computation Success!")

    df = pd.read_csv('/Users/kirubha/Documents/GitHub/TeamC_hackathon/csv/local_output.csv')
    if len(df.columns) == 1 and len(df) == 1:
        x = f"Output: {df.iloc[0, 0]}"
    else:
        # LLM to process things
        visualizer(df, ['visu_1'])


if __name__ == "__main__":
    main()
