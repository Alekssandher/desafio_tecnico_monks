class MarketingDashboard {
            constructor() {
                this.token = localStorage.getItem('token');
                this.currentUser = null;
                this.currentData = [];
                this.currentOffset = 0;
                this.currentLimit = 10;
                this.currentSort = null;
                this.currentSortDesc = false;
                this.apiUrl = 'http://localhost:8000'; 
                
                this.init();
            }

            init() {
                this.bindEvents();
                if (this.token) {
                    this.showDashboard();
                    this.loadData();
                } else {
                    this.showLogin();
                }
            }

            bindEvents() {
                document.getElementById('loginForm').addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.login();
                });

                document.getElementById('logoutBtn').addEventListener('click', () => {
                    this.logout();
                });

        
                document.getElementById('applyFilters').addEventListener('click', () => {
                    this.currentOffset = 0;
                    this.loadData();
                });

                document.getElementById('clearFilters').addEventListener('click', () => {
                    this.clearFilters();
                });

                document.getElementById('prevPage').addEventListener('click', () => {
                    if (this.currentOffset > 0) {
                        this.currentOffset -= this.currentLimit;
                        this.loadData();
                    }
                });

                document.getElementById('nextPage').addEventListener('click', () => {
                    this.currentOffset += this.currentLimit;
                    this.loadData();
                });

                document.getElementById('limit').addEventListener('change', (e) => {
                    this.currentLimit = parseInt(e.target.value);
                    this.currentOffset = 0;
                    this.loadData();
                });
            }

            async login() {
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                
                try {
                    const formData = new FormData();
                    formData.append('email', email);
                    formData.append('password', password);

                    const response = await fetch(`${this.apiUrl}/login`, {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error('Credenciais inválidas');
                    }

                    const data = await response.json();
                    this.token = data.token;
                    localStorage.setItem('token', this.token);
                    
                    this.showDashboard();
                    this.loadData();
                    this.hideError('loginError');
                } catch (error) {
                    this.showError('loginError', error.message);
                }
            }

            logout() {
                this.token = null;
                this.currentUser = null;
                localStorage.removeItem('token');
                this.showLogin();
            }

            async loadData() {
                try {
                    this.showLoading();
                    
                    const params = new URLSearchParams({
                        offset: this.currentOffset,
                        limit: this.currentLimit
                    });

                    const startDate = document.getElementById('startDate').value;
                    const endDate = document.getElementById('endDate').value;
                    
                    if (startDate) params.append('start_date', startDate);
                    if (endDate) params.append('end_date', endDate);
                    if (this.currentSort) {
                        params.append('order_by', this.currentSort);
                        params.append('descending', this.currentSortDesc);
                    }

                    const response = await fetch(`${this.apiUrl}/metrics/csv?${params}`, {
                        headers: {
                            'Authorization': `Bearer ${this.token}`,
                            'Content-Type': 'application/json'
                        }
                    });

                    if (!response.ok) {
                        if (response.status === 401) {
                            this.logout();
                            return;
                        }
                        throw new Error('Erro ao carregar dados');
                    }

                    const data = await response.json();
                    this.currentData = data.data_preview;
                    this.renderTable();
                    this.updateMetrics();
                    this.updatePagination();
                    this.hideLoading();
                    this.hideError('error');
                } catch (error) {
                    this.hideLoading();
                    this.showError('error', error.message);
                }
            }

            renderTable() {
                if (!this.currentData.length) {
                    this.showError('error', 'Nenhum dado encontrado');
                    return;
                }

                const columns = Object.keys(this.currentData[0]);
                

                const isAdmin = this.getCurrentUserRole() === 'admin';

                const visibleColumns = columns.filter(col => 
                    isAdmin || col !== 'cost_micros'
                );

                this.renderTableHeader(visibleColumns);
                this.renderTableBody(visibleColumns);
                
                document.getElementById('dataTable').classList.remove('hidden');
            }

            renderTableHeader(columns) {
                const header = document.getElementById('tableHeader');
                header.innerHTML = '';

                columns.forEach(column => {
                    const th = document.createElement('th');
                    th.textContent = this.formatColumnName(column);
                    th.className = 'sortable';
                    th.dataset.column = column;
                    
                    if (this.currentSort === column) {
                        th.classList.add(this.currentSortDesc ? 'sort-desc' : 'sort-asc');
                    }

                    th.addEventListener('click', () => {
                        this.sortTable(column);
                    });

                    header.appendChild(th);
                });
            }

            renderTableBody(columns) {
                const tbody = document.getElementById('tableBody');
                tbody.innerHTML = '';

                this.currentData.forEach(row => {
                    const tr = document.createElement('tr');
                    
                    columns.forEach(column => {
                        const td = document.createElement('td');
                        td.textContent = this.formatCellValue(row[column], column);
                        tr.appendChild(td);
                    });
                    
                    tbody.appendChild(tr);
                });
            }

            sortTable(column) {
                if (this.currentSort === column) {
                    this.currentSortDesc = !this.currentSortDesc;
                } else {
                    this.currentSort = column;
                    this.currentSortDesc = false;
                }
                
                this.currentOffset = 0;
                this.loadData();
            }

            updateMetrics() {
                const totalRecords = this.currentData.length;
                const totalClicks = this.currentData.reduce((sum, row) => sum + (row.clicks || 0), 0);
                const totalImpressions = this.currentData.reduce((sum, row) => sum + (row.impressions || 0), 0);
                const totalConversions = this.currentData.reduce((sum, row) => sum + (row.conversions || 0), 0);

                document.getElementById('totalRecords').textContent = totalRecords.toLocaleString();
                document.getElementById('totalClicks').textContent = totalClicks.toLocaleString();
                document.getElementById('totalImpressions').textContent = totalImpressions.toLocaleString();
                document.getElementById('totalConversions').textContent = totalConversions.toLocaleString();
                
                document.getElementById('metricsInfo').classList.remove('hidden');
            }

            updatePagination() {
                const currentPage = Math.floor(this.currentOffset / this.currentLimit) + 1;
                document.getElementById('pageInfo').textContent = `Página ${currentPage}`;
                
                document.getElementById('prevPage').disabled = this.currentOffset === 0;
                document.getElementById('nextPage').disabled = this.currentData.length < this.currentLimit;
                
                document.getElementById('pagination').classList.remove('hidden');
            }

            clearFilters() {
                document.getElementById('startDate').value = '';
                document.getElementById('endDate').value = '';
                document.getElementById('limit').value = '10';
                this.currentLimit = 10;
                this.currentOffset = 0;
                this.currentSort = null;
                this.currentSortDesc = false;
                this.loadData();
            }

            formatColumnName(column) {
                const names = {
                    'date': 'Data',
                    'account_id': 'ID Conta',
                    'campaign_id': 'ID Campanha',
                    'clicks': 'Clicks',
                    'conversions': 'Conversões',
                    'impressions': 'Impressões',
                    'interactions': 'Interações',
                    'cost_micros': 'Custo (µ)'
                };
                return names[column] || column.toUpperCase();
            }

            formatCellValue(value, column) {
                if (value === null || value === undefined) return '-';
                
                if (column === 'date') {
                    return new Date(value).toLocaleDateString('pt-BR');
                }
                
                if (typeof value === 'number' && column !== 'account_id' && column !== 'campaign_id') {
                    return value.toLocaleString('pt-BR', { 
                        minimumFractionDigits: column === 'conversions' ? 2 : 0,
                        maximumFractionDigits: column === 'conversions' ? 2 : 0
                    });
                }
                
                return value;
            }

            getCurrentUserRole() {
                if (!this.token) return null;
                try {
                    const payload = JSON.parse(atob(this.token.split('.')[1]));
                    return payload.role;
                } catch (e) {
                    return null;
                }
            }

            getCurrentUserEmail() {
                if (!this.token) return null;
                try {
                    const payload = JSON.parse(atob(this.token.split('.')[1]));
                    return payload.sub;
                } catch (e) {
                    return null;
                }
            }

            showLogin() {
                document.getElementById('loginScreen').classList.remove('hidden');
                document.getElementById('dashboardScreen').classList.add('hidden');
                document.getElementById('email').focus();
            }

            showDashboard() {
                document.getElementById('loginScreen').classList.add('hidden');
                document.getElementById('dashboardScreen').classList.remove('hidden');
                
                document.getElementById('userEmail').textContent = this.getCurrentUserEmail();
                document.getElementById('userRole').textContent = this.getCurrentUserRole();
            }

            showLoading() {
                document.getElementById('loading').classList.remove('hidden');
                document.getElementById('dataTable').classList.add('hidden');
            }

            hideLoading() {
                document.getElementById('loading').classList.add('hidden');
            }

            showError(elementId, message) {
                const element = document.getElementById(elementId);
                element.textContent = message;
                element.classList.remove('hidden');
            }

            hideError(elementId) {
                document.getElementById(elementId).classList.add('hidden');
            }
        }

        // init
        document.addEventListener('DOMContentLoaded', () => {
            new MarketingDashboard();
        });