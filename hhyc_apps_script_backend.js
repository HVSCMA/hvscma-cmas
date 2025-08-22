
/**
 * HHYC VOLUNTEER MANAGEMENT SYSTEM - APPS SCRIPT BACKEND
 * Complete API backend for Hidden Harbor Yacht Club volunteer management
 * Handles authentication, CRUD operations, email notifications
 * 
 * Database Structure: Events, Tasks, Volunteers, Signups, Config sheets
 * Authentication: Admin password 7591, Volunteer gate code 1957
 */

// ================================
//        CONFIGURATION
// ================================

const SHEET_NAMES = {
  EVENTS: 'Events',
  TASKS: 'Tasks', 
  VOLUNTEERS: 'Volunteers',
  SIGNUPS: 'Signups',
  CONFIG: 'Config'
};

const CONFIG_KEYS = {
  ADMIN_PASSWORD: 'AdminPassword',
  VOLUNTEER_GATE_CODE: 'VolunteerGateCode',
  CLUB_NAME: 'ClubName',
  CONTACT_EMAIL: 'ContactEmail'
};

// ================================
//     UTILITY FUNCTIONS
// ================================

/**
 * Get configuration value from Config sheet
 */
function getConfig(key) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.CONFIG);
    const data = sheet.getDataRange().getValues();

    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === key) {
        return data[i][1];
      }
    }
    return null;
  } catch (error) {
    console.error('Error getting config:', error);
    return null;
  }
}

/**
 * Generate unique ID with prefix
 */
function generateId(prefix) {
  const timestamp = Date.now().toString().slice(-6);
  const random = Math.floor(Math.random() * 100).toString().padStart(2, '0');
  return prefix + timestamp + random;
}

/**
 * Format date for display
 */
function formatDate(date) {
  return new Date(date).toLocaleDateString();
}

/**
 * Format time for display  
 */
function formatTime(time) {
  if (typeof time === 'string') return time;
  return new Date(time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

// ================================
//     AUTHENTICATION FUNCTIONS
// ================================

/**
 * Authenticate admin access
 */
function authenticateAdmin(password) {
  const adminPassword = getConfig(CONFIG_KEYS.ADMIN_PASSWORD);
  return password === adminPassword;
}

/**
 * Authenticate volunteer access
 */
function authenticateVolunteer(gateCode) {
  const volunteerGateCode = getConfig(CONFIG_KEYS.VOLUNTEER_GATE_CODE);
  return gateCode === volunteerGateCode;
}

// ================================
//     EVENTS MANAGEMENT
// ================================

/**
 * Get all events
 */
function getAllEvents() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.EVENTS);
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    const events = [];

    for (let i = 1; i < data.length; i++) {
      const event = {};
      headers.forEach((header, index) => {
        event[header] = data[i][index];
      });
      events.push(event);
    }

    return { success: true, data: events };
  } catch (error) {
    console.error('Error getting events:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Get single event by ID
 */
function getEvent(eventId) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.EVENTS);
    const data = sheet.getDataRange().getValues();
    const headers = data[0];

    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === eventId) {
        const event = {};
        headers.forEach((header, index) => {
          event[header] = data[i][index];
        });
        return { success: true, data: event };
      }
    }

    return { success: false, error: 'Event not found' };
  } catch (error) {
    console.error('Error getting event:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Create new event
 */
function createEvent(eventData) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.EVENTS);
    const eventId = generateId('EVT');
    const now = new Date();

    const newRow = [
      eventId,
      eventData.eventName,
      eventData.eventDate,
      eventData.startTime,
      eventData.endTime,
      eventData.description,
      eventData.location,
      'Active',
      eventData.createdBy || 'Admin',
      now
    ];

    sheet.appendRow(newRow);

    return { success: true, data: { eventId: eventId } };
  } catch (error) {
    console.error('Error creating event:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Update event
 */
function updateEvent(eventId, eventData) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.EVENTS);
    const data = sheet.getDataRange().getValues();

    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === eventId) {
        // Update specific columns based on eventData
        if (eventData.eventName) data[i][1] = eventData.eventName;
        if (eventData.eventDate) data[i][2] = eventData.eventDate;
        if (eventData.startTime) data[i][3] = eventData.startTime;
        if (eventData.endTime) data[i][4] = eventData.endTime;
        if (eventData.description) data[i][5] = eventData.description;
        if (eventData.location) data[i][6] = eventData.location;
        if (eventData.status) data[i][7] = eventData.status;

        // Write back to sheet
        sheet.getRange(i + 1, 1, 1, data[i].length).setValues([data[i]]);

        return { success: true, data: { eventId: eventId } };
      }
    }

    return { success: false, error: 'Event not found' };
  } catch (error) {
    console.error('Error updating event:', error);
    return { success: false, error: error.message };
  }
}

