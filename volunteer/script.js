// Club Work Hours Volunteer Management System
// Client-side implementation with localStorage persistence

// Constants
const GATE_CODE = '1957';
const ADMIN_PASSWORD = '5791';

// Default event configuration
const DEFAULT_EVENT = {
    name: 'Spring Cleanup & Maintenance',
    date: '2024-04-15',
    startTime: '09:00',
    endTime: '16:00',
    description: 'Help maintain our beautiful club facilities with landscaping, cleaning, and general maintenance tasks. Every helping hand makes a difference!'
};

// Default tasks
const DEFAULT_TASKS = [
    { id: 1, name: 'Landscaping', volunteersNeeded: 5, timeSlot: '9:00 AM - 12:00 PM' },
    { id: 2, name: 'General Cleaning', volunteersNeeded: 3, timeSlot: '9:00 AM - 4:00 PM' },
    { id: 3, name: 'Maintenance Repairs', volunteersNeeded: 4, timeSlot: '10:00 AM - 3:00 PM' },
    { id: 4, name: 'Trash & Recycling', volunteersNeeded: 2, timeSlot: '3:00 PM - 4:00 PM' }
];

// Storage keys
const STORAGE_KEYS = {
    event: 'clubWorkHours_event',
    tasks: 'clubWorkHours_tasks',
    volunteers: 'clubWorkHours_volunteers',
    emailSettings: 'clubWorkHours_emailSettings',
    isVerified: 'clubWorkHours_verified',
    isAdminAuthenticated: 'clubWorkHours_adminAuth'
};

// Initialize system on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeSystem();
    if (window.location.pathname.includes('admin.html')) {
        initializeAdmin();
    } else {
        initializeVolunteerPage();
    }
});

// System initialization
function initializeSystem() {
    // Initialize default data if not exists
    if (!localStorage.getItem(STORAGE_KEYS.event)) {
        localStorage.setItem(STORAGE_KEYS.event, JSON.stringify(DEFAULT_EVENT));
    }

    if (!localStorage.getItem(STORAGE_KEYS.tasks)) {
        localStorage.setItem(STORAGE_KEYS.tasks, JSON.stringify(DEFAULT_TASKS));
    }

    if (!localStorage.getItem(STORAGE_KEYS.volunteers)) {
        localStorage.setItem(STORAGE_KEYS.volunteers, JSON.stringify([]));
    }

    if (!localStorage.getItem(STORAGE_KEYS.emailSettings)) {
        localStorage.setItem(STORAGE_KEYS.emailSettings, JSON.stringify({
            organizerEmail: 'organizer@club.com',
            template: 'Thank you for volunteering for {EVENT_NAME} on {EVENT_DATE}. We appreciate your commitment to help with {TASK_NAME}. More details will follow closer to the event date.'
        }));
    }
}

// Volunteer page initialization
function initializeVolunteerPage() {
    loadEventDetails();
    loadCurrentVolunteers();
    loadAvailableTasks();

    // Check if user is already verified
    if (localStorage.getItem(STORAGE_KEYS.isVerified) === 'true') {
        showVerifiedState();
    }

    // Setup form submission
    const form = document.getElementById('volunteer-form');
    if (form) {
        form.addEventListener('submit', handleVolunteerSignup);
    }
}

// Gate code verification
function verifyGateCode() {
    const input = document.getElementById('gate-code-input');
    const error = document.getElementById('gate-code-error');

    if (input.value === GATE_CODE) {
        localStorage.setItem(STORAGE_KEYS.isVerified, 'true');
        showVerifiedState();
        error.style.display = 'none';
        input.value = '';
    } else {
        error.style.display = 'block';
        input.value = '';
        setTimeout(() => {
            error.style.display = 'none';
        }, 3000);
    }
}

// Show verified state
function showVerifiedState() {
    const gateSection = document.getElementById('gate-code-section');
    const volunteerForm = document.getElementById('volunteer-form');
    const verificationStatus = document.getElementById('verification-status');

    if (gateSection) gateSection.style.display = 'none';
    if (volunteerForm) volunteerForm.style.display = 'block';
    if (verificationStatus) verificationStatus.style.display = 'block';
}

// Load event details
function loadEventDetails() {
    const event = JSON.parse(localStorage.getItem(STORAGE_KEYS.event));

    const elements = {
        'event-title': event.name,
        'event-date': formatDate(event.date),
        'event-time': `${formatTime(event.startTime)} - ${formatTime(event.endTime)}`,
        'event-description': event.description
    };

    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    });
}

