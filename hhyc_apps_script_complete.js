/**
 * HHYC Volunteer Management System - Complete Backend API
 * WILLOW v40 - Nautical Blue Theme for Hidden Harbor Yacht Club
 * Authentication: Admin 7591, Gate Code 1957
 */

// Configuration
const CONFIG = {
  ADMIN_PASSWORD: '7591',
  GATE_CODE: '1957',
  SHEET_ID: '1pir0qLHMFYJiiQtjHPlc43F2XlYe1g7XwWQvplx1OZ8'
};

// Initialize database structure
function initializeDatabase() {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);

  // Create Events sheet
  let eventsSheet = ss.getSheetByName('Events');
  if (!eventsSheet) {
    eventsSheet = ss.insertSheet('Events');
    eventsSheet.getRange(1, 1, 1, 10).setValues([['EventID', 'EventName', 'EventDate', 'StartTime', 'EndTime', 'Location', 'Description', 'ImageURL', 'CreatedBy', 'CreatedDate']]);
  }

  // Create Tasks sheet
  let tasksSheet = ss.getSheetByName('Tasks');
  if (!tasksSheet) {
    tasksSheet = ss.insertSheet('Tasks');
    tasksSheet.getRange(1, 1, 1, 6).setValues([['TaskID', 'EventID', 'TaskName', 'VolunteersNeeded', 'TaskDescription', 'CreatedDate']]);
  }

  // Create Volunteers sheet (simplified)
  let volunteersSheet = ss.getSheetByName('Volunteers');
  if (!volunteersSheet) {
    volunteersSheet = ss.insertSheet('Volunteers');
    volunteersSheet.getRange(1, 1, 1, 4).setValues([['VolunteerID', 'Name', 'Address', 'Email']]);
  }

  // Create Signups sheet
  let signupsSheet = ss.getSheetByName('Signups');
  if (!signupsSheet) {
    signupsSheet = ss.insertSheet('Signups');
    signupsSheet.getRange(1, 1, 1, 5).setValues([['SignupID', 'TaskID', 'VolunteerID', 'SignupDate', 'Status']]);
  }

  // Create Cancellations sheet
  let cancellationsSheet = ss.getSheetByName('Cancellations');
  if (!cancellationsSheet) {
    cancellationsSheet = ss.insertSheet('Cancellations');
    cancellationsSheet.getRange(1, 1, 1, 4).setValues([['CancellationID', 'SignupID', 'Reason', 'CancellationDate']]);
  }
}

// Main request handler
function doGet(e) {
  return handleRequest(e);
}

function doPost(e) {
  return handleRequest(e);
}

