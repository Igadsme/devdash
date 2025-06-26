// DevDash JavaScript Application
class DevDashApp {
    constructor() {
        this.apiBase = window.location.origin.replace(':5000', ':8000');
        this.token = localStorage.getItem('auth_token');
        this.user = null;
        this.timer = {
            timeLeft: 25 * 60,
            isRunning: false,
            session: 1,
            sessionType: 'work',
            interval: null
        };
        
        this.init();
    }

    async init() {
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        this.setupEventListeners();
        
        if (this.token) {
            await this.verifyAuth();
        } else {
            this.showLandingPage();
        }
    }

    setupEventListeners() {
        // Landing page
        document.getElementById('login-btn')?.addEventListener('click', () => this.showAuthModal());
        
        // Auth modal
        document.getElementById('close-modal')?.addEventListener('click', () => this.hideAuthModal());
        document.getElementById('show-register')?.addEventListener('click', () => this.showRegisterForm());
        document.getElementById('show-login')?.addEventListener('click', () => this.showLoginForm());
        document.getElementById('login-form-element')?.addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('register-form-element')?.addEventListener('submit', (e) => this.handleRegister(e));
        
        // Dashboard
        document.getElementById('logout-btn')?.addEventListener('click', () => this.logout());
        
        // Pomodoro timer
        document.getElementById('start-timer')?.addEventListener('click', () => this.startTimer());
        document.getElementById('pause-timer')?.addEventListener('click', () => this.pauseTimer());
        document.getElementById('reset-timer')?.addEventListener('click', () => this.resetTimer());
        
        // Tasks
        document.getElementById('add-task-btn')?.addEventListener('click', () => this.showTaskModal());
        document.getElementById('close-task-modal')?.addEventListener('click', () => this.hideTaskModal());
        document.getElementById('task-form')?.addEventListener('submit', (e) => this.handleCreateTask(e));
        
        // AI Insights
        document.getElementById('generate-insights')?.addEventListener('click', () => this.generateInsights());
    }

    async apiRequest(method, endpoint, data = null) {
        const url = `${this.apiBase}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (this.token) {
            options.headers.Authorization = `Bearer ${this.token}`;
        }

        if (data) {
            if (method === 'GET') {
                const params = new URLSearchParams(data);
                url += `?${params}`;
            } else {
                options.body = JSON.stringify(data);
            }
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                if (response.status === 401) {
                    this.logout();
                    throw new Error('Unauthorized');
                }
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    async verifyAuth() {
        try {
            this.user = await this.apiRequest('GET', '/api/auth/me');
            this.showDashboard();
            await this.loadDashboardData();
        } catch (error) {
            this.logout();
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${this.apiBase}/api/auth/login`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            this.token = data.access_token;
            localStorage.setItem('auth_token', this.token);
            
            await this.verifyAuth();
            this.hideAuthModal();
        } catch (error) {
            alert('Login failed. Please check your credentials.');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const fullName = document.getElementById('register-fullname').value;
        const password = document.getElementById('register-password').value;

        try {
            await this.apiRequest('POST', '/api/auth/register', {
                username,
                email,
                full_name: fullName,
                password
            });

            alert('Registration successful! Please login.');
            this.showLoginForm();
        } catch (error) {
            alert('Registration failed. Please try again.');
        }
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('auth_token');
        this.showLandingPage();
    }

    showLandingPage() {
        document.getElementById('landing-page').classList.remove('hidden');
        document.getElementById('dashboard').classList.add('hidden');
        document.getElementById('auth-modal').classList.add('hidden');
    }

    showDashboard() {
        document.getElementById('landing-page').classList.add('hidden');
        document.getElementById('dashboard').classList.remove('hidden');
        document.getElementById('auth-modal').classList.add('hidden');
        
        if (this.user) {
            document.getElementById('user-name').textContent = this.user.full_name || this.user.username;
        }
    }