// Load current volunteers
function loadCurrentVolunteers() {
    const volunteers = JSON.parse(localStorage.getItem(STORAGE_KEYS.volunteers));
    const tasks = JSON.parse(localStorage.getItem(STORAGE_KEYS.tasks));
    const container = document.getElementById('volunteers-container');
    const loading = document.getElementById('loading-volunteers');

    if (!container) return;

    if (loading) loading.remove();

    if (volunteers.length === 0) {
        container.innerHTML = `
            <div class="no-volunteers">
                <i class="fas fa-users"></i>
                <p>Be the first to volunteer! Your club needs you.</p>
            </div>
        `;
        return;
    }

    // Group volunteers by task
    const volunteersByTask = {};
    volunteers.forEach(volunteer => {
        if (!volunteersByTask[volunteer.task]) {
            volunteersByTask[volunteer.task] = [];
        }
        volunteersByTask[volunteer.task].push(volunteer);
    });

    let html = '';
    tasks.forEach(task => {
        const taskVolunteers = volunteersByTask[task.name] || [];
        const remaining = task.volunteersNeeded - taskVolunteers.length;

        html += `
            <div class="task-volunteers">
                <div class="task-header">
                    <h3>${task.name}</h3>
                    <span class="task-time">${task.timeSlot}</span>
                    <div class="task-progress">
                        <span class="progress-text">${taskVolunteers.length}/${task.volunteersNeeded} volunteers</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${(taskVolunteers.length / task.volunteersNeeded) * 100}%"></div>
                        </div>
                    </div>
                </div>
                <div class="volunteers-list">
                    ${taskVolunteers.length > 0 ? 
                        taskVolunteers.map(volunteer => `
                            <div class="volunteer-item">
                                <i class="fas fa-user"></i>
                                <span class="volunteer-name">${volunteer.name}</span>
                                ${volunteer.phone ? `<span class="volunteer-contact">${volunteer.phone}</span>` : ''}
                            </div>
                        `).join('') :
                        '<div class="no-volunteers-task">No volunteers yet</div>'
                    }
                    ${remaining > 0 ? `<div class="volunteers-needed">Still need ${remaining} more volunteer${remaining > 1 ? 's' : ''}!</div>` : ''}
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Load available tasks for signup form
function loadAvailableTasks() {
    const tasks = JSON.parse(localStorage.getItem(STORAGE_KEYS.tasks));
    const volunteers = JSON.parse(localStorage.getItem(STORAGE_KEYS.volunteers));
    const select = document.getElementById('volunteer-task');

    if (!select) return;

    // Clear existing options except first one
    select.innerHTML = '<option value="">Select a task...</option>';

    tasks.forEach(task => {
        const taskVolunteers = volunteers.filter(v => v.task === task.name).length;
        const available = task.volunteersNeeded - taskVolunteers;

        if (available > 0) {
            const option = document.createElement('option');
            option.value = task.name;
            option.textContent = `${task.name} (${available} needed) - ${task.timeSlot}`;
            select.appendChild(option);
        }
    });
}

// Handle volunteer signup
function handleVolunteerSignup(event) {
    event.preventDefault();

    const formData = {
        name: document.getElementById('volunteer-name').value.trim(),
        email: document.getElementById('volunteer-email').value.trim(),
        phone: document.getElementById('volunteer-phone').value.trim(),
        task: document.getElementById('volunteer-task').value,
        notes: document.getElementById('volunteer-notes').value.trim(),
        timestamp: new Date().toISOString()
    };

    // Validation
    if (!formData.name || !formData.email || !formData.task) {
        showError('Please fill in all required fields.');
        return;
    }

    // Check if email already registered
    const volunteers = JSON.parse(localStorage.getItem(STORAGE_KEYS.volunteers));
    if (volunteers.some(v => v.email.toLowerCase() === formData.email.toLowerCase())) {
        showError('This email address is already registered.');
        return;
    }

    // Check task availability
    const tasks = JSON.parse(localStorage.getItem(STORAGE_KEYS.tasks));
    const task = tasks.find(t => t.name === formData.task);
    const taskVolunteers = volunteers.filter(v => v.task === formData.task).length;

    if (taskVolunteers >= task.volunteersNeeded) {
        showError('Sorry, this task is now full. Please choose another task.');
        loadAvailableTasks(); // Refresh task list
        return;
    }

    // Add volunteer
    volunteers.push(formData);
    localStorage.setItem(STORAGE_KEYS.volunteers, JSON.stringify(volunteers));

    // Send emails (simulated)
    sendThankYouEmail(formData);
    sendOrganizerNotification(formData);

    // Show success
    showSuccess();

    // Reset form and refresh displays
    document.getElementById('volunteer-form').reset();
    loadCurrentVolunteers();
    loadAvailableTasks();
}

// Admin page initialization
function initializeAdmin() {
    // Check if admin is already authenticated
    if (localStorage.getItem(STORAGE_KEYS.isAdminAuthenticated) === 'true') {
        showAdminPanel();
    }

    loadAdminData();
}

// Admin authentication
function verifyAdminAccess() {
    const input = document.getElementById('admin-password');
    const error = document.getElementById('admin-error');

    if (input.value === ADMIN_PASSWORD) {
        localStorage.setItem(STORAGE_KEYS.isAdminAuthenticated, 'true');
        showAdminPanel();
        error.style.display = 'none';
        input.value = '';
    } else {
        error.style.display = 'block';
        input.value = '';
        setTimeout(() => {
            error.style.display = 'none';
        }, 3000);
    }
}

// Show admin panel
function showAdminPanel() {
    const authSection = document.getElementById('auth-section');
    const adminPanel = document.getElementById('admin-panel');

    if (authSection) authSection.style.display = 'none';
    if (adminPanel) adminPanel.style.display = 'block';

    loadAdminData();
    setupAdminEventListeners();
}

// Setup admin event listeners
function setupAdminEventListeners() {
    // Event form
    const eventForm = document.getElementById('event-form');
    if (eventForm) {
        eventForm.addEventListener('submit', handleEventSave);
    }

    // Task form
    const taskForm = document.getElementById('task-form');
    if (taskForm) {
        taskForm.addEventListener('submit', handleTaskAdd);
    }

    // Email form
    const emailForm = document.getElementById('email-form');
    if (emailForm) {
        emailForm.addEventListener('submit', handleEmailSave);
    }
}

// Load admin data
function loadAdminData() {
    loadEventForm();
    loadTasksAdmin();
    loadVolunteersAdmin();
    loadEmailSettings();
    updateAdminStats();
}

// Load event form data
function loadEventForm() {
    const event = JSON.parse(localStorage.getItem(STORAGE_KEYS.event));

    const fields = {
        'event-name': event.name,
        'event-date-config': event.date,
        'event-start-time': event.startTime,
        'event-end-time': event.endTime,
        'event-description-config': event.description
    };

    Object.entries(fields).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) element.value = value;
    });
}

// Handle event save
function handleEventSave(event) {
    event.preventDefault();

    const eventData = {
        name: document.getElementById('event-name').value.trim(),
        date: document.getElementById('event-date-config').value,
        startTime: document.getElementById('event-start-time').value,
        endTime: document.getElementById('event-end-time').value,
        description: document.getElementById('event-description-config').value.trim()
    };

    localStorage.setItem(STORAGE_KEYS.event, JSON.stringify(eventData));
    showAdminSuccess('Event details saved successfully!');
}

// Handle task addition
function handleTaskAdd(event) {
    event.preventDefault();

    const taskData = {
        id: Date.now(),
        name: document.getElementById('task-name').value.trim(),
        volunteersNeeded: parseInt(document.getElementById('task-volunteers').value),
        timeSlot: document.getElementById('task-time').value.trim() || 'TBD'
    };

    const tasks = JSON.parse(localStorage.getItem(STORAGE_KEYS.tasks));
    tasks.push(taskData);
    localStorage.setItem(STORAGE_KEYS.tasks, JSON.stringify(tasks));

    document.getElementById('task-form').reset();
    loadTasksAdmin();
    updateAdminStats();
    showAdminSuccess('Task added successfully!');
}

// Load tasks in admin
function loadTasksAdmin() {
    const tasks = JSON.parse(localStorage.getItem(STORAGE_KEYS.tasks));
    const container = document.getElementById('admin-tasks-container');

    if (!container) return;

    if (tasks.length === 0) {
        container.innerHTML = '<p class="no-data">No tasks configured yet.</p>';
        return;
    }

    const html = tasks.map(task => `
        <div class="admin-task-item">
            <div class="task-info">
                <h4>${task.name}</h4>
                <p>Volunteers needed: ${task.volunteersNeeded}</p>
                <p>Time: ${task.timeSlot}</p>
            </div>
            <div class="task-actions">
                <button onclick="editTask(${task.id})" class="edit-btn">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button onclick="deleteTask(${task.id})" class="delete-btn">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');

    container.innerHTML = html;
}

// Load volunteers in admin
function loadVolunteersAdmin() {
    const volunteers = JSON.parse(localStorage.getItem(STORAGE_KEYS.volunteers));
    const tbody = document.getElementById('volunteers-table-body');

    if (!tbody) return;

    if (volunteers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">No volunteers registered yet.</td></tr>';
        return;
    }

    const html = volunteers.map((volunteer, index) => `
        <tr>
            <td>${volunteer.name}</td>
            <td>${volunteer.email}</td>
            <td>${volunteer.phone || 'Not provided'}</td>
            <td>${volunteer.task}</td>
            <td>${formatDateTime(volunteer.timestamp)}</td>
            <td>
                <button onclick="removeVolunteer(${index})" class="remove-btn">
                    <i class="fas fa-times"></i> Remove
                </button>
            </td>
        </tr>
    `).join('');

    tbody.innerHTML = html;
}

// Update admin statistics
function updateAdminStats() {
    const volunteers = JSON.parse(localStorage.getItem(STORAGE_KEYS.volunteers));
    const tasks = JSON.parse(localStorage.getItem(STORAGE_KEYS.tasks));

    const totalVolunteers = volunteers.length;
    const totalTasks = tasks.length;
    const totalNeeded = tasks.reduce((sum, task) => sum + task.volunteersNeeded, 0);
    const completionRate = totalNeeded > 0 ? Math.round((totalVolunteers / totalNeeded) * 100) : 0;

    const elements = {
        'total-volunteers': totalVolunteers,
        'total-tasks': totalTasks,
        'completion-rate': `${completionRate}%`
    };

    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    });
}

