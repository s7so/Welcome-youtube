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
        departments: [],
        loading: false,
        searchTerm: '',
        selectedDepartment: '',
        dateRange: {
            start: new Date().toISOString().split('T')[0],
            end: new Date().toISOString().split('T')[0]
        },
        stats: {
            totalRecords: 0,
            presentToday: 0,
            lateToday: 0,
            absentToday: 0,
            presentPercentage: 0,
            latePercentage: 0,
            absentPercentage: 0
        },
        pagination: {
            currentPage: 1,
            totalPages: 1,
            total: 0,
            startIndex: 0,
            endIndex: 0
        },

        init() {
            this.loadDepartments();
            this.loadAttendanceLogs();
            this.loadStats();
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

        async loadAttendanceLogs() {
            this.loading = true;
            try {
                const params = new URLSearchParams({
                    start_date: this.dateRange.start,
                    end_date: this.dateRange.end,
                    search: this.searchTerm,
                    department: this.selectedDepartment,
                    page: this.pagination.currentPage
                });

                const response = await fetch(`/api/attendance/?${params}`);
                if (response.ok) {
                    const data = await response.json();
                    this.attendanceLogs = data.results;
                    this.pagination = data.pagination;
                }
            } catch (error) {
                console.error('Error loading attendance logs:', error);
            } finally {
                this.loading = false;
            }
        },

        async loadStats() {
            try {
                const response = await fetch('/api/attendance/stats/');
                if (response.ok) {
                    this.stats = await response.json();
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        },

        async triggerSync() {
            this.loading = true;
            try {
                const response = await fetch('/api/attendance/sync/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });

                if (response.ok) {
                    this.showNotification('تمت المزامنة بنجاح', 'success');
                    this.loadAttendanceLogs();
                    this.loadStats();
                } else {
                    this.showNotification('فشلت عملية المزامنة', 'error');
                }
            } catch (error) {
                console.error('Error syncing attendance:', error);
                this.showNotification('حدث خطأ في المزامنة', 'error');
            } finally {
                this.loading = false;
            }
        },

        async deleteLog(logId) {
            if (!confirm('هل أنت متأكد من حذف هذا السجل؟')) {
                return;
            }

            try {
                const response = await fetch(`/api/attendance/${logId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });

                if (response.ok) {
                    this.showNotification('تم حذف السجل بنجاح', 'success');
                    this.loadAttendanceLogs();
                } else {
                    this.showNotification('فشل في حذف السجل', 'error');
                }
            } catch (error) {
                console.error('Error deleting log:', error);
                this.showNotification('حدث خطأ في حذف السجل', 'error');
            }
        },

        editLog(log) {
            // TODO: Implement edit modal
            console.log('Edit log:', log);
        },

        previousPage() {
            if (this.pagination.currentPage > 1) {
                this.pagination.currentPage--;
                this.loadAttendanceLogs();
            }
        },

        nextPage() {
            if (this.pagination.currentPage < this.pagination.totalPages) {
                this.pagination.currentPage++;
                this.loadAttendanceLogs();
            }
        },

        getStatusClass(status) {
            const classes = {
                'present': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
                'late': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
                'absent': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
                'leave': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'
            };
            return classes[status] || classes['present'];
        },

        getStatusText(status) {
            const texts = {
                'present': 'حاضر',
                'late': 'متأخر',
                'absent': 'غائب',
                'leave': 'إجازة'
            };
            return texts[status] || 'حاضر';
        },

        formatDate(date) {
            return new Date(date).toLocaleDateString('ar-SA');
        },

        formatNumber(num) {
            return num.toLocaleString('ar-SA');
        },

        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        },

        showNotification(message, type = 'success') {
            if (window.atlasApp) {
                window.atlasApp.showNotification(message, type);
            }
        }
    }));

    // Reports component
    Alpine.data('reportsManager', () => ({
        reports: [],
        loading: false,
        selectedReport: null,
        reportData: [],
        departments: [],
        filters: {
            year: '2024',
            month: '',
            department: ''
        },
        stats: {
            totalAttendance: 0,
            averageHours: 0,
            overtimeHours: 0,
            leaveDays: 0
        },
        init() {
            this.loadDepartments();
            this.loadStats();
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
        async loadStats() {
            try {
                const response = await fetch('/api/reports/stats/');
                if (response.ok) {
                    this.stats = await response.json();
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        },
        async generateReport() {
            if (!this.selectedReport) {
                this.showNotification('يرجى اختيار نوع التقرير', 'warning');
                return;
            }

            this.loading = true;
            try {
                const params = new URLSearchParams({
                    type: this.selectedReport,
                    year: this.filters.year,
                    month: this.filters.month,
                    department: this.filters.department
                });

                const response = await fetch(`/api/reports/generate/?${params}`);
                if (response.ok) {
                    this.reportData = await response.json();
                    this.showNotification('تم إنشاء التقرير بنجاح', 'success');
                } else {
                    this.showNotification('حدث خطأ في إنشاء التقرير', 'error');
                }
            } catch (error) {
                console.error('Error generating report:', error);
                this.showNotification('حدث خطأ في إنشاء التقرير', 'error');
            } finally {
                this.loading = false;
            }
        },
        showNotification(message, type = 'success') {
            if (window.atlasApp) {
                window.atlasApp.showNotification(message, type);
            }
        }
    }));

    // Settings manager component
    Alpine.data('settingsManager', () => ({
        activeTab: 'general',
        loading: false,
        settings: {
            company: {
                name: 'شركة مصافي الوسط',
                address: 'الرياض، المملكة العربية السعودية',
                phone: '+966-11-123-4567',
                email: 'info@wasco.com.sa'
            },
            system: {
                timezone: 'Asia/Riyadh',
                language: 'ar',
                dateFormat: 'DD/MM/YYYY',
                darkMode: false
            },
            attendance: {
                startTime: '08:00',
                endTime: '16:00',
                dailyHours: 8,
                workDays: ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس'],
                gracePeriod: 15,
                maxOvertime: 4,
                autoLogout: true,
                lateAlerts: true
            },
            notifications: {
                email: {
                    dailyReport: true,
                    lateAlerts: false,
                    monthlyReport: true
                },
                sms: {
                    lateAlerts: false,
                    overtimeReminders: true
                }
            },
            security: {
                passwordMinLength: 8,
                passwordRequireUppercase: true,
                passwordRequireNumbers: true,
                passwordRequireSymbols: false,
                sessionTimeout: 30,
                autoLogout: true,
                preventMultipleLogins: false
            },
            integrations: {
                fingertec: {
                    ip: '192.168.1.100',
                    port: 4370,
                    username: 'admin',
                    password: '',
                    autoSync: true
                },
                backup: {
                    path: '/backup/',
                    retention: 7,
                    autoBackup: true
                }
            }
        },

        init() {
            this.loadSettings();
        },

        async loadSettings() {
            this.loading = true;
            try {
                const response = await fetch('/api/settings/');
                if (response.ok) {
                    const data = await response.json();
                    this.settings = { ...this.settings, ...data };
                }
            } catch (error) {
                console.error('Error loading settings:', error);
            } finally {
                this.loading = false;
            }
        },

        async saveAllSettings() {
            this.loading = true;
            try {
                const response = await fetch('/api/settings/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(this.settings)
                });

                if (response.ok) {
                    this.showNotification('تم حفظ الإعدادات بنجاح', 'success');
                } else {
                    this.showNotification('حدث خطأ في حفظ الإعدادات', 'error');
                }
            } catch (error) {
                console.error('Error saving settings:', error);
                this.showNotification('حدث خطأ في حفظ الإعدادات', 'error');
            } finally {
                this.loading = false;
            }
        },

        async testFingerTecConnection() {
            this.loading = true;
            try {
                const response = await fetch('/api/integrations/fingertec/test/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(this.settings.integrations.fingertec)
                });

                if (response.ok) {
                    this.showNotification('تم الاتصال بالجهاز بنجاح', 'success');
                } else {
                    this.showNotification('فشل الاتصال بالجهاز', 'error');
                }
            } catch (error) {
                console.error('Error testing connection:', error);
                this.showNotification('حدث خطأ في اختبار الاتصال', 'error');
            } finally {
                this.loading = false;
            }
        },

        async createBackup() {
            this.loading = true;
            try {
                const response = await fetch('/api/integrations/backup/create/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });

                if (response.ok) {
                    this.showNotification('تم إنشاء النسخة الاحتياطية بنجاح', 'success');
                } else {
                    this.showNotification('فشل في إنشاء النسخة الاحتياطية', 'error');
                }
            } catch (error) {
                console.error('Error creating backup:', error);
                this.showNotification('حدث خطأ في إنشاء النسخة الاحتياطية', 'error');
            } finally {
                this.loading = false;
            }
        },

        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        },

        showNotification(message, type = 'success') {
            if (window.atlasApp) {
                window.atlasApp.showNotification(message, type);
            }
        }
    }));

    // Department manager component
    Alpine.data('departmentManager', () => ({
        departments: [],
        loading: false,
        searchTerm: '',
        showAddModal: false,
        editingDepartment: {
            name: '',
            description: '',
            manager: '',
            is_active: true
        },
        stats: {
            totalDepartments: 0,
            totalEmployees: 0,
            averageEmployees: 0
        },

        init() {
            this.loadDepartments();
            this.loadStats();
        },

        async loadDepartments() {
            this.loading = true;
            try {
                const response = await fetch('/api/departments/');
                if (response.ok) {
                    this.departments = await response.json();
                }
            } catch (error) {
                console.error('Error loading departments:', error);
            } finally {
                this.loading = false;
            }
        },

        async loadStats() {
            try {
                const response = await fetch('/api/departments/stats/');
                if (response.ok) {
                    this.stats = await response.json();
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        },

        get filteredDepartments() {
            if (!this.searchTerm) {
                return this.departments;
            }
            return this.departments.filter(dept => 
                dept.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                (dept.description && dept.description.toLowerCase().includes(this.searchTerm.toLowerCase()))
            );
        },

        openAddModal() {
            this.editingDepartment = {
                name: '',
                description: '',
                manager: '',
                is_active: true
            };
            this.showAddModal = true;
        },

        openEditModal(department) {
            this.editingDepartment = { ...department };
            this.showAddModal = true;
        },

        async saveDepartment() {
            try {
                const url = this.editingDepartment.id 
                    ? `/api/departments/${this.editingDepartment.id}/`
                    : '/api/departments/';
                
                const method = this.editingDepartment.id ? 'PATCH' : 'POST';
                
                const response = await fetch(url, {
                    method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(this.editingDepartment)
                });

                if (response.ok) {
                    this.showAddModal = false;
                    this.loadDepartments();
                    this.loadStats();
                    this.showNotification('تم حفظ القسم بنجاح', 'success');
                } else {
                    this.showNotification('حدث خطأ في حفظ القسم', 'error');
                }
            } catch (error) {
                console.error('Error saving department:', error);
                this.showNotification('حدث خطأ في حفظ القسم', 'error');
            }
        },

        async deleteDepartment(departmentId) {
            if (!confirm('هل أنت متأكد من حذف هذا القسم؟')) {
                return;
            }

            try {
                const response = await fetch(`/api/departments/${departmentId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });

                if (response.ok) {
                    this.loadDepartments();
                    this.loadStats();
                    this.showNotification('تم حذف القسم بنجاح', 'success');
                } else {
                    this.showNotification('فشل في حذف القسم', 'error');
                }
            } catch (error) {
                console.error('Error deleting department:', error);
                this.showNotification('حدث خطأ في حذف القسم', 'error');
            }
        },

        viewEmployees(department) {
            // TODO: Navigate to department employees page
            console.log('View employees for department:', department);
        },

        formatDate(date) {
            return new Date(date).toLocaleDateString('ar-SA');
        },

        formatNumber(num) {
            return num.toLocaleString('ar-SA');
        },

        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        },

        showNotification(message, type = 'success') {
            if (window.atlasApp) {
                window.atlasApp.showNotification(message, type);
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