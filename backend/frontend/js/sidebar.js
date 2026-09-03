// document.addEventListener("DOMContentLoaded", () => {
//     const container = document.getElementById("sidebar-container");
//     if (!container) return;

//     // Route guard: Check if user is logged in
//     const token = localStorage.getItem("access_token");
//     if (!token && !window.location.pathname.endsWith("login.html") && !window.location.pathname.endsWith("register.html")) {
//         window.location.href = "login.html";
//         return;
//     }

//     // Render sidebar HTML
//     container.innerHTML = `
//         <div class="sidebar-brand">
//             <span class="brand-logo">☕</span>
//             <span class="brand-text">Monika G Cafe</span>
//         </div>
//         <ul class="sidebar-menu">
//             <li><a href="dashboard.html" id="nav-dashboard">📊 Dashboard</a></li>
//             <li><a href="menu.html" id="nav-menu">🍟 Menu Catalog</a></li>
//             <li><a href="orders.html" id="nav-orders">🛒 Order Desk</a></li>
//             <li><a href="billing.html" id="nav-billing">🧾 Billing / Invoice</a></li>
//             <li><a href="inventory.html" id="nav-inventory">📦 Inventory</a></li>
//             <li><a href="employees.html" id="nav-employees">👥 Employees</a></li>
//             <li><a href="customer.html" id="nav-customer">👤 Customers</a></li>
//             <li><a href="reservation.html" id="nav-reservation">📅 Reservations</a></li>
//             <li><a href="feedback.html" id="nav-feedback">💬 Feedback</a></li>
//             <li><a href="report.html" id="nav-report">📈 Sales Reports</a></li>
//         </ul>
//         <div class="sidebar-footer">
//             <button id="logoutBtn" class="btn btn-logout">🚪 Logout</button>
//         </div>
//     `;

//     // Highlight active link based on current path
//     const currentPath = window.location.pathname.split("/").pop();
//     const navLinks = container.querySelectorAll(".sidebar-menu a");
//     navLinks.forEach(link => {
//         if (link.getAttribute("href") === currentPath) {
//             link.classList.add("active");
//         }
//     });

//     // Logout listener
//     const logoutBtn = document.getElementById("logoutBtn");
//     if (logoutBtn) {
//         logoutBtn.addEventListener("click", () => {
//             localStorage.removeItem("access_token");
//             window.location.href = "login.html";
//         });
//     }
// });

// async function fetchAllCustomerLogs() {
//     const directoryGrid = document.getElementById("customerDirectoryGrid");
//     try {
//         const response = await apiRequest("/customers");

//         // Debugging: This will print the exact structure to your F12 Console
//         console.log("[API Debug] /customers response data:", response);

//         if (!response) {
//             directoryGrid.innerHTML = `<tr><td colspan="5" style="text-align: center;" class="error-text">No response from server. Check auth token status.</td></tr>`;
//             return;
//         }

//         // Extract array if backend wrapped it inside an object wrapper (e.g., response.data or response.customers)
//         let customersArray = null;
//         if (Array.isArray(response)) {
//             customersArray = response;
//         } else if (response && Array.isArray(response.data)) {
//             customersArray = response.data;
//         } else if (response && Array.isArray(response.customers)) {
//             customersArray = response.customers;
//         }

//         // If we found a valid list, render it out to the grid matrix
//         if (customersArray) {
//             if (customersArray.length === 0) {
//                 directoryGrid.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-secondary);">No customer profiles found in database.</td></tr>`;
//             } else {
//                 directoryGrid.innerHTML = customersArray.map(user => {
//                     // Fallback keys if your schema uses 'user_id' instead of 'id'
//                     const userId = user.id || user.user_id;
//                     const phone = user.phone_profile || user.phone || 'N/A';