// ================================
//     TASKS MANAGEMENT
// ================================

/**
 * Get tasks for an event
 */
function getEventTasks(eventId) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.TASKS);
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    const tasks = [];

    for (let i = 1; i < data.length; i++) {
      if (data[i][1] === eventId) { // EventID is column 1
        const task = {};
        headers.forEach((header, index) => {
          task[header] = data[i][index];
        });
        tasks.push(task);
      }
    }

    return { success: true, data: tasks };
  } catch (error) {
    console.error('Error getting tasks:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Create new task
 */
function createTask(taskData) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.TASKS);
    const taskId = generateId('TSK');

    const newRow = [
      taskId,
      taskData.eventId,
      taskData.taskName,
      taskData.taskDescription,
      taskData.volunteersNeeded,
      0, // volunteersSignedUp starts at 0
      taskData.startTime,
      taskData.endTime,
      taskData.priority || 'Medium',
      'Open'
    ];

    sheet.appendRow(newRow);

    return { success: true, data: { taskId: taskId } };
  } catch (error) {
    console.error('Error creating task:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Update task signup count
 */
function updateTaskSignupCount(taskId) {
  try {
    // Count signups for this task
    const signupsSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.SIGNUPS);
    const signupsData = signupsSheet.getDataRange().getValues();
    let signupCount = 0;

    for (let i = 1; i < signupsData.length; i++) {
      if (signupsData[i][2] === taskId && signupsData[i][5] === 'Confirmed') { // TaskID and Status
        signupCount++;
      }
    }

    // Update task sheet
    const tasksSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.TASKS);
    const tasksData = tasksSheet.getDataRange().getValues();

    for (let i = 1; i < tasksData.length; i++) {
      if (tasksData[i][0] === taskId) {
        tasksData[i][5] = signupCount; // VolunteersSignedUp column

        // Update status based on capacity
        const volunteersNeeded = tasksData[i][4];
        if (signupCount >= volunteersNeeded) {
          tasksData[i][9] = 'Full';
        } else {
          tasksData[i][9] = 'Open';
        }

        tasksSheet.getRange(i + 1, 1, 1, tasksData[i].length).setValues([tasksData[i]]);
        break;
      }
    }

    return { success: true, data: { signupCount: signupCount } };
  } catch (error) {
    console.error('Error updating task signup count:', error);
    return { success: false, error: error.message };
  }
}

// ================================
//     VOLUNTEERS MANAGEMENT
// ================================

/**
 * Get all volunteers
 */
function getAllVolunteers() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.VOLUNTEERS);
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    const volunteers = [];

    for (let i = 1; i < data.length; i++) {
      const volunteer = {};
      headers.forEach((header, index) => {
        volunteer[header] = data[i][index];
      });
      volunteers.push(volunteer);
    }

    return { success: true, data: volunteers };
  } catch (error) {
    console.error('Error getting volunteers:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Find or create volunteer
 */
function findOrCreateVolunteer(volunteerData) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.VOLUNTEERS);
    const data = sheet.getDataRange().getValues();
    const headers = data[0];

    // Try to find existing volunteer by email
    for (let i = 1; i < data.length; i++) {
      if (data[i][3] === volunteerData.email) { // Email column
        const volunteer = {};
        headers.forEach((header, index) => {
          volunteer[header] = data[i][index];
        });
        return { success: true, data: volunteer, created: false };
      }
    }

    // Create new volunteer
    const volunteerId = generateId('VOL');
    const newRow = [
      volunteerId,
      volunteerData.firstName,
      volunteerData.lastName,
      volunteerData.email,
      volunteerData.phone || '',
      volunteerData.membershipStatus || 'Guest',
      volunteerData.preferredTasks || '',
      volunteerData.skillsExperience || '',
      volunteerData.availability || '',
      new Date(),
      0, // totalHours
      'Active'
    ];

    sheet.appendRow(newRow);

    const newVolunteer = {
      VolunteerID: volunteerId,
      FirstName: volunteerData.firstName,
      LastName: volunteerData.lastName,
      Email: volunteerData.email,
      Phone: volunteerData.phone || '',
      MembershipStatus: volunteerData.membershipStatus || 'Guest',
      PreferredTasks: volunteerData.preferredTasks || '',
      SkillsExperience: volunteerData.skillsExperience || '',
      Availability: volunteerData.availability || '',
      JoinDate: new Date(),
      TotalHours: 0,
      Status: 'Active'
    };

    return { success: true, data: newVolunteer, created: true };
  } catch (error) {
    console.error('Error finding/creating volunteer:', error);
    return { success: false, error: error.message };
  }
}

