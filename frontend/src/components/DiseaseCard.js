// src/components/DiseaseCard.js
// (Unchanged: you can use it later to show RAG disease details if needed)
import React from "react";

const DiseaseCard = ({ disease }) => {
  if (!disease) return null;

  return (
    <div
      className="disease-card"
      style={{
        background: "#f9faf9",
        border: "1px solid #dfe8df",
        borderRadius: "12px",
        padding: "16px",
        marginBottom: "18px",
      }}
    >
      <div
        className="disease-header"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "8px",
        }}
      >
        <div
          className="disease-name"
          style={{
            fontSize: "20px",
            fontWeight: "bold",
            color: "#2c5530",
          }}
        >
          {disease.disease_name}
        </div>

        <div
          className="disease-crop"
          style={{
            background: "#d0f0d0",
            padding: "6px 12px",
            borderRadius: "14px",
            fontSize: "15px",
            fontWeight: "600",
            color: "#2e7d32",
          }}
        >
          {disease.crop}
        </div>
      </div>

      <div className="disease-section" style={{ marginBottom: "10px" }}>
        <div
          className="section-title"
          style={{ fontSize: "17px", fontWeight: "600", color: "#455a64" }}
        >
          Description
        </div>
        <div
          className="section-content"
          style={{ fontSize: "16px", color: "#4e4e4e", lineHeight: 1.4 }}
        >
          {disease.description}
        </div>
      </div>

      <div className="disease-section" style={{ marginBottom: "10px" }}>
        <div
          className="section-title"
          style={{ fontSize: "17px", fontWeight: "600", color: "#455a64" }}
        >
          Symptoms
        </div>
        <div
          className="section-content"
          style={{ fontSize: "16px", color: "#4e4e4e", lineHeight: 1.4 }}
        >
          {disease.symptoms}
        </div>
      </div>

      <div className="disease-section" style={{ marginBottom: "10px" }}>
        <div
          className="section-title"
          style={{ fontSize: "17px", fontWeight: "600", color: "#455a64" }}
        >
          Solution
        </div>
        <div
          className="section-content"
          style={{ fontSize: "16px", color: "#4e4e4e", lineHeight: 1.4 }}
        >
          {disease.solution}
        </div>
      </div>

      {disease.pesticides && disease.pesticides.length > 0 && (
        <div className="disease-section" style={{ marginTop: "12px" }}>
          <div
            className="section-title"
            style={{ fontSize: "17px", fontWeight: "600", color: "#455a64" }}
          >
            Recommended Pesticides
          </div>

          <div className="pesticides-list" style={{ marginTop: "4px" }}>
            {disease.pesticides.map((pesticide, index) => (
              <a
                key={index}
                href={pesticide.url}
                target="_blank"
                rel="noopener noreferrer"
                className="pesticide-item"
                style={{
                  display: "block",
                  padding: "6px 0",
                  fontSize: "15px",
                  color: "#1976d2",
                  textDecoration: "none",
                  fontWeight: "500",
                }}
              >
                • {pesticide.name}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DiseaseCard;
