import React, { useContext } from "react";
import { FaFolder, FaFileAlt, FaChevronRight, FaChevronDown, FaFilePdf, FaFileImage } from "react-icons/fa";
import { Context } from "../../context/Context";

// Helper function to get the correct icon based on the file type
const getFileIcon = (fileName) => {
  const fileExtension = fileName.split('.').pop().toLowerCase();
  
  switch (fileExtension) {
    case 'pdf':
      return <FaFilePdf />;
    case 'txt':
      return <FaFileAlt />;
    case 'jpg':
    case 'jpeg':
    case 'png':
      return <FaFileImage />;
    case 'folder':
      return <FaFolder />;
    default:
      return <FaFileAlt />;
  }
};

// Viewer component
const Viewer = () => {
  const { fileHistory } = useContext(Context);
  
  return (
    <div className="App">
      <h2>File Explorer</h2>
      <div style={{ marginTop: "20px" }}>
        <p className="fileHistory">
          {fileHistory.length > 0
            ? fileHistory.map((file, index) => (
                <span key={index} style={{ display: "flex", alignItems: "center" }}>
                  {getFileIcon(file.fileName)}
                  <span style={{ marginLeft: "10px" }}>{file.fileName}</span>
                  <br />
                </span>
              ))
            : "No files uploaded."}
        </p>
      </div>
    </div>
  );
};

export default Viewer;
