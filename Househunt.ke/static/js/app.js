/**
 * HouseHunt Kenya — Interactive Frontend JavaScript
 * Powers dynamic filtering, favorite persistence, moving cost calculation,
 * comparison drawer, AI search, and modal interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
    initFavorites();
    initComparisonDrawer();
    initViewSwitchers();
    initModals();
    initAiAssistant();
    initCalculatorLiveSync();
});

/* ==========================================================================
   Favorites Management (AJAX + UI Feedback)
   ========================================================================== */
function initFavorites() {
    document.querySelectorAll('.btn-card-fav').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();

            const propId = btn.dataset.propId;
            if (!propId) return;

            try {
                const response = await fetch('/api/favorites/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ property_id: parseInt(propId) })
                });

                if (response.status === 401) {
                    window.location.href = '/auth?tab=login';
                    return;
                }

                const data = await response.json();
                if (data.success) {
                    btn.classList.toggle('active', data.favorited);
                    const icon = btn.querySelector('i');
                    if (icon) {
                        icon.className = data.favorited ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
                    }

                    // Update navigation counter
                    const badge = document.querySelector('.nav-badge-fav');
                    if (badge) {
                        badge.textContent = data.favorites_count;
                        badge.style.display = data.favorites_count > 0 ? 'inline-block' : 'none';
                    }
                }
            } catch (err) {
                console.error('Failed to toggle favorite:', err);
            }
        });
    });
}

/* ==========================================================================
   Property Comparison Drawer (Max 3 Properties)
   ========================================================================== */
function initComparisonDrawer() {
    let compareIds = JSON.parse(sessionStorage.getItem('househunt_compare') || '[]');
    updateCompareDrawerUI(compareIds);

    document.querySelectorAll('.btn-add-compare').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const propId = parseInt(btn.dataset.propId);
            const propTitle = btn.dataset.propTitle || `Property #${propId}`;

            if (compareIds.includes(propId)) {
                compareIds = compareIds.filter(id => id !== propId);
                btn.innerHTML = '<i class="fa-solid fa-code-compare"></i> Compare';
            } else {
                if (compareIds.length >= 3) {
                    alert('You can compare a maximum of 3 properties at a time.');
                    return;
                }
                compareIds.push(propId);
                btn.innerHTML = '<i class="fa-solid fa-check"></i> Added';
            }

            sessionStorage.setItem('househunt_compare', JSON.stringify(compareIds));
            updateCompareDrawerUI(compareIds);
        });
    });
}

function updateCompareDrawerUI(compareIds) {
    let drawer = document.getElementById('compareDrawer');
    if (!drawer) {
        drawer = document.createElement('div');
        drawer.id = 'compareDrawer';
        drawer.className = 'compare-drawer';
        drawer.innerHTML = `
            <div style="display:flex; align-items:center; gap:0.75rem;">
                <strong style="color:var(--gold-bright);"><i class="fa-solid fa-code-compare"></i> Comparing (<span id="compareCount">0</span>/3)</strong>
                <div id="compareItemsList" class="compare-drawer-items"></div>
            </div>
            <div style="display:flex; gap:0.5rem;">
                <button id="btnClearCompare" class="btn btn-secondary btn-sm">Clear</button>
                <a id="btnGoCompare" href="/compare" class="btn btn-primary btn-sm">Compare Now</a>
            </div>
        `;
        document.body.appendChild(drawer);

        document.getElementById('btnClearCompare')?.addEventListener('click', () => {
            sessionStorage.removeItem('househunt_compare');
            updateCompareDrawerUI([]);
            document.querySelectorAll('.btn-add-compare').forEach(b => {
                b.innerHTML = '<i class="fa-solid fa-code-compare"></i> Compare';
            });
        });
    }

    const countSpan = document.getElementById('compareCount');
    const goBtn = document.getElementById('btnGoCompare');
    if (countSpan) countSpan.textContent = compareIds.length;
    if (goBtn) goBtn.href = `/compare?ids=${compareIds.join(',')}`;

    if (compareIds.length > 0) {
        drawer.classList.add('active');
    } else {
        drawer.classList.remove('active');
    }
}