function handleRequest(e) {
  try {
    initializeDatabase();

    const action = e.parameter.action;
    const data = e.parameter.data ? JSON.parse(e.parameter.data) : {};

    let response = {};

    switch (action) {
      case 'authenticate':
        response = authenticate(data);
        break;
      case 'getEvents':
        response = getEvents();
        break;
      case 'createEvent':
        response = createEvent(data);
        break;
      case 'updateEvent':
        response = updateEvent(data);
        break;
      case 'deleteEvent':
        response = deleteEvent(data);
        break;
      case 'getTasks':
        response = getTasks(data.eventId);
        break;
      case 'createTask':
        response = createTask(data);
        break;
      case 'signupVolunteer':
        response = signupVolunteer(data);
        break;
      case 'cancelSignup':
        response = cancelSignup(data);
        break;
      case 'getEventWithSignups':
        response = getEventWithSignups();
        break;
      default:
        response = {success: false, message: 'Invalid action'};
    }

    return ContentService
      .createTextOutput(JSON.stringify(response))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({success: false, message: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Authentication
function authenticate(data) {
  if (data.type === 'admin' && data.password === CONFIG.ADMIN_PASSWORD) {
    return {success: true, message: 'Admin authenticated'};
  }
  if (data.type === 'gate' && data.code === CONFIG.GATE_CODE) {
    return {success: true, message: 'Gate code verified'};
  }
  return {success: false, message: 'Invalid credentials'};
}

// Event management
function getEvents() {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const sheet = ss.getSheetByName('Events');
  const data = sheet.getDataRange().getValues();
  const events = [];

  for (let i = 1; i < data.length; i++) {
    events.push({
      id: data[i][0],
      name: data[i][1],
      date: data[i][2],
      startTime: data[i][3],
      endTime: data[i][4],
      location: data[i][5],
      description: data[i][6],
      imageUrl: data[i][7]
    });
  }

  return {success: true, events: events};
}

function createEvent(data) {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const sheet = ss.getSheetByName('Events');
  const eventId = 'EVT' + Date.now();

  sheet.appendRow([
    eventId,
    data.name,
    data.date,
    data.startTime,
    data.endTime,
    data.location,
    data.description,
    data.imageUrl || '',
    'Admin',
    new Date()
  ]);

  return {success: true, message: 'Event created', eventId: eventId};
}

function updateEvent(data) {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const sheet = ss.getSheetByName('Events');
  const values = sheet.getDataRange().getValues();

  for (let i = 1; i < values.length; i++) {
    if (values[i][0] === data.id) {
      sheet.getRange(i + 1, 2, 1, 6).setValues([[
        data.name,
        data.date,
        data.startTime,
        data.endTime,
        data.location,
        data.description
      ]]);
      return {success: true, message: 'Event updated'};
    }
  }

  return {success: false, message: 'Event not found'};
}

function deleteEvent(data) {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const sheet = ss.getSheetByName('Events');
  const values = sheet.getDataRange().getValues();

  for (let i = 1; i < values.length; i++) {
    if (values[i][0] === data.id) {
      sheet.deleteRow(i + 1);
      return {success: true, message: 'Event deleted'};
    }
  }

  return {success: false, message: 'Event not found'};
}

// Task management
function createTask(data) {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const sheet = ss.getSheetByName('Tasks');
  const taskId = 'TSK' + Date.now();

  sheet.appendRow([
    taskId,
    data.eventId,
    data.taskName,
    data.volunteersNeeded,
    data.taskDescription,
    new Date()
  ]);

  return {success: true, message: 'Task created', taskId: taskId};
}

function getTasks(eventId) {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
  const sheet = ss.getSheetByName('Tasks');
  const data = sheet.getDataRange().getValues();
  const tasks = [];

  for (let i = 1; i < data.length; i++) {
    if (data[i][1] === eventId) {
      tasks.push({
        id: data[i][0],
        eventId: data[i][1],
        name: data[i][2],
        volunteersNeeded: data[i][3],
        description: data[i][4]
      });
    }
  }

  return {success: true, tasks: tasks};
}

// Volunteer management
function signupVolunteer(data) {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);

  // Add/update volunteer
  const volunteerSheet = ss.getSheetByName('Volunteers');
  const volunteerId = 'VOL' + Date.now();
  volunteerSheet.appendRow([volunteerId, data.name, data.address, data.email]);

  // Add signup
  const signupSheet = ss.getSheetByName('Signups');
  const signupId = 'SGN' + Date.now();
  signupSheet.appendRow([signupId, data.taskId, volunteerId, new Date(), 'Active']);

  return {success: true, message: 'Volunteer signed up', signupId: signupId};
}

function cancelSignup(data) {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);

  // Add cancellation record
  const cancellationSheet = ss.getSheetByName('Cancellations');
  const cancellationId = 'CAN' + Date.now();
  cancellationSheet.appendRow([cancellationId, data.signupId, data.reason, new Date()]);

  // Update signup status
  const signupSheet = ss.getSheetByName('Signups');
  const values = signupSheet.getDataRange().getValues();

  for (let i = 1; i < values.length; i++) {
    if (values[i][0] === data.signupId) {
      signupSheet.getRange(i + 1, 5).setValue('Cancelled');
      break;
    }
  }

  return {success: true, message: 'Signup cancelled'};
}

function getEventWithSignups() {
  const ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);

  // Get events
  const eventsSheet = ss.getSheetByName('Events');
  const eventsData = eventsSheet.getDataRange().getValues();

  // Get tasks
  const tasksSheet = ss.getSheetByName('Tasks');
  const tasksData = tasksSheet.getDataRange().getValues();

  // Get signups
  const signupsSheet = ss.getSheetByName('Signups');
  const signupsData = signupsSheet.getDataRange().getValues();

  // Get volunteers
  const volunteersSheet = ss.getSheetByName('Volunteers');
  const volunteersData = volunteersSheet.getDataRange().getValues();

  const events = [];

  for (let i = 1; i < eventsData.length; i++) {
    const event = {
      id: eventsData[i][0],
      name: eventsData[i][1],
      date: eventsData[i][2],
      startTime: eventsData[i][3],
      endTime: eventsData[i][4],
      location: eventsData[i][5],
      description: eventsData[i][6],
      imageUrl: eventsData[i][7],
      tasks: []
    };

    // Get tasks for this event
    for (let j = 1; j < tasksData.length; j++) {
      if (tasksData[j][1] === event.id) {
        const task = {
          id: tasksData[j][0],
          name: tasksData[j][2],
          volunteersNeeded: tasksData[j][3],
          description: tasksData[j][4],
          volunteers: []
        };

        // Get volunteers for this task
        for (let k = 1; k < signupsData.length; k++) {
          if (signupsData[k][1] === task.id && signupsData[k][4] === 'Active') {
            const volunteerId = signupsData[k][2];

            // Find volunteer details
            for (let l = 1; l < volunteersData.length; l++) {
              if (volunteersData[l][0] === volunteerId) {
                task.volunteers.push({
                  id: volunteerId,
                  name: volunteersData[l][1],
                  signupId: signupsData[k][0]
                });
                break;
              }
            }
          }
        }

        event.tasks.push(task);
      }
    }

    events.push(event);
  }

  return {success: true, events: events};
}