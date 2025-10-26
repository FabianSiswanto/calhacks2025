#!/usr/bin/env node

const axios = require('axios');

// Configuration
const API_BASE_URL = 'http://127.0.0.1:5000';
const DELAY_BETWEEN_CALLS = 3000; // 3 seconds between each call

// Test data for different steps
const testSteps = [
  {
    step_order: 1,
    header: "Step 1: Getting Started",
    body: "Welcome! Let's begin by opening your design tool and creating a new project."
  },
  {
    step_order: 2,
    header: "Step 2: Create Frame",
    body: "Create a new frame by clicking the Frame tool and drawing a rectangle on the canvas."
  },
  {
    step_order: 3,
    header: "Step 3: Add Components",
    body: "Add text, buttons, and other UI components to your frame using the component library."
  },
  {
    step_order: 4,
    header: "Step 4: Style Elements",
    body: "Customize colors, fonts, and spacing using the design panel on the right."
  },
  {
    step_order: 5,
    header: "Step 5: Add Interactions",
    body: "Create clickable prototypes by connecting frames with interactive elements."
  },
  {
    step_order: 6,
    header: "Step 6: Test Prototype",
    body: "Preview your prototype and test all interactions to ensure they work correctly."
  },
  {
    step_order: 7,
    header: "Step 7: Share & Collaborate",
    body: "Share your design with team members and gather feedback for improvements."
  },
  {
    step_order: 8,
    header: "Step 8: Export Assets",
    body: "Export your designs as images or code for development handoff."
  }
];

// Function to make API call
async function callStartStep(stepData) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/start-step`, {
      user_id: 'overlay-user',
      lesson_id: 32,
      step_order: stepData.step_order,
      header: stepData.header,
      body: stepData.body
    });
    
    console.log(`✅ Step ${stepData.step_order}: ${stepData.header}`);
    console.log(`   Response: ${response.data.message}`);
    console.log(`   Data sent: ${JSON.stringify(response.data.step_data, null, 2)}`);
    console.log('---');
    
    return response.data;
  } catch (error) {
    console.error(`❌ Error calling Step ${stepData.step_order}:`, error.message);
    if (error.response) {
      console.error(`   Status: ${error.response.status}`);
      console.error(`   Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
    console.log('---');
    return null;
  }
}

// Function to delay execution
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Main loop function
async function runTestLoop() {
  console.log('🚀 Starting Overlay Text Update Test');
  console.log(`📡 API Base URL: ${API_BASE_URL}`);
  console.log(`⏱️  Delay between calls: ${DELAY_BETWEEN_CALLS}ms`);
  console.log(`📝 Total steps to test: ${testSteps.length}`);
  console.log('='.repeat(50));
  
  let cycleCount = 0;
  
  while (true) {
    cycleCount++;
    console.log(`\n🔄 Starting Cycle ${cycleCount}`);
    console.log('='.repeat(30));
    
    for (const step of testSteps) {
      await callStartStep(step);
      await delay(DELAY_BETWEEN_CALLS);
    }
    
    console.log(`\n✅ Completed Cycle ${cycleCount}`);
    console.log('⏳ Waiting 5 seconds before next cycle...');
    await delay(5000);
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Test stopped by user');
  console.log('👋 Goodbye!');
  process.exit(0);
});

// Start the test
console.log('🎯 Overlay Text Update Test Script');
console.log('Press Ctrl+C to stop the test');
console.log('');

runTestLoop().catch(error => {
  console.error('💥 Fatal error:', error);
  process.exit(1);
});
