// Volunteer Management System - Complete JavaScript
// Admin password: 7591, Gate code: 1957

// Global variables
let events = [];
let currentEvent = null;
const ADMIN_PASSWORD = '7591';
const GATE_CODE = '1957';

// Storage keys
const EVENTS_STORAGE_KEY = 'volunteerEvents';
const VOLUNTEERS_STORAGE_KEY = 'volunteerData';

// Initialize system on page load
document.addEventListener('DOMContentLoaded', function() {
    loadEventsFromStorage();

    // Check what page we're on and initialize accordingly
    if (window.location.pathname.includes('/admin.html')) {
        initializeAdminPage();
    } else {
        initializePublicPage();
    }
});

// Storage functions
function saveEventsToStorage() {
    localStorage.setItem(EVENTS_STORAGE_KEY, JSON.stringify(events));
}

function loadEventsFromStorage() {
    const stored = localStorage.getItem(EVENTS_STORAGE_KEY);
    events = stored ? JSON.parse(stored) : [];
}

function saveVolunteerData(eventSlug, volunteers) {
    const allVolunteers = JSON.parse(localStorage.getItem(VOLUNTEERS_STORAGE_KEY) || '{}');
    allVolunteers[eventSlug] = volunteers;
    localStorage.setItem(VOLUNTEERS_STORAGE_KEY, JSON.stringify(allVolunteers));
}

function loadVolunteerData(eventSlug) {
    const allVolunteers = JSON.parse(localStorage.getItem(VOLUNTEERS_STORAGE_KEY) || '{}');
    return allVolunteers[eventSlug] || [];
}

// Public page initialization
function initializePublicPage() {
    displayEventList();
}

// Admin page initialization
function initializeAdminPage() {
    // Admin page is protected by password, so don't initialize until authenticated
}

// Display event list on main page
function displayEventList() {
    const container = document.getElementById('events-container');
    const noEventsDiv = document.getElementById('no-events');

    if (events.length === 0) {
        container.innerHTML = '';
        noEventsDiv.style.display = 'block';
        return;
    }

    noEventsDiv.style.display = 'none';

    container.innerHTML = events.map(event => {
        const volunteers = loadVolunteerData(event.eventSlug);
        const totalVolunteers = volunteers.length;
        const totalNeeded = event.tasks.reduce((sum, task) => sum + task.needed, 0);

        return `
            <div class="event-card">
                ${event.imageUrl ? `<img src="${event.imageUrl}" alt="${event.eventName}" class="event-image" onerror="this.style.display='none'">` : ''}
                <div class="event-header">
                    <div>
                        <h3 class="event-title">${event.eventName}</h3>
                        <p class="event-date">
                            <i class="fas fa-calendar"></i>
                            ${formatEventDate(event.eventDate)} • ${event.startTime} - ${event.endTime}
                        </p>
                    </div>
                    <div class="volunteer-count">
                        ${totalVolunteers}/${totalNeeded} volunteers
                    </div>
                </div>
                <p class="event-description">${event.description}</p>
                <div class="event-actions">
                    <a href="#" onclick="showEventSignup('${event.eventSlug}')" class="volunteer-btn">
                        <i class="fas fa-hand-paper"></i>
                        Volunteer Now
                    </a>
                </div>
            </div>
        `;
    }).join('');
}

