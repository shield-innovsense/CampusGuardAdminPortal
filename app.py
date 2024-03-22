import streamlit as st
from pymongo import MongoClient
import pandas as pd
import base64
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()

mongo_url=os.getenv("Mongo_url")
# MongoDB connection
client = MongoClient(f"mongodb+srv://{mongo_url}")
db = client["CampusGuard"]  
collection = db["UserReports5"]  
data = {
    'Timestamp': [],
    'Incident Type': [],
    'Location': []   
}

# Main display logic
st.title("Incident Reports Retrieval")
incident_types = ["Mobile Phone", "No Helmet", "Sleeping", "Triples", "Violence"]
filter_type = st.selectbox("**Filter by Incident Type**", incident_types, index=len(incident_types) - 1)  

if filter_type != "All":
    reports = collection.find({"incident_type": filter_type})
else:
    reports = collection.find({})

for report in reports:
    st.subheader(f"Incident Type: {report['incident_type']}")
    st.write(f"Location: {report['location']}")
    st.write(f"Timestamp: {report['timestamp']}")
    
    incident_data = report.get('incident_data', [])
    
    if incident_data:  
        img_count = 0
        video_count = 0
        c=1

        for image_info in incident_data:
            if image_info.get("file_type") in ["image/jpg", "image/jpeg", "image/png"]:
                img_count += 1
            elif image_info.get("file_type") == "video/mp4":
                video_count += 1

        if img_count > 0:
            st.write(f"Image{'s' if img_count > 1 else ''}:")
            for i, image_info in enumerate(incident_data, 1):
                if image_info.get("file_type") in ["image/jpg", "image/jpeg", "image/png"]:
                    encoded_image = base64.b64encode(image_info["file_content"]).decode("utf-8")
                    image_data = f"data:image/{image_info['file_type']};base64,{encoded_image}"
                    st.image(image_data, caption=f"Image {i}", use_column_width=True)
                

        if video_count > 0:
            st.write(f"Video{'s' if video_count > 1 else ''}:")
            for i, image_info in enumerate(incident_data, 1):
                if image_info.get("file_type") == "video/mp4":
                    st.video(image_info.get("file_content"), format="video/mp4")
                    


    
    st.write("-" * 20)
    data['Timestamp'].append(report['timestamp'])
    data['Incident Type'].append(report['incident_type'])
    data['Location'].append(report['location']) 




df = pd.DataFrame(data)


csv_file = "incident_reports.csv"

df.to_csv(csv_file, index=False)



with st.sidebar:
    st.markdown(f"Download the CSV file [here](data:text/csv;base64,{base64.b64encode(open(csv_file, 'rb').read()).decode()}), Right-click and save-as.")

    if st.button("Analyze"):
        df = pd.read_csv("incident_reports.csv")
        df2=pd.read_csv("faculty_incharge.csv")

        # Clean location names by removing leading and trailing whitespace
        df['Location'] = df['Location'].str.strip()

        # Count unique locations
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
        df2 = df2.rename(columns={'Place': 'Location'})
        location_incharge_details = pd.DataFrame(columns=['Location', 'Incharge Name', 'Mobile Number', 'Employee No', 'Department'])

# Iterate over unique locations and fetch incharge details for each location
        for location in unique_locations:
            # Filter incharge details for the current location
            location_incharge = df2[df2['Location'] == location]
            location_incharge['Mobile Number'] = location_incharge['Mobile Number'].astype(str)
            location_incharge['Mobile Number'] = location_incharge['Mobile Number'].str.cat(sep=', ')

            # Append the filtered incharge details to the DataFrame
            location_incharge_details = pd.concat([location_incharge_details, location_incharge], ignore_index=True)

        # Display all location and incharge details
        st.write("**Incharge Details for Unique Locations:**")
        st.write(location_incharge_details)

