# Club Work Hours Volunteer Management System

A comprehensive volunteer management system for club work hour events with automated email notifications and secure access controls.

## 🚀 Live System

**Main Volunteer Signup**: `https://hvscma.com/volunteer/`
**Admin Panel**: `https://hvscma.com/volunteer/admin.html`

## 🔐 Access Credentials

- **Volunteer Gate Code**: `1957` (required for signups and removals)
- **Admin Password**: `5791` (access to organizer panel - no hints provided)

## ✨ Features

### **For Volunteers**
- **Event Overview**: Clear display of event details and purpose
- **Current Participants**: See who's already signed up for each task
- **Easy Signup**: Streamlined form with gate code validation
- **Task Availability**: Real-time display of available volunteer spots
- **Thank You Emails**: Automatic confirmation with event details
- **Secure Removal**: Gate code required to remove signups

### **For Organizers**
- **Password Protection**: Secure admin access (password: 5791)
- **Event Configuration**: Set event name, date, time, and description
- **Task Management**: Add, edit, and delete volunteer tasks
- **Volunteer Tracking**: View all signups with contact details
- **Email Notifications**: Automatic roster updates after each signup
- **Export Tools**: Generate CSV and printable volunteer lists
- **Real-time Updates**: Live progress tracking by task

## 🏗️ System Architecture

### **Frontend**
- **HTML5**: Semantic markup with accessibility features
- **CSS3**: Responsive design with professional styling
- **Vanilla JavaScript**: No dependencies, lightweight and fast
- **Local Storage**: Client-side data persistence

### **Security Features**
- **Gate Code Validation**: Prevents unauthorized volunteer signups
- **Admin Password Protection**: Secures organizer tools
- **Input Validation**: Prevents malicious data entry
- **Two-Step Deletion**: Confirms volunteer removal actions

### **Email System** (Ready for Integration)
- **Thank You Emails**: Sent to volunteers upon signup
- **Organizer Updates**: Complete roster sent after each change
- **HTML Templates**: Professional email formatting
- **SMTP Configuration**: Ready for email provider setup

## 📋 Default Tasks

The system comes pre-configured with common club work tasks:

1. **Landscaping & Grounds** - Weeding, planting, lawn maintenance (4 volunteers)
2. **Building Maintenance** - Painting, repairs, cleaning (3 volunteers)
3. **Dock & Marina** - Dock repairs, marina cleanup (3 volunteers)
4. **General Cleanup** - Trash pickup, organizing storage (2 volunteers)

## 🎯 Usage Instructions

### **For Members (Volunteers)**
1. Visit the main signup page
2. Review event details and current volunteers
3. Complete the signup form
4. Enter gate code `1957` when prompted
5. Receive confirmation email with event details

### **For Organizers**
1. Access admin panel at `/admin.html`
2. Enter password `5791`
3. Configure event details and tasks
4. Monitor volunteer signups in real-time
5. Use export tools for planning and communication

## 🔧 Technical Details

### **File Structure**
```
volunteer/
├── index.html          # Main volunteer signup page
├── admin.html          # Password-protected organizer panel
├── style.css           # Complete responsive styling
├── script.js           # All functionality and logic
└── data/
    ├── events.json     # Event configuration data
    └── volunteers.json # Volunteer signup data
```

### **Browser Compatibility**
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 80+

### **Mobile Responsive**
- Touch-friendly interface
- Optimized for tablets and smartphones
- Progressive web app capabilities

## 📧 Email Configuration (Optional)

To enable automated emails, configure SMTP settings in the admin panel:

```javascript
// Example Gmail configuration
SMTP_HOST: smtp.gmail.com
SMTP_PORT: 587
SMTP_USER: your-email@gmail.com
SMTP_PASS: your-app-password
```

## 🔄 Data Management

### **Automatic Saving**
- All data saved to browser localStorage
- No server-side database required
- Cross-session persistence

### **Export Options**
- CSV export for spreadsheet analysis
- Printable HTML reports
- Real-time volunteer rosters

## 🎨 Customization

### **Branding**
- Update club name in header
- Modify color scheme in CSS variables
- Replace contact information

### **Tasks**
- Add/edit/delete tasks through admin panel
- Customize volunteer requirements
- Set task categories and descriptions

## 🔒 Security Considerations

- Gate codes stored in JavaScript (consider server-side validation for production)
- Admin password protection (consider session management for production)
- Input sanitization for XSS prevention
- HTTPS recommended for production deployment

## 📞 Support

For technical issues or customization requests, contact the system administrator.

## 📄 License

This volunteer management system is provided for club use. Modify and distribute as needed for your organization.

---

**Last Updated**: August 2024
**Version**: 1.0.0
**Deployed**: https://hvscma.com/volunteer/