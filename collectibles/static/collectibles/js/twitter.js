// Twitter-specific JavaScript for masonry layout and widget loading

// Calculate and set grid row spans for Twitter cards (masonry layout)
function updateTwitterCardSpans() {
    const videoList = document.getElementById('videoList');
    if (!videoList || !videoList.classList.contains('card-view') || !videoList.classList.contains('twitter-list')) {
        return;
    }

    const items = videoList.querySelectorAll('.video-item');
    const rowHeight = 20; // Must match grid-auto-rows in CSS
    const maxCardHeight = 650; // Max height for embedded tweets in card view

    items.forEach(item => {
        const height = Math.min(item.offsetHeight, maxCardHeight + 100); // +100 for buttons/padding
        const rowSpan = Math.ceil((height + 16) / rowHeight); // +16 for gap
        item.style.setProperty('--row-span', rowSpan);
    });

    console.log(`Updated ${items.length} Twitter card spans`);
}

// Load Twitter widgets for embedded tweets
function loadTwitterWidgets() {
    if (typeof twttr !== 'undefined' && twttr.widgets) {
        console.log('Loading Twitter widgets...');
        twttr.widgets.load(document.getElementById('videoList')).then(function() {
            console.log('✓ Twitter widgets loaded successfully');
            // Update card spans multiple times as content loads
            setTimeout(updateTwitterCardSpans, 500);
            setTimeout(updateTwitterCardSpans, 1500);
            setTimeout(updateTwitterCardSpans, 3000);
            // Final update for late-loading images
            setTimeout(updateTwitterCardSpans, 5000);
        }).catch(function(error) {
            console.error('✗ Failed to load Twitter widgets:', error);
        });
    } else {
        console.log('Waiting for Twitter widgets.js...');
        setTimeout(loadTwitterWidgets, 100);
    }
}

// Handle Twitter widget events for dynamic span updates
if (typeof twttr !== 'undefined') {
    twttr.events.bind('rendered', function(event) {
        console.log('Twitter widget rendered:', event.target);
        // Update immediately and again after a short delay
        updateTwitterCardSpans();
        setTimeout(updateTwitterCardSpans, 500);
    });

    twttr.events.bind('loaded', function(event) {
        console.log('Twitter widget loaded:', event.widgets);
        setTimeout(updateTwitterCardSpans, 300);
    });
}

// Initialize Twitter widgets after DOM loads
document.addEventListener('DOMContentLoaded', function() {
    loadTwitterWidgets();

    // Update spans on window resize (debounced)
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(updateTwitterCardSpans, 250);
    });
});