// ================================
//     SIGNUPS MANAGEMENT
// ================================

/**
 * Create volunteer signup
 */
function createSignup(signupData) {
  try {
    // First check if task is full
    const task = getTask(signupData.taskId);
    if (!task.success) {
      return { success: false, error: 'Task not found' };
    }

    if (task.data.VolunteersSignedUp >= task.data.VolunteersNeeded) {
      return { success: false, error: 'Task is full' };
    }

    // Check if volunteer already signed up for this task
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.SIGNUPS);
    const data = sheet.getDataRange().getValues();

    for (let i = 1; i < data.length; i++) {
      if (data[i][2] === signupData.taskId && data[i][3] === signupData.volunteerId && data[i][5] === 'Confirmed') {
        return { success: false, error: 'Already signed up for this task' };
      }
    }

    // Create signup
    const signupId = generateId('SGN');
    const newRow = [
      signupId,
      signupData.eventId,
      signupData.taskId,
      signupData.volunteerId,
      new Date(),
      'Confirmed',
      signupData.notes || '',
      false, // checkedIn
      0, // hoursWorked
      0  // rating
    ];

    sheet.appendRow(newRow);

    // Update task signup count
    updateTaskSignupCount(signupData.taskId);

    // Send confirmation email
    sendSignupConfirmation(signupData);

    return { success: true, data: { signupId: signupId } };
  } catch (error) {
    console.error('Error creating signup:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Get task signups with volunteer details
 */
function getTaskSignups(taskId) {
  try {
    const signupsSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.SIGNUPS);
    const volunteersSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.VOLUNTEERS);

    const signupsData = signupsSheet.getDataRange().getValues();
    const volunteersData = volunteersSheet.getDataRange().getValues();

    const signups = [];

    // Get signups for this task
    for (let i = 1; i < signupsData.length; i++) {
      if (signupsData[i][2] === taskId && signupsData[i][5] === 'Confirmed') {
        const volunteerId = signupsData[i][3];

        // Find volunteer details
        for (let j = 1; j < volunteersData.length; j++) {
          if (volunteersData[j][0] === volunteerId) {
            signups.push({
              signupId: signupsData[i][0],
              volunteerId: volunteerId,
              firstName: volunteersData[j][1],
              lastName: volunteersData[j][2],
              email: volunteersData[j][3],
              phone: volunteersData[j][4],
              signupDate: signupsData[i][4],
              notes: signupsData[i][6]
            });
            break;
          }
        }
      }
    }

    return { success: true, data: signups };
  } catch (error) {
    console.error('Error getting task signups:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Get single task by ID
 */
function getTask(taskId) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.TASKS);
    const data = sheet.getDataRange().getValues();
    const headers = data[0];

    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === taskId) {
        const task = {};
        headers.forEach((header, index) => {
          task[header] = data[i][index];
        });
        return { success: true, data: task };
      }
    }

    return { success: false, error: 'Task not found' };
  } catch (error) {
    console.error('Error getting task:', error);
    return { success: false, error: error.message };
  }
}

// ================================
//     EMAIL NOTIFICATIONS
// ================================

/**
 * Send signup confirmation email
 */
