// Volunteer Management System - Complete Client-Side Implementation
// Admin Password: 7591, Gate Code: 1957

class VolunteerManager {
    constructor() {
        this.adminPassword = '7591';
        this.gateCode = '1957';
        this.events = this.loadEvents();
        this.volunteers = this.loadVolunteers();
        this.init();
    }

    init() {
        // Initialize based on current page
        if (window.location.pathname.includes('admin.html')) {
            this.initAdminPanel();
        } else {
            this.initMainPage();
        }
    }

    // Data Management
    loadEvents() {
        return JSON.parse(localStorage.getItem('volunteer_events') || '[]');
    }

    saveEvents() {
        localStorage.setItem('volunteer_events', JSON.stringify(this.events));
    }

    loadVolunteers() {
        return JSON.parse(localStorage.getItem('volunteer_volunteers') || '{}');
    }

    saveVolunteers() {
        localStorage.setItem('volunteer_volunteers', JSON.stringify(this.volunteers));
    }

    // Main Page Functionality
    initMainPage() {
        this.loadMainPageEvents();
    }

    loadMainPageEvents() {
        const container = document.getElementById('events-container');
        if (!container) return;

        if (this.events.length === 0) {
            container.innerHTML = `
                <div class="no-events">
                    <i class="fas fa-calendar-times"></i>
                    <h3>No Events Available</h3>
                    <p>There are currently no volunteer events scheduled. Check back soon!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.events.map(event => `
            <div class="event-card" onclick="window.open('${event.eventSlug}/', '_self')">
                ${event.imageUrl ? `<img src="${event.imageUrl}" alt="${event.eventName}" class="event-image">` : ''}
                <div class="event-title">${event.eventName}</div>
                <div class="event-date">
                    <i class="fas fa-calendar"></i> 
                    ${this.formatDate(event.eventDate)} • ${this.formatTime(event.startTime)} - ${this.formatTime(event.endTime)}
                </div>
                <div class="event-description">${event.description}</div>
                <div class="volunteer-count">
                    <i class="fas fa-users"></i> 
                    ${this.getEventVolunteerCount(event.eventSlug)} / ${this.getEventTotalNeeded(event)} volunteers signed up
                </div>
            </div>
        `).join('');
    }

    getEventVolunteerCount(eventSlug) {
        const eventVolunteers = this.volunteers[eventSlug] || [];
        return eventVolunteers.length;
    }

    getEventTotalNeeded(event) {
        return event.tasks.reduce((total, task) => total + task.needed, 0);
    }

    // Admin Panel Functionality
    initAdminPanel() {
        this.setupAdminLogin();
        this.setupAdminNavigation();
        this.setupEventCreation();
    }

    setupAdminLogin() {
        const loginBtn = document.getElementById('login-btn');
        const passwordInput = document.getElementById('admin-password');
        const loginScreen = document.getElementById('login-screen');
        const adminPanel = document.getElementById('admin-panel');
        const errorDiv = document.getElementById('password-error');

        if (!loginBtn || !passwordInput) return;

        const checkPassword = () => {
            const password = passwordInput.value;
            if (password === this.adminPassword) {
                loginScreen.style.display = 'none';
                adminPanel.style.display = 'block';
                this.loadExistingEvents();
            } else {
                errorDiv.style.display = 'flex';
                passwordInput.value = '';
                passwordInput.focus();
            }
        };

        loginBtn.addEventListener('click', checkPassword);
        passwordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') checkPassword();
        });

        // Hide error on input
        passwordInput.addEventListener('input', () => {
            errorDiv.style.display = 'none';
        });
    }

    setupAdminNavigation() {
        const createBtn = document.getElementById('create-event-btn');
        const manageBtn = document.getElementById('manage-events-btn');
        const createSection = document.getElementById('create-event-section');
        const manageSection = document.getElementById('manage-events-section');

        if (!createBtn || !manageBtn) return;

        createBtn.addEventListener('click', () => {
            createBtn.classList.add('active');
            manageBtn.classList.remove('active');
            createSection.style.display = 'block';
            manageSection.style.display = 'none';
        });

        manageBtn.addEventListener('click', () => {
            manageBtn.classList.add('active');
            createBtn.classList.remove('active');
            manageSection.style.display = 'block';
            createSection.style.display = 'none';
            this.loadExistingEvents();
        });
    }

    setupEventCreation() {
        const form = document.getElementById('create-event-form');
        const addTaskBtn = document.getElementById('add-task-btn');
        const tasksContainer = document.getElementById('tasks-container');

        if (!form) return;

        // Auto-generate slug from event name
        const eventNameInput = document.getElementById('event-name');
        const eventSlugInput = document.getElementById('event-slug');

        if (eventNameInput && eventSlugInput) {
            eventNameInput.addEventListener('input', () => {
                const slug = eventNameInput.value
                    .toLowerCase()
                    .replace(/[^a-z0-9\s-]/g, '')
                    .replace(/\s+/g, '-')
                    .replace(/-+/g, '-')
                    .trim();
                eventSlugInput.value = slug;
            });
        }

        // Add task functionality
        if (addTaskBtn && tasksContainer) {
            addTaskBtn.addEventListener('click', () => {
                this.addTaskItem(tasksContainer);
            });

            // Setup remove task buttons for existing tasks
            this.setupRemoveTaskButtons(tasksContainer);
        }

        // Form submission
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createEvent(form);
        });
    }

    addTaskItem(container) {
        const taskItem = document.createElement('div');
        taskItem.className = 'task-item';
        taskItem.innerHTML = `
            <input type="text" placeholder="Task name (e.g., Set up tables)" class="task-name" required>
            <input type="number" placeholder="# needed" class="task-count" min="1" max="50" required>
            <button type="button" class="btn-remove-task">Remove</button>
        `;
        container.appendChild(taskItem);
        this.setupRemoveTaskButtons(container);
    }

    setupRemoveTaskButtons(container) {
        container.querySelectorAll('.btn-remove-task').forEach(btn => {
            btn.onclick = () => {
                if (container.children.length > 1) {
                    btn.parentElement.remove();
                }
            };
        });
    }

    createEvent(form) {
        const formData = new FormData(form);

        // Collect tasks
        const taskItems = document.querySelectorAll('.task-item');
        const tasks = [];

        taskItems.forEach((item, index) => {
            const name = item.querySelector('.task-name').value.trim();
            const needed = parseInt(item.querySelector('.task-count').value);

            if (name && needed > 0) {
                tasks.push({
                    id: index + 1,
                    name,
                    needed,
                    volunteers: []
                });
            }
        });

        if (tasks.length === 0) {
            alert('Please add at least one task.');
            return;
        }

        const event = {
            eventSlug: document.getElementById('event-slug').value.trim(),
            eventName: document.getElementById('event-name').value.trim(),
            eventDate: document.getElementById('event-date').value,
            startTime: document.getElementById('start-time').value,
            endTime: document.getElementById('end-time').value,
            description: document.getElementById('event-description').value.trim(),
            imageUrl: document.getElementById('event-image').value.trim(),
            organizerEmail: document.getElementById('organizer-email').value.trim(),
            tasks,
            createdAt: new Date().toISOString()
        };

        // Check for duplicate slug
        if (this.events.find(e => e.eventSlug === event.eventSlug)) {
            alert('Event URL slug already exists. Please choose a different one.');
            return;
        }

        this.events.push(event);
        this.saveEvents();

        // Create event page
        this.createEventPage(event);

        // Show success message
        this.showSuccessMessage('Event created successfully! Event page is now available.');

        // Reset form
        form.reset();
        document.getElementById('tasks-container').innerHTML = `
            <div class="task-item">
                <input type="text" placeholder="Task name (e.g., Set up tables)" class="task-name">
                <input type="number" placeholder="# needed" class="task-count" min="1" max="50">
                <button type="button" class="btn-remove-task">Remove</button>
            </div>
        `;
        this.setupRemoveTaskButtons(document.getElementById('tasks-container'));
    }

    createEventPage(event) {
        // This would create the individual event signup page
        // For now, we'll simulate this with localStorage data
        console.log(`Event page created: /volunteer/${event.eventSlug}/`);
    }

    loadExistingEvents() {
        const container = document.getElementById('existing-events-container');
        if (!container) return;

        if (this.events.length === 0) {
            container.innerHTML = `
                <div class="no-events">
                    <i class="fas fa-calendar-times"></i>
                    <h3>No Events Created</h3>
                    <p>Create your first event to get started.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.events.map(event => `
            <div class="event-card">
                ${event.imageUrl ? `<img src="${event.imageUrl}" alt="${event.eventName}" class="event-image">` : ''}
                <div class="event-title">${event.eventName}</div>
                <div class="event-date">
                    <i class="fas fa-calendar"></i> 
                    ${this.formatDate(event.eventDate)} • ${this.formatTime(event.startTime)} - ${this.formatTime(event.endTime)}
                </div>
                <div class="event-description">${event.description}</div>
                <div class="volunteer-count">
                    <i class="fas fa-users"></i> 
                    ${this.getEventVolunteerCount(event.eventSlug)} / ${this.getEventTotalNeeded(event)} volunteers
                </div>
                <div style="margin-top: 1rem;">
                    <button class="btn btn-primary" onclick="window.open('../${event.eventSlug}/', '_blank')">
                        <i class="fas fa-eye"></i> View Event Page
                    </button>
                    <button class="btn btn-secondary" onclick="volunteerManager.deleteEvent('${event.eventSlug}')">
                        <i class="fas fa-trash"></i> Delete Event
                    </button>
                </div>
            </div>
        `).join('');
    }

    deleteEvent(eventSlug) {
        if (confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
            this.events = this.events.filter(e => e.eventSlug !== eventSlug);
            delete this.volunteers[eventSlug];
            this.saveEvents();
            this.saveVolunteers();
            this.loadExistingEvents();
            this.showSuccessMessage('Event deleted successfully.');
        }
    }

    // Utility Functions
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }

