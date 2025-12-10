// Main application JavaScript

class HackerHub {
    constructor() {
        this.apiBase = '/api';
        this.currentUser = null;
        this.init();
    }

    async init() {
        this.loadUser();
        this.bindEvents();
        
        // Load tools if on tools page
        if (window.location.pathname.includes('/tools')) {
            this.loadTools();
        }
    }

    async loadUser() {
        try {
            const response = await fetch(`${this.apiBase}/user/profile`);
            if (response.ok) {
                this.currentUser = await response.json();
                this.updateUI();
            }
        } catch (error) {
            console.log('No user session');
        }
    }

    updateUI() {
        // Update UI based on user state
        const userElements = document.querySelectorAll('.user-info');
        userElements.forEach(el => {
            if (this.currentUser) {
                el.innerHTML = `
                    <div class="user-avatar">${this.currentUser.username.charAt(0)}</div>
                    <div>
                        <h3>${this.currentUser.username}</h3>
                        <p>${this.currentUser.experience} Level</p>
                    </div>
                `;
            }
        });
    }

    bindEvents() {
        // Search functionality
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTools(e.target.value);
            });
        }

        // Platform tabs
        document.querySelectorAll('.platform-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('.platform-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                this.loadToolsByPlatform(e.target.dataset.platform);
            });
        });

        // Follow buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('follow-btn')) {
                this.toggleFollow(e.target.dataset.tool);
            }
        });
    }

    async loadTools() {
        try {
            const response = await fetch(`${this.apiBase}/tools`);
            const tools = await response.json();
            this.renderTools(tools);
        } catch (error) {
            console.error('Error loading tools:', error);
        }
    }

    async loadToolsByPlatform(platform) {
        try {
            const response = await fetch(`${this.apiBase}/tools?platform=${platform}`);
            const categories = await response.json();
            this.renderCategories(categories, platform);
        } catch (error) {
            console.error('Error loading platform tools:', error);
        }
    }

    async searchTools(query) {
        if (query.length < 2) return;
        
        try {
            const response = await fetch(`${this.apiBase}/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            this.renderSearchResults(results);
        } catch (error) {
            console.error('Error searching:', error);
        }
    }

    renderTools(tools) {
        const container = document.querySelector('.tools-list');
        if (!container) return;

        container.innerHTML = '';
        
        for (const [platform, categories] of Object.entries(tools)) {
            for (const [category, subcategories] of Object.entries(categories)) {
                for (const [subcategory, toolList] of Object.entries(subcategories)) {
                    toolList.forEach(tool => {
                        const isFollowing = this.currentUser?.followed_tools?.includes(tool.name);
                        
                        const toolCard = `
                            <div class="tool-card">
                                <div class="tool-header">
                                    <h3 class="tool-name">${tool.name}</h3>
                                    ${!this.currentUser?.anonymous ? `
                                        <button class="follow-btn" data-tool="${tool.name}">
                                            ${isFollowing ? '⭐ Following' : '☆ Follow'}
                                        </button>
                                    ` : ''}
                                </div>
                                <p class="tool-desc">${tool.desc}</p>
                                <div class="tool-meta">
                                    <span class="platform">${platform}</span>
                                    <span class="difficulty ${tool.difficulty}">${tool.difficulty}</span>
                                </div>
                                ${tool.command ? `
                                    <div class="tool-command">
                                        <code>${tool.command}</code>
                                        <button class="copy-btn" onclick="navigator.clipboard.writeText('${tool.command}')">
                                            <i class="fas fa-copy"></i>
                                        </button>
                                    </div>
                                ` : ''}
                            </div>
                        `;
                        container.innerHTML += toolCard;
                    });
                }
            }
        }
    }

    renderCategories(categories, platform) {
        const categoriesContainer = document.querySelector('.categories');
        const toolsContainer = document.querySelector('.tools-list');
        
        if (categoriesContainer) {
            categoriesContainer.innerHTML = '';
            
            for (const [category, subcategories] of Object.entries(categories)) {
                const categoryHtml = `
                    <div class="category">
                        <h4>${category.replace(/_/g, ' ').toUpperCase()}</h4>
                        ${Object.keys(subcategories).map(subcategory => `
                            <div class="subcategory" onclick="hackerHub.loadSubcategory('${platform}', '${category}', '${subcategory}')">
                                ${subcategory.replace(/_/g, ' ')}
                            </div>
                        `).join('')}
                    </div>
                `;
                categoriesContainer.innerHTML += categoryHtml;
            }
        }
        
        // Clear tools list initially
        if (toolsContainer) {
            toolsContainer.innerHTML = '<p>Select a subcategory to view tools</p>';
        }
    }

    async loadSubcategory(platform, category, subcategory) {
        try {
            const response = await fetch(
                `${this.apiBase}/tools?platform=${platform}&category=${category}&subcategory=${subcategory}`
            );
            const tools = await response.json();
            this.renderSubcategoryTools(tools, subcategory);
        } catch (error) {
            console.error('Error loading subcategory:', error);
        }
    }

    renderSubcategoryTools(tools, subcategory) {
        const container = document.querySelector('.tools-list');
        if (!container) return;

        container.innerHTML = '';
        
        if (tools.length === 0) {
            container.innerHTML = '<p>No tools found in this category</p>';
            return;
        }
        
        tools.forEach(tool => {
            const isFollowing = this.currentUser?.followed_tools?.includes(tool.name);
            
            const toolCard = `
                <div class="tool-card">
                    <div class="tool-header">
                        <h3 class="tool-name">${tool.name}</h3>
                        ${!this.currentUser?.anonymous ? `
                            <button class="follow-btn" data-tool="${tool.name}">
                                ${isFollowing ? '⭐ Following' : '☆ Follow'}
                            </button>
                        ` : ''}
                    </div>
                    <p class="tool-desc">${tool.desc}</p>
                    <div class="tool-meta">
                        <span class="difficulty ${tool.difficulty}">${tool.difficulty}</span>
                        <span>${subcategory.replace(/_/g, ' ')}</span>
                    </div>
                    ${tool.command ? `
                        <div class="tool-command">
                            <code>${tool.command}</code>
                            <button class="copy-btn" onclick="navigator.clipboard.writeText('${tool.command}')">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                    ` : ''}
                </div>
            `;
            container.innerHTML += toolCard;
        });
    }

    renderSearchResults(results) {
        const container = document.querySelector('.tools-list');
        if (!container) return;

        container.innerHTML = '';
        
        if (results.length === 0) {
            container.innerHTML = '<p>No tools found matching your search</p>';
            return;
        }
        
        results.forEach(tool => {
            const toolCard = `
                <div class="tool-card">
                    <div class="tool-header">
                        <h3 class="tool-name">${tool.name}</h3>
                        ${!this.currentUser?.anonymous ? `
                            <button class="follow-btn" data-tool="${tool.name}">
                                ☆ Follow
                            </button>
                        ` : ''}
                    </div>
                    <p class="tool-desc">${tool.desc}</p>
                    <div class="tool-meta">
                        <span>${tool.platform} > ${tool.category}</span>
                        <span class="difficulty ${tool.difficulty}">${tool.difficulty}</span>
                    </div>
                </div>
            `;
            container.innerHTML += toolCard;
        });
    }

    async toggleFollow(toolName) {
        if (!this.currentUser || this.currentUser.anonymous) {
            alert('Please create an account to follow tools');
            return;
        }
        
        const isFollowing = this.currentUser.followed_tools?.includes(toolName);
        const endpoint = isFollowing ? 'unfollow' : 'follow';
        
        try {
            const response = await fetch(`${this.apiBase}/user/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tool: toolName })
            });
            
            if (response.ok) {
                // Update local state
                if (isFollowing) {
                    this.currentUser.followed_tools = this.currentUser.followed_tools.filter(t => t !== toolName);
                } else {
                    if (!this.currentUser.followed_tools) this.currentUser.followed_tools = [];
                    this.currentUser.followed_tools.push(toolName);
                }
                
                // Update UI
                const button = document.querySelector(`[data-tool="${toolName}"]`);
                if (button) {
                    button.textContent = isFollowing ? '☆ Follow' : '⭐ Following';
                }
            }
        } catch (error) {
            console.error('Error toggling follow:', error);
        }
    }
}

// Initialize the app
let hackerHub;
document.addEventListener('DOMContentLoaded', () => {
    hackerHub = new HackerHub();
    window.hackerHub = hackerHub; // Make available globally
});

// Utility functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        background: ${type === 'success' ? '#00ff88' : '#ff4757'};
        color: #050508;
        border-radius: 5px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .tool-command {
        background: rgba(0, 0, 0, 0.3);
        padding: 0.8rem;
        border-radius: 5px;
        margin-top: 1rem;
        font-family: 'Roboto Mono', monospace;
        font-size: 0.9rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .copy-btn {
        background: transparent;
        border: 1px solid var(--primary);
        color: var(--primary);
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .copy-btn:hover {
        background: var(--primary);
        color: var(--dark);
    }
`;
document.head.appendChild(style);
