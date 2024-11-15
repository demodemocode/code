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