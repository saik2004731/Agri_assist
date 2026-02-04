import React, { useState, useEffect, useRef } from "react";
import { chatAPI } from "../services/api";

// Map from <select> value → language string sent to backend
const LANGUAGE_LABELS = {
  none: "English",
  ta: "Tamil",
  te: "Telugu",
  hi: "Hindi",
  ml: "Malayalam",
  kn: "Kannada",
  gu: "Gujarati",
  mr: "Marathi",
};

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [language, setLanguage] = useState("none");

  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  // cnnPrediction = class index (number) from backend
  const [cnnPrediction, setCnnPrediction] = useState(null);
  // cnnLabel = human readable disease name (string)
  const [cnnLabel, setCnnLabel] = useState("");

  const [isPredicting, setIsPredicting] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // -------------------------
  // IMAGE UPLOAD → CNN PRED
  // -------------------------
  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setSelectedImage(file);
    setPreviewUrl(URL.createObjectURL(file));
    setIsPredicting(true);

    try {
      const result = await chatAPI.predictImage(file);
      // result from backend should be:
      // { prediction: <int>, class_name: <str>, confidence: <float> }

      const classIndex = result?.prediction;
      const className = result?.class_name;

      setCnnPrediction(classIndex || 0); // store index for backend
      setCnnLabel(className || "Disease not recognized");

      // Show one clean assistant message with detected disease
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: className
            ? `${className} detected`
            : "Disease not recognized",
        },
      ]);
    } catch (error) {
      console.error("Error in image prediction:", error);
      setCnnLabel("Error analyzing image.");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error analyzing the image.",
        },
      ]);
    } finally {
      setIsPredicting(false);
    }
  };

  // -------------------------
  // SEND CHAT MESSAGE
  // -------------------------
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isSending) return;

    const userText = inputMessage.trim();
    setInputMessage("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userText,
      },
    ]);

    setIsSending(true);

    try {
      const languageLabel = LANGUAGE_LABELS[language] || "English";

      const res = await chatAPI.sendMessage(
        userText,
        languageLabel,
        cnnPrediction // can be null or class index
      );

      const replyText =
        res?.response || "Sorry, I could not generate a response.";

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: replyText,
        },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Unable to respond. Please try again.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-card">
        {/* Top bar: title + language */}
        <div className="top-bar">
          <div className="app-title">AgriAssist</div>

          <div className="language-select">
            <label htmlFor="language">Language:</label>
            <select
              id="language"
              name="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="none">English Only</option>
              <option value="ta">Tamil</option>
              <option value="te">Telugu</option>
              <option value="hi">Hindi</option>
              <option value="ml">Malayalam</option>
              <option value="kn">Kannada</option>
              <option value="gu">Gujarati</option>
              <option value="mr">Marathi</option>
            </select>
          </div>
        </div>

        {/* Image + detection */}
        <div className="image-section">
          <label className="upload-button">
            <span role="img" aria-label="camera">
              📷
            </span>
            <span className="upload-text">
              {selectedImage ? "Change image" : "Upload leaf image"}
            </span>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
            />
          </label>

          {previewUrl && (
            <div className="image-preview">
              <img src={previewUrl} alt="Leaf preview" />
            </div>
          )}

          {isPredicting && (
            <div className="cnn-status">Analyzing image…</div>
          )}

          {cnnLabel && !isPredicting && (
            <div className="cnn-result">{cnnLabel}</div>
          )}
        </div>

        {/* Messages */}
        <div className="messages-area">
          {messages.length === 0 && (
            <div className="welcome-text">
              Type any agriculture question.
              <br />
              You can also upload a leaf image for disease detection.
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={
                msg.role === "user"
                  ? "message message-user"
                  : "message message-assistant"
              }
            >
              {msg.content}
            </div>
          ))}

          {isSending && (
            <div className="message message-assistant">
              Thinking…
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input row */}
        <form className="input-row" onSubmit={handleSendMessage}>
          <input
            type="text"
            className="chat-input"
            placeholder="Type your question…"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
          />
          <button className="send-button" type="submit">
            ➤
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