    formatTime(timeStr) {
        const time = new Date(`2000-01-01T${timeStr}`);
        return time.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
    }

    showSuccessMessage(message) {
        // Remove existing success messages
        const existing = document.querySelector('.success-message');
        if (existing) existing.remove();

        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = `
            <i class="fas fa-check-circle"></i>
            ${message}
        `;

        const adminSection = document.querySelector('.admin-section');
        if (adminSection) {
            adminSection.insertBefore(successDiv, adminSection.firstChild);
        }

        // Remove after 5 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.remove();
            }
        }, 5000);
    }

    // Simulate email notifications
    sendEmail(type, data) {
        console.log(`📧 Email sent (${type}):`, data);

        if (type === 'volunteer_signup') {
            console.log(`✅ Thank you email sent to ${data.email}`);
        } else if (type === 'organizer_update') {
            console.log(`📊 Organizer roster update sent to ${data.organizerEmail}`);
        }
    }
}

// Individual Event Page Functionality
class EventPageManager {
    constructor(eventSlug) {
        this.eventSlug = eventSlug;
        this.gateCode = '1957';
        this.volunteerManager = new VolunteerManager();
        this.event = this.volunteerManager.events.find(e => e.eventSlug === eventSlug);

        if (this.event) {
            this.volunteers = this.volunteerManager.volunteers[eventSlug] || [];
            this.initEventPage();
        } else {
            this.show404();
        }
    }