//                     return `
//                         <tr>
//                             <td><strong>#${userId}</strong></td>
//                             <td>${user.first_name || ''} ${user.last_name || ''}</td>
//                             <td>${user.email || 'N/A'}</td>
//                             <td>${phone}</td>
//                             <td>
//                                 <button class="btn btn-secondary" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;" 
//                                     onclick="selectCustomerForLookup(${userId})">
//                                     🔍 View Metrics
//                                 </button>
//                             </td>
//                         </tr>
//                     `;
//                 }).join("");
//             }
//         } else {
//             // Handle explicit backend error details returned from your schemas
//             const errMsg = response.detail || "Received data is not an array list.";
//             directoryGrid.innerHTML = `<tr><td colspan="5" style="text-align: center;" class="error-text">Backend error: ${errMsg}</td></tr>`;
//         }
//     } catch (err) {
//         console.error("[Fatal Log Error]:", err);
//         directoryGrid.innerHTML = `<tr><td colspan="5" style="text-align: center;" class="error-text">Network error pulling operational registry.</td></tr>`;
//     }
// }

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("sidebar-container");
    if (!container) return;

    // Route guard: Check if user is logged in
    const token = localStorage.getItem("access_token");
    if (!token && !window.location.pathname.endsWith("login.html") && !window.location.pathname.endsWith("register.html")) {
        window.location.href = "login.html";
        return;
    }

    // Inject self-contained styles so the sidebar doesn't depend on main.css
    // definitions. Warm, cozy cafe look: cream surface, wood-brown accents,
    // soft rounded shapes, serif brand name.
    if (!document.getElementById("sidebar-cozy-styles")) {
        const style = document.createElement("style");
        style.id = "sidebar-cozy-styles";
        style.textContent = `
            .sidebar {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                bottom: 0 !important;
                height: 100vh !important;
                width: 270px !important;
                border-radius: 0 !important;
                background: #062b21 !important;
                background-image: linear-gradient(180deg, rgba(6, 43, 33, 0.98) 0%, rgba(4, 26, 20, 0.99) 100%) !important;
                color: #f0fdf4 !important;
                display: flex !important;
                flex-direction: column !important;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                border-right: 1px solid rgba(16, 185, 129, 0.2) !important;
                box-shadow: 4px 0 25px rgba(0, 0, 0, 0.4) !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
                padding: 1.75rem 1.25rem !important;
                z-index: 100 !important;
            }

            .sidebar-brand {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 14px;
                margin-bottom: 16px;
                background: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.25);
                border-radius: 14px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }
            .brand-logo {
                font-size: 1.7rem;
                flex-shrink: 0;
            }
            .brand-text {
                font-family: 'Outfit', sans-serif !important;
                font-weight: 700 !important;
                font-size: 1.15rem !important;
                color: #ffffff !important;
                background: linear-gradient(135deg, #059669 0%, #10b981 50%, #f59e0b 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .sidebar-menu {
                list-style: none;
                margin: 0;
                padding: 0 4px;
                flex: 1;
                overflow-y: auto;
            }
            .sidebar-section-header {
                font-size: 0.68rem;
                font-weight: 700;
                color: #f59e0b;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                margin: 14px 10px 6px 10px;
            }
            .sidebar-menu li { margin-bottom: 4px; }
            .sidebar-menu a {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 14px;
                border-radius: 10px;
                color: #a7f3d0 !important;
                text-decoration: none !important;
                font-size: 0.88rem !important;
                font-weight: 500;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                border: 1px solid transparent;
            }
            .sidebar-menu a:hover {
                background: rgba(16, 185, 129, 0.14) !important;
                color: #ffffff !important;
                border-color: rgba(16, 185, 129, 0.3);
                transform: translateX(4px);
            }
            .sidebar-menu a.active {
                background: linear-gradient(135deg, #059669 0%, #10b981 50%, #f59e0b 100%) !important;
                color: #ffffff !important;
                font-weight: 600;
                box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
            }

            .sidebar-footer {
                padding-top: 14px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
            .btn-logout {
                width: 100%;
                background: rgba(239, 68, 68, 0.15) !important;
                border: 1px solid rgba(239, 68, 68, 0.3) !important;
                color: #ef4444 !important;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-weight: 600 !important;
                font-size: 0.85rem !important;
                border-radius: 10px !important;
                padding: 10px 14px !important;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .btn-logout:hover {
                background: #ef4444 !important;
                color: #ffffff !important;
                box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
            }
        `;
        document.head.appendChild(style);
    }

    // Render sidebar HTML
    container.innerHTML = `
        <div class="sidebar-brand">
            <span class="brand-logo">☕</span>
            <div>
                <div class="brand-text">Monika G Cafe</div>
                <span class="version-badge" style="margin-top: 2px; font-size: 0.68rem; padding: 2px 8px;">v1.1.0</span>
            </div>
        </div>
        <ul class="sidebar-menu">
            <div class="sidebar-section-header">MAIN HUB</div>
            <li><a href="dashboard.html" id="nav-dashboard">📊 Dashboard</a></li>
            
            <div class="sidebar-section-header">OPERATIONS</div>
            <li><a href="menu.html" id="nav-menu">🍟 Menu Catalog</a></li>
            <li><a href="orders.html" id="nav-orders">🛒 Order Desk</a></li>
            <li><a href="billing.html" id="nav-billing">🧾 Billing / Invoice</a></li>
            <li><a href="inventory.html" id="nav-inventory">📦 Inventory Desk</a></li>
            
            <div class="sidebar-section-header">MANAGEMENT</div>
            <li><a href="employees.html" id="nav-employees">👥 Employees</a></li>
            <li><a href="customer.html" id="nav-customer">👤 Customers</a></li>
            <li><a href="reservation.html" id="nav-reservation">📅 Reservations</a></li>
            
            <div class="sidebar-section-header">INSIGHTS</div>
            <li><a href="feedback.html" id="nav-feedback">💬 Feedback</a></li>
            <li><a href="report.html" id="nav-report">📈 Sales Reports</a></li>
        </ul>
        <div class="sidebar-footer">
            <div style="font-size: 0.72rem; color: #a7f3d0; text-align: center; margin-bottom: 8px;">Monika G Cafe System v1.1.0</div>
            <button id="logoutBtn" class="btn btn-logout">🚪 Logout</button>
        </div>
    `;

    // Highlight active link based on current path
    const currentPath = window.location.pathname.split("/").pop();
    const navLinks = container.querySelectorAll(".sidebar-menu a");
    navLinks.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });

    // Logout listener
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("access_token");
            window.location.href = "login.html";
        });
    }
});

