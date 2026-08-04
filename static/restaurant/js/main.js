(() => {
    'use strict';

    const body = document.body;
    const lang = body.dataset.lang || 'ar';
    const currency = body.dataset.currency || '₪';
    const storageKey = 'fries-station-cart';

    const safeJSON = (value, fallback) => {
        try { return JSON.parse(value); } catch (_) { return fallback; }
    };

    const parsePrice = value => {
        const arabicDigits = '٠١٢٣٤٥٦٧٨٩';
        const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
        let normalized = String(value ?? '')
            .replace(/[٠-٩]/g, digit => arabicDigits.indexOf(digit))
            .replace(/[۰-۹]/g, digit => persianDigits.indexOf(digit))
            .replace(/٬/g, '')
            .replace(/٫/g, '.')
            .replace(/[^0-9,.-]/g, '');
        if (normalized.includes(',')) {
            if (normalized.includes('.')) {
                normalized = normalized.replace(/,/g, '');
            } else {
                const commaParts = normalized.split(',');
                normalized = commaParts.length === 2 && commaParts[1].length <= 2
                    ? commaParts.join('.')
                    : commaParts.join('');
            }
        }
        const number = Number(normalized);
        return Number.isFinite(number) ? Math.max(0, number) : 0;
    };

    let storedValue = null;
    try { storedValue = window.localStorage.getItem(storageKey); } catch (_) { storedValue = null; }
    const storedCart = safeJSON(storedValue, []);
    let cart = Array.isArray(storedCart) ? storedCart
        .filter(item => item && typeof item === 'object')
        .map(item => ({
            id: String(item.id || ''),
            nameAr: String(item.nameAr || ''),
            nameEn: String(item.nameEn || ''),
            price: parsePrice(item.price),
            priceTextAr: String(item.priceTextAr || ''),
            priceTextEn: String(item.priceTextEn || ''),
            priced: item.priced !== false,
            sizeId: String(item.sizeId || ''),
            sizeAr: String(item.sizeAr || ''),
            sizeEn: String(item.sizeEn || ''),
            qty: Number.isFinite(Number(item.qty)) ? Math.min(99, Math.max(1, Math.trunc(Number(item.qty)))) : 1,
        }))
        .filter(item => item.id && (item.nameAr || item.nameEn)) : [];

    const saveCart = () => {
        try { localStorage.setItem(storageKey, JSON.stringify(cart)); } catch (_) { /* Storage can be unavailable. */ }
        renderCart();
    };

    const formatPrice = value => {
        const number = parsePrice(value);
        return `${number.toFixed(number % 1 ? 2 : 0)} ${currency}`;
    };

    const itemSize = item => (lang === 'ar' ? item.sizeAr : (item.sizeEn || item.sizeAr));
    const itemName = item => {
        const base = lang === 'ar' ? item.nameAr : item.nameEn;
        const size = itemSize(item);
        return size ? `${base} — ${size}` : base;
    };
    const itemPriceLabel = item => {
        if (item.priced) return formatPrice(item.price);
        return lang === 'ar' ? item.priceTextAr : (item.priceTextEn || item.priceTextAr);
    };

    // Looked up lazily so the cart keeps working even if a browser extension
    // (translate, dark mode, ...) replaces parts of the DOM after load.
    let drawer = document.querySelector('.order-drawer');
    const getDrawer = () => {
        if (!drawer || !drawer.isConnected) drawer = document.querySelector('.order-drawer');
        return drawer;
    };
    const cartFeedback = document.getElementById('cart-feedback');
    const clearCartButton = document.getElementById('clear-cart');
    const fulfillmentInputs = document.querySelectorAll('input[name="fulfillment"]');
    const deliveryFields = document.getElementById('delivery-fields');
    const orderName = document.getElementById('order-name');
    const orderPhone = document.getElementById('order-phone');
    const orderAddress = document.getElementById('order-address');
    let lastFocusedElement = null;
    let feedbackTimer = null;
    let inertBackgroundElements = [];

    const drawerFocusable = () => [...(getDrawer()?.querySelectorAll('button, a[href], input, textarea, [tabindex]:not([tabindex="-1"])') || [])]
        .filter(element => !element.disabled && element.offsetParent !== null);

    const openCart = () => {
        const panel = getDrawer();
        if (!panel) return;
        setNavOpen(false);
        lastFocusedElement = document.activeElement;
        inertBackgroundElements = [...body.children].filter(element => (
            element !== panel
            && !element.hasAttribute('inert')
            && !['SCRIPT', 'STYLE'].includes(element.tagName)
        ));
        inertBackgroundElements.forEach(element => element.setAttribute('inert', ''));
        panel.hidden = false;
        panel.removeAttribute('inert');
        panel.classList.add('is-open');
        panel.setAttribute('aria-hidden', 'false');
        body.classList.add('drawer-open');
        drawerFocusable()[0]?.focus();
    };

    const closeCart = () => {
        const panel = getDrawer();
        if (!panel) return;
        panel.classList.remove('is-open');
        panel.setAttribute('aria-hidden', 'true');
        panel.setAttribute('inert', '');
        panel.hidden = true;
        body.classList.remove('drawer-open');
        inertBackgroundElements.forEach(element => element.removeAttribute('inert'));
        inertBackgroundElements = [];
        if (lastFocusedElement instanceof HTMLElement) lastFocusedElement.focus();
    };

    const showCartFeedback = message => {
        if (!cartFeedback) return;
        cartFeedback.textContent = message;
        cartFeedback.classList.add('show');
        window.clearTimeout(feedbackTimer);
        feedbackTimer = window.setTimeout(() => cartFeedback.classList.remove('show'), 3200);
    };

    const pulseCartButtons = () => {
        document.querySelectorAll('.header-whatsapp, .floating-whatsapp').forEach(button => {
            button.classList.remove('cart-pulse');
            void button.offsetWidth; // Restart the animation on repeated adds.
            button.classList.add('cart-pulse');
            window.setTimeout(() => button.classList.remove('cart-pulse'), 750);
        });
    };

    const selectedFulfillment = () => document.querySelector('input[name="fulfillment"]:checked')?.value || 'pickup';

    const updateDeliveryFields = () => {
        const isDelivery = selectedFulfillment() === 'delivery';
        deliveryFields?.classList.toggle('hidden', !isDelivery);
        [orderName, orderPhone, orderAddress].forEach(field => {
            if (field) field.required = isDelivery;
        });
    };

    fulfillmentInputs.forEach(input => input.addEventListener('change', () => {
        updateDeliveryFields();
        if (selectedFulfillment() === 'delivery') orderName?.focus();
    }));

    const renderCart = () => {
        const cartItems = document.getElementById('cart-items');
        const cartEmpty = document.getElementById('cart-empty');
        const cartTotal = document.getElementById('cart-total');
        if (!cartItems || !cartEmpty || !cartTotal) return;
        const totalQty = cart.reduce((sum, item) => sum + item.qty, 0);
        const total = cart.reduce((sum, item) => sum + (item.priced ? Number(item.price) * item.qty : 0), 0);
        const hasUnpricedItems = cart.some(item => !item.priced);
        document.querySelectorAll('.cart-count, .floating-count').forEach(counter => {
            counter.textContent = totalQty;
            counter.classList.toggle('hidden', totalQty === 0);
        });
        document.querySelectorAll('.floating-whatsapp').forEach(button => {
            button.classList.toggle('is-empty', totalQty === 0);
        });
        cartTotal.textContent = hasUnpricedItems
            ? (total > 0 ? `${formatPrice(total)} + ${lang === 'ar' ? 'عرض يُؤكد سعره' : 'offer price to confirm'}` : (lang === 'ar' ? 'يُحدد عند التأكيد' : 'Confirmed on contact'))
            : formatPrice(total);
        cartEmpty.classList.toggle('hidden', cart.length > 0);
        clearCartButton?.classList.toggle('hidden', cart.length === 0);

        cartItems.innerHTML = cart.map(item => `
            <article class="cart-item" data-cart-id="${escapeHTML(item.id)}">
                <div>
                    <h3>${escapeHTML(lang === 'ar' ? item.nameAr : item.nameEn)}</h3>
                    ${itemSize(item) ? `<span class="cart-size">${escapeHTML(itemSize(item))}</span>` : ''}
                    <span class="cart-item-price">${escapeHTML(itemPriceLabel(item))}</span>
                </div>
                <div class="qty-control">
                    <button type="button" data-cart-action="decrease" aria-label="${lang === 'ar' ? 'تقليل الكمية' : 'Decrease quantity'}">−</button>
                    <strong>${item.qty}</strong>
                    <button type="button" data-cart-action="increase" aria-label="${lang === 'ar' ? 'زيادة الكمية' : 'Increase quantity'}">+</button>
                    <button type="button" class="remove-item" data-cart-action="remove" aria-label="${lang === 'ar' ? 'حذف الطبق' : 'Remove item'}">×</button>
                </div>
            </article>
        `).join('');
    };

    const escapeHTML = value => String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');

    const selectedSize = button => {
        // The picker lives in the same card, keyed by the dish id.
        const itemId = button.dataset.item;
        if (!itemId) return null;
        return document.querySelector(
            `.size-picker input[name="size-${CSS.escape(itemId)}"]:checked`,
        );
    };

    const buttonToCartItem = button => {
        const isOffer = button.dataset.offer === 'true';
        const priceTextAr = button.dataset.priceTextAr || '';
        const priceTextEn = button.dataset.priceTextEn || priceTextAr;
        const activePriceText = lang === 'ar' ? priceTextAr : priceTextEn;
        const fixedPricePattern = /^\s*[\d٠-٩۰-۹]+(?:[.,٫][\d٠-٩۰-۹]{1,2})?\s*(?:₪|ILS|شيكل)?\s*$/i;
        const offerHasFixedPrice = isOffer && fixedPricePattern.test(activePriceText) && parsePrice(activePriceText) > 0;
        const size = isOffer ? null : selectedSize(button);
        const itemId = String(button.dataset.id || '');
        return {
            id: size ? `${itemId}:${size.value}` : itemId,
            itemId,
            sizeId: size ? String(size.value) : '',
            sizeAr: size ? (size.dataset.sizeAr || '') : '',
            sizeEn: size ? (size.dataset.sizeEn || '') : '',
            nameAr: button.dataset.nameAr || '',
            nameEn: button.dataset.nameEn || '',
            price: isOffer
                ? (offerHasFixedPrice ? parsePrice(activePriceText) : 0)
                : parsePrice(size ? size.dataset.price : button.dataset.price),
            priceTextAr,
            priceTextEn,
            priced: !isOffer || offerHasFixedPrice,
            qty: 1,
        };
    };

    const syncCartWithPage = () => {
        const availableButtons = [...document.querySelectorAll('.js-add-item[data-id]')];
        const byId = new Map(availableButtons.map(button => [String(button.dataset.id), button]));
        cart = cart
            .filter(item => byId.has(item.itemId || item.id))
            .map(item => {
                // Re-read the dish from the page, but keep the size this line
                // was added with rather than whatever the card shows now.
                const button = byId.get(item.itemId || item.id);
                const fresh = buttonToCartItem(button);
                if (!item.sizeId) return {...fresh, qty: Math.min(99, Math.max(1, item.qty))};
                const picker = document.querySelector(
                    `.size-picker input[name="size-${CSS.escape(item.itemId || item.id)}"][value="${CSS.escape(item.sizeId)}"]`,
                );
                if (!picker) return null;   // that size is gone from the menu
                return {
                    ...fresh,
                    id: `${item.itemId || item.id}:${item.sizeId}`,
                    sizeId: item.sizeId,
                    sizeAr: picker.dataset.sizeAr || '',
                    sizeEn: picker.dataset.sizeEn || '',
                    price: parsePrice(picker.dataset.price),
                    qty: Math.min(99, Math.max(1, item.qty)),
                };
            })
            .filter(Boolean);
    };

    document.addEventListener('click', event => {
        const target = event.target instanceof Element ? event.target : null;
        if (!target) return;
        const openButton = target.closest('.js-open-cart');
        if (openButton) {
            event.preventDefault();
            openCart();
            return;
        }

        if (target.closest('.js-close-cart')) {
            closeCart();
            return;
        }

        const addButton = target.closest('.js-add-item');
        if (addButton) {
            const freshItem = buttonToCartItem(addButton);
            const existing = cart.find(item => item.id === freshItem.id);
            if (existing) {
                Object.assign(existing, freshItem, {qty: Math.min(99, existing.qty + 1)});
            } else {
                cart.push(freshItem);
            }
            saveCart();
            addButton.classList.add('added');
            const addedName = itemName(freshItem);
            showCartFeedback(
                lang === 'ar'
                    ? `تمت إضافة ${addedName} إلى السلة`
                    : `${addedName} was added to your cart`,
            );
            navigator.vibrate?.(35);
            const addLabel = addButton.querySelector('.add-label');
            const originalLabel = addLabel?.textContent;
            if (addLabel) addLabel.textContent = lang === 'ar' ? 'تمت الإضافة' : 'Added';
            pulseCartButtons();
            setTimeout(() => {
                addButton.classList.remove('added');
                if (addLabel && originalLabel) addLabel.textContent = originalLabel;
            }, 900);
            return;
        }

        const cartAction = target.closest('[data-cart-action]');
        if (cartAction) {
            const row = cartAction.closest('[data-cart-id]');
            const item = cart.find(entry => entry.id === row?.dataset.cartId);
            if (!item) return;
            const action = cartAction.dataset.cartAction;
            if (action === 'increase') item.qty = Math.min(99, item.qty + 1);
            if (action === 'decrease') item.qty = Math.max(1, item.qty - 1);
            if (action === 'remove') cart = cart.filter(entry => entry.id !== item.id);
            saveCart();
        }
    });

    clearCartButton?.addEventListener('click', () => {
        if (!cart.length) return;
        const approved = window.confirm(lang === 'ar' ? 'هل تريد مسح جميع الأصناف من الطلب؟' : 'Clear all items from the order?');
        if (!approved) return;
        cart = [];
        saveCart();
        showCartFeedback(lang === 'ar' ? 'تم مسح الطلب.' : 'Order cleared.');
    });

    // The order is priced by the server. This sends dish ids and quantities
    // only — any price held in the page or in localStorage is ignored, which
    // is what stops a customer from editing what the restaurant is owed.
    const orderEndpoint = body.dataset.orderUrl || '/order/';
    const csrfToken = () => document.querySelector('#csrf-holder input[name=csrfmiddlewaretoken]')?.value || '';

    const t = (ar, en) => (lang === 'ar' ? ar : en);

    // Opens the restaurant's own WhatsApp chat with the order number and a
    // link to the order page.
    //
    // The receipt image is deliberately not pushed through the share sheet:
    // that sheet cannot address the restaurant's chat, so whether anything
    // arrived depended on the customer picking the right conversation. The
    // link always lands in the right chat, and the image stays available on
    // the order page it points to.
    //
    // A top-level navigation rather than window.open on purpose: opening a
    // window needs transient user activation, and that has already expired
    // by the time the order request comes back, so it would be blocked.
    const openRestaurantChat = data => {
        if (!data.whatsapp_url) return false;
        window.location.href = data.whatsapp_url;
        return true;
    };

    const sendButton = document.getElementById('send-whatsapp');
    sendButton?.addEventListener('click', async () => {
        if (!cart.length) {
            showCartFeedback(t('أضف طبقًا واحدًا على الأقل.', 'Add at least one dish.'));
            return;
        }

        const fulfillment = selectedFulfillment();
        const isDelivery = fulfillment === 'delivery';
        const name = orderName?.value.trim() || '';
        const phone = orderPhone?.value.trim() || '';
        const address = orderAddress?.value.trim() || '';
        const notes = document.getElementById('order-notes')?.value.trim() || '';

        if (isDelivery && (!name || !phone || !address)) {
            showCartFeedback(t('أدخل الاسم ورقم الجوال وعنوان التوصيل.', 'Enter the customer name, phone and delivery address.'));
            (!name ? orderName : !phone ? orderPhone : orderAddress)?.focus();
            return;
        }
        const phoneDigits = phone.replace(/\D/g, '');
        const phoneHasInvalidCharacters = /[^0-9٠-٩۰-۹+\-()\s]/.test(phone);
        if (isDelivery && (phoneHasInvalidCharacters || phoneDigits.length < 7 || phoneDigits.length > 15)) {
            showCartFeedback(t('أدخل رقم جوال صحيحًا للتوصيل.', 'Enter a valid delivery phone number.'));
            orderPhone?.focus();
            return;
        }

        const originalLabel = sendButton.innerHTML;
        sendButton.disabled = true;
        sendButton.textContent = t('جارٍ إنشاء الطلب…', 'Creating order…');

        try {
            const response = await fetch(orderEndpoint, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken()},
                body: JSON.stringify({
                    items: cart.map(item => ({
                        id: item.itemId || item.id,
                        size: item.sizeId || undefined,
                        qty: item.qty,
                    })),
                    fulfillment,
                    name,
                    phone,
                    address,
                    notes,
                }),
            });

            let data = {};
            try { data = await response.json(); } catch (_) { data = {}; }

            if (!response.ok) {
                showCartFeedback(data.error || t('تعذر إنشاء الطلب. حاول مجددًا.', 'Could not create the order. Try again.'));
                return;
            }

            // The order is recorded on the server now, so the cart has done
            // its job. Clear it before going anywhere, because assigning
            // location.href ends this page's work immediately.
            cart = [];
            saveCart();
            closeCart();

            if (!openRestaurantChat(data)) {
                // The order exists but there is nowhere to send it. Show the
                // number so the customer is not left with a lost order.
                showCartFeedback(t(
                    `تم تسجيل الطلب ${data.code} لكن رقم واتساب غير مضبوط. أبلغ المطعم بالرقم.`,
                    `Order ${data.code} was saved but no WhatsApp number is configured. Give the restaurant this number.`,
                ));
            }
        } catch (_) {
            showCartFeedback(t('تعذر الاتصال بالخادم. تحقق من الإنترنت.', 'Could not reach the server. Check your connection.'));
        } finally {
            sendButton.disabled = false;
            sendButton.innerHTML = originalLabel;
        }
    });

    // Mobile navigation
    const navToggle = document.querySelector('.nav-toggle');
    const nav = document.querySelector('.main-nav');
    const mobileNavQuery = window.matchMedia('(max-width: 820px)');
    const setNavOpen = open => {
        if (!nav || !navToggle) return;
        const shouldOpen = Boolean(open && mobileNavQuery.matches);
        nav.classList.toggle('open', shouldOpen);
        navToggle.setAttribute('aria-expanded', String(shouldOpen));
        navToggle.setAttribute(
            'aria-label',
            shouldOpen ? navToggle.dataset.closeLabel : navToggle.dataset.openLabel,
        );
        body.classList.toggle('nav-open', shouldOpen);
        if (mobileNavQuery.matches) {
            nav.setAttribute('aria-hidden', String(!shouldOpen));
        } else {
            nav.removeAttribute('aria-hidden');
        }
    };
    navToggle?.addEventListener('click', event => {
        event.stopPropagation();
        setNavOpen(!nav?.classList.contains('open'));
    });
    nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
        setNavOpen(false);
    }));
    document.addEventListener('click', event => {
        if (!nav?.classList.contains('open')) return;
        const target = event.target instanceof Element ? event.target : null;
        if (target && !target.closest('.main-nav') && !target.closest('.nav-toggle')) setNavOpen(false);
    });
    const handleNavViewportChange = () => setNavOpen(false);
    mobileNavQuery.addEventListener?.('change', handleNavViewportChange);
    window.addEventListener('orientationchange', handleNavViewportChange);
    setNavOpen(false);

    // Header state and active navigation
    const header = document.querySelector('.site-header');
    const onScroll = () => header?.classList.toggle('scrolled', window.scrollY > 18);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });

    // Category filtering
    const filterButtons = document.querySelectorAll('[data-filter]');
    const cards = document.querySelectorAll('.menu-card[data-category]');
    const filterEmpty = document.getElementById('filter-empty');
    const menuGrid = document.getElementById('menu-grid');
    const activeFilterLabel = document.getElementById('active-filter-label');
    const visibleMenuCount = document.getElementById('visible-menu-count');
    const totalMenuCount = document.getElementById('total-menu-count');
    const loadMoreButton = document.getElementById('menu-load-more');
    const remainingMenuCount = document.getElementById('remaining-menu-count');
    const menuSearch = document.getElementById('menu-search');
    const pageSize = Math.max(1, Number(menuGrid?.dataset.pageSize) || 6);
    let currentFilter = 'all';
    let visibleLimit = pageSize;
    const applyFilter = (filter, {
        scrollToMenu = false,
        source = null,
        resetLimit = true,
    } = {}) => {
        currentFilter = filter;
        if (resetLimit) visibleLimit = pageSize;
        const searchTerm = (menuSearch?.value || '').trim().toLocaleLowerCase();
        filterButtons.forEach(button => {
            const active = button.dataset.filter === filter;
            button.classList.toggle('active', active);
            button.setAttribute('aria-pressed', String(active));
        });
        const matchingCards = [...cards].filter(card => {
            const matchesCategory = filter === 'all' || card.dataset.category === filter;
            const matchesSearch = !searchTerm || (card.dataset.search || card.textContent)
                .toLocaleLowerCase()
                .includes(searchTerm);
            return matchesCategory && matchesSearch;
        });
        cards.forEach(card => card.classList.add('is-hidden'));
        const visibleCards = matchingCards.slice(0, visibleLimit);
        visibleCards.forEach(card => card.classList.remove('is-hidden'));
        const visibleCount = visibleCards.length;
        const totalCount = matchingCards.length;
        const remainingCount = Math.max(0, totalCount - visibleCount);
        const labelSource = source || [...filterButtons].find(button => (
            button.dataset.filter === filter && button.dataset.filterLabel
        ));
        if (activeFilterLabel && labelSource?.dataset.filterLabel) {
            activeFilterLabel.textContent = labelSource.dataset.filterLabel;
        }
        if (visibleMenuCount) visibleMenuCount.textContent = visibleCount;
        if (totalMenuCount) totalMenuCount.textContent = totalCount;
        if (remainingMenuCount) remainingMenuCount.textContent = remainingCount;
        if (loadMoreButton) {
            const shouldShow = remainingCount > 0;
            loadMoreButton.classList.toggle('hidden', !shouldShow);
            loadMoreButton.hidden = !shouldShow;
        }
        if (filterEmpty) {
            const isEmpty = totalCount === 0;
            filterEmpty.classList.toggle('hidden', !isEmpty);
            filterEmpty.hidden = !isEmpty;
        }
        visibleCards.slice(0, 8).forEach((card, index) => {
            card.animate(
                [
                    {opacity: .25, transform: 'translateY(8px)'},
                    {opacity: 1, transform: 'translateY(0)'},
                ],
                {duration: 220, delay: index * 22, easing: 'ease-out'},
            );
        });
        source?.scrollIntoView?.({behavior: 'smooth', block: 'nearest', inline: 'center'});
        if (scrollToMenu && window.matchMedia('(max-width: 560px)').matches) {
            window.setTimeout(() => menuGrid?.scrollIntoView({behavior: 'smooth', block: 'start'}), 80);
        }
    };
    filterButtons.forEach(button => button.addEventListener('click', () => {
        if (button.dataset.clearSearch === 'true' && menuSearch) {
            menuSearch.value = '';
        }
        applyFilter(
            button.dataset.filter || 'all',
            {scrollToMenu: true, source: button},
        );
    }));
    document.querySelectorAll('[data-footer-filter]').forEach(link => link.addEventListener('click', () => {
        applyFilter(link.dataset.footerFilter || 'all', {scrollToMenu: true});
    }));
    loadMoreButton?.addEventListener('click', () => {
        visibleLimit += pageSize;
        applyFilter(currentFilter, {resetLimit: false});
        const lastVisibleCard = [...cards].filter(card => !card.classList.contains('is-hidden')).at(-1);
        lastVisibleCard?.focus?.({preventScroll: true});
    });
    menuSearch?.addEventListener('input', () => {
        const searchFilter = menuSearch.value.trim() ? 'all' : currentFilter;
        applyFilter(searchFilter, {resetLimit: true});
    });
    const initialFilter = [...filterButtons].find(button => button.classList.contains('active'));
    applyFilter(initialFilter?.dataset.filter || 'all');

    // Lightweight testimonial motion
    const reviewTrack = document.querySelector('.reviews-track');
    document.querySelector('.review-arrow.next')?.addEventListener('click', () => {
        const first = reviewTrack?.firstElementChild;
        if (!first) return;
        reviewTrack.append(first);
        first.animate([{opacity:.2, transform:'translateX(-18px)'},{opacity:1, transform:'translateX(0)'}], {duration:320, easing:'ease-out'});
    });
    document.querySelector('.review-arrow.prev')?.addEventListener('click', () => {
        const last = reviewTrack?.lastElementChild;
        if (!last) return;
        reviewTrack.prepend(last);
        last.animate([{opacity:.2, transform:'translateX(18px)'},{opacity:1, transform:'translateX(0)'}], {duration:320, easing:'ease-out'});
    });

    // Keep the active link aligned with the section that has reached the header.
    const navLinks = [...document.querySelectorAll('.main-nav a[href^="#"]')];
    const sectionLinks = navLinks
        .map(link => ({link, section: document.querySelector(link.getAttribute('href'))}))
        .filter(item => item.section);
    let navFrame = null;
    const updateActiveNav = () => {
        navFrame = null;
        if (!sectionLinks.length) return;
        const headerOffset = (header?.getBoundingClientRect().height || 0) + 24;
        const currentPosition = window.scrollY + headerOffset;
        let current = sectionLinks[0];
        sectionLinks.forEach(item => {
            if (item.section.offsetTop <= currentPosition) current = item;
        });
        navLinks.forEach(link => {
            const active = link === current.link;
            link.classList.toggle('active', active);
            if (active) link.setAttribute('aria-current', 'location');
            else link.removeAttribute('aria-current');
        });
    };
    const requestActiveNavUpdate = () => {
        if (navFrame !== null) return;
        navFrame = window.requestAnimationFrame(updateActiveNav);
    };
    updateActiveNav();
    window.addEventListener('scroll', requestActiveNavUpdate, {passive: true});
    window.addEventListener('resize', requestActiveNavUpdate, {passive: true});

    // FAQ accordion
    document.querySelectorAll('.faq-item button').forEach(button => {
        button.addEventListener('click', () => {
            const item = button.closest('.faq-item');
            const willOpen = !item.classList.contains('open');
            document.querySelectorAll('.faq-item.open').forEach(openItem => {
                openItem.classList.remove('open');
                openItem.querySelector('button')?.setAttribute('aria-expanded', 'false');
                openItem.querySelector('.faq-answer')?.setAttribute('aria-hidden', 'true');
            });
            item.classList.toggle('open', willOpen);
            button.setAttribute('aria-expanded', String(willOpen));
            item.querySelector('.faq-answer')?.setAttribute('aria-hidden', String(!willOpen));
        });
    });

    document.querySelector('.reservation-form')?.addEventListener('submit', event => {
        const submitButton = event.currentTarget.querySelector('button[type="submit"]');
        if (!submitButton || submitButton.disabled) return;
        submitButton.disabled = true;
        const label = submitButton.dataset.submitLabel;
        if (label) submitButton.querySelector('b').textContent = label;
    });

    // Reveal-on-scroll animations
    const revealElements = document.querySelectorAll('.reveal');
    if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -30px' });
        revealElements.forEach(element => observer.observe(element));
    } else {
        revealElements.forEach(element => element.classList.add('revealed'));
    }

    // Subtle hero parallax, disabled on touch/reduced motion
    const parallax = document.querySelector('.js-parallax');
    if (parallax && matchMedia('(pointer:fine)').matches && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
        parallax.addEventListener('pointermove', event => {
            const rect = parallax.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width - .5;
            const y = (event.clientY - rect.top) / rect.height - .5;
            parallax.style.transform = `perspective(900px) rotateY(${x * 4}deg) rotateX(${y * -4}deg)`;
        });
        parallax.addEventListener('pointerleave', () => parallax.style.transform = '');
    }

    window.addEventListener('keydown', event => {
        if (event.key === 'Escape' && getDrawer()?.classList.contains('is-open')) closeCart();
        else if (event.key === 'Escape' && nav?.classList.contains('open')) {
            setNavOpen(false);
            navToggle?.focus();
        }
        if (event.key === 'Tab' && getDrawer()?.classList.contains('is-open')) {
            const focusable = drawerFocusable();
            if (!focusable.length) return;
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        }
    });

    syncCartWithPage();
    saveCart();
    updateDeliveryFields();
    const refreshIcons = () => {
        if (!window.lucide?.createIcons) return;
        window.lucide.createIcons();
        document.documentElement.classList.add('icons-ready');
    };
    document.addEventListener('DOMContentLoaded', refreshIcons);
    window.addEventListener('load', refreshIcons);
})();