    showAuthModal() {
        document.getElementById('auth-modal').classList.remove('hidden');
        document.getElementById('auth-modal').classList.add('flex');
        this.showLoginForm();
    }

    hideAuthModal() {
        document.getElementById('auth-modal').classList.add('hidden');
        document.getElementById('auth-modal').classList.remove('flex');
    }

    showLoginForm() {
        document.getElementById('login-form').classList.remove('hidden');
        document.getElementById('register-form').classList.add('hidden');
    }

    showRegisterForm() {
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('register-form').classList.remove('hidden');
    }

    async loadDashboardData() {
        await Promise.all([
            this.loadDashboardStats(),
            this.loadTasks(),
            this.loadGitHubStats(),
            this.loadPomodoroSessions(),
            this.loadInsights()
        ]);
        
        this.initCharts();
    }

    async loadDashboardStats() {
        try {
            const stats = await this.apiRequest('GET', '/api/dashboard-stats');
            
            document.getElementById('today-commits').textContent = stats.todayCommits;
            document.getElementById('today-focus').textContent = `${stats.todayFocusTime}h`;
            document.getElementById('week-commits').textContent = stats.weekCommits;
            document.getElementById('week-focus').textContent = `${stats.weekFocusTime}h`;
            document.getElementById('week-tasks').textContent = stats.weekTasks;
            document.getElementById('week-streak').textContent = stats.streak;
        } catch (error) {
            console.error('Failed to load dashboard stats:', error);
        }
    }

    async loadTasks() {
        try {
            const tasks = await this.apiRequest('GET', '/api/tasks/');
            this.renderTasks(tasks.slice(0, 5)); // Show only first 5 tasks
        } catch (error) {
            console.error('Failed to load tasks:', error);
        }
    }

    renderTasks(tasks) {
        const tasksList = document.getElementById('tasks-list');
        
        if (tasks.length === 0) {
            tasksList.innerHTML = '<div class="text-center py-4 text-gray-500">No tasks yet. Create your first task!</div>';
            return;
        }

        tasksList.innerHTML = tasks.map(task => `
            <div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <input type="checkbox" ${task.completed ? 'checked' : ''} 
                       onchange="app.toggleTask(${task.id}, this.checked)"
                       class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                <div class="flex-1">
                    <p class="text-sm font-medium ${task.completed ? 'line-through opacity-60' : ''} text-gray-900">
                        ${task.title}
                    </p>
                    ${task.description ? `<p class="text-xs text-gray-500 mt-1">${task.description}</p>` : ''}
                </div>
                <span class="text-xs px-2 py-1 rounded-full ${this.getPriorityColor(task.priority)}">
                    ${task.completed ? 'Done' : task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                </span>
            </div>
        `).join('');
    }

    getPriorityColor(priority) {
        switch (priority) {
            case 'high': return 'bg-red-100 text-red-600';
            case 'medium': return 'bg-yellow-100 text-yellow-600';
            case 'low': return 'bg-green-100 text-green-600';
            default: return 'bg-gray-100 text-gray-600';
        }
    }

    async toggleTask(taskId, completed) {
        try {
            await this.apiRequest('PUT', `/api/tasks/${taskId}`, { completed });
            await this.loadTasks();
            await this.loadDashboardStats();
        } catch (error) {
            console.error('Failed to toggle task:', error);
        }
    }

    showTaskModal() {
        document.getElementById('task-modal').classList.remove('hidden');
        document.getElementById('task-modal').classList.add('flex');
    }

    hideTaskModal() {
        document.getElementById('task-modal').classList.add('hidden');
        document.getElementById('task-modal').classList.remove('flex');
        document.getElementById('task-form').reset();
    }

    async handleCreateTask(e) {
        e.preventDefault();
        
        const title = document.getElementById('task-title').value;
        const description = document.getElementById('task-description').value;
        const priority = document.getElementById('task-priority').value;

        try {
            await this.apiRequest('POST', '/api/tasks/', {
                title,
                description: description || null,
                priority
            });

            this.hideTaskModal();
            await this.loadTasks();
            await this.loadDashboardStats();
        } catch (error) {
            console.error('Failed to create task:', error);
            alert('Failed to create task. Please try again.');
        }
    }

