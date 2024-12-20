function downloadCSV(data, fileName = "data.csv") {
    // Convert JSON data to CSV format
    const csv = data.map(row => Object.values(row).join(",")).join("\n");
  
    // Create a Blob object and URL for the CSV
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
  
    // Create a temporary link and trigger download
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  

import * as XLSX from "xlsx";
import { saveAs } from "file-saver";

function downloadExcel(data, fileName = "data.xlsx") {
  // Create a worksheet from the JSON data
  const worksheet = XLSX.utils.json_to_sheet(data);

  // Create a new workbook and append the worksheet
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");

  // Write the workbook and create a Blob object
  const excelBuffer = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
  const blob = new Blob([excelBuffer], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8",
  });

  // Use FileSaver.js to save the file
  saveAs(blob, fileName);
}


import jsPDF from "jspdf";
import "jspdf-autotable";

function printPDF(data, fileName = "data.pdf") {
  // Create a new instance of jsPDF
  const doc = new jsPDF();

  // Extract column headers from data keys
  const columns = Object.keys(data[0]).map(key => ({ header: key, dataKey: key }));

  // Add title to the PDF
  doc.text("Data Table", 14, 10);

  // Use AutoTable to add the table
  doc.autoTable({
    columns, // Columns for the table
    body: data, // Data for the table
    startY: 20, // Table start position
    theme: "grid", // Table style
    headStyles: { fillColor: [22, 160, 133] }, // Header color
    styles: { fontSize: 10 } // Table font size
  });

  // Save the generated PDF
  doc.save(fileName);
}

function deleteResourceWithAuth(resourceId) {
  axios
    .delete(`https://your-api-url.com/resources/${resourceId}`, {
      headers: {
        Authorization: `Bearer YOUR_JWT_TOKEN`
      }
    })
    .then(response => {
      console.log('Resource deleted:', response.data);
    })
    .catch(error => {
      console.error('Error deleting resource:', error.response ? error.response.data : error.message);
    });
}


import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://your-api-url.com',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer YOUR_JWT_TOKEN`, // Replace with your token
  },
});

export default apiClient;


export const getResource = async (resourceId) => {
  try {
    const response = await apiClient.get(`/resources/${resourceId}`);
    console.log('GET response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error in GET:', error.response ? error.response.data : error.message);
  }
};


export const createResource = async (data) => {
  try {
    const response = await apiClient.post('/resources', data);
    console.log('POST response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error in POST:', error.response ? error.response.data : error.message);
  }
};


export const updateResource = async (resourceId, updatedData) => {
  try {
    const response = await apiClient.put(`/resources/${resourceId}`, updatedData);
    console.log('PUT response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error in PUT:', error.response ? error.response.data : error.message);
  }
};

export const deleteResource = async (resourceId) => {
  try {
    const response = await apiClient.delete(`/resources/${resourceId}`);
    console.log('DELETE response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error in DELETE:', error.response ? error.response.data : error.message);
  }
};

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        // Disable CORS by not allowing any origins or methods
        registry.addMapping("/**") // Apply to all endpoints
                .allowedOrigins()    // No origins allowed
                .allowedMethods();   // No methods allowed
    }
}


import React from "react";
import ReactDOM from "react-dom";
import Report from "./Report"; // Import the Report component

const openReportInNewTab = (data) => {
  // Open a new blank tab
  const newTab = window.open("", "_blank");

  if (!newTab) {
    alert("Failed to open new tab. Check your browser's pop-up blocker.");
    return;
  }

  // Write the basic HTML structure to the new tab
  newTab.document.write(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Report</title>
      <div id="root"></div>
    </head>
    <body>
      <div id="root"></div>
    </body>
    </html>
  `);

  // Close the document to finish the HTML writing process
  newTab.document.close();

  // Render the Report component into the new tab
  ReactDOM.render(<Report data={data} />, newTab.document.getElementById("root"));
};



apiClient.interceptors.request.use(
  (config) => {
    const token = Cookies.get('token'); // Replace 'token' with the actual cookie name
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

