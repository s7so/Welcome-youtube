// Atlas - Main JavaScript Application
// Modern, interactive frontend with Alpine.js

// Global Alpine.js data and functions
document.addEventListener('alpine:init', () => {
    Alpine.data('atlasApp', () => ({
        // App state
        darkMode: localStorage.getItem('darkMode') === 'true',
        sidebarOpen: false,
        notifications: [],
        loading: false,
        currentUser: null,

        // Initialize app
        init() {
            this.setupDarkMode();
            this.setupNotifications();
            this.loadCurrentUser();
            this.setupAutoRefresh();
        },

        // Dark mode toggle
        toggleDarkMode() {
            this.darkMode = !this.darkMode;
            localStorage.setItem('darkMode', this.darkMode);
            document.documentElement.classList.toggle('dark', this.darkMode);
        },

        setupDarkMode() {
            document.documentElement.classList.toggle('dark', this.darkMode);
        },

        // Sidebar toggle
        toggleSidebar() {
            this.sidebarOpen = !this.sidebarOpen;
        },

        // Notification system
        showNotification(message, type = 'success', duration = 5000) {
            const notification = {
                id: Date.now(),
                message,
                type,
                visible: true
            };
            
            this.notifications.push(notification);
            
            setTimeout(() => {
                this.hideNotification(notification.id);
            }, duration);
        },

        hideNotification(id) {
            const index = this.notifications.findIndex(n => n.id === id);
            if (index > -1) {
                this.notifications[index].visible = false;
                setTimeout(() => {
                    this.notifications.splice(index, 1);
                }, 300);
            }
        },

        setupNotifications() {
            // Listen for custom events
            window.addEventListener('show-notification', (e) => {
                this.showNotification(e.detail.message, e.detail.type, e.detail.duration);
            });
        },

        // Load current user
        async loadCurrentUser() {
            try {
                const response = await fetch('/api/auth/user/');
                if (response.ok) {
                    this.currentUser = await response.json();
                }
            } catch (error) {
                console.error('Error loading user:', error);
            }
        },

        // Auto refresh data
        setupAutoRefresh() {
            // Refresh dashboard data every 30 seconds
            setInterval(() => {
                this.refreshDashboardData();
            }, 30000);
        },

        async refreshDashboardData() {
            // Trigger refresh events for dashboard components
            window.dispatchEvent(new CustomEvent('refresh-dashboard'));
        },

        // Loading state
        setLoading(loading) {
            this.loading = loading;
        },

        // Format numbers
        formatNumber(num) {
            return new Intl.NumberFormat('ar-SA').format(num);
        },

        // Format dates
        formatDate(date) {
            return new Intl.DateTimeFormat('ar-SA', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).format(new Date(date));
        },

        // Format time
        formatTime(time) {
            return new Intl.DateTimeFormat('ar-SA', {
                hour: '2-digit',
                minute: '2-digit'
            }).format(new Date(time));
        }
    }));

    // Dashboard component
    Alpine.data('dashboard', () => ({
        stats: {
            totalEmployees: 0,
            activeEmployees: 0,
            presentToday: 0,
            absentToday: 0
        },
        recentActivity: [],
        loading: true,

        init() {
            this.loadDashboardData();
            this.setupRefresh();
        },

        setupRefresh() {
            window.addEventListener('refresh-dashboard', () => {
                this.loadDashboardData();
            });
        },

        async loadDashboardData() {
            try {
                this.loading = true;
                await Promise.all([
                    this.loadStats(),
                    this.loadRecentActivity()
                ]);
            } catch (error) {
                console.error('Error loading dashboard data:', error);
            } finally {
                this.loading = false;
            }
        },

        async loadStats() {
            try {
                const response = await fetch('/api/dashboard/stats/');
                if (response.ok) {
                    this.stats = await response.json();
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        },

        async loadRecentActivity() {
            try {
                const response = await fetch('/api/dashboard/recent-activity/');
                if (response.ok) {
                    this.recentActivity = await response.json();
                }
            } catch (error) {
                console.error('Error loading recent activity:', error);
            }
        }
    }));

    // Employee management component
    Alpine.data('employeeManager', () => ({
        employees: [],
        departments: [],
        loading: false,
        searchTerm: '',
        selectedDepartment: '',
        showAddModal: false,
        editingEmployee: null,

        init() {
            this.loadEmployees();
            this.loadDepartments();
        },

        async loadEmployees() {
            try {
                this.loading = true;
                const response = await fetch('/api/employees/');
                if (response.ok) {
                    this.employees = await response.json();
                }
            } catch (error) {
                console.error('Error loading employees:', error);
            } finally {
                this.loading = false;
            }
        },

        async loadDepartments() {
            try {
                const response = await fetch('/api/departments/');
                if (response.ok) {
                    this.departments = await response.json();
                }
            } catch (error) {
                console.error('Error loading departments:', error);
            }
        },

        get filteredEmployees() {
            let filtered = this.employees;
            
            if (this.searchTerm) {
                filtered = filtered.filter(emp => 
                    emp.full_name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                    emp.employee_id.toLowerCase().includes(this.searchTerm.toLowerCase())
                );
            }
            
            if (this.selectedDepartment) {
                filtered = filtered.filter(emp => emp.department === this.selectedDepartment);
            }
            
            return filtered;
        },

        openAddModal() {
            this.editingEmployee = null;
            this.showAddModal = true;
        },

        openEditModal(employee) {
            this.editingEmployee = { ...employee };
            this.showAddModal = true;
        },

        async saveEmployee() {
            try {
                const url = this.editingEmployee?.id 
                    ? `/api/employees/${this.editingEmployee.id}/`
                    : '/api/employees/';
                
                const method = this.editingEmployee?.id ? 'PATCH' : 'POST';
                
                const response = await fetch(url, {
                    method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(this.editingEmployee)
                });

                if (response.ok) {
                    this.showAddModal = false;
                    this.loadEmployees();
                    window.dispatchEvent(new CustomEvent('show-notification', {
                        detail: {
                            message: 'تم حفظ بيانات الموظف بنجاح',
                            type: 'success'
                        }
                    }));
                }
            } catch (error) {
                console.error('Error saving employee:', error);
                window.dispatchEvent(new CustomEvent('show-notification', {
                    detail: {
                        message: 'حدث خطأ أثناء حفظ البيانات',
                        type: 'error'
                    }
                }));
            }
        },

        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        }
    }));

    // Attendance component
    Alpine.data('attendanceManager', () => ({
        attendanceLogs: [],
        loading: false,
        dateRange: {
            start: new Date().toISOString().split('T')[0],
            end: new Date().toISOString().split('T')[0]
        },

        init() {
            this.loadAttendanceLogs();
        },

        async loadAttendanceLogs() {
            try {
                this.loading = true;
                const params = new URLSearchParams({
                    start_date: this.dateRange.start,
                    end_date: this.dateRange.end
                });
                
                const response = await fetch(`/api/attendance/?${params}`);
                if (response.ok) {
                    this.attendanceLogs = await response.json();
                }
            } catch (error) {
                console.error('Error loading attendance logs:', error);
            } finally {
                this.loading = false;
            }
        },

        async triggerSync() {
            try {
                const response = await fetch('/api/attendance/sync/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });

                if (response.ok) {
                    window.dispatchEvent(new CustomEvent('show-notification', {
                        detail: {
                            message: 'تم بدء عملية المزامنة',
                            type: 'success'
                        }
                    }));
                    
                    // Reload data after sync
                    setTimeout(() => {
                        this.loadAttendanceLogs();
                    }, 5000);
                }
            } catch (error) {
                console.error('Error triggering sync:', error);
                window.dispatchEvent(new CustomEvent('show-notification', {
                    detail: {
                        message: 'حدث خطأ أثناء المزامنة',
                        type: 'error'
                    }
                }));
            }
        },

        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        }
    }));

    // Reports component
    Alpine.data('reportsManager', () => ({
        reports: [],
        loading: false,
        selectedReport: null,
        reportData: null,

        init() {
            this.loadReports();
        },

        async loadReports() {
            try {
                const response = await fetch('/api/reports/');
                if (response.ok) {
                    this.reports = await response.json();
                }
            } catch (error) {
                console.error('Error loading reports:', error);
            }
        },

        async generateReport(reportType, params = {}) {
            try {
                this.loading = true;
                const queryParams = new URLSearchParams(params);
                const response = await fetch(`/api/reports/${reportType}/?${queryParams}`);
                
                if (response.ok) {
                    this.reportData = await response.json();
                    this.selectedReport = reportType;
                }
            } catch (error) {
                console.error('Error generating report:', error);
            } finally {
                this.loading = false;
            }
        }
    }));
});

// Utility functions
window.AtlasUtils = {
    // Format currency
    formatCurrency(amount, currency = 'SAR') {
        return new Intl.NumberFormat('ar-SA', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    // Format percentage
    formatPercentage(value, total) {
        const percentage = total > 0 ? (value / total) * 100 : 0;
        return `${percentage.toFixed(1)}%`;
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Copy to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (error) {
            console.error('Failed to copy text:', error);
            return false;
        }
    },

    // Download file
    downloadFile(data, filename, type = 'text/csv') {
        const blob = new Blob([data], { type });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add loading animation
    const loader = document.getElementById('app-loader');
    if (loader) {
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 300);
        }, 1000);
    }
});