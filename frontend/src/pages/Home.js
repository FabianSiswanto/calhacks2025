import React, { useState } from "react";
import "./Home.css";
import connect from "./connect.js";

const Home = () => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  const handleSubmit = () => {
    setIsSubmitted(true);
  };

  const handleTriggerChildProcess = async () => {
    if (window.electronAPI) {
      try {
        const result = await window.electronAPI.triggerChildProcess();
      } catch (error) {
        console.error("Error triggering child process: ", error);
      }
    } else {
      console.error("Not running in Electron environment");
    }
  };

  const handleStartLearning = async () => {
    setIsRunning(true);
    try {
      await connect();
      console.log("Learning flow completed!");
    } catch (error) {
      console.error("Error running learning flow:", error);
    } finally {
      setIsRunning(false);
    }
  };

  const lessonItems = [
    {
      number: 1,
      title: "Interface Mastery",
      description: "Understanding the Figma interface, including the toolbar, layers panel, properties panel, and how to navigate the canvas effectively.",
      icon: "🎨",
      difficulty: "Beginner"
    },
    {
      number: 2,
      title: "Shape Creation",
      description: "Creating and manipulating basic shapes, using selection tools, and applying transformations like rotation, scaling, and positioning.",
      icon: "🔷",
      difficulty: "Beginner"
    },
    {
      number: 3,
      title: "Frames & Layouts",
      description: "Working with frames and artboards to organize your designs and create responsive layouts for different screen sizes.",
      icon: "📐",
      difficulty: "Intermediate"
    },
    {
      number: 4,
      title: "Typography",
      description: "Mastering text tools, typography settings, and text styling to create readable and visually appealing content.",
      icon: "✍️",
      difficulty: "Beginner"
    },
    {
      number: 5,
      title: "Vector Tools",
      description: "Using the pen tool and vector editing capabilities to create custom shapes, icons, and illustrations.",
      icon: "✏️",
      difficulty: "Intermediate"
    },
    {
      number: 6,
      title: "Colors & Effects",
      description: "Applying colors, gradients, and effects like shadows, blurs, and strokes to enhance your designs.",
      icon: "🌈",
      difficulty: "Intermediate"
    },
    {
      number: 7,
      title: "Components",
      description: "Creating and managing components and variants to build reusable design elements and maintain consistency across projects.",
      icon: "🧩",
      difficulty: "Advanced"
    },
    {
      number: 8,
      title: "Auto Layout",
      description: "Understanding auto layout to create flexible, responsive designs that automatically adjust to content changes.",
      icon: "📱",
      difficulty: "Advanced"
    },
    {
      number: 9,
      title: "Prototyping",
      description: "Using prototyping features to connect frames, add interactions, and create clickable mockups that simulate user flows.",
      icon: "🔗",
      difficulty: "Advanced"
    },
    {
      number: 10,
      title: "Collaboration",
      description: "Collaborating with team members through commenting, sharing files, and using version history to track design changes.",
      icon: "👥",
      difficulty: "Intermediate"
    }
  ];

  if (isSubmitted) {
    return (
      <div className="home-container">
        <section className="hero-section">
          <div className="hero-background"></div>
          <div
            style={{
              width: "60%",
              margin: "0 auto",
              padding: "40px 32px 200px",
            }}>
            <h2
              style={{
                fontSize: 36,
                marginBottom: 40,
                color: "#2d2d2d",
                fontFamily: "inherit",
                textAlign: "center"
              }}>
              <i>Lessons to be learned...</i>
            </h2>
            <div className="lessons-grid">
              {lessonItems.map((lesson, index) => (
                <div key={index} className="lesson-card">
                  <div className="lesson-icon">{lesson.icon}</div>
                  <div className="lesson-content">
                    <div className="lesson-header">
                      <h3 className="lesson-title">Lesson {lesson.number}: {lesson.title}</h3>
                      <span className={`lesson-difficulty ${lesson.difficulty.toLowerCase()}`}>
                        {lesson.difficulty}
                      </span>
                    </div>
                    <p className="lesson-description">{lesson.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <div
          style={{
            position: "fixed",
            left: 0,
            right: 0,
            bottom: 0,
            padding: "24px 32px",
            background: "transparent",
            zIndex: 1000,
            display: "flex",
            justifyContent: "center",
            gap: "20px",
          }}>
          <button
            onClick={handleTriggerChildProcess}
            style={{
              height: 72,
              padding: "0 80px",
              borderRadius: 40,
              border: "none",
              background: "#3b82f6",
              color: "#ffffff",
              fontWeight: 600,
              fontSize: 20,
              cursor: "pointer",
              boxShadow: "0 4px 12px rgba(59, 130, 246, 0.3)",
              transition: "all 0.2s ease",
              fontFamily: "inherit",
            }}
            onMouseEnter={(e) => {
              e.target.style.background = "#2563eb";
              e.target.style.transform = "scale(1.05)";
            }}
            onMouseLeave={(e) => {
              e.target.style.background = "#3b82f6";
              e.target.style.transform = "scale(1)";
            }}>
            Start
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <section className="hero-section">
        <div className="hero-background"></div>
        <div className="hero-content">
          <h1 className="hero-title">
            Learn <i>Anything,</i> Fast.
          </h1>
        </div>
      </section>

      <div
        style={{
          position: "fixed",
          left: 0,
          right: 0,
          bottom: 0,
          padding: "24px 32px",
          background: "transparent",
          zIndex: 1000,
        }}>
        <div
          style={{
            maxWidth: 1200,
            margin: "0 auto",
            position: "relative",
          }}>
          <input
            type="text"
            placeholder="Ask anything"
            style={{
              width: "100%",
              height: 144,
              padding: "0 180px 0 28px",
              borderRadius: 80,
              border: "1.5px solid rgba(0,0,0,0.12)",
              outline: "none",
              fontSize: 18,
              boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
              transition: "all 0.2s ease",
              fontFamily: "inherit",
            }}
            onFocus={(e) => {
              e.target.style.borderColor = "rgba(59, 130, 246, 0.5)";
              e.target.style.boxShadow = "0 4px 12px rgba(59, 130, 246, 0.15)";
            }}
            onBlur={(e) => {
              e.target.style.borderColor = "rgba(0,0,0,0.12)";
              e.target.style.boxShadow = "0 2px 8px rgba(0,0,0,0.04)";
            }}
          />
          <button
            onClick={handleSubmit}
            style={{
              position: "absolute",
              right: 16,
              top: "50%",
              transform: "translateY(-50%)",
              height: 112,
              width: 112,
              borderRadius: "50%",
              border: "none",
              background: "#3b82f6",
              color: "#ffffff",
              fontWeight: 600,
              fontSize: 24,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 4px 12px rgba(59, 130, 246, 0.3)",
              transition: "all 0.2s ease",
              fontFamily: "inherit",
            }}
            onMouseEnter={(e) => {
              e.target.style.background = "#2563eb";
              e.target.style.transform = "translateY(-50%) scale(1.05)";
            }}
            onMouseLeave={(e) => {
              e.target.style.background = "#3b82f6";
              e.target.style.transform = "translateY(-50%) scale(1)";
            }}>
            →
          </button>
        </div>
      </div>
    </div>
  );
};

export default Home;