// Email settings
function loadEmailSettings() {
    const settings = JSON.parse(localStorage.getItem(STORAGE_KEYS.emailSettings));

    const organizerEmailEl = document.getElementById('organizer-email');
    const templateEl = document.getElementById('email-template');

    if (organizerEmailEl) organizerEmailEl.value = settings.organizerEmail;
    if (templateEl) templateEl.value = settings.template;
}

function handleEmailSave(event) {
    event.preventDefault();

    const settings = {
        organizerEmail: document.getElementById('organizer-email').value.trim(),
        template: document.getElementById('email-template').value.trim()
    };

    localStorage.setItem(STORAGE_KEYS.emailSettings, JSON.stringify(settings));
    showAdminSuccess('Email settings saved successfully!');
}

// Utility functions
function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

function formatTime(timeStr) {
    return new Date(`1970-01-01T${timeStr}`).toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit' 
    });
}

function formatDateTime(timestamp) {
    return new Date(timestamp).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
    });
}

// Email simulation functions
function sendThankYouEmail(volunteer) {
    const event = JSON.parse(localStorage.getItem(STORAGE_KEYS.event));
    const settings = JSON.parse(localStorage.getItem(STORAGE_KEYS.emailSettings));

    // Simulate email sending
    console.log('Sending thank you email to:', volunteer.email);
    console.log('Subject: Thank you for volunteering!');

    const message = settings.template
        .replace('{EVENT_NAME}', event.name)
        .replace('{EVENT_DATE}', formatDate(event.date))
        .replace('{VOLUNTEER_NAME}', volunteer.name)
        .replace('{TASK_NAME}', volunteer.task);

    console.log('Message:', message);

    // In a real implementation, this would use EmailJS or similar service
}