// Show individual event signup (simulates going to unique URL)
function showEventSignup(eventSlug) {
    const event = events.find(e => e.eventSlug === eventSlug);
    if (!event) return;

    currentEvent = event;

    // Create modal for event signup
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        padding: 20px;
    `;

    const volunteers = loadVolunteerData(eventSlug);

    modal.innerHTML = `
        <div style="background: white; border-radius: 15px; max-width: 800px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 30px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="color: #1e40af; margin: 0;">${event.eventName}</h2>
                <button onclick="closeModal()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #64748b;">×</button>
            </div>

            ${event.imageUrl ? `<img src="${event.imageUrl}" alt="${event.eventName}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 10px; margin-bottom: 20px;" onerror="this.style.display='none'">` : ''}

            <div style="margin-bottom: 30px;">
                <p style="color: #64748b; margin-bottom: 10px;">
                    <i class="fas fa-calendar"></i> ${formatEventDate(event.eventDate)} • ${event.startTime} - ${event.endTime}
                </p>
                <p style="color: #64748b; line-height: 1.6;">${event.description}</p>
            </div>

            <div style="margin-bottom: 30px;">
                <h3 style="color: #1e40af; margin-bottom: 20px;"><i class="fas fa-users"></i> Current Volunteers</h3>
                <div id="current-volunteers">
                    ${displayCurrentVolunteers(event, volunteers)}
                </div>
            </div>

            <div>
                <h3 style="color: #1e40af; margin-bottom: 20px;"><i class="fas fa-hand-paper"></i> Sign Up to Help</h3>
                <div id="signup-section">
                    <div style="background: #f0f9ff; border: 1px solid #bae6fd; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                        <i class="fas fa-shield-alt" style="color: #0ea5e9;"></i>
                        <strong>Member Verification Required:</strong> Please enter the club gate code to continue.
                    </div>
                    <form id="volunteer-signup-form" onsubmit="submitVolunteerSignup(event)">
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151;">
                                <i class="fas fa-key"></i> Gate Code *
                            </label>
                            <input type="password" id="gate-code" maxlength="4" required style="width: 100%; padding: 12px 15px; border: 2px solid #e2e8f0; border-radius: 8px;">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151;">
                                <i class="fas fa-user"></i> Your Name *
                            </label>
                            <input type="text" id="volunteer-name" required style="width: 100%; padding: 12px 15px; border: 2px solid #e2e8f0; border-radius: 8px;">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151;">
                                <i class="fas fa-envelope"></i> Email *
                            </label>
                            <input type="email" id="volunteer-email" required style="width: 100%; padding: 12px 15px; border: 2px solid #e2e8f0; border-radius: 8px;">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151;">
                                <i class="fas fa-phone"></i> Phone (optional)
                            </label>
                            <input type="tel" id="volunteer-phone" style="width: 100%; padding: 12px 15px; border: 2px solid #e2e8f0; border-radius: 8px;">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151;">
                                <i class="fas fa-tasks"></i> Choose Your Task *
                            </label>
                            <select id="volunteer-task" required style="width: 100%; padding: 12px 15px; border: 2px solid #e2e8f0; border-radius: 8px;">
                                <option value="">Select a task...</option>
                                ${event.tasks.map(task => {
                                    const taskVolunteers = volunteers.filter(v => v.taskId === task.id).length;
                                    const available = task.needed - taskVolunteers;
                                    return `<option value="${task.id}" ${available <= 0 ? 'disabled' : ''}>${task.name} (${available} spots available)</option>`;
                                }).join('')}
                            </select>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #374151;">
                                <i class="fas fa-comment"></i> Notes (optional)
                            </label>
                            <textarea id="volunteer-notes" rows="3" placeholder="Any special requests or notes..." style="width: 100%; padding: 12px 15px; border: 2px solid #e2e8f0; border-radius: 8px;"></textarea>
                        </div>
                        <button type="submit" style="background: linear-gradient(135deg, #059669, #10b981); color: white; padding: 15px 30px; border: none; border-radius: 10px; font-weight: 600; width: 100%; cursor: pointer;">
                            <i class="fas fa-check"></i> Sign Me Up!
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

// Display current volunteers for an event
function displayCurrentVolunteers(event, volunteers) {
    if (volunteers.length === 0) {
        return '<p style="color: #94a3b8; font-style: italic;">No volunteers signed up yet. Be the first!</p>';
    }

    return event.tasks.map(task => {
        const taskVolunteers = volunteers.filter(v => v.taskId === task.id);
        const available = task.needed - taskVolunteers.length;

        return `
            <div style="margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 8px;">
                <h4 style="color: #1e40af; margin-bottom: 10px;">${task.name}</h4>
                <p style="color: #64748b; margin-bottom: 10px;">
                    <strong>${taskVolunteers.length}/${task.needed}</strong> volunteers
                    ${available > 0 ? `• <span style="color: #059669;">${available} spots available</span>` : '• <span style="color: #dc2626;">Full</span>'}
                </p>
                ${taskVolunteers.length > 0 ? `
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        ${taskVolunteers.map(volunteer => `
                            <span style="background: #0ea5e9; color: white; padding: 4px 12px; border-radius: 15px; font-size: 0.9rem;">
                                ${volunteer.name}
                            </span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

// Submit volunteer signup
function submitVolunteerSignup(event) {
    event.preventDefault();

    const gateCode = document.getElementById('gate-code').value;
    const name = document.getElementById('volunteer-name').value;
    const email = document.getElementById('volunteer-email').value;
    const phone = document.getElementById('volunteer-phone').value;
    const taskId = parseInt(document.getElementById('volunteer-task').value);
    const notes = document.getElementById('volunteer-notes').value;

    // Validate gate code
    if (gateCode !== GATE_CODE) {
        alert('Incorrect gate code. Please verify your club membership.');
        return;
    }

    // Get current volunteers and add new one
    const volunteers = loadVolunteerData(currentEvent.eventSlug);
    const newVolunteer = {
        id: Date.now(),
        name,
        email,
        phone,
        taskId,
        notes,
        signupDate: new Date().toISOString()
    };

    volunteers.push(newVolunteer);
    saveVolunteerData(currentEvent.eventSlug, volunteers);

    // Send thank you email (simulated)
    sendThankYouEmail(newVolunteer, currentEvent);

    // Send organizer notification (simulated)
    sendOrganizerNotification(currentEvent, volunteers);

    // Show success message
    alert(`Thank you, ${name}! You've successfully signed up for ${currentEvent.eventName}. You'll receive a confirmation email shortly.`);

    // Close modal and refresh
    closeModal();
    displayEventList();
}

// Close modal
function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

// Admin functions
function verifyAdminPassword() {
    const password = document.getElementById('admin-password').value;
    const errorDiv = document.getElementById('password-error');

    if (password === ADMIN_PASSWORD) {
        document.getElementById('admin-login').style.display = 'none';
        document.getElementById('admin-panel').style.display = 'block';
        loadAdminData();
    } else {
        errorDiv.style.display = 'block';
        document.getElementById('admin-password').value = '';
    }
}

function loadAdminData() {
    displayManageEvents();
}

// Admin navigation
function showCreateEvent() {
    document.getElementById('create-event').style.display = 'block';
    document.getElementById('manage-events').style.display = 'none';

    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector('.nav-btn').classList.add('active');
}

function showManageEvents() {
    document.getElementById('create-event').style.display = 'none';
    document.getElementById('manage-events').style.display = 'block';

    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.nav-btn')[1].classList.add('active');

    displayManageEvents();
}

// Display events management
function displayManageEvents() {
    const container = document.getElementById('events-management');

    if (events.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b; padding: 40px;">No events created yet. Create your first event to get started!</p>';
        return;
    }

    container.innerHTML = events.map(event => {
        const volunteers = loadVolunteerData(event.eventSlug);
        return `
            <div class="event-management-card">
                <div class="event-management-header">
                    <div>
                        <h3 style="color: #1e40af; margin-bottom: 5px;">${event.eventName}</h3>
                        <p style="color: #64748b;">${formatEventDate(event.eventDate)} • ${volunteers.length} volunteers</p>
                    </div>
                    <div class="management-actions">
                        <button onclick="viewEventDetails('${event.eventSlug}')" class="management-btn view-btn">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <button onclick="editEvent('${event.eventSlug}')" class="management-btn edit-btn">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button onclick="deleteEvent('${event.eventSlug}')" class="management-btn delete-btn">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Event form handling
document.addEventListener('DOMContentLoaded', function() {
    const eventForm = document.getElementById('event-form');
    if (eventForm) {
        eventForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createNewEvent();
        });
    }

    // Auto-generate slug from event name
    const eventNameInput = document.getElementById('event-name');
    const eventSlugInput = document.getElementById('event-slug');

    if (eventNameInput && eventSlugInput) {
        eventNameInput.addEventListener('input', function() {
            const slug = this.value.toLowerCase()
                .replace(/[^a-z0-9]+/g, '-')
                .replace(/(^-|-$)/g, '');
            eventSlugInput.value = slug;
        });
    }
});

// Create new event
function createNewEvent() {
    const eventData = {
        eventSlug: document.getElementById('event-slug').value,
        eventName: document.getElementById('event-name').value,
        eventDate: document.getElementById('event-date').value,
        startTime: document.getElementById('start-time').value,
        endTime: document.getElementById('end-time').value,
        description: document.getElementById('event-description').value,
        imageUrl: document.getElementById('event-image').value,
        organizerEmail: document.getElementById('organizer-email').value,
        tasks: [],
        createdDate: new Date().toISOString()
    };

    // Collect tasks
    const taskItems = document.querySelectorAll('.task-item');
    taskItems.forEach((item, index) => {
        const name = item.querySelector('.task-name').value;
        const needed = parseInt(item.querySelector('.task-count').value);

        if (name && needed > 0) {
            eventData.tasks.push({
                id: index + 1,
                name,
                needed
            });
        }
    });

    // Validate
    if (eventData.tasks.length === 0) {
        alert('Please add at least one volunteer task.');
        return;
    }

    // Check for duplicate slug
    if (events.find(e => e.eventSlug === eventData.eventSlug)) {
        alert('An event with this URL slug already exists. Please choose a different one.');
        return;
    }

    // Add to events array
    events.push(eventData);
    saveEventsToStorage();

    // Show success message
    alert(`Event "${eventData.eventName}" created successfully!`);

    // Reset form
    document.getElementById('event-form').reset();

    // Refresh management view
    displayManageEvents();
}

// Task management
function addTask() {
    const container = document.getElementById('tasks-container');
    const taskDiv = document.createElement('div');
    taskDiv.className = 'task-item';
    taskDiv.innerHTML = `
        <input type="text" placeholder="Task description (e.g., Set up tables and chairs)" class="task-name" required>
        <input type="number" placeholder="# needed" class="task-count" min="1" required>
        <button type="button" onclick="removeTask(this)" class="remove-task">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(taskDiv);
}

function removeTask(button) {
    const taskItem = button.closest('.task-item');
    taskItem.remove();
}

// Delete event
function deleteEvent(eventSlug) {
    if (!confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
        return;
    }

    // Remove event
    events = events.filter(e => e.eventSlug !== eventSlug);
    saveEventsToStorage();

    // Remove associated volunteer data
    const allVolunteers = JSON.parse(localStorage.getItem(VOLUNTEERS_STORAGE_KEY) || '{}');
    delete allVolunteers[eventSlug];
    localStorage.setItem(VOLUNTEERS_STORAGE_KEY, JSON.stringify(allVolunteers));

    // Refresh display
    displayManageEvents();

    alert('Event deleted successfully.');
}

// Email functions (simulated)
function sendThankYouEmail(volunteer, event) {
    console.log('Thank you email sent to:', volunteer.email);
    console.log('Event:', event.eventName);
    // In a real system, this would integrate with an email service
}

function sendOrganizerNotification(event, volunteers) {
    console.log('Organizer notification sent to:', event.organizerEmail);
    console.log('Total volunteers:', volunteers.length);
    // In a real system, this would send updated volunteer roster
}

// Utility functions
function formatEventDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Allow Enter key for admin password
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && document.getElementById('admin-password') === document.activeElement) {
        verifyAdminPassword();
    }
});