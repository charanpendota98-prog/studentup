/* v201 — Latest Notifications sliding track (front page).
 *
 * Enduku: ee behaviour demo (preview/worldclass) lo inline script ga mattrame
 * undedi — theme ki eppudu raledu. Ippudu idhe file theme lo: auto-slide
 * (3.2s), prev/next/pause buttons, hover/touch pause, keyboard ←/→, tab
 * hidden aithe aagipothundi, `prefers-reduced-motion` unte auto-slide ledu.
 *
 * Ticker (su-t-prev/toggle/next) behaviour studentup-menu.js lo undi — ikkada
 * duplicate cheyyaledu. Bonus: "/" shortcut hero search ni focus chestundi
 * (demo lo unna `<kbd>/</kbd>` hint nijamga pani cheyyali).
 */
( function () {
	'use strict';

	function reducedMotion() {
		return !!( window.matchMedia && window.matchMedia( '(prefers-reduced-motion: reduce)' ).matches );
	}

	var track = document.getElementById( 'su-jobs-track-wrap' );
	if ( track ) {
		var STEP = 310;
		var running = true;
		var timer = null;

		function behavior() {
			return reducedMotion() ? 'auto' : 'smooth';
		}

		function slide( dir ) {
			track.scrollBy( { left: dir * STEP, behavior: behavior() } );
		}

		function tick() {
			if ( track.scrollLeft + track.clientWidth >= track.scrollWidth - 10 ) {
				track.scrollTo( { left: 0, behavior: behavior() } );
			} else {
				slide( 1 );
			}
		}

		function stop() {
			if ( timer ) {
				window.clearInterval( timer );
				timer = null;
			}
		}

		function start() {
			if ( timer || reducedMotion() || ! running ) {
				return;
			}
			timer = window.setInterval( tick, 3200 );
		}

		start();
		track.addEventListener( 'mouseenter', stop );
		track.addEventListener( 'mouseleave', start );
		track.addEventListener( 'focusin', stop );
		track.addEventListener( 'focusout', start );
		track.addEventListener( 'touchstart', stop, { passive: true } );
		track.addEventListener( 'touchend', start, { passive: true } );
		document.addEventListener( 'visibilitychange', function () {
			if ( document.hidden ) {
				stop();
			} else {
				start();
			}
		} );

		track.addEventListener( 'keydown', function ( event ) {
			if ( event.key === 'ArrowRight' ) {
				stop();
				slide( 1 );
			} else if ( event.key === 'ArrowLeft' ) {
				stop();
				slide( -1 );
			}
		} );

		var nextBtn = document.getElementById( 'su-track-next' );
		if ( nextBtn ) {
			nextBtn.addEventListener( 'click', function () {
				stop();
				slide( 1 );
			} );
		}

		var prevBtn = document.getElementById( 'su-track-prev' );
		if ( prevBtn ) {
			prevBtn.addEventListener( 'click', function () {
				stop();
				slide( -1 );
			} );
		}
		/* v202 FIX: pause/play (⏸) button removed from markup (owner feedback) —
		 * track still auto-pauses on hover/touch/focus/visibility change above. */

		/* v209: dot indicators (Eenadu hero-slider pattern) — active dot scroll ni
		 * follow chestundi (auto-slide, prev/next, swipe — anni); dot tap cheste
		 * aa card ki smooth scroll. Post count marithe dots automatic ga adjust. */
		var dotWrap = document.querySelector( '.su-sdots' );
		if ( dotWrap ) {
			var dots = dotWrap.querySelectorAll( '.su-sdot' );
			if ( dots.length ) {
				var firstCard = track.firstElementChild;
				function cardStep() {
					if ( ! firstCard ) {
						return STEP;
					}
					var cs = window.getComputedStyle( firstCard.parentNode );
					var gap = parseFloat( cs.columnGap || cs.gap || '0' ) || 0;
					return firstCard.getBoundingClientRect().width + gap;
				}
				function paintDots() {
					var step = cardStep();
					var on = step > 0 ? Math.max( 0, Math.min( dots.length - 1, Math.round( track.scrollLeft / step ) ) ) : 0;
					Array.prototype.forEach.call( dots, function ( d, i ) {
						d.classList.toggle( 'on', i === on );
						d.setAttribute( 'aria-selected', i === on ? 'true' : 'false' );
					} );
				}
				paintDots();
				var raf = null;
				track.addEventListener( 'scroll', function () {
					if ( raf ) {
						return;
					}
					raf = window.requestAnimationFrame( function () {
						raf = null;
						paintDots();
					} );
				}, { passive: true } );
				window.addEventListener( 'resize', paintDots );
				Array.prototype.forEach.call( dots, function ( d, i ) {
					d.addEventListener( 'click', function () {
						stop();
						track.scrollTo( { left: i * cardStep(), behavior: behavior() } );
						paintDots();
						start();
					} );
				} );
			}
		}
	}

	/* "/" → hero search (typing lo unte vaddu). */
	var search = document.querySelector( '.su-hero-search input[type="search"]' );
	if ( search ) {
		document.addEventListener( 'keydown', function ( event ) {
			if ( event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey ) {
				return;
			}
			var el = event.target;
			var tag = el && el.tagName ? el.tagName.toLowerCase() : '';
			if ( tag === 'input' || tag === 'textarea' || tag === 'select' || ( el && el.isContentEditable ) ) {
				return;
			}
			event.preventDefault();
			search.focus();
		} );
	}
}() );
