// Club Work Hours Volunteer Management System JavaScript
// Gate codes: 1957 for volunteers, 5791 for admin access

// System Configuration
const CONFIG = {
    VOLUNTEER_GATE_CODE: '1957',
    ADMIN_PASSWORD: '5791',
    EMAIL_NOTIFICATIONS: true,
    AUTO_SAVE: true
};

// Global state
let currentEvent = null;
let volunteers = [];
let tasks = [];
let isVerified = false;
let isAdminVerified = false;

// Initialize system on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Volunteer Management System Initialized');

    // Check if this is admin page
    if (window.location.pathname.includes('admin.html')) {
        initializeAdminPage();
    } else {
        initializeMainPage();
    }

    // Load saved data
    loadEventData();
    loadVolunteers();
    loadTasks();
});

// Main page initialization
function initializeMainPage() {
    console.log('📋 Initializing main volunteer signup page');

    // Set up form handlers
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', handleVolunteerSignup);
    }

    // Set up gate code modal handlers
    setupGateCodeModal();

    // Load and display current data
    updateEventDisplay();
    updateVolunteersDisplay();
    updateTasksDisplay();

    // Show verification status if previously verified
    if (localStorage.getItem('volunteer_verified') === 'true') {
        showVerificationStatus();
        isVerified = true;
    }
}

// Admin page initialization
function initializeAdminPage() {
    console.log('🔧 Initializing admin page');

    // Check if admin is already verified
    if (localStorage.getItem('admin_verified') === 'true') {
        showAdminContent();
        isAdminVerified = true;
    }

    // Set up admin password verification
    setupAdminAccess();

    // Set up form handlers
    setupAdminForms();
}

// Event data management
function loadEventData() {
    const savedEvent = localStorage.getItem('club_event_data');
    if (savedEvent) {
        currentEvent = JSON.parse(savedEvent);
    } else {
        // Default event data
        currentEvent = {
            name: 'Spring Cleanup & Maintenance',
            date: '2024-04-15',
            startTime: '09:00',
            endTime: '16:00',
            description: 'Help maintain our beautiful club facilities with landscaping, cleaning, and general maintenance tasks. Every helping hand makes a difference!',
            organizerEmail: 'organizer@club.com'
        };
        saveEventData();
    }
}

function saveEventData() {
    if (CONFIG.AUTO_SAVE) {
        localStorage.setItem('club_event_data', JSON.stringify(currentEvent));
    }
}

// Volunteers data management
function loadVolunteers() {
    const savedVolunteers = localStorage.getItem('club_volunteers_data');
    if (savedVolunteers) {
        volunteers = JSON.parse(savedVolunteers);
    } else {
        volunteers = [];
    }
}

function saveVolunteers() {
    if (CONFIG.AUTO_SAVE) {
        localStorage.setItem('club_volunteers_data', JSON.stringify(volunteers));
    }
}

// Tasks data management
function loadTasks() {
    const savedTasks = localStorage.getItem('club_tasks_data');
    if (savedTasks) {
        tasks = JSON.parse(savedTasks);
    } else {
        // Default tasks
        tasks = [
            {
                id: 'task-1',
                name: 'Landscaping & Grounds',
                description: 'Weeding, planting, lawn maintenance',
                category: 'Landscaping',
                volunteersNeeded: 4,
                volunteers: []
            },
            {
                id: 'task-2', 
                name: 'Building Maintenance',
                description: 'Painting, repairs, cleaning',
                category: 'Maintenance',
                volunteersNeeded: 3,
                volunteers: []
            },
            {
                id: 'task-3',
                name: 'Dock & Marina',
                description: 'Dock repairs, marina cleanup',
                category: 'Maintenance', 
                volunteersNeeded: 3,
                volunteers: []
            },
            {
                id: 'task-4',
                name: 'General Cleanup',
                description: 'Trash pickup, organizing storage',
                category: 'Cleaning',
                volunteersNeeded: 2,
                volunteers: []
            }
        ];
        saveTasks();
    }
}

function saveTasks() {
    if (CONFIG.AUTO_SAVE) {
        localStorage.setItem('club_tasks_data', JSON.stringify(tasks));
    }
}

