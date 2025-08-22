// WILLOW v40 CORRECTED HHYC APPS SCRIPT BACKEND
// Complete volunteer management system with simplified data collection

// Configuration
const ADMIN_PASSWORD = '7591';
const GATE_CODE = '1957';

// Initialize database sheets
function initializeDatabase() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // Create Events sheet
  let eventsSheet = ss.getSheetByName('Events');
  if (!eventsSheet) {
    eventsSheet = ss.insertSheet('Events');
    eventsSheet.getRange(1, 1, 1, 10).setValues([[
      'EventID', 'EventName', 'EventDate', 'StartTime', 'EndTime', 
      'Location', 'Description', 'ImageURL', 'CreatedBy', 'CreatedDate'
    ]]);
  }

  // Create Tasks sheet  
  let tasksSheet = ss.getSheetByName('Tasks');
  if (!tasksSheet) {
    tasksSheet = ss.insertSheet('Tasks');
    tasksSheet.getRange(1, 1, 1, 6).setValues([[
      'TaskID', 'EventID', 'TaskName', 'VolunteersNeeded', 'TaskDescription', 'CreatedDate'
    ]]);
  }

  // Create Volunteers sheet (simplified)
  let volunteersSheet = ss.getSheetByName('Volunteers');
  if (!volunteersSheet) {
    volunteersSheet = ss.insertSheet('Volunteers');
    volunteersSheet.getRange(1, 1, 1, 4).setValues([[
      'VolunteerID', 'Name', 'Address', 'Email'
    ]]);
  }

  // Create Signups sheet
  let signupsSheet = ss.getSheetByName('Signups');
  if (!signupsSheet) {
    signupsSheet = ss.insertSheet('Signups');
    signupsSheet.getRange(1, 1, 1, 5).setValues([[
      'SignupID', 'TaskID', 'VolunteerID', 'SignupDate', 'Status'
    ]]);
  }

  // Create Cancellations sheet
  let cancellationsSheet = ss.getSheetByName('Cancellations');
  if (!cancellationsSheet) {
    cancellationsSheet = ss.insertSheet('Cancellations');
    cancellationsSheet.getRange(1, 1, 1, 4).setValues([[
      'CancellationID', 'SignupID', 'Reason', 'CancellationDate'
    ]]);
  }

  return {
    events: eventsSheet,
    tasks: tasksSheet,
    volunteers: volunteersSheet,
    signups: signupsSheet,
    cancellations: cancellationsSheet
  };
}

// Main handler functions
function doGet(e) {
  initializeDatabase();

  const action = e.parameter.action;

  switch(action) {
    case 'getEvents':
      return ContentService.createTextOutput(JSON.stringify(getEvents()))
        .setMimeType(ContentService.MimeType.JSON);

    case 'getEventDetails':
      return ContentService.createTextOutput(JSON.stringify(getEventDetails(e.parameter.eventId)))
        .setMimeType(ContentService.MimeType.JSON);

    default:
      return ContentService.createTextOutput(JSON.stringify({error: 'Invalid action'}))
        .setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  initializeDatabase();

  const data = JSON.parse(e.postData.contents);
  const action = data.action;

  switch(action) {
    case 'authenticate':
      return ContentService.createTextOutput(JSON.stringify(authenticate(data)))
        .setMimeType(ContentService.MimeType.JSON);

    case 'createEvent':
      return ContentService.createTextOutput(JSON.stringify(createEvent(data)))
        .setMimeType(ContentService.MimeType.JSON);

    case 'updateEvent':
      return ContentService.createTextOutput(JSON.stringify(updateEvent(data)))
        .setMimeType(ContentService.MimeType.JSON);

    case 'deleteEvent':
      return ContentService.createTextOutput(JSON.stringify(deleteEvent(data)))
        .setMimeType(ContentService.MimeType.JSON);

    case 'createTask':
      return ContentService.createTextOutput(JSON.stringify(createTask(data)))
        .setMimeType(ContentService.MimeType.JSON);

    case 'signupVolunteer':
      return ContentService.createTextOutput(JSON.stringify(signupVolunteer(data)))
        .setMimeType(ContentService.MimeType.JSON);

    case 'cancelSignup':
      return ContentService.createTextOutput(JSON.stringify(cancelSignup(data)))
        .setMimeType(ContentService.MimeType.JSON);

    default:
      return ContentService.createTextOutput(JSON.stringify({error: 'Invalid action'}))
        .setMimeType(ContentService.MimeType.JSON);
  }
}

// Authentication function
function authenticate(data) {
  if (data.type === 'admin' && data.password === ADMIN_PASSWORD) {
    return {success: true, message: 'Admin authenticated'};
  } else if (data.type === 'gate' && data.gateCode === GATE_CODE) {
    return {success: true, message: 'Gate code verified'};
  } else {
    return {success: false, message: 'Invalid credentials'};
  }
}

// Event management functions
function getEvents() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const eventsSheet = ss.getSheetByName('Events');
  const data = eventsSheet.getDataRange().getValues();

  if (data.length <= 1) return [];

  const events = [];
  for (let i = 1; i < data.length; i++) {
    events.push({
      eventId: data[i][0],
      eventName: data[i][1],
      eventDate: data[i][2],
      startTime: data[i][3],
      endTime: data[i][4],
      location: data[i][5],
      description: data[i][6],
      imageURL: data[i][7],
      createdBy: data[i][8],
      createdDate: data[i][9]
    });
  }

  return events;
}