function sendSignupConfirmation(signupData) {
  try {
    // Get volunteer details
    const volunteer = getVolunteerById(signupData.volunteerId);
    if (!volunteer.success) return;

    // Get event and task details
    const event = getEvent(signupData.eventId);
    const task = getTask(signupData.taskId);
    if (!event.success || !task.success) return;

    const clubName = getConfig(CONFIG_KEYS.CLUB_NAME);
    const contactEmail = getConfig(CONFIG_KEYS.CONTACT_EMAIL);

    const subject = `${clubName} - Volunteer Signup Confirmation`;
    const body = `
Dear ${volunteer.data.FirstName},

Thank you for volunteering for our upcoming event!

EVENT DETAILS:
• Event: ${event.data.EventName}
• Date: ${formatDate(event.data.EventDate)}
• Time: ${formatTime(event.data.StartTime)} - ${formatTime(event.data.EndTime)}
• Location: ${event.data.Location}

YOUR TASK:
• Task: ${task.data.TaskName}
• Task Time: ${formatTime(task.data.StartTime)} - ${formatTime(task.data.EndTime)}
• Description: ${task.data.TaskDescription}

We appreciate your commitment to ${clubName}. If you have any questions or need to make changes, please contact us at ${contactEmail}.

Best regards,
${clubName} Volunteer Coordination Team
    `;

    MailApp.sendEmail(volunteer.data.Email, subject, body);

    return { success: true };
  } catch (error) {
    console.error('Error sending confirmation email:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Get volunteer by ID
 */
function getVolunteerById(volunteerId) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAMES.VOLUNTEERS);
    const data = sheet.getDataRange().getValues();
    const headers = data[0];

    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === volunteerId) {
        const volunteer = {};
        headers.forEach((header, index) => {
          volunteer[header] = data[i][index];
        });
        return { success: true, data: volunteer };
      }
    }

    return { success: false, error: 'Volunteer not found' };
  } catch (error) {
    console.error('Error getting volunteer:', error);
    return { success: false, error: error.message };
  }
}

// ================================
//     WEB APP ENTRY POINTS
// ================================

/**
 * Handle GET requests
 */
function doGet(e) {
  const action = e.parameter.action;

  try {
    switch (action) {
      case 'getAllEvents':
        return ContentService.createTextOutput(JSON.stringify(getAllEvents()))
          .setMimeType(ContentService.MimeType.JSON);

      case 'getEvent':
        return ContentService.createTextOutput(JSON.stringify(getEvent(e.parameter.eventId)))
          .setMimeType(ContentService.MimeType.JSON);

      case 'getEventTasks':
        return ContentService.createTextOutput(JSON.stringify(getEventTasks(e.parameter.eventId)))
          .setMimeType(ContentService.MimeType.JSON);

      case 'getTaskSignups':
        return ContentService.createTextOutput(JSON.stringify(getTaskSignups(e.parameter.taskId)))
          .setMimeType(ContentService.MimeType.JSON);

      case 'getAllVolunteers':
        return ContentService.createTextOutput(JSON.stringify(getAllVolunteers()))
          .setMimeType(ContentService.MimeType.JSON);

      default:
        return ContentService.createTextOutput(JSON.stringify({
          success: false,
          error: 'Invalid action'
        })).setMimeType(ContentService.MimeType.JSON);
    }
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.message
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Handle POST requests
 */
function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  const action = data.action;

  try {
    switch (action) {
      case 'authenticateAdmin':
        return ContentService.createTextOutput(JSON.stringify({
          success: authenticateAdmin(data.password)
        })).setMimeType(ContentService.MimeType.JSON);

      case 'authenticateVolunteer':
        return ContentService.createTextOutput(JSON.stringify({
          success: authenticateVolunteer(data.gateCode)
        })).setMimeType(ContentService.MimeType.JSON);

      case 'createEvent':
        return ContentService.createTextOutput(JSON.stringify(createEvent(data.eventData)))
          .setMimeType(ContentService.MimeType.JSON);

      case 'updateEvent':
        return ContentService.createTextOutput(JSON.stringify(updateEvent(data.eventId, data.eventData)))
          .setMimeType(ContentService.MimeType.JSON);

      case 'createTask':
        return ContentService.createTextOutput(JSON.stringify(createTask(data.taskData)))
          .setMimeType(ContentService.MimeType.JSON);

      case 'volunteerSignup':
        // Find or create volunteer first
        const volunteerResult = findOrCreateVolunteer(data.volunteerData);
        if (!volunteerResult.success) {
          return ContentService.createTextOutput(JSON.stringify(volunteerResult))
            .setMimeType(ContentService.MimeType.JSON);
        }

        // Create signup
        const signupData = {
          eventId: data.eventId,
          taskId: data.taskId,
          volunteerId: volunteerResult.data.VolunteerID,
          notes: data.notes
        };

        return ContentService.createTextOutput(JSON.stringify(createSignup(signupData)))
          .setMimeType(ContentService.MimeType.JSON);

      default:
        return ContentService.createTextOutput(JSON.stringify({
          success: false,
          error: 'Invalid action'
        })).setMimeType(ContentService.MimeType.JSON);
    }
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.message
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// ================================
//     INITIALIZATION FUNCTIONS
// ================================

/**
 * Initialize database with sample data (run once)
 */
function initializeDatabase() {
  // This function should be run once to set up the initial data structure
  // The actual data initialization will be done through the web interface
  console.log('Database structure ready for initialization');
}
