<%inherit file="/base.mako" />
<%namespace name="utils" file="/_utils.mako" />

<div class="row">
    <div class="span7 box">
        <h1>fill out your payment details</h1>
        <div class="span6 offset1">
            <form method="POST" id="kyc">
                ${ utils.csrf_token_input() | n }
                <div class="actions">
                    <button class="btn btn-inverse">save</button>
                </div>
            </form>
        </div>
    </div>
</div>
