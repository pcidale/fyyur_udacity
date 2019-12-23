
$(document).ready(function() {
    // Venue
    // Edit
    $(document.body).on('click', '#edit-venue', function(e) {
        window.location.replace('/venues/' + e.target.dataset['id'] + '/edit');
    });

    // Delete
    $(document.body).on('click', '.venue-btn-delete', function(e) {
        if (confirm('Are you sure you want to delete the venue ' + e.target.dataset['name'] + '?')) {
            $.ajax({
                url: '/venues/' + e.target.dataset['id'],
                type: 'DELETE',
                success: function(result) {
                    window.location.replace("/");	
                }
            });
        }
    });
    
    // Artist
    // Edit
    $(document.body).on('click', '#edit-artist', function(e) {
        window.location.replace('/artists/' + e.target.dataset['id'] + '/edit');
    });
});