/* ==========================================================================
   Listings View Switcher (Grid vs List)
   ========================================================================== */
function initViewSwitchers() {
    const gridBtn = document.getElementById('viewGridBtn');
    const listBtn = document.getElementById('viewListBtn');
    const container = document.getElementById('propertiesGrid');

    if (!gridBtn || !listBtn || !container) return;

    gridBtn.addEventListener('click', () => {
        gridBtn.classList.add('active');
        listBtn.classList.remove('active');
        container.className = 'properties-grid';
    });

    listBtn.addEventListener('click', () => {
        listBtn.classList.add('active');
        gridBtn.classList.remove('active');
        container.className = 'properties-list';
    });
}

/* ==========================================================================
   Modals (Inquiry, Viewing Scheduler, Anti-Scam Report)
   ========================================================================== */
function initModals() {
    // Open Modal
    document.querySelectorAll('[data-modal-target]').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = trigger.getAttribute('data-modal-target');
            const modal = document.getElementById(modalId);
            if (modal) modal.classList.add('active');
        });
    });

    // Close Modal
    document.querySelectorAll('.btn-close-modal, .modal-overlay').forEach(el => {
        el.addEventListener('click', (e) => {
            if (e.target === el || el.classList.contains('btn-close-modal')) {
                document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
            }
        });
    });

    // Submit In-App Inquiry Form
    const inquiryForm = document.getElementById('inquiryForm');
    if (inquiryForm) {
        inquiryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = inquiryForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';

            const payload = {
                property_id: inquiryForm.property_id.value,
                name: inquiryForm.name.value,
                phone: inquiryForm.phone.value,
                email: inquiryForm.email.value,
                message: inquiryForm.message.value
            };

            try {
                const res = await fetch('/api/inquiries', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.success) {
                    alert(data.message);
                    inquiryForm.reset();
                    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
                } else {
                    alert(data.error || 'Failed to submit inquiry.');
                }
            } catch (err) {
                alert('An error occurred. Please try again.');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send Inquiry';
            }
        });
    }

    // Submit Schedule Viewing Form
    const viewingForm = document.getElementById('viewingForm');
    if (viewingForm) {
        viewingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = viewingForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Scheduling...';

            const payload = {
                property_id: viewingForm.property_id.value,
                date: viewingForm.date.value,
                time: viewingForm.time.value,
                notes: viewingForm.notes.value
            };

            try {
                const res = await fetch('/api/viewings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.status === 401) {
                    alert('Please sign in or create an account to schedule viewings.');
                    window.location.href = '/auth?tab=login';
                    return;
                }

                const data = await res.json();
                if (data.success) {
                    alert(data.message);
                    viewingForm.reset();
                    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
                } else {
                    alert(data.error || 'Failed to schedule viewing.');
                }
            } catch (err) {
                alert('Could not schedule viewing. Please try again.');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Confirm Viewing Request';
            }
        });
    }

    // Submit Anti-Scam Report Form
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = reportForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Reporting...';

            const payload = {
                property_id: reportForm.property_id.value,
                reason: reportForm.reason.value,
                details: reportForm.details.value
            };

            try {
                const res = await fetch('/api/reports', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.success) {
                    alert(data.message);
                    reportForm.reset();
                    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
                } else {
                    alert(data.error || 'Failed to report.');
                }
            } catch (err) {
                alert('Error submitting report.');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Report';
            }
        });

    // Star rating selector + review submission
    const starWrap = document.getElementById('starRatingInput');
    let selectedRating = 5;
    if (starWrap) {
        const stars = Array.from(starWrap.querySelectorAll('.star-option'));
        const paint = (val) => stars.forEach(s => s.classList.toggle('active', parseInt(s.dataset.value) <= val));
        paint(selectedRating);
        stars.forEach(s => s.addEventListener('click', () => { selectedRating = parseInt(s.dataset.value); paint(selectedRating); }));
    }
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const comment = document.getElementById('reviewComment').value.trim();
            if (!comment) { alert('Please write a short comment.'); return; }
            try {
                const res = await fetch('/api/reviews', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ property_id: parseInt(reviewForm.property_id.value), rating: selectedRating, comment })
                });
                const data = await res.json();
                if (data.success) { alert(data.message); window.location.reload(); }
                else { alert(data.error || 'Failed to submit review.'); }
            } catch (err) { alert('Could not submit review.'); }
        });
    }
    }
}