    initEventPage() {
        this.renderEventPage();
        this.setupVolunteerSignup();
    }

    renderEventPage() {
        document.title = `${this.event.eventName} | Volunteer Signup`;

        const container = document.querySelector('.container') || document.body;
        container.innerHTML = `
            <header class="header">
                <div class="header-content">
                    <i class="fas fa-hands-helping header-icon"></i>
                    <h1>${this.event.eventName}</h1>
                    <p class="subtitle">Join us and make a difference!</p>
                </div>
            </header>

            ${this.event.imageUrl ? `
                <div style="text-align: center; margin-bottom: 2rem;">
                    <img src="${this.event.imageUrl}" alt="${this.event.eventName}" class="event-image" style="max-width: 100%; height: 300px; object-fit: cover; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                </div>
            ` : ''}

            <section class="events-section">
                <h2><i class="fas fa-info-circle"></i> Event Details</h2>
                <div class="event-details">
                    <p><strong>Date:</strong> ${this.volunteerManager.formatDate(this.event.eventDate)}</p>
                    <p><strong>Time:</strong> ${this.volunteerManager.formatTime(this.event.startTime)} - ${this.volunteerManager.formatTime(this.event.endTime)}</p>
                    <p><strong>Description:</strong> ${this.event.description}</p>
                </div>
            </section>

            <section class="events-section">
                <h2><i class="fas fa-users"></i> Current Volunteers</h2>
                <div id="current-volunteers"></div>
            </section>

            <section class="events-section">
                <h2><i class="fas fa-hand-paper"></i> Volunteer Signup</h2>
                <div id="volunteer-form-container"></div>
            </section>

            <footer class="footer">
                <p>Thank you for volunteering! 🤝</p>
                <p><a href="../">View All Events</a></p>
            </footer>
        `;

        this.renderCurrentVolunteers();
        this.renderVolunteerForm();
    }

