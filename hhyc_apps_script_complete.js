
// HHYC Volunteer Management System - Complete Apps Script Backend
// WILLOW v40 Perfection Protocol - Simplified Data Collection

// Configuration
const ADMIN_PASSWORD = "7591";
const GATE_CODE = "1957";

// Get spreadsheet and sheets
function getSpreadsheet() {
  return SpreadsheetApp.openById("1pir0qLHMFYJiiQtjHPlc43F2XlYe1g7XwWQvplx1OZ8");
}

// Initialize database sheets if they don't exist
function initializeSheets() {
  const ss = getSpreadsheet();

  // Events sheet
  let eventsSheet = ss.getSheetByName("Events");
  if (!eventsSheet) {
    eventsSheet = ss.insertSheet("Events");
    eventsSheet.getRange(1, 1, 1, 10).setValues([
      ["EventID", "EventName", "EventDate", "StartTime", "EndTime", "Location", "Description", "ImageURL", "CreatedBy", "CreatedDate"]
    ]);
  }

  // Tasks sheet
  let tasksSheet = ss.getSheetByName("Tasks");
  if (!tasksSheet) {
    tasksSheet = ss.insertSheet("Tasks");
    tasksSheet.getRange(1, 1, 1, 6).setValues([
      ["TaskID", "EventID", "TaskName", "VolunteersNeeded", "TaskDescription", "CreatedDate"]
    ]);
  }

  // Volunteers sheet - SIMPLIFIED
  let volunteersSheet = ss.getSheetByName("Volunteers");
  if (!volunteersSheet) {
    volunteersSheet = ss.insertSheet("Volunteers");
    volunteersSheet.getRange(1, 1, 1, 4).setValues([
      ["VolunteerID", "Name", "Address", "Email"]
    ]);
  }

  // Signups sheet
  let signupsSheet = ss.getSheetByName("Signups");
  if (!signupsSheet) {
    signupsSheet = ss.insertSheet("Signups");
    signupsSheet.getRange(1, 1, 1, 5).setValues([
      ["SignupID", "TaskID", "VolunteerID", "SignupDate", "Status"]
    ]);
  }

  // Cancellations sheet
  let cancellationsSheet = ss.getSheetByName("Cancellations");
  if (!cancellationsSheet) {
    cancellationsSheet = ss.insertSheet("Cancellations");
    cancellationsSheet.getRange(1, 1, 1, 4).setValues([
      ["CancellationID", "SignupID", "Reason", "CancellationDate"]
    ]);
  }
}

