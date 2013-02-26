<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

${ utils.bike(listing, hide_button=True) }

<div class="row">
    <div class="span7 box">
        <h1>you have completed the demo!</h1>
        <p class="swell">Your card ending in ${ charge.source.last_four } has
            been authorized for $${ listing.price }.00 as a demonstration, but it
            will not actually be charged.</p>
        <p class="swell">Start integrating payments by visiting
            <a href="https://www.balancedpayments.com">balancedpayments.com</a></p>
    </div>
</div>