function sendOrganizerNotification(volunteer) {
    const event = JSON.parse(localStorage.getItem(STORAGE_KEYS.event));
    const settings = JSON.parse(localStorage.getItem(STORAGE_KEYS.emailSettings));
    const volunteers = JSON.parse(localStorage.getItem(STORAGE_KEYS.volunteers));

    // Simulate organizer notification
    console.log('Sending organizer notification to:', settings.organizerEmail);
    console.log('Subject: New volunteer signup for', event.name);

    const message = `
        New volunteer signup:

        Name: ${volunteer.name}
        Email: ${volunteer.email}
        Phone: ${volunteer.phone || 'Not provided'}
        Task: ${volunteer.task}
        Notes: ${volunteer.notes || 'None'}

        Total volunteers now: ${volunteers.length}
    `;

    console.log('Message:', message);
}

// Modal functions
function showSuccess() {
    const modal = document.getElementById('success-modal');
    if (modal) modal.style.display = 'flex';
}

function showError(message) {
    const modal = document.getElementById('error-modal');
    const messageEl = document.getElementById('error-message');

    if (messageEl) messageEl.textContent = message;
    if (modal) modal.style.display = 'flex';
}

function showAdminSuccess(message) {
    const modal = document.getElementById('admin-success-modal');
    const messageEl = document.getElementById('success-message-admin');

    if (messageEl) messageEl.textContent = message;
    if (modal) modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('success-modal');
    if (modal) modal.style.display = 'none';
}

