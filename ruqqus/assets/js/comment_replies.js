// https://stackoverflow.com/a/42183824/11724748

/*
function toggleDropdown(e) {
    const _d = $(e.target).closest('.dropdown'),
        _m = $('.dropdown-menu', _d);
    setTimeout(function () {
        const shouldOpen = e.type !== 'click' && _d.is(':hover');
        _m.toggleClass('show', shouldOpen);
        _d.toggleClass('show', shouldOpen);
        $('[data-toggle="dropdown"]', _d).attr('aria-expanded', shouldOpen);
    }, e.type === 'mouseleave' ? 150 : 0);
}

// Display profile card on hover

$('body')
    .on('mouseenter mouseleave', '.user-profile', toggleDropdown)
    .on('click', '.dropdown-menu a', toggleDropdown);

// Toggle comment collapse

$(".toggle-collapse").click(function (event) {
    event.preventDefault();

    var id = $(this).parent().attr("id");

    document.getElementById(id).classList.toggle("collapsed");
});
*/
// Reply to parent comment

function addReplyForm(commentId, postId) {

    var id = "reply-to-" + commentId;

    document.getElementById(id).innerHTML = '<div class="comment-write child"> <form id="reply-to-t3_'+commentId+'" action="/api/comment" method="post" class="input-group"> <input type="hidden" name="formkey" value="'+formkey()+'"> <input type="hidden" name="parent_fullname" value="t3_'+commentId+'"> <input type="hidden" name="submission" value="'+postId+'"> <textarea name="body" form="reply-to-t3_'+commentId+'" class="form-control rounded" aria-label="With textarea" placeholder="Add your comment..." rows="7"></textarea> <div class="bg-light comment-format"> <small class="format"><i class="fas fa-bold" aria-hidden="true"></i></small> <small class="format"><i class="fas fa-italic" aria-hidden="true"></i></small> <small class="format"><i class="fas fa-quote-right" aria-hidden="true"></i></small> <small class="format"><i class="fas fa-link" aria-hidden="true"></i></small> <button onclick="delReplyForm('+commentId+')" class="btn btn-link text-danger ml-auto cancel-form">Cancel</button> <button form="reply-to-t3_'+commentId+'" class="btn btn-primary ml-2">Comment</button> </div> </form> </div>';

}

    // Removes reply form innerHTML on click

function delReplyForm(commentId) {

    var id = "reply-to-" + commentId;

    document.getElementById(id).innerHTML = '';

};