/* ==========================================================================
   AI House-Hunting Assistant
   ========================================================================== */
function initAiAssistant() {
    const aiForm = document.getElementById('aiAssistantForm');
    const aiInput = document.getElementById('aiAssistantInput');
    const aiResultsBox = document.getElementById('aiResultsBox');

    if (!aiForm || !aiInput) return;

    aiForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = aiInput.value.trim();
        if (!prompt) return;

        const submitBtn = aiForm.querySelector('button');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
        }

        try {
            const res = await fetch('/api/ai-search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });

            const data = await res.json();
            if (data.success) {
                if (aiResultsBox) {
                    aiResultsBox.style.display = 'block';
                    aiResultsBox.scrollIntoView({ behavior: 'smooth' });

                    const explHtml = data.filters.explanation.map(exp => `<li><i class="fa-solid fa-check" style="color:var(--emerald-verified)"></i> ${exp}</li>`).join('');
                    
                    let housesHtml = '';
                    if (data.results.length === 0) {
                        housesHtml = `
                            <div style="padding: 2rem; text-align: center; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-md);">
                                <i class="fa-solid fa-search" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                                <p>No available listings matched all criteria. Try adjusting rent budget or location.</p>
                            </div>
                        `;
                    } else {
                        housesHtml = `<div class="properties-grid" style="margin-top:1.5rem;">` +
                            data.results.map(p => `
                                <div class="property-card">
                                    <div class="card-image-wrap">
                                        <img src="${p.featured_image}" class="card-image" alt="${p.title}">
                                        ${p.is_property_verified ? '<span class="badge-verified-property"><i class="fa-solid fa-certificate"></i> Verified</span>' : ''}
                                    </div>
                                    <div class="card-body">
                                        <div class="card-location"><i class="fa-solid fa-location-dot"></i> ${p.estate}, ${p.town}</div>
                                        <h3 class="card-title"><a href="/properties/${p.id}">${p.title}</a></h3>
                                        <div class="card-price-row">
                                            <div class="card-rent">KSh ${p.monthly_rent.toLocaleString()} <span>/ month</span></div>
                                            <div class="card-upfront-pill">Move-in: <strong>KSh ${p.total_upfront_cost.toLocaleString()}</strong></div>
                                        </div>
                                        <a href="/properties/${p.id}" class="btn btn-outline btn-sm" style="margin-top:auto;">View Property Details</a>
                                    </div>
                                </div>
                            `).join('') + `</div>`;
                    }

                    aiResultsBox.innerHTML = `
                        <div style="background:var(--bg-card); border:1px solid var(--gold-border); border-radius:var(--radius-lg); padding:1.5rem; margin-bottom:2.5rem;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                                <h3 style="color:var(--gold-bright); font-size:1.2rem;"><i class="fa-solid fa-robot"></i> AI Assistant Search Results (${data.results_count} found)</h3>
                                <button onclick="document.getElementById('aiResultsBox').style.display='none'" class="btn btn-secondary btn-sm">&times; Close</button>
                            </div>
                            <div style="background:rgba(9,14,26,0.8); padding:0.85rem 1.25rem; border-radius:var(--radius-md); margin-bottom:1rem;">
                                <strong style="font-size:0.82rem; text-transform:uppercase; color:var(--text-muted); display:block; margin-bottom:0.4rem;">How AI understood your request:</strong>
                                <ul style="list-style:none; display:flex; flex-wrap:wrap; gap:1rem; font-size:0.88rem; color:var(--text-main);">
                                    ${explHtml}
                                </ul>
                            </div>
                            ${housesHtml}
                        </div>
                    `;
                }
            }
        } catch (err) {
            console.error('AI search failed', err);
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Find';
            }
        }
    });
}

