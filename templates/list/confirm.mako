<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

${ utils.bike(listing, hide_button=True) }

<div class="row">
    <div class="span7 box">
        <h1>list your bike</h1>
        <div class="span5 offset1">
            <form method="POST" id="kyc">
                ${ utils.csrf_token_input() | n }
                <p>We already have your details on file, click "confirm" to list this bike on Rentmybike for $${ listing.price } per rental.</p>
                <div class="actions">
                    <button class="btn btn-inverse">confirm</button>
                </div>
            </form>
        </div>
    </div>
</div>
