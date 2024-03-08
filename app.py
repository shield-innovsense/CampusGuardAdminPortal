import streamlit as st
from pymongo import MongoClient
import base64
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import pandas as pd

load_dotenv()

url = client = os.getenv("MONGODB_CLIENT")

client = MongoClient(url)
db = client["CampusGuard"]  # Replace with your database name
collection = db["UserReports"]  # Replace with your collection name


st.title("Incident Reports Retrieval")
incident_types = ["Mobile Phone", "No Helmet", "Sleeping", "Triples", "Violence"]
filter_type = st.selectbox("**Filter by Incident Type**", incident_types, index=len(incident_types) - 1)  

if filter_type != "All":
    reports = collection.find({"incident_type": filter_type})
else:
    reports = collection.find({})

# Store data for CSV
data = {
    'Timestamp': [],
    'Incident Type': [],
    'Location': []
    
}
for report in reports:
   
    st.subheader(f"Incident Type: {report['incident_type']}")
    st.write(f"Location: {report['location']}")
    st.write(f"Timestamp: {report['timestamp']}")
   

    if report["file_type"] in ["image/jpg", "image/jpeg", "image/png"]:
        encoded_image = base64.b64encode(report["file_content"]).decode("utf-8")
        image_data = f"data:image/{report['file_type']};base64,{encoded_image}"
        st.image(image_data, width=300)
    elif report["file_type"] == "video/mp4":
        st.video(report["file_content"], format="video/mp4")
    else:
        st.write("No image or video available for this report.")

    st.write("-" * 20)
    
    # Update data for CSV
    data['Timestamp'].append(report['timestamp'])
    data['Incident Type'].append(report['incident_type'])
    data['Location'].append(report['location'])
   
  # Create DataFrame
df = pd.DataFrame(data)

    # Save to CSV
csv_file = "incident_reports.csv"
df.to_csv(csv_file, index=False)

with st.sidebar:
    st.markdown(f"Download the CSV file [here](data:text/csv;base64,{base64.b64encode(open(csv_file, 'rb').read()).decode()}), Right-click and save-as.")

    if st.button("Analyze"):
        df = pd.read_csv("incident_reports.csv")

    # Clean location names by removing leading and trailing whitespace
        df['Location'] = df['Location'].str.strip()

        # Debugging: Print unique values of the "Location" column
        unique_locations = df['Location'].unique()
        st.write("Unique Locations:", unique_locations)

        # Count occurrences of each location
        location_counts = df['Location'].value_counts()

        # Plot bar chart
        fig, ax = plt.subplots()
        ax.bar(location_counts.index, location_counts.values)
        ax.set_xlabel('Location')
        ax.set_ylabel('Count')
        ax.set_title('Incident Counts by Location')
        ax.tick_params(axis='x', rotation=0)  
        plt.tight_layout()
      

        # Display the plot using Streamlit
        st.pyplot(fig)
        max_count_location = location_counts.idxmax()
        max_count = location_counts.max()

        # Filter DataFrame to get reports for the location with maximum count
        max_count_reports = df[df['Location'] == max_count_location]

        # Display the location with maximum count and corresponding data
        st.write(f"**Location with Maximum Count:** {max_count_location}")
        st.write(f"**Maximum Count:** {max_count}")
        # st.write("Reports:")
        # st.write(max_count_reports)