/* ==========================================================================
   Upfront Move-in Cost Calculator Live Sync
   ========================================================================== */
function initCalculatorLiveSync() {
    const rentInput = document.getElementById('calcRent');
    const depositInput = document.getElementById('calcDeposit');
    const waterInput = document.getElementById('calcWater');
    const electricityInput = document.getElementById('calcElectricity');
    const garbageInput = document.getElementById('calcGarbage');
    const moverInput = document.getElementById('calcMover');
    const agentInput = document.getElementById('calcAgent');
    const budgetInput = document.getElementById('calcBudget');

    const totalDisplay = document.getElementById('calcTotalUpfront');
    const breakdownPills = document.getElementById('calcBreakdownPills');
    const budgetAlert = document.getElementById('calcBudgetAlert');

    if (!rentInput || !totalDisplay) return;

    function recalculate() {
        const rent = parseFloat(rentInput.value) || 0;
        const deposit = parseFloat(depositInput.value) || 0;
        const water = parseFloat(waterInput ? waterInput.value : 0) || 0;
        const electricity = parseFloat(electricityInput ? electricityInput.value : 0) || 0;
        const garbage = parseFloat(garbageInput ? garbageInput.value : 0) || 0;
        const mover = parseFloat(moverInput ? moverInput.value : 0) || 0;
        const agent = parseFloat(agentInput ? agentInput.value : 0) || 0;
        const budget = parseFloat(budgetInput ? budgetInput.value : 0) || 0;

        const total = rent + deposit + water + electricity + garbage + mover + agent;
        totalDisplay.textContent = `KSh ${total.toLocaleString()}`;

        if (budgetAlert) {
            if (budget > 0) {
                if (total > budget) {
                    const deficit = total - budget;
                    budgetAlert.style.display = 'block';
                    budgetAlert.className = 'alert alert-danger';
                    budgetAlert.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> <strong>Exceeds Your Upfront Savings:</strong> You need an additional <strong>KSh ${deficit.toLocaleString()}</strong> before move-in day.`;
                } else {
                    const surplus = budget - total;
                    budgetAlert.style.display = 'block';
                    budgetAlert.className = 'alert alert-success';
                    budgetAlert.innerHTML = `<i class="fa-solid fa-circle-check"></i> <strong>Within Your Budget:</strong> You have a safe cushion of <strong>KSh ${surplus.toLocaleString()}</strong> remaining.`;
                }
            } else {
                budgetAlert.style.display = 'none';
            }
        }
    }

    [rentInput, depositInput, waterInput, electricityInput, garbageInput, moverInput, agentInput, budgetInput].forEach(inp => {
        if (inp) inp.addEventListener('input', recalculate);
    });

    // Property preset selector on calculator page
    const presetSelect = document.getElementById('calcPropertyPreset');
    if (presetSelect) {
        presetSelect.addEventListener('change', () => {
            const opt = presetSelect.options[presetSelect.selectedIndex];
            if (!opt || !opt.dataset.rent) return;

            rentInput.value = opt.dataset.rent || 0;
            depositInput.value = opt.dataset.deposit || 0;
            if (waterInput) waterInput.value = opt.dataset.water || 0;
            if (electricityInput) electricityInput.value = opt.dataset.electricity || 0;
            if (garbageInput) garbageInput.value = opt.dataset.garbage || 0;
            if (agentInput) agentInput.value = opt.dataset.agent || 0;

            recalculate();
        });
    }

    recalculate();
}

