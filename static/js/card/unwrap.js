$(document).ready(function(){
	$('.obscurer').bind("click",function(){
		$(this).removeClass("obscurer");
		$(this).addClass("revealer");
	});
});
