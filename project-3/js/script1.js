$(function() {

	$(".like-unlike").click(function() {

		var post_id = $(this).attr('post-id');
		var like_unlike = $(this).text();
		var post_likes = $(".likes_" + post_id).text();
		var post_likes_int = parseInt(post_likes);

		if (like_unlike === "Like") {
			$(this).text("Unlike");
			post_likes_int += 1;
			$(".likes_" + post_id).text(post_likes_int);
			$.ajax({
				url: "/blog/like/" + post_id,
				type: 'POST'
			});
		}

		else {
			$(this).text("Like");
			post_likes_int -= 1;
			$(".likes_" + post_id).text(post_likes_int);
			$.ajax({
				url: "/blog/like/" + post_id,
				type: 'DELETE'
			});
		}
	});	
})
