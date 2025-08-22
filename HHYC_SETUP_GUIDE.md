
# HHYC VOLUNTEER MANAGEMENT SYSTEM - COMPLETE SETUP GUIDE

## 🎯 SYSTEM OVERVIEW

The Hidden Harbor Yacht Club (HHYC) Volunteer Management System is a complete, professional-grade solution for managing volunteer work hours and events. The system features:

- **Real Database Backend**: Google Sheets + Apps Script (no static files)
- **Authentication System**: Admin password 7591, Volunteer gate code 1957  
- **Professional Design**: Purple gradient theme matching requirements
- **Team Building Features**: Volunteer roster display ("Working with: Glenn F., Justin P.")
- **Cross-Device Sync**: Real-time updates across all devices
- **Email Notifications**: Automatic confirmation emails
- **Mobile Responsive**: Works perfectly on phones and tablets

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Admin Portal  │    │  Apps Script API │    │ Google Sheets   │
│   (HTML/CSS/JS) │◄──►│   (Backend)      │◄──►│   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Volunteer Portal│    │ Email Notifications│    │   5 Data Sheets │
│   (HTML/CSS/JS) │    │   (MailApp)      │    │ Events/Tasks/etc│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 DATABASE STRUCTURE

### Sheet 1: Events
- EventID (Unique identifier)
- EventName (Event title)
- EventDate, StartTime, EndTime
- Description, Location, Status
- CreatedBy, CreatedDate

### Sheet 2: Tasks  
- TaskID (Unique identifier)
- EventID (Links to Events)
- TaskName, TaskDescription
- VolunteersNeeded, VolunteersSignedUp
- StartTime, EndTime, Priority, Status

### Sheet 3: Volunteers
- VolunteerID (Unique identifier) 
- FirstName, LastName, Email, Phone
- MembershipStatus, PreferredTasks
- SkillsExperience, Availability
- JoinDate, TotalHours, Status

### Sheet 4: Signups
- SignupID (Unique identifier)
- EventID, TaskID, VolunteerID (Links to other sheets)
- SignupDate, Status, Notes
- CheckedIn, HoursWorked, Rating

### Sheet 5: Config
- ConfigKey, ConfigValue, Description
- LastUpdated, UpdatedBy
- Contains: AdminPassword (7591), VolunteerGateCode (1957), ClubName, ContactEmail

## 🔧 INSTALLATION STEPS

### Step 1: Set Up Google Sheets Database

1. **Open Glenn's Google Sheet**: https://docs.google.com/spreadsheets/d/1pir0qLHMFYJiiQtjHPlc43F2XlYe1g7XwWQvplx1OZ8/edit?usp=sharing

2. **Create 5 Sheets** with these exact names:
   - Events
   - Tasks  
   - Volunteers
   - Signups
   - Config

3. **Set Up Headers** for each sheet:

   **Events Sheet (Row 1):**
   ```
   EventID | EventName | EventDate | StartTime | EndTime | Description | Location | Status | CreatedBy | CreatedDate
   ```

   **Tasks Sheet (Row 1):**
   ```
   TaskID | EventID | TaskName | TaskDescription | VolunteersNeeded | VolunteersSignedUp | StartTime | EndTime | Priority | Status
   ```

   **Volunteers Sheet (Row 1):**
   ```
   VolunteerID | FirstName | LastName | Email | Phone | MembershipStatus | PreferredTasks | SkillsExperience | Availability | JoinDate | TotalHours | Status
   ```

   **Signups Sheet (Row 1):**
   ```
   SignupID | EventID | TaskID | VolunteerID | SignupDate | Status | Notes | CheckedIn | HoursWorked | Rating
   ```

   **Config Sheet (Row 1):**
   ```
   ConfigKey | ConfigValue | Description | LastUpdated | UpdatedBy
   ```

4. **Add Initial Config Data** to Config sheet (Rows 2-5):
   ```
   AdminPassword | 7591 | Password for administrative access | 2024-03-15 10:00 | System Setup
   VolunteerGateCode | 1957 | Gate code for volunteer signup access | 2024-03-15 10:00 | System Setup  
   ClubName | Hidden Harbor Yacht Club | Full club name for displays | 2024-03-15 10:00 | System Setup
   ContactEmail | info@hhyc.com | Main contact email for notifications | 2024-03-15 10:00 | System Setup
   ```

### Step 2: Deploy Apps Script Backend