// Main request handler
function doGet(e) {
  const action = e.parameter.action;

  switch(action) {
    case 'getEvents':
      return ContentService.createTextOutput(JSON.stringify(getEvents())).setMimeType(ContentService.MimeType.JSON);
    case 'getEventDetails':
      return ContentService.createTextOutput(JSON.stringify(getEventDetails(e.parameter.eventId))).setMimeType(ContentService.MimeType.JSON);
    default:
      return ContentService.createTextOutput(JSON.stringify({error: "Invalid action"})).setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  const action = data.action;

  switch(action) {
    case 'authenticate':
      return ContentService.createTextOutput(JSON.stringify(authenticate(data.password, data.type))).setMimeType(ContentService.MimeType.JSON);
    case 'createEvent':
      return ContentService.createTextOutput(JSON.stringify(createEvent(data))).setMimeType(ContentService.MimeType.JSON);
    case 'updateEvent':
      return ContentService.createTextOutput(JSON.stringify(updateEvent(data))).setMimeType(ContentService.MimeType.JSON);
    case 'deleteEvent':
      return ContentService.createTextOutput(JSON.stringify(deleteEvent(data.eventId))).setMimeType(ContentService.MimeType.JSON);
    case 'createTask':
      return ContentService.createTextOutput(JSON.stringify(createTask(data))).setMimeType(ContentService.MimeType.JSON);
    case 'signupVolunteer':
      return ContentService.createTextOutput(JSON.stringify(signupVolunteer(data))).setMimeType(ContentService.MimeType.JSON);
    case 'cancelSignup':
      return ContentService.createTextOutput(JSON.stringify(cancelSignup(data))).setMimeType(ContentService.MimeType.JSON);
    default:
      return ContentService.createTextOutput(JSON.stringify({error: "Invalid action"})).setMimeType(ContentService.MimeType.JSON);
  }
}

// Authentication
function authenticate(password, type) {
  if (type === "admin" && password === ADMIN_PASSWORD) {
    return {success: true, role: "admin"};
  } else if (type === "volunteer" && password === GATE_CODE) {
    return {success: true, role: "volunteer"};
  }
  return {success: false, error: "Invalid credentials"};
}

// Event management functions
function getEvents() {
  initializeSheets();
  const ss = getSpreadsheet();
  const eventsSheet = ss.getSheetByName("Events");
  const tasksSheet = ss.getSheetByName("Tasks");
  const signupsSheet = ss.getSheetByName("Signups");
  const volunteersSheet = ss.getSheetByName("Volunteers");

  const events = [];
  const eventData = eventsSheet.getDataRange().getValues();

  for (let i = 1; i < eventData.length; i++) {
    const event = {
      id: eventData[i][0],
      name: eventData[i][1],
      date: eventData[i][2],
      startTime: eventData[i][3],
      endTime: eventData[i][4],
      location: eventData[i][5],
      description: eventData[i][6],
      imageUrl: eventData[i][7],
      tasks: getTasksForEvent(eventData[i][0])
    };
    events.push(event);
  }

  return events;
}

function getTasksForEvent(eventId) {
  const ss = getSpreadsheet();
  const tasksSheet = ss.getSheetByName("Tasks");
  const signupsSheet = ss.getSheetByName("Signups");
  const volunteersSheet = ss.getSheetByName("Volunteers");

  const tasks = [];
  const taskData = tasksSheet.getDataRange().getValues();

  for (let i = 1; i < taskData.length; i++) {
    if (taskData[i][1] == eventId) {
      const task = {
        id: taskData[i][0],
        name: taskData[i][2],
        volunteersNeeded: taskData[i][3],
        description: taskData[i][4],
        participants: getParticipantsForTask(taskData[i][0])
      };
      tasks.push(task);
    }
  }

  return tasks;
}

function getParticipantsForTask(taskId) {
  const ss = getSpreadsheet();
  const signupsSheet = ss.getSheetByName("Signups");
  const volunteersSheet = ss.getSheetByName("Volunteers");

  const participants = [];
  const signupData = signupsSheet.getDataRange().getValues();
  const volunteerData = volunteersSheet.getDataRange().getValues();

  for (let i = 1; i < signupData.length; i++) {
    if (signupData[i][1] == taskId && signupData[i][4] === "Active") {
      const volunteerId = signupData[i][2];
      const volunteer = volunteerData.find(v => v[0] == volunteerId);
      if (volunteer) {
        participants.push({
          name: volunteer[1],
          email: volunteer[3]
        });
      }
    }
  }

  return participants;
}

// Volunteer signup with simplified data collection
function signupVolunteer(data) {
  initializeSheets();
  const ss = getSpreadsheet();

  // Add or update volunteer (simplified)
  const volunteersSheet = ss.getSheetByName("Volunteers");
  const volunteerData = volunteersSheet.getDataRange().getValues();

  let volunteerId = null;

  // Check if volunteer exists by email
  for (let i = 1; i < volunteerData.length; i++) {
    if (volunteerData[i][3] === data.email) {
      volunteerId = volunteerData[i][0];
      // Update existing volunteer
      volunteersSheet.getRange(i + 1, 2, 1, 3).setValues([[data.name, data.address, data.email]]);
      break;
    }
  }

  // Create new volunteer if not found
  if (!volunteerId) {
    volunteerId = "VOL" + Date.now();
    volunteersSheet.appendRow([volunteerId, data.name, data.address, data.email]);
  }

  // Create signup
  const signupsSheet = ss.getSheetByName("Signups");
  const signupId = "SU" + Date.now();
  signupsSheet.appendRow([signupId, data.taskId, volunteerId, new Date(), "Active"]);

  return {success: true, message: "Signup successful"};
}

// Event creation with image upload
function createEvent(data) {
  initializeSheets();
  const ss = getSpreadsheet();
  const eventsSheet = ss.getSheetByName("Events");

  const eventId = "EVT" + Date.now();
  eventsSheet.appendRow([
    eventId,
    data.name,
    data.date,
    data.startTime,
    data.endTime,
    data.location,
    data.description,
    data.imageUrl || "",
    "Admin",
    new Date()
  ]);

  return {success: true, eventId: eventId};
}

// Event updating
function updateEvent(data) {
  const ss = getSpreadsheet();
  const eventsSheet = ss.getSheetByName("Events");
  const eventData = eventsSheet.getDataRange().getValues();

  for (let i = 1; i < eventData.length; i++) {
    if (eventData[i][0] === data.eventId) {
      eventsSheet.getRange(i + 1, 2, 1, 7).setValues([[
        data.name,
        data.date,
        data.startTime,
        data.endTime,
        data.location,
        data.description,
        data.imageUrl || eventData[i][7]
      ]]);
      return {success: true};
    }
  }

  return {success: false, error: "Event not found"};
}

// Task creation (simplified)
function createTask(data) {
  initializeSheets();
  const ss = getSpreadsheet();
  const tasksSheet = ss.getSheetByName("Tasks");

  const taskId = "TSK" + Date.now();
  tasksSheet.appendRow([
    taskId,
    data.eventId,
    data.taskName,
    data.volunteersNeeded,
    data.description,
    new Date()
  ]);

  return {success: true, taskId: taskId};
}

// Cancellation with reason and gate code
function cancelSignup(data) {
  if (data.gateCode !== GATE_CODE) {
    return {success: false, error: "Invalid gate code"};
  }

  const ss = getSpreadsheet();
  const signupsSheet = ss.getSheetByName("Signups");
  const cancellationsSheet = ss.getSheetByName("Cancellations");
  const signupData = signupsSheet.getDataRange().getValues();

  for (let i = 1; i < signupData.length; i++) {
    if (signupData[i][0] === data.signupId) {
      // Mark signup as cancelled
      signupsSheet.getRange(i + 1, 5).setValue("Cancelled");

      // Record cancellation with reason
      const cancellationId = "CAN" + Date.now();
      cancellationsSheet.appendRow([cancellationId, data.signupId, data.reason, new Date()]);

      return {success: true, message: "Signup cancelled"};
    }
  }

  return {success: false, error: "Signup not found"};
}