    // Pomodoro Timer
    startTimer() {
        if (this.timer.isRunning) return;

        this.timer.isRunning = true;
        document.getElementById('start-timer').disabled = true;
        document.getElementById('pause-timer').disabled = false;

        this.timer.interval = setInterval(() => {
            this.timer.timeLeft--;
            this.updateTimerDisplay();

            if (this.timer.timeLeft <= 0) {
                this.completeSession();
            }
        }, 1000);
    }

    pauseTimer() {
        if (!this.timer.isRunning) return;

        this.timer.isRunning = false;
        document.getElementById('start-timer').disabled = false;
        document.getElementById('pause-timer').disabled = true;
        
        if (this.timer.interval) {
            clearInterval(this.timer.interval);
            this.timer.interval = null;
        }
    }

    resetTimer() {
        this.pauseTimer();
        this.timer.timeLeft = 25 * 60;
        this.timer.session = 1;
        this.timer.sessionType = 'work';
        this.updateTimerDisplay();
        document.getElementById('timer-session').textContent = 'Work Session 1';
    }

    async completeSession() {
        this.pauseTimer();

        // Save session to database
        try {
            await this.apiRequest('POST', '/api/pomodoro/sessions', {
                duration: this.timer.sessionType === 'work' ? 25 : 5,
                session_type: this.timer.sessionType,
                completed: true
            });
        } catch (error) {
            console.error('Failed to save session:', error);
        }

        alert(`${this.timer.sessionType === 'work' ? 'Work' : 'Break'} session completed!`);

        // Switch to next session
        const isWorkSession = this.timer.sessionType === 'work';
        this.timer.sessionType = isWorkSession ? 'break' : 'work';
        this.timer.timeLeft = isWorkSession ? 5 * 60 : 25 * 60;
        
        if (!isWorkSession) {
            this.timer.session++;
        }

        this.updateTimerDisplay();
        document.getElementById('timer-session').textContent = 
            `${this.timer.sessionType === 'work' ? 'Work' : 'Break'} Session ${this.timer.session}`;
            
        await this.loadDashboardStats();
    }

    updateTimerDisplay() {
        const minutes = Math.floor(this.timer.timeLeft / 60);
        const seconds = this.timer.timeLeft % 60;
        const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        document.getElementById('timer-display').textContent = display;

        // Update progress circle
        const totalTime = this.timer.sessionType === 'work' ? 25 * 60 : 5 * 60;
        const progress = (totalTime - this.timer.timeLeft) / totalTime;
        const offset = 283 - (progress * 283);
        
        document.getElementById('timer-progress').style.strokeDashoffset = offset;
    }

    async loadGitHubStats() {
        try {
            // First sync GitHub data to generate some sample data
            await this.apiRequest('POST', '/api/github/sync');
            
            const stats = await this.apiRequest('GET', '/api/github/stats');
            this.githubStats = stats;
        } catch (error) {
            console.error('Failed to load GitHub stats:', error);
            this.githubStats = [];
        }
    }

    async loadPomodoroSessions() {
        try {
            const sessions = await this.apiRequest('GET', '/api/pomodoro/sessions');
            this.pomodoroSessions = sessions;
        } catch (error) {
            console.error('Failed to load pomodoro sessions:', error);
            this.pomodoroSessions = [];
        }
    }

    async loadInsights() {
        try {
            const insights = await this.apiRequest('GET', '/api/insights/');
            this.renderInsights(insights.slice(0, 3));
        } catch (error) {
            console.error('Failed to load insights:', error);
        }
    }