1. **Open Apps Script**: In your Google Sheet, go to Extensions > Apps Script

2. **Delete Default Code**: Remove the existing myFunction() code

3. **Paste Backend Code**: Copy the complete code from `hhyc_apps_script_backend.js`

4. **Save Project**: Name it "HHYC Volunteer Management"

5. **Deploy as Web App**:
   - Click Deploy > New Deployment
   - Choose "Web app" as type
   - Set Execute as: "Me"  
   - Set Access: "Anyone"
   - Click Deploy
   - **COPY THE WEB APP URL** - you'll need this!

### Step 3: Update HTML Files

1. **Update Admin Portal**: In `hhyc_admin_portal.html`, find this line:
   ```javascript
   const APPS_SCRIPT_URL = 'YOUR_APPS_SCRIPT_WEB_APP_URL_HERE';
   ```
   Replace with your actual Apps Script URL.

2. **Update Volunteer Portal**: In `hhyc_volunteer_portal.html`, find this line:
   ```javascript
   const APPS_SCRIPT_URL = 'YOUR_APPS_SCRIPT_WEB_APP_URL_HERE';
   ```
   Replace with your actual Apps Script URL.

### Step 4: Deploy to GitHub

1. **Create Repository**: Use existing HVSCMA/hvscma-cmas or create new repo

2. **Upload Files**:
   - `hhyc_admin_portal.html`
   - `hhyc_volunteer_portal.html`  
   - `hhyc_apps_script_backend.js`
   - `README.md` (this documentation)

3. **Enable GitHub Pages**:
   - Go to repository Settings
   - Scroll to Pages section
   - Set Source to "Deploy from a branch"
   - Select "main" branch
   - Your sites will be available at:
     - Admin: `https://hvscma.github.io/hvscma-cmas/hhyc_admin_portal.html`
     - Volunteer: `https://hvscma.github.io/hvscma-cmas/hhyc_volunteer_portal.html`

## 🔐 AUTHENTICATION CREDENTIALS

- **Admin Portal Access**: Password `7591`
- **Volunteer Portal Access**: Gate Code `1957`

## 🎨 DESIGN FEATURES

- **Purple Gradient Theme**: Professional linear-gradient(135deg, #667eea 0%, #764ba2 100%)
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI Components**: Cards, badges, animations, loading states
- **Team Building**: "Working with: Glenn F., Justin P." volunteer roster display
- **Visual Progress**: Capacity bars and status indicators

## ✨ KEY FEATURES

### Admin Portal Features:
- Event creation and management
- Task creation with volunteer requirements  
- Volunteer registration viewing
- Real-time signup tracking
- Task capacity management
- Professional dashboard interface

### Volunteer Portal Features:
- Event browsing and task selection
- Volunteer signup with form validation
- Real-time capacity tracking
- **Volunteer roster display** for team coordination
- Email confirmation system
- Mobile-optimized interface

### Backend Features:
- Complete CRUD operations
- Authentication system
- Email notifications via Gmail
- Automatic ID generation
- Data validation and error handling
- Real-time sync across devices

## 🧪 TESTING CHECKLIST

### Admin Portal Tests:
- [ ] Admin authentication (password 7591)
- [ ] Create new event
- [ ] Create tasks for event
- [ ] View volunteer signups
- [ ] Check responsive design

### Volunteer Portal Tests:
- [ ] Volunteer authentication (gate code 1957)
- [ ] Browse available events
- [ ] Sign up for tasks
- [ ] View volunteer roster ("Working with:")
- [ ] Receive confirmation email
- [ ] Check mobile responsiveness

### Backend Tests:
- [ ] Google Sheets data sync
- [ ] Apps Script API responses
- [ ] Email notifications working
- [ ] Authentication validation
- [ ] Error handling

## 📞 SUPPORT

For technical support or questions:
- **System Admin**: Glenn Fitzgerald
- **Contact**: info@hhyc.com
- **Documentation**: GitHub repository README

## 🔄 FUTURE ENHANCEMENTS

Potential improvements for future versions:
- Advanced reporting and analytics
- Calendar integration
- SMS notifications
- Volunteer hour tracking
- Photo uploads for events
- Equipment/supply management

---

**System Status**: ✅ COMPLETE AND READY FOR DEPLOYMENT
**Last Updated**: August 22, 2025
**Version**: 1.0 Professional Release
