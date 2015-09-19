$(document).ready(function() {
	// scroll button hover
		$("#sec1-button").mouseover( function() {
		$(this).css("background-color", "rgba(255,255,255,0.1)");
		$(this).css("color", "rgba(12,134,241,1)");
		$(this).css("border", "1px solid rgba(12,134,241,0.8)");
		$(this).css("cursor", "pointer");
	});
	// scroll button unhover
		$("#sec1-button").mouseout( function() {
		$(this).css("background-color", "");
		$(this).css("color", "");
		$(this).css("border", "");
		$(this).css("cursor", "");
	});

	// scroll button hover
		$("#sec2-button").mouseover( function() {
		$(this).css("background-color", "rgba(255,255,255,0.1)");
		$(this).css("color", "rgba(12,134,241,1)");
		$(this).css("border", "1px solid rgba(12,134,241,0.8)");
		$(this).css("cursor", "pointer");
	});
	// scroll button unhover
		$("#sec2-button").mouseout( function() {
		$(this).css("background-color", "");
		$(this).css("color", "");
		$(this).css("border", "");
		$(this).css("cursor", "");
	});

	// scroll page down
	$("#sec1-button").click( function() {
		$("html, body").animate( {
        	scrollTop: $("#sec2").offset().top - 60
        }, 1000);
	});
	// scroll page down
	$("#sec2-button").click( function() {
		$("html, body").animate( {
        	scrollTop: $("#sec3").offset().top - 60
        }, 1000);
	});
	// nav home
	$("#nav-home").click( function() {
		$("html, body").animate( {
        	scrollTop: $("#sec1").offset().top - 60
        }, 1000);
	});
	// nav info
	$("#nav-info").click( function() {
		$("html, body").animate( {
        	scrollTop: $("#sec2").offset().top - 60
        }, 1000);
	});
	// nav signup
	$("#nav-signup").click( function() {
		$("html, body").animate( {
        	scrollTop: $("#sec3").offset().top - 60
        }, 1000);
	});
});