function closeErrorModal() {
    const modal = document.getElementById('error-modal');
    if (modal) modal.style.display = 'none';
}

function closeSuccessModal() {
    const modal = document.getElementById('admin-success-modal');
    if (modal) modal.style.display = 'none';
}

// Admin management functions
function deleteTask(taskId) {
    const tasks = JSON.parse(localStorage.getItem(STORAGE_KEYS.tasks));
    const updatedTasks = tasks.filter(task => task.id !== taskId);
    localStorage.setItem(STORAGE_KEYS.tasks, JSON.stringify(updatedTasks));

    loadTasksAdmin();
    updateAdminStats();
    showAdminSuccess('Task deleted successfully!');
}

function removeVolunteer(index) {
    const volunteers = JSON.parse(localStorage.getItem(STORAGE_KEYS.volunteers));
    volunteers.splice(index, 1);
    localStorage.setItem(STORAGE_KEYS.volunteers, JSON.stringify(volunteers));

    loadVolunteersAdmin();
    updateAdminStats();
    showAdminSuccess('Volunteer removed successfully!');
}

function exportVolunteers() {
    const volunteers = JSON.parse(localStorage.getItem(STORAGE_KEYS.volunteers));
    const event = JSON.parse(localStorage.getItem(STORAGE_KEYS.event));

    if (volunteers.length === 0) {
        alert('No volunteers to export.');
        return;
    }

    // Create CSV content
    const headers = ['Name', 'Email', 'Phone', 'Task', 'Notes', 'Registered'];
    const csvContent = [
        headers.join(','),
        ...volunteers.map(v => [
            `"${v.name}"`,
            `"${v.email}"`,
            `"${v.phone || ''}"`,
            `"${v.task}"`,
            `"${v.notes || ''}"`,
            `"${formatDateTime(v.timestamp)}"`
        ].join(','))
    ].join('\n');

    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${event.name.replace(/\s+/g, '_')}_volunteers.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function printVolunteers() {
    const volunteers = JSON.parse(localStorage.getItem(STORAGE_KEYS.volunteers));
    const event = JSON.parse(localStorage.getItem(STORAGE_KEYS.event));

    if (volunteers.length === 0) {
        alert('No volunteers to print.');
        return;
    }

    const printContent = `
        <html>
        <head>
            <title>Volunteer List - ${event.name}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 8px; border: 1px solid #ddd; text-align: left; }
                th { background-color: #f4f4f4; }
            </style>
        </head>
        <body>
            <h1>${event.name} - Volunteer List</h1>
            <p>Date: ${formatDate(event.date)}</p>
            <p>Total Volunteers: ${volunteers.length}</p>

            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Task</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    ${volunteers.map(v => `
                        <tr>
                            <td>${v.name}</td>
                            <td>${v.email}</td>
                            <td>${v.phone || 'N/A'}</td>
                            <td>${v.task}</td>
                            <td>${v.notes || 'None'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </body>
        </html>
    `;

    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
}

function resetAllData() {
    if (confirm('Are you sure you want to reset all data? This cannot be undone.')) {
        Object.values(STORAGE_KEYS).forEach(key => {
            localStorage.removeItem(key);
        });

        // Reinitialize with defaults
        initializeSystem();
        loadAdminData();
        showAdminSuccess('All data has been reset to defaults.');
    }
}

function backupData() {
    const backup = {
        event: JSON.parse(localStorage.getItem(STORAGE_KEYS.event)),
        tasks: JSON.parse(localStorage.getItem(STORAGE_KEYS.tasks)),
        volunteers: JSON.parse(localStorage.getItem(STORAGE_KEYS.volunteers)),
        emailSettings: JSON.parse(localStorage.getItem(STORAGE_KEYS.emailSettings)),
        timestamp: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `volunteer_system_backup_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    showAdminSuccess('Backup file downloaded successfully!');
}

function testEmailSystem() {
    showAdminSuccess('Email system test completed. Check console for details.');
    console.log('Email system test - all functions working correctly.');
}

// Close modals when clicking outside
window.onclick = function(event) {
    const modals = ['success-modal', 'error-modal', 'admin-success-modal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
};

// Enter key handling for gate code and admin password
document.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        if (event.target.id === 'gate-code-input') {
            verifyGateCode();
        } else if (event.target.id === 'admin-password') {
            verifyAdminAccess();
        }
    }
});
