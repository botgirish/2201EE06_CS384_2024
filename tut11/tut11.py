import streamlit as st
import pandas as pd

# Function to process the uploaded Excel file
def process_excel(uploaded_file):
    # Load student data
    student_data = pd.read_excel(uploaded_file, sheet_name='Sheet1')

    # Create Grade Statistics DataFrame
    data = {
        "Subject Code": [None] * 11,
        "Month Year": ["Nov-24"] * 11,
        "Grade": ["AA", "AB", "BB", "BC", "CC", "CD", "DD", "F", "I", "PP", "NP"],
        "a": [91, 81, 71, 61, 51, 41, 31, 0, None, None, None],
        "b": [100, 90, 80, 70, 60, 50, 40, 30, None, None, None],
        "min (x)": [None] * 11,
        "max (x)": [None] * 11,
    }
    df = pd.DataFrame(data)

    # Calculate min and max Total for each grade
    grade_stats = student_data.groupby('Grade')['Total'].agg(['min', 'max']).reset_index()
    for index, row in df.iterrows():
        grade = row['Grade']
        if grade in grade_stats['Grade'].values:
            grade_row = grade_stats[grade_stats['Grade'] == grade]
            df.at[index, 'min (x)'] = grade_row['min'].values[0]
            df.at[index, 'max (x)'] = grade_row['max'].values[0]

    # Scaling formula
    def scale_marks(row, grade_df):
        grade = row['Grade']
        if grade in grade_df['Grade'].values:
            grade_row = grade_df[grade_df['Grade'] == grade]
            a, b = grade_row['a'].values[0], grade_row['b'].values[0]
            min_x, max_x = grade_row['min (x)'].values[0], grade_row['max (x)'].values[0]
            return (((b - a) * (row['Total'] - min_x)) / (max_x - min_x)) + a
        return None

    student_data['Scaled'] = student_data.apply(scale_marks, axis=1, grade_df=df)

    # Calculate Grade Counts and IAPC Difference
    total_students = len(student_data)
    grade_counts = student_data['Grade'].value_counts().reset_index()
    grade_counts.columns = ['Grade', 'Count']

    iapc_values = [5, 15, 25, 30, 15, 5, 5, 0]  # Example IAPC distribution
    iapc_index = ['AA', 'AB', 'BB', 'BC', 'CC', 'CD', 'DD', 'F']
    iapc_dict = dict(zip(iapc_index, iapc_values))

    grade_counts['IAPC'] = grade_counts['Grade'].map(iapc_dict)
    grade_counts['IAPC_count'] = (grade_counts['IAPC'] * total_students / 100).round().astype(int)
    grade_counts['Difference'] = grade_counts['Count'] - grade_counts['IAPC_count']
    grade_counts_sorted = grade_counts.sort_values(by='Grade').reset_index(drop=True)

    return student_data, df, grade_counts_sorted

# Streamlit App
st.title("Excel Processor for Grades and Scaled Scores")
uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])

if uploaded_file:
    st.success("File uploaded successfully!")
    student_data, df, grade_counts_sorted = process_excel(uploaded_file)

    # Display DataFrames
    st.header("Student Data")
    st.dataframe(student_data)
    st.header("Grade Statistics")
    st.dataframe(df)
    st.header("Sorted Grade Counts Difference")
    st.dataframe(grade_counts_sorted)

    # Download Processed Data
    with pd.ExcelWriter("processed_data.xlsx", engine='openpyxl') as writer:
        student_data.to_excel(writer, sheet_name="student_data", index=False)
        df.to_excel(writer, sheet_name="grade_statistics", index=False)
        grade_counts_sorted.to_excel(writer, sheet_name="grade_counts_sorted", index=False)

    with open("processed_data.xlsx", "rb") as file:
        st.download_button("Download Processed Excel", data=file, file_name="processed_data.xlsx")