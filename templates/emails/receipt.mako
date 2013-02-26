<%inherit file="/emails/base.mako" />

<p>Hello ${ name },</p>

<p>Thanks for renting this bike with Rent My Bike.</p>

<p>Your card ending in ${ charge.source.last_four } has
    been authorized for $${ listing.price }.00 as a demonstration, but it
    will not actually be charged.</p>
<p>Start integrating payments by visiting
    <a href="https://www.balancedpayments.com">balancedpayments.com</a></p>