// Update displays
function updateEventDisplay() {
    if (!currentEvent) return;

    // Update event details
    const eventTitle = document.getElementById('event-title');
    const eventDate = document.getElementById('event-date');
    const eventTime = document.getElementById('event-time');
    const eventDescription = document.getElementById('event-description');

    if (eventTitle) eventTitle.textContent = currentEvent.name;
    if (eventDate) eventDate.textContent = formatDate(currentEvent.date);
    if (eventTime) eventTime.textContent = `${formatTime(currentEvent.startTime)} - ${formatTime(currentEvent.endTime)}`;
    if (eventDescription) eventDescription.textContent = currentEvent.description;
}

function updateVolunteersDisplay() {
    const container = document.getElementById('volunteers-container');
    if (!container) return;

    if (volunteers.length === 0) {
        container.innerHTML = `
            <div class="no-volunteers">
                <i class="fas fa-users"></i>
                <p>Be the first to volunteer! Your participation makes a difference.</p>
            </div>
        `;
        return;
    }

    // Group volunteers by task
    const volunteersByTask = {};
    volunteers.forEach(volunteer => {
        if (!volunteersByTask[volunteer.taskRole]) {
            volunteersByTask[volunteer.taskRole] = [];
        }
        volunteersByTask[volunteer.taskRole].push(volunteer);
    });

    let html = '<div class="volunteers-grid">';

    // Display each task group
    tasks.forEach(task => {
        const taskVolunteers = volunteersByTask[task.name] || [];
        const progress = (taskVolunteers.length / task.volunteersNeeded) * 100;

        html += `
            <div class="task-group">
                <div class="task-header">
                    <h3 class="task-title">${task.name}</h3>
                    <span class="task-count">${taskVolunteers.length}/${task.volunteersNeeded}</span>
                </div>
                <div class="task-progress">
                    <div class="task-progress-bar" style="width: ${Math.min(progress, 100)}%"></div>
                </div>
                <div class="volunteers-list">
        `;

        if (taskVolunteers.length > 0) {
            taskVolunteers.forEach(volunteer => {
                html += `
                    <div class="volunteer-item">
                        <div class="volunteer-info">
                            <div class="volunteer-name">${volunteer.name}</div>
                            <div class="volunteer-contact">${volunteer.email}</div>
                        </div>
                        ${isVerified ? `<button class="remove-volunteer" onclick="removeVolunteer('${volunteer.id}')">
                            <i class="fas fa-times"></i>
                        </button>` : ''}
                    </div>
                `;
            });
        } else {
            html += `
                <div class="no-volunteers-task">
                    <i class="fas fa-hand-paper"></i>
                    <span>Still needs volunteers!</span>
                </div>
            `;
        }

        html += `
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

function updateTasksDisplay() {
    // Update task dropdown in signup form
    const taskSelect = document.getElementById('task_role');
    if (!taskSelect) return;

    // Clear existing options except the first one
    taskSelect.innerHTML = '<option value="">Select a task...</option>';

    tasks.forEach(task => {
        const volunteersCount = volunteers.filter(v => v.taskRole === task.name).length;
        const isAvailable = volunteersCount < task.volunteersNeeded;
        const availabilityText = isAvailable ? `(${task.volunteersNeeded - volunteersCount} spots left)` : '(Full)';

        const option = document.createElement('option');
        option.value = task.name;
        option.textContent = `${task.name} ${availabilityText}`;
        option.disabled = !isAvailable;

        taskSelect.appendChild(option);
    });

    // Update tasks container for display
    const tasksContainer = document.getElementById('tasks-container');
    if (tasksContainer) {
        let html = '';
        tasks.forEach(task => {
            const volunteersCount = volunteers.filter(v => v.taskRole === task.name).length;
            const progress = (volunteersCount / task.volunteersNeeded) * 100;
            const isComplete = volunteersCount >= task.volunteersNeeded;

            html += `
                <div class="task-requirement ${isComplete ? 'complete' : ''}">
                    <div class="task-info">
                        <h4>${task.name}</h4>
                        <p>${task.description}</p>
                        <div class="task-progress">
                            <div class="task-progress-bar" style="width: ${Math.min(progress, 100)}%"></div>
                        </div>
                    </div>
                    <div class="task-status">
                        <span class="volunteers-count">${volunteersCount}/${task.volunteersNeeded}</span>
                        ${isComplete ? '<i class="fas fa-check-circle complete-icon"></i>' : ''}
                    </div>
                </div>
            `;
        });
        tasksContainer.innerHTML = html;
    }
}

// Volunteer signup handling
function handleVolunteerSignup(event) {
    event.preventDefault();

    // Check if user is verified
    if (!isVerified) {
        showGateCodeModal();
        return;
    }

    // Get form data
    const formData = new FormData(event.target);
    const volunteer = {
        id: 'vol-' + Date.now(),
        name: formData.get('volunteer_name'),
        email: formData.get('email'),
        phone: formData.get('phone') || '',
        taskRole: formData.get('task_role'),
        notes: formData.get('notes') || '',
        signupDate: new Date().toISOString()
    };

    // Validate required fields
    if (!volunteer.name || !volunteer.email || !volunteer.taskRole) {
        showError('Please fill in all required fields.');
        return;
    }

    // Check if task is full
    const task = tasks.find(t => t.name === volunteer.taskRole);
    const currentVolunteers = volunteers.filter(v => v.taskRole === volunteer.taskRole);

    if (currentVolunteers.length >= task.volunteersNeeded) {
        showError('Sorry, this task is already full. Please choose another task.');
        return;
    }

    // Add volunteer
    volunteers.push(volunteer);
    saveVolunteers();

    // Update displays
    updateVolunteersDisplay();
    updateTasksDisplay();

    // Send emails
    if (CONFIG.EMAIL_NOTIFICATIONS) {
        sendThankYouEmail(volunteer);
        sendOrganizerUpdate(volunteer, 'new');
    }

    // Show success message
    showSuccessModal();

    // Reset form
    event.target.reset();

    console.log('✅ Volunteer signup successful:', volunteer.name);
}

// Gate code verification
function setupGateCodeModal() {
    const gateCodeInput = document.getElementById('gate-code-input');
    if (gateCodeInput) {
        gateCodeInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                verifyGateCode();
            }
        });
    }
}

function showGateCodeModal() {
    const modal = document.getElementById('gate-code-modal');
    if (modal) {
        modal.style.display = 'block';
        const input = document.getElementById('gate-code-input');
        if (input) {
            input.focus();
        }
    }
}

function closeGateCodeModal() {
    const modal = document.getElementById('gate-code-modal');
    if (modal) {
        modal.style.display = 'none';
        const input = document.getElementById('gate-code-input');
        const error = document.getElementById('gate-code-error');
        if (input) input.value = '';
        if (error) error.classList.remove('show');
    }
}

function verifyGateCode() {
    const input = document.getElementById('gate-code-input');
    const error = document.getElementById('gate-code-error');

    if (input.value === CONFIG.VOLUNTEER_GATE_CODE) {
        isVerified = true;
        localStorage.setItem('volunteer_verified', 'true');
        closeGateCodeModal();
        showVerificationStatus();

        // Re-submit the form if it was pending
        const form = document.getElementById('signup-form');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    } else {
        error.classList.add('show');
        input.value = '';
        input.focus();
    }
}

function showVerificationStatus() {
    const status = document.getElementById('verification-status');
    if (status) {
        status.classList.add('show');
    }
}

// Admin access
function setupAdminAccess() {
    const adminPasswordInput = document.getElementById('admin-password');
    if (adminPasswordInput) {
        adminPasswordInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                verifyAdminAccess();
            }
        });
    }
}

function verifyAdminAccess() {
    const input = document.getElementById('admin-password');
    const error = document.getElementById('access-error');

    if (input.value === CONFIG.ADMIN_PASSWORD) {
        isAdminVerified = true;
        localStorage.setItem('admin_verified', 'true');
        showAdminContent();
    } else {
        error.classList.add('show');
        input.value = '';
        input.focus();
    }
}

function showAdminContent() {
    const accessControl = document.getElementById('access-control');
    const adminContent = document.getElementById('admin-content');

    if (accessControl) accessControl.style.display = 'none';
    if (adminContent) adminContent.style.display = 'block';

    // Initialize admin functionality
    loadAdminData();
}

// Admin functionality
function setupAdminForms() {
    const eventForm = document.getElementById('event-config-form');
    if (eventForm) {
        eventForm.addEventListener('submit', handleEventConfiguration);
    }

    const addTaskBtn = document.getElementById('add-task-btn');
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', showTaskModal);
    }

    const taskForm = document.getElementById('task-form');
    if (taskForm) {
        taskForm.addEventListener('submit', handleTaskSave);
    }
}

function loadAdminData() {
    // Load event configuration into form
    if (currentEvent) {
        const form = document.getElementById('event-config-form');
        if (form) {
            form.event_name.value = currentEvent.name || '';
            form.event_date.value = currentEvent.date || '';
            form.start_time.value = currentEvent.startTime || '';
            form.end_time.value = currentEvent.endTime || '';
            form.event_description.value = currentEvent.description || '';
            form.organizer_email.value = currentEvent.organizerEmail || '';
        }
    }

    // Load tasks list
    updateAdminTasksList();

    // Load volunteers list
    updateAdminVolunteersList();
}

function handleEventConfiguration(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    currentEvent = {
        name: formData.get('event_name'),
        date: formData.get('event_date'),
        startTime: formData.get('start_time'),
        endTime: formData.get('end_time'),
        description: formData.get('event_description'),
        organizerEmail: formData.get('organizer_email')
    };

    saveEventData();
    updateEventDisplay();

    showAlert('Event configuration saved successfully!', 'success');
}

function updateAdminTasksList() {
    const container = document.getElementById('tasks-list');
    if (!container) return;

    if (tasks.length === 0) {
        container.innerHTML = '<p>No tasks configured. Add your first task above.</p>';
        return;
    }

    let html = '';
    tasks.forEach(task => {
        const volunteersCount = volunteers.filter(v => v.taskRole === task.name).length;

        html += `
            <div class="task-item">
                <div class="task-info">
                    <h4>${task.name}</h4>
                    <p>${task.description}</p>
                    <div class="task-stats">
                        Category: ${task.category} | 
                        Volunteers: ${volunteersCount}/${task.volunteersNeeded}
                    </div>
                </div>
                <div class="task-actions">
                    <button class="edit-task" onclick="editTask('${task.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="delete-task" onclick="deleteTask('${task.id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function updateAdminVolunteersList() {
    const container = document.getElementById('admin-volunteers-container');
    if (!container) return;

    if (volunteers.length === 0) {
        container.innerHTML = '<p>No volunteers signed up yet.</p>';
        return;
    }

    let html = '<div class="admin-volunteers-list">';
    volunteers.forEach(volunteer => {
        html += `
            <div class="admin-volunteer-item">
                <div class="volunteer-details">
                    <h4>${volunteer.name}</h4>
                    <p><strong>Task:</strong> ${volunteer.taskRole}</p>
                    <p><strong>Email:</strong> ${volunteer.email}</p>
                    ${volunteer.phone ? `<p><strong>Phone:</strong> ${volunteer.phone}</p>` : ''}
                    ${volunteer.notes ? `<p><strong>Notes:</strong> ${volunteer.notes}</p>` : ''}
                    <p><strong>Signed up:</strong> ${formatDateTime(volunteer.signupDate)}</p>
                </div>
                <div class="volunteer-actions">
                    <button class="remove-volunteer" onclick="removeVolunteerAdmin('${volunteer.id}')">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                </div>
            </div>
        `;
    });
    html += '</div>';

    container.innerHTML = html;
}

// Task management
function showTaskModal(taskId = null) {
    const modal = document.getElementById('task-modal');
    const form = document.getElementById('task-form');
    const title = modal.querySelector('h3');

    if (taskId) {
        // Edit mode
        const task = tasks.find(t => t.id === taskId);
        if (task) {
            title.textContent = 'Edit Task';
            form.task_name.value = task.name;
            form.task_description.value = task.description;
            form.volunteers_needed.value = task.volunteersNeeded;
            form.task_category.value = task.category;
            form.dataset.taskId = taskId;
        }
    } else {
        // Add mode
        title.textContent = 'Add New Task';
        form.reset();
        delete form.dataset.taskId;
    }

    modal.style.display = 'block';
}

function closeTaskModal() {
    const modal = document.getElementById('task-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function handleTaskSave(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const taskData = {
        name: formData.get('task_name'),
        description: formData.get('task_description'),
        volunteersNeeded: parseInt(formData.get('volunteers_needed')),
        category: formData.get('task_category')
    };

    const taskId = event.target.dataset.taskId;

    if (taskId) {
        // Update existing task
        const taskIndex = tasks.findIndex(t => t.id === taskId);
        if (taskIndex !== -1) {
            tasks[taskIndex] = { ...tasks[taskIndex], ...taskData };
        }
    } else {
        // Add new task
        const newTask = {
            id: 'task-' + Date.now(),
            ...taskData,
            volunteers: []
        };
        tasks.push(newTask);
    }

    saveTasks();
    updateAdminTasksList();
    updateTasksDisplay();
    closeTaskModal();

    showAlert('Task saved successfully!', 'success');
}

function editTask(taskId) {
    showTaskModal(taskId);
}

function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
        tasks = tasks.filter(t => t.id !== taskId);

        // Remove volunteers from this task
        volunteers = volunteers.filter(v => {
            const task = tasks.find(t => t.name === v.taskRole);
            return task !== undefined;
        });

        saveTasks();
        saveVolunteers();
        updateAdminTasksList();
        updateTasksDisplay();
        updateVolunteersDisplay();

        showAlert('Task deleted successfully!', 'success');
    }
}

// Volunteer removal
function removeVolunteer(volunteerId) {
    const volunteer = volunteers.find(v => v.id === volunteerId);
    if (!volunteer) return;

    // Show confirmation modal
    const modal = document.getElementById('delete-modal');
    const nameEl = document.getElementById('delete-volunteer-name');
    const roleEl = document.getElementById('delete-volunteer-role');

    if (nameEl) nameEl.textContent = volunteer.name;
    if (roleEl) roleEl.textContent = volunteer.taskRole;

    modal.style.display = 'block';
    modal.dataset.volunteerId = volunteerId;
}

function removeVolunteerAdmin(volunteerId) {
    removeVolunteer(volunteerId);
}

function closeDeleteModal() {
    const modal = document.getElementById('delete-modal');
    if (modal) {
        modal.style.display = 'none';
        delete modal.dataset.volunteerId;
    }
}

function confirmDelete() {
    if (!isVerified) {
        closeDeleteModal();
        showGateCodeModal();
        return;
    }

    const modal = document.getElementById('delete-modal');
    const volunteerId = modal.dataset.volunteerId;

    if (volunteerId) {
        const volunteer = volunteers.find(v => v.id === volunteerId);
        volunteers = volunteers.filter(v => v.id !== volunteerId);

        saveVolunteers();
        updateVolunteersDisplay();
        updateTasksDisplay();

        if (isAdminVerified) {
            updateAdminVolunteersList();
        }

        // Send notification email
        if (CONFIG.EMAIL_NOTIFICATIONS && volunteer) {
            sendOrganizerUpdate(volunteer, 'removed');
        }

        showAlert('Volunteer removed successfully.', 'success');
    }

    closeDeleteModal();
}

// Email functionality (simulated)
function sendThankYouEmail(volunteer) {
    console.log('📧 Sending thank you email to:', volunteer.email);

    // In a real implementation, this would make an API call to send actual emails
    const emailContent = {
        to: volunteer.email,
        subject: `Thank you for volunteering - ${currentEvent.name}`,
        html: `
            <h2>Thank You for Volunteering!</h2>
            <p>Dear ${volunteer.name},</p>
            <p>Thank you for signing up to help with <strong>${currentEvent.name}</strong>!</p>

            <h3>Event Details:</h3>
            <ul>
                <li><strong>Date:</strong> ${formatDate(currentEvent.date)}</li>
                <li><strong>Time:</strong> ${formatTime(currentEvent.startTime)} - ${formatTime(currentEvent.endTime)}</li>
                <li><strong>Your Task:</strong> ${volunteer.taskRole}</li>
            </ul>

            <p>${currentEvent.description}</p>

            <p>We'll send you more details closer to the event date. If you have any questions, please don't hesitate to reach out.</p>

            <p>Best regards,<br>The Event Organizing Team</p>
        `
    };

    // Simulate email sending
    setTimeout(() => {
        console.log('✅ Thank you email sent successfully');
    }, 1000);
}

function sendOrganizerUpdate(volunteer, action) {
    console.log('📧 Sending organizer update for:', action, volunteer.name);

    const actionText = action === 'new' ? 'signed up' : 'was removed';
    const totalVolunteers = volunteers.length;

    const emailContent = {
        to: currentEvent.organizerEmail,
        subject: `Volunteer Update - ${currentEvent.name}`,
        html: `
            <h2>Volunteer Update</h2>
            <p><strong>${volunteer.name}</strong> ${actionText} for ${currentEvent.name}</p>

            <h3>Volunteer Details:</h3>
            <ul>
                <li><strong>Name:</strong> ${volunteer.name}</li>
                <li><strong>Email:</strong> ${volunteer.email}</li>
                <li><strong>Phone:</strong> ${volunteer.phone || 'Not provided'}</li>
                <li><strong>Task:</strong> ${volunteer.taskRole}</li>
                ${volunteer.notes ? `<li><strong>Notes:</strong> ${volunteer.notes}</li>` : ''}
            </ul>

            <h3>Current Volunteer Count:</h3>
            <p><strong>Total Volunteers:</strong> ${totalVolunteers}</p>

            <h4>By Task:</h4>
            <ul>
                ${tasks.map(task => {
                    const count = volunteers.filter(v => v.taskRole === task.name).length;
                    return `<li>${task.name}: ${count}/${task.volunteersNeeded}</li>`;
                }).join('')}
            </ul>

            <p>You can manage volunteers at: <a href="${window.location.origin}/volunteer/admin.html">Admin Panel</a></p>
        `
    };

    // Simulate email sending
    setTimeout(() => {
        console.log('✅ Organizer update email sent successfully');
    }, 1000);
}

// Export functionality
function exportVolunteers() {
    const csvContent = generateVolunteerCSV();
    downloadCSV(csvContent, `volunteers-${currentEvent.name}-${new Date().toISOString().split('T')[0]}.csv`);
}

function generateVolunteerCSV() {
    const headers = ['Name', 'Email', 'Phone', 'Task', 'Notes', 'Signup Date'];
    const rows = volunteers.map(v => [
        v.name,
        v.email,
        v.phone || '',
        v.taskRole,
        v.notes || '',
        formatDateTime(v.signupDate)
    ]);

    const csvContent = [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n');

    return csvContent;
}

function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function printVolunteers() {
    const printContent = generateVolunteerPrintHTML();
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
}

function generateVolunteerPrintHTML() {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Volunteer List - ${currentEvent.name}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #1e40af; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f9fafb; }
                .task-group { margin-bottom: 30px; }
            </style>
        </head>
        <body>
            <h1>${currentEvent.name} - Volunteer List</h1>
            <p><strong>Date:</strong> ${formatDate(currentEvent.date)}</p>
            <p><strong>Time:</strong> ${formatTime(currentEvent.startTime)} - ${formatTime(currentEvent.endTime)}</p>
            <p><strong>Total Volunteers:</strong> ${volunteers.length}</p>

            ${tasks.map(task => {
                const taskVolunteers = volunteers.filter(v => v.taskRole === task.name);
                return `
                    <div class="task-group">
                        <h2>${task.name} (${taskVolunteers.length}/${task.volunteersNeeded})</h2>
                        ${taskVolunteers.length > 0 ? `
                            <table>
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Phone</th>
                                        <th>Notes</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${taskVolunteers.map(v => `
                                        <tr>
                                            <td>${v.name}</td>
                                            <td>${v.email}</td>
                                            <td>${v.phone || ''}</td>
                                            <td>${v.notes || ''}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        ` : '<p>No volunteers assigned yet.</p>'}
                    </div>
                `;
            }).join('')}

            <p style="margin-top: 40px; color: #666;">
                Generated on ${new Date().toLocaleString()}
            </p>
        </body>
        </html>
    `;
}

// Utility functions
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatTime(timeString) {
    return new Date('2000-01-01 ' + timeString).toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

function formatDateTime(isoString) {
    return new Date(isoString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

// Modal helpers
function showSuccessModal() {
    const modal = document.getElementById('success-modal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeModal() {
    const modal = document.getElementById('success-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function showError(message) {
    const modal = document.getElementById('error-modal');
    const messageEl = document.getElementById('error-message');

    if (messageEl) messageEl.textContent = message;
    if (modal) modal.style.display = 'block';
}

function closeErrorModal() {
    const modal = document.getElementById('error-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function showAlert(message, type = 'info') {
    // Simple alert for now - could be enhanced with custom modal
    alert(message);
}

// Click outside modal to close
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        // Close any open modals
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
            }
        });
    }
});

console.log('✅ Club Work Hours Volunteer Management System loaded successfully');