async function fetchAllCustomerLogs() {
    const directoryGrid = document.getElementById("customerDirectoryGrid");
    try {
        const response = await apiRequest("/customers");

        // Debugging: This will print the exact structure to your F12 Console
        console.log("[API Debug] /customers response data:", response);

        if (!response) {
            directoryGrid.innerHTML = `<tr><td colspan="5" style="text-align: center;" class="error-text">No response from server. Check auth token status.</td></tr>`;
            return;
        }

        // Extract array if backend wrapped it inside an object wrapper (e.g., response.data or response.customers)
        let customersArray = null;
        if (Array.isArray(response)) {
            customersArray = response;
        } else if (response && Array.isArray(response.data)) {
            customersArray = response.data;
        } else if (response && Array.isArray(response.customers)) {
            customersArray = response.customers;
        }

        // If we found a valid list, render it out to the grid matrix
        if (customersArray) {
            if (customersArray.length === 0) {
                directoryGrid.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-secondary);">No customer profiles found in database.</td></tr>`;
            } else {
                directoryGrid.innerHTML = customersArray.map(user => {
                    // Fallback keys if your schema uses 'user_id' instead of 'id'
                    const userId = user.id || user.user_id;
                    const phone = user.phone_profile || user.phone || 'N/A';

                    return `
                        <tr>
                            <td><strong>#${userId}</strong></td>
                            <td>${user.first_name || ''} ${user.last_name || ''}</td>
                            <td>${user.email || 'N/A'}</td>
                            <td>${phone}</td>
                            <td>
                                <button class="btn btn-secondary" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;" 
                                    onclick="selectCustomerForLookup(${userId})">
                                    🔍 View Metrics
                                </button>
                            </td>
                        </tr>
                    `;
                }).join("");
            }
        } else {
            // Handle explicit backend error details returned from your schemas
            const errMsg = response.detail || "Received data is not an array list.";
            directoryGrid.innerHTML = `<tr><td colspan="5" style="text-align: center;" class="error-text">Backend error: ${errMsg}</td></tr>`;
        }
    } catch (err) {
        console.error("[Fatal Log Error]:", err);
        directoryGrid.innerHTML = `<tr><td colspan="5" style="text-align: center;" class="error-text">Network error pulling operational registry.</td></tr>`;
    }
}