    renderCurrentVolunteers() {
        const container = document.getElementById('current-volunteers');
        if (!container) return;

        if (this.volunteers.length === 0) {
            container.innerHTML = `
                <div class="no-events">
                    <i class="fas fa-user-plus"></i>
                    <h3>Be the First to Volunteer!</h3>
                    <p>No one has signed up yet. Be the first to join this event!</p>
                </div>
            `;
            return;
        }

        // Group volunteers by task
        const volunteersByTask = {};
        this.volunteers.forEach(volunteer => {
            if (!volunteersByTask[volunteer.taskId]) {
                volunteersByTask[volunteer.taskId] = [];
            }
            volunteersByTask[volunteer.taskId].push(volunteer);
        });

        container.innerHTML = this.event.tasks.map(task => {
            const taskVolunteers = volunteersByTask[task.id] || [];
            const remaining = Math.max(0, task.needed - taskVolunteers.length);

            return `
                <div class="event-card">
                    <div class="event-title">${task.name}</div>
                    <div class="volunteer-count">
                        ${taskVolunteers.length} / ${task.needed} volunteers signed up
                        ${remaining > 0 ? `<span style="color: #e53e3e;"> (${remaining} more needed)</span>` : '<span style="color: #38a169;"> (Complete!)</span>'}
                    </div>
                    ${taskVolunteers.length > 0 ? `
                        <div style="margin-top: 1rem;">
                            <strong>Volunteers:</strong>
                            <ul style="margin-left: 1rem; margin-top: 0.5rem;">
                                ${taskVolunteers.map(v => `<li>${v.name} ${v.phone ? `(${v.phone})` : ''}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    }

    renderVolunteerForm() {
        const container = document.getElementById('volunteer-form-container');
        if (!container) return;

        // Check if any tasks still need volunteers
        const availableTasks = this.event.tasks.filter(task => {
            const taskVolunteers = this.volunteers.filter(v => v.taskId === task.id);
            return taskVolunteers.length < task.needed;
        });

        if (availableTasks.length === 0) {
            container.innerHTML = `
                <div class="no-events">
                    <i class="fas fa-check-circle"></i>
                    <h3>All Positions Filled!</h3>
                    <p>Thank you for your interest! All volunteer positions for this event have been filled.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <form id="volunteer-signup-form" class="admin-form">
                <div class="form-row">
                    <div class="form-group">
                        <label for="volunteer-name">Your Name *</label>
                        <input type="text" id="volunteer-name" required>
                    </div>
                    <div class="form-group">
                        <label for="volunteer-email">Email Address *</label>
                        <input type="email" id="volunteer-email" required>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="volunteer-phone">Phone Number (optional)</label>
                        <input type="tel" id="volunteer-phone">
                    </div>
                    <div class="form-group">
                        <label for="volunteer-task">Choose Your Task *</label>
                        <select id="volunteer-task" required>
                            <option value="">Select a task...</option>
                            ${availableTasks.map(task => {
                                const taskVolunteers = this.volunteers.filter(v => v.taskId === task.id);
                                const remaining = task.needed - taskVolunteers.length;
                                return `<option value="${task.id}">${task.name} (${remaining} needed)</option>`;
                            }).join('')}
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label for="volunteer-notes">Notes (optional)</label>
                    <textarea id="volunteer-notes" rows="2" placeholder="Any special requests or notes..."></textarea>
                </div>
                <div class="form-group">
                    <label for="gate-code">Club Gate Code *</label>
                    <input type="password" id="gate-code" maxlength="4" required>
                    <div id="gate-code-error" class="error-message" style="display: none;">
                        <i class="fas fa-exclamation-triangle"></i>
                        Incorrect gate code. Please try again.
                    </div>
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-check"></i>
                    Sign Me Up!
                </button>
            </form>
        `;
    }

    setupVolunteerSignup() {
        const form = document.getElementById('volunteer-signup-form');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.processSignup(form);
        });

        // Hide gate code error on input
        const gateCodeInput = document.getElementById('gate-code');
        const errorDiv = document.getElementById('gate-code-error');

        if (gateCodeInput && errorDiv) {
            gateCodeInput.addEventListener('input', () => {
                errorDiv.style.display = 'none';
            });
        }
    }

    processSignup(form) {
        const gateCode = document.getElementById('gate-code').value;
        const errorDiv = document.getElementById('gate-code-error');

        if (gateCode !== this.gateCode) {
            errorDiv.style.display = 'flex';
            document.getElementById('gate-code').focus();
            return;
        }

        const volunteer = {
            id: Date.now().toString(),
            name: document.getElementById('volunteer-name').value.trim(),
            email: document.getElementById('volunteer-email').value.trim(),
            phone: document.getElementById('volunteer-phone').value.trim(),
            taskId: parseInt(document.getElementById('volunteer-task').value),
            notes: document.getElementById('volunteer-notes').value.trim(),
            signupDate: new Date().toISOString()
        };

        // Add to volunteers list
        if (!this.volunteerManager.volunteers[this.eventSlug]) {
            this.volunteerManager.volunteers[this.eventSlug] = [];
        }
        this.volunteerManager.volunteers[this.eventSlug].push(volunteer);
        this.volunteerManager.saveVolunteers();

        // Update local volunteers array
        this.volunteers = this.volunteerManager.volunteers[this.eventSlug];

        // Send emails
        this.volunteerManager.sendEmail('volunteer_signup', {
            email: volunteer.email,
            name: volunteer.name,
            eventName: this.event.eventName,
            taskName: this.event.tasks.find(t => t.id === volunteer.taskId).name
        });

        this.volunteerManager.sendEmail('organizer_update', {
            organizerEmail: this.event.organizerEmail,
            eventName: this.event.eventName,
            volunteerCount: this.volunteers.length,
            newVolunteer: volunteer
        });

        // Show success and refresh
        alert('Thank you for signing up! You will receive a confirmation email shortly.');

        // Refresh the page displays
        this.renderCurrentVolunteers();
        this.renderVolunteerForm();
    }

    show404() {
        document.body.innerHTML = `
            <div class="container">
                <div class="events-section" style="text-align: center;">
                    <h1><i class="fas fa-exclamation-triangle"></i> Event Not Found</h1>
                    <p>The event you're looking for doesn't exist or has been removed.</p>
                    <a href="../" class="btn btn-primary">
                        <i class="fas fa-arrow-left"></i>
                        Back to Events
                    </a>
                </div>
            </div>
        `;
    }
}

// Initialize the appropriate manager based on the current page
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.includes('/volunteer/') && path !== '/volunteer/' && !path.includes('admin.html')) {
        // Individual event page
        const pathParts = path.split('/');
        const eventSlug = pathParts[pathParts.length - 2] || pathParts[pathParts.length - 1];
        if (eventSlug && eventSlug !== 'volunteer') {
            new EventPageManager(eventSlug);
            return;
        }
    }

    // Main page or admin page
    window.volunteerManager = new VolunteerManager();
});