<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

${ utils.bike(listing, hide_button=True) }

<div class="row">
    <div class="span7 box">
        <h1>you are now a merchant!</h1>
        <div class="swell">
            <p>Rentmybike is a demo marketplace for Balanced. You are now able
                to sell on any marketplace powered by Balanced.</p>
            <p>Start integrating payments by visiting
                <a href="https://www.balancedpayments.com">balancedpayments.com</a></p>
        </div>
    </div>
</div>