    renderInsights(insights) {
        const insightsList = document.getElementById('insights-list');
        
        if (insights.length === 0) {
            insightsList.innerHTML = `
                <div class="text-center py-4">
                    <p class="text-gray-500 mb-4">No insights available yet. Generate your first insights!</p>
                    <button id="generate-insights" class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg">
                        Generate Insights
                    </button>
                </div>
            `;
            document.getElementById('generate-insights')?.addEventListener('click', () => this.generateInsights());
            return;
        }

        insightsList.innerHTML = insights.map(insight => `
            <div class="p-4 rounded-lg border-l-4 ${this.getInsightColor(insight.type)}">
                <div class="flex items-start space-x-3">
                    <i data-lucide="${this.getInsightIcon(insight.type)}" class="w-5 h-5 mt-0.5"></i>
                    <div>
                        <p class="text-sm font-medium text-gray-900">${insight.title}</p>
                        <p class="text-xs text-gray-600 mt-1">${insight.description}</p>
                        <p class="text-xs text-gray-500 mt-1">Confidence: ${insight.confidence}%</p>
                    </div>
                </div>
            </div>
        `).join('');

        // Re-initialize icons for new content
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    getInsightIcon(type) {
        switch (type) {
            case 'peak_hours': return 'lightbulb';
            case 'focus_trend': return 'trending-up';
            case 'break_reminder': return 'alert-triangle';
            default: return 'brain';
        }
    }

    getInsightColor(type) {
        switch (type) {
            case 'peak_hours': return 'text-blue-600 bg-blue-50 border-blue-400';
            case 'focus_trend': return 'text-green-600 bg-green-50 border-green-400';
            case 'break_reminder': return 'text-orange-600 bg-orange-50 border-orange-400';
            default: return 'text-purple-600 bg-purple-50 border-purple-400';
        }
    }

    async generateInsights() {
        try {
            const button = document.getElementById('generate-insights');
            button.textContent = 'Generating...';
            button.disabled = true;

            await this.apiRequest('POST', '/api/insights/generate');
            await this.loadInsights();
        } catch (error) {
            console.error('Failed to generate insights:', error);
            alert('Failed to generate insights. Please try again.');
        } finally {
            const button = document.getElementById('generate-insights');
            if (button) {
                button.textContent = 'Generate Insights';
                button.disabled = false;
            }
        }
    }

    initCharts() {
        this.initGitHubChart();
        this.initFocusChart();
    }

    initGitHubChart() {
        const ctx = document.getElementById('github-chart');
        if (!ctx) return;

        // Generate last 7 days labels
        const labels = [];
        const today = new Date();
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(today.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
        }

        // Generate data based on GitHub stats or mock data
        const data = labels.map((_, index) => {
            const checkDate = new Date(today);
            checkDate.setDate(today.getDate() - (6 - index));
            
            const stat = this.githubStats?.find(s => {
                const statDate = new Date(s.date);
                return statDate.toDateString() === checkDate.toDateString();
            });
            
            return stat?.commits || Math.floor(Math.random() * 15);
        });

        new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Commits',
                    data,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    initFocusChart() {
        const ctx = document.getElementById('focus-chart');
        if (!ctx) return;

        // Generate last 7 days labels
        const labels = [];
        const today = new Date();
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(today.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
        }

        // Calculate focus hours per day
        const data = labels.map((_, index) => {
            const checkDate = new Date(today);
            checkDate.setDate(today.getDate() - (6 - index));
            checkDate.setHours(0, 0, 0, 0);
            
            const nextDay = new Date(checkDate);
            nextDay.setDate(checkDate.getDate() + 1);

            const daysSessions = this.pomodoroSessions?.filter(session => {
                const sessionDate = new Date(session.started_at);
                return sessionDate >= checkDate && sessionDate < nextDay && session.completed;
            }) || [];

            const totalMinutes = daysSessions.reduce((sum, session) => sum + session.duration, 0);
            return Math.round((totalMinutes / 60) * 100) / 100;
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Focus Hours',
                    data,
                    backgroundColor: '#10b981',
                    borderRadius: 6,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 8
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DevDashApp();
});