function createEvent(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const eventsSheet = ss.getSheetByName('Events');

  const eventId = 'EVT' + Date.now();
  const newRow = [
    eventId,
    data.eventName,
    data.eventDate,
    data.startTime,
    data.endTime,
    data.location,
    data.description,
    data.imageURL || '',
    'Admin',
    new Date()
  ];

  eventsSheet.appendRow(newRow);

  return {success: true, eventId: eventId, message: 'Event created successfully'};
}

function updateEvent(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const eventsSheet = ss.getSheetByName('Events');
  const values = eventsSheet.getDataRange().getValues();

  for (let i = 1; i < values.length; i++) {
    if (values[i][0] === data.eventId) {
      eventsSheet.getRange(i + 1, 2, 1, 7).setValues([[
        data.eventName,
        data.eventDate, 
        data.startTime,
        data.endTime,
        data.location,
        data.description,
        data.imageURL || values[i][7]
      ]]);
      return {success: true, message: 'Event updated successfully'};
    }
  }

  return {success: false, message: 'Event not found'};
}

function deleteEvent(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const eventsSheet = ss.getSheetByName('Events');
  const values = eventsSheet.getDataRange().getValues();

  for (let i = 1; i < values.length; i++) {
    if (values[i][0] === data.eventId) {
      eventsSheet.deleteRow(i + 1);
      return {success: true, message: 'Event deleted successfully'};
    }
  }

  return {success: false, message: 'Event not found'};
}

// Task management
function createTask(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tasksSheet = ss.getSheetByName('Tasks');

  const taskId = 'TSK' + Date.now();
  const newRow = [
    taskId,
    data.eventId,
    data.taskName,
    data.volunteersNeeded,
    data.taskDescription,
    new Date()
  ];

  tasksSheet.appendRow(newRow);

  return {success: true, taskId: taskId, message: 'Task created successfully'};
}

// Volunteer signup
function signupVolunteer(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const volunteersSheet = ss.getSheetByName('Volunteers');
  const signupsSheet = ss.getSheetByName('Signups');

  // Create or find volunteer
  let volunteerId = findOrCreateVolunteer(data.name, data.address, data.email);

  // Create signup
  const signupId = 'SGN' + Date.now();
  const newRow = [
    signupId,
    data.taskId,
    volunteerId,
    new Date(),
    'Active'
  ];

  signupsSheet.appendRow(newRow);

  return {success: true, signupId: signupId, message: 'Volunteer signed up successfully'};
}

function findOrCreateVolunteer(name, address, email) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const volunteersSheet = ss.getSheetByName('Volunteers');
  const values = volunteersSheet.getDataRange().getValues();

  // Check if volunteer exists (by email)
  for (let i = 1; i < values.length; i++) {
    if (values[i][3] === email) {
      return values[i][0];
    }
  }

  // Create new volunteer
  const volunteerId = 'VOL' + Date.now();
  volunteersSheet.appendRow([volunteerId, name, address, email]);

  return volunteerId;
}

function cancelSignup(data) {
  if (!authenticate({type: 'gate', gateCode: data.gateCode}).success) {
    return {success: false, message: 'Invalid gate code'};
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const signupsSheet = ss.getSheetByName('Signups');
  const cancellationsSheet = ss.getSheetByName('Cancellations');

  // Record cancellation
  const cancellationId = 'CAN' + Date.now();
  cancellationsSheet.appendRow([
    cancellationId,
    data.signupId,
    data.reason,
    new Date()
  ]);

  // Update signup status
  const values = signupsSheet.getDataRange().getValues();
  for (let i = 1; i < values.length; i++) {
    if (values[i][0] === data.signupId) {
      signupsSheet.getRange(i + 1, 5).setValue('Cancelled');
      break;
    }
  }

  return {success: true, message: 'Signup cancelled successfully'};
}

function getEventDetails(eventId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const eventsSheet = ss.getSheetByName('Events');
  const tasksSheet = ss.getSheetByName('Tasks');
  const signupsSheet = ss.getSheetByName('Signups');
  const volunteersSheet = ss.getSheetByName('Volunteers');

  // Get event
  const eventData = eventsSheet.getDataRange().getValues();
  let event = null;
  for (let i = 1; i < eventData.length; i++) {
    if (eventData[i][0] === eventId) {
      event = {
        eventId: eventData[i][0],
        eventName: eventData[i][1],
        eventDate: eventData[i][2],
        startTime: eventData[i][3],
        endTime: eventData[i][4],
        location: eventData[i][5],
        description: eventData[i][6],
        imageURL: eventData[i][7]
      };
      break;
    }
  }

  if (!event) return null;

  // Get tasks with volunteers
  const taskData = tasksSheet.getDataRange().getValues();
  const signupData = signupsSheet.getDataRange().getValues();
  const volunteerData = volunteersSheet.getDataRange().getValues();

  const tasks = [];
  for (let i = 1; i < taskData.length; i++) {
    if (taskData[i][1] === eventId) {
      const task = {
        taskId: taskData[i][0],
        taskName: taskData[i][2],
        volunteersNeeded: taskData[i][3],
        taskDescription: taskData[i][4],
        volunteers: []
      };

      // Get volunteers for this task
      for (let j = 1; j < signupData.length; j++) {
        if (signupData[j][1] === task.taskId && signupData[j][4] === 'Active') {
          const volunteerId = signupData[j][2];

          // Find volunteer name
          for (let k = 1; k < volunteerData.length; k++) {
            if (volunteerData[k][0] === volunteerId) {
              task.volunteers.push({
                signupId: signupData[j][0],
                name: volunteerData[k][1],
                email: volunteerData[k][3]
              });
              break;
            }
          }
        }
      }

      tasks.push(task);
    }
  }

  return {event: event, tasks: tasks};
}