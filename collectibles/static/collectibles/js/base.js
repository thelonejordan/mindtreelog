// Base JavaScript for all collection types

// Load saved view preference or default to list view
function loadViewPreference() {
    const savedView = localStorage.getItem('videoView') || 'list';
    setView(savedView);
}

function setView(view) {
    const videoList = document.getElementById('videoList');
    const cardBtn = document.getElementById('cardViewBtn');
    const listBtn = document.getElementById('listViewBtn');
    const collectionType = videoList.dataset.collectionType;

    if (view === 'card') {
        videoList.classList.remove('list-view');
        videoList.classList.add('card-view');
        cardBtn.classList.add('active');
        listBtn.classList.remove('active');

        // For Twitter, calculate masonry grid spans after a delay
        if (collectionType === 'twitter' && typeof updateTwitterCardSpans === 'function') {
            setTimeout(updateTwitterCardSpans, 500);
        }
    } else {
        videoList.classList.remove('card-view');
        videoList.classList.add('list-view');
        listBtn.classList.add('active');
        cardBtn.classList.remove('active');
    }

    // Save preference
    localStorage.setItem('videoView', view);
}

// Collection switcher
function switchCollection(type) {
    window.location.href = `/collections/${type}`;
}

// Modal functions
function openModal() {
    document.getElementById('addVideoModal').classList.add('show');
    document.getElementById('item_url').focus();
}

function closeModal() {
    document.getElementById('addVideoModal').classList.remove('show');
    document.getElementById('item_url').value = '';
}

function closeModalOnOutsideClick(event) {
    if (event.target.id === 'addVideoModal') {
        closeModal();
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key to close modal
    if (e.key === 'Escape') {
        closeModal();
    }
    // Ctrl/Cmd + K to open modal
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        openModal();
    }
});

// Auto-dismiss messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    loadViewPreference();

    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    